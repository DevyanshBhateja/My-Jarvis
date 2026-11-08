"""Streaming Coqui XTTS v2 TTS with chunked playback and cancellation."""

from __future__ import annotations

import io
import numpy as np
import os
import queue
import re
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from typing import Callable, Optional
from shutil import which

try:
    from TTS.api import TTS
except ImportError:
    TTS = None


def _pick_player() -> list[str]:
    """Find available audio player (pw-play, paplay, ffplay, or mpg123)."""
    # Prefer PipeWire/PulseAudio native players for better integration
    for command in (
        ("pw-play",),
        ("paplay",),
        ("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-volume", "80", "-nostdin"),
        ("mpg123", "-q")
    ):
        if which(command[0]) is not None:
            print(f"[COQUI-TTS] Found audio player: {command[0]}")
            return list(command)
    raise RuntimeError("No supported audio player found. Install pw-play, paplay, ffmpeg/ffplay, or mpg123.")


class _TextChunker:
    """Split incoming text into sentence chunks for streaming TTS."""
    
    def __init__(self, max_chars: int = 140):
        self.max_chars = max_chars
        self.buffer = ""

    def feed(self, text: str) -> list[str]:
        """Feed text incrementally, return ready chunks."""
        self.buffer += text
        ready: list[str] = []
        while True:
            chunk, remainder = self._extract_chunk(self.buffer)
            if chunk is None:
                break
            ready.append(chunk)
            self.buffer = remainder
        return ready

    def flush(self) -> str:
        """Flush remaining buffered text."""
        text = self.buffer.strip()
        self.buffer = ""
        return text

    def _extract_chunk(self, text: str) -> tuple[str | None, str]:
        """Extract one sentence or max_chars chunk."""
        stripped = text.lstrip()
        if not stripped:
            return None, ""
        text = stripped

        # Look for sentence boundary
        sentence_match = re.search(r"[.!?]+(?:\s|$)", text)
        if sentence_match:
            end = sentence_match.end()
            return text[:end].strip(), text[end:]

        # Not enough for max_chars yet
        if len(text) < self.max_chars:
            return None, text

        # Split at word boundary
        split_at = text.rfind(" ", 0, self.max_chars)
        if split_at <= 0:
            split_at = self.max_chars
        return text[:split_at].strip(), text[split_at:]


def _float32_to_wav_bytes(audio: np.ndarray, sample_rate: int = 22050) -> bytes:
    """Convert float32 audio array to WAV bytes."""
    import wave
    
    # Ensure audio is float32 in range [-1, 1]
    if audio.dtype != np.float32:
        audio = audio.astype(np.float32)
    
    # Clip to [-1, 1] range
    audio = np.clip(audio, -1.0, 1.0)
    
    # Convert to int16
    audio_int16 = (audio * 32767).astype(np.int16)
    
    # Write to WAV in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())
    
    wav_buffer.seek(0)
    return wav_buffer.read()


def _int16_to_wav_bytes(int16_array: np.ndarray, sample_rate: int = 22050) -> bytes:
    """Convert int16 numpy array to WAV bytes (mono)."""
    import wave
    
    if int16_array.dtype != np.int16:
        int16_array = int16_array.astype(np.int16)
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(int16_array.tobytes())
    
    wav_buffer.seek(0)
    return wav_buffer.read()


@dataclass
class StreamingCoquiTtsSession:
    """Manages a Coqui XTTS v2 TTS session with streaming playback."""
    
    tts_engine: object  # TTS instance
    speaker_wav: str | None  # Path to speaker WAV for voice cloning (optional)
    cancel_event: threading.Event
    state: object | None = None
    on_start: Optional[Callable[[], None]] = None
    on_end: Optional[Callable[[], None]] = None
    max_chunk_chars: int = 140
    language: str = "en"

    def __post_init__(self) -> None:
        self._chunker = _TextChunker(max_chars=self.max_chunk_chars)
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._started = False
        self._process_lock = threading.Lock()
        self._process: subprocess.Popen | None = None
        self._player = _pick_player()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def feed(self, text: str) -> None:
        """Feed text for TTS synthesis. Chunks are queued for playback."""
        if self.cancel_event.is_set():
            return
        for chunk in self._chunker.feed(text):
            self._queue.put(chunk)

    def finish(self) -> None:
        """Finish TTS session and wait for all buffered audio to play."""
        if self.cancel_event.is_set():
            if self._worker.is_alive():
                self._worker.join(timeout=1.0)
            return

        if not self.cancel_event.is_set():
            remainder = self._chunker.flush()
            if remainder:
                self._queue.put(remainder)
        self._queue.put(None)
        self._queue.join()
        if self._worker.is_alive():
            self._worker.join()

    def cancel(self) -> None:
        """Cancel TTS session immediately."""
        self.cancel_event.set()
        with self._process_lock:
            process = self._process
        if process is not None and process.poll() is None:
            process.kill()

        while True:
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break
        self._worker.join(timeout=1.0)

    def _set_state(self, speaking: bool) -> None:
        """Update state to mark speaking/not speaking."""
        if self.state is not None and hasattr(self.state, "mark_speaking"):
            self.state.mark_speaking(speaking)

    def _synthesize_and_play(self, text: str) -> None:
        """Synthesize text with Coqui XTTS v2 and play audio."""
        if not text.strip() or self.cancel_event.is_set():
            return

        try:
            print(f"[COQUI-TTS] Synthesizing: {text[:80]}")
            
            # Detect model sample rate dynamically (XTTS v2 is 24000, older models are 22050)
            sample_rate = 24000
            if hasattr(self.tts_engine, "synthesizer") and hasattr(self.tts_engine.synthesizer, "output_sample_rate"):
                sample_rate = self.tts_engine.synthesizer.output_sample_rate

            try:
                wav = self.tts_engine.tts(
                    text=text,
                    language=self.language,
                    speaker_wav=self.speaker_wav,
                )
            except ValueError as e:
                msg = str(e).lower()
                if "multi" in msg and "language" in msg or "not multi" in msg:
                    print("[COQUI-TTS] Model rejected 'language' param; retrying without it")
                    wav = self.tts_engine.tts(text=text, speaker_wav=self.speaker_wav)
                else:
                    raise
            
            if self.cancel_event.is_set():
                return
            
            # Normalize raw output to a 1D float32 numpy array
            if hasattr(wav, "detach"):  # torch.Tensor
                wav = wav.detach().cpu().numpy()
            elif isinstance(wav, list):
                wav = np.array(wav, dtype=np.float32)
            elif isinstance(wav, np.ndarray):
                wav = wav.astype(np.float32)
            
            # Convert to valid 16-bit PCM WAV bytes
            if isinstance(wav, np.ndarray):
                audio_bytes = _float32_to_wav_bytes(wav.squeeze(), sample_rate=sample_rate)
            elif isinstance(wav, (bytes, bytearray)):
                audio_bytes = wav
            else:
                raise TypeError(f"Unsupported audio output type: {type(wav).__name__}")
            
            # Write to temporary file and play
            fd, path = tempfile.mkstemp(suffix=".wav", prefix="jarvis_coqui_")
            os.close(fd)
            
            try:
                with open(path, 'wb') as f:
                       f.write(audio_bytes)
                
                if self.cancel_event.is_set():
                    return
                
                if not self._started:
                    self._started = True
                    self._set_state(True)
                    if self.on_start is not None:
                        self.on_start()
                
                print(f"[COQUI-TTS] Playing audio ({len(audio_bytes)} bytes)")
                process = subprocess.Popen(
                    self._player + [path],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
                with self._process_lock:
                    self._process = process
                
                try:
                    while process.poll() is None:
                        if self.cancel_event.wait(0.05):
                            process.kill()
                            break
                finally:
                    with self._process_lock:
                        self._process = None
                    returncode = process.poll()
                    if returncode is None:
                        process.kill()
                        returncode = process.wait(timeout=1.0)
                    
                    if returncode != 0:
                        stderr_output = process.stderr.read().decode('utf-8', errors='replace') if process.stderr else ""
                        print(f"[WARN] Player exited with code {returncode}. stderr: {stderr_output[:200]}")
                    else:
                        print(f"[COQUI-TTS] Player finished successfully (rc={returncode})")
            finally:
                   try:
                       os.unlink(path)
                   except FileNotFoundError:
                       pass
        
        except Exception as e:
            print(f"[ERROR] Coqui TTS synthesis/playback failed: {e}")
            import traceback
            traceback.print_exc()

    def _run(self) -> None:
        """Worker thread main loop."""
        try:
            while not self.cancel_event.is_set():
                try:
                    chunk = self._queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                if chunk is None:
                    self._queue.task_done()
                    break
                
                try:
                    self._synthesize_and_play(chunk)
                except Exception as e:
                    print(f"[ERROR] TTS chunk processing failed: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    self._queue.task_done()
        
        except Exception as e:
            print(f"[ERROR] Coqui TTS session worker crashed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self._set_state(False)
            if self.on_end is not None:
                self.on_end()


class CoquiXTTSPlayer:
    """Coqui XTTS v2 player with streaming support."""
    
    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/xtts_v2",
        gpu: bool = True,
        speaker_wav: str | None = None,
        language: str = "en"
    ):
        """
        Initialize Coqui XTTS v2 player.
        
        Args:
            model_name: Coqui model identifier (default: tts_models/en/ljspeech/xtts_v2)
            gpu: Use GPU if available (default: True)
            speaker_wav: Optional path to speaker WAV for voice cloning
            language: Language code for TTS (default: "en")
        """
        if TTS is None:
            raise RuntimeError(
                "Coqui TTS not installed. Install with: pip install TTS"
            )
        
        device = "cuda" if gpu else "cpu"
        # Allow overriding model via env var for different TTS installations
        env_model = os.getenv("JARVIS_COQUI_MODEL")
        candidates = []
        if model_name:
            candidates.append(model_name)
        if env_model and env_model not in candidates:
            candidates.append(env_model)
        # Common fallbacks if xtts_v2 isn't available in this TTS installation
        for fallback in (
            "tts_models/en/ljspeech/vits",
            "tts_models/en/vctk/vits",
            "tts_models/en/ljspeech/tacotron2-DDC",
        ):
            if fallback not in candidates:
                candidates.append(fallback)

        last_exc: Exception | None = None
        self.model_name = None
        print(f"[COQUI-TTS] Attempting to load Coqui TTS model on {device}. Candidates: {candidates}")
        for candidate in candidates:
            try:
                print(f"[COQUI-TTS] Trying model: {candidate}")
                self.tts = TTS(model_name=candidate, gpu=gpu, progress_bar=True)
                self.model_name = candidate
                print(f"[COQUI-TTS] Successfully loaded model: {candidate}")
                break
            except KeyError as e:
                print(f"[COQUI-TTS] Model key error for {candidate}: {e}")
                last_exc = e
            except Exception as e:
                print(f"[COQUI-TTS] Failed to load model {candidate}: {e}")
                last_exc = e

        if self.model_name is None:
            raise RuntimeError(
                "Failed to load any Coqui TTS model from candidates: " + ", ".join(candidates)
            ) from last_exc
        self.speaker_wav = speaker_wav
        self.language = language
        # Newer TTS versions recommend using .to(device)
        try:
            if hasattr(self.tts, "to"):
                self.tts.to(device)
        except Exception:
            # Non-fatal; GPU migration handled by constructor in many versions
            pass
        print(f"[COQUI-TTS] Model loaded successfully: {self.model_name}")

    def start_session(
        self,
        cancel_event: threading.Event,
        state: object | None = None,
        on_start: Optional[Callable[[], None]] = None,
        on_end: Optional[Callable[[], None]] = None,
    ) -> StreamingCoquiTtsSession:
        """Start a new streaming TTS session."""
        return StreamingCoquiTtsSession(
            tts_engine=self.tts,
            speaker_wav=self.speaker_wav,
            cancel_event=cancel_event,
            state=state,
            on_start=on_start,
            on_end=on_end,
            language=self.language
        )

    def speak(
        self,
        text: str,
        cancel_event: Optional[threading.Event] = None,
        on_start: Optional[Callable[[], None]] = None,
        on_end: Optional[Callable[[], None]] = None,
    ) -> None:
        """Synthesize and play text synchronously."""
        if not text or not text.strip():
            return
        cancel = cancel_event or threading.Event()
        session = self.start_session(
            cancel_event=cancel,
            on_start=on_start,
            on_end=on_end,
        )
        session.feed(text)
        session.finish()
