"""Chunked, cancelable Edge TTS playback."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import os
import queue
import re
import subprocess
import tempfile
import threading
from typing import Callable, Optional
from shutil import which

import edge_tts


def _pick_player() -> list[str]:
    for command in (("mpg123", "-q"), ("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet")):
        if which(command[0]) is not None:
            print(f"[TTS] Found audio player: {command[0]}")
            return list(command)
    raise RuntimeError("No supported audio player found. Install mpg123 or ffmpeg/ffplay.")


class _TextChunker:
    def __init__(self, max_chars: int = 140):
        self.max_chars = max_chars
        self.buffer = ""

    def feed(self, text: str) -> list[str]:
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
        text = self.buffer.strip()
        self.buffer = ""
        return text

    def _extract_chunk(self, text: str) -> tuple[str | None, str]:
        stripped = text.lstrip()
        if not stripped:
            return None, ""
        text = stripped

        sentence_match = re.search(r"[.!?]+(?:\s|$)", text)
        if sentence_match:
            end = sentence_match.end()
            return text[:end].strip(), text[end:]

        if len(text) < self.max_chars:
            return None, text

        split_at = text.rfind(" ", 0, self.max_chars)
        if split_at <= 0:
            split_at = self.max_chars
        return text[:split_at].strip(), text[split_at:]


async def _save_edge_tts(text: str, voice: str, output_path: str) -> None:
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(output_path)


@dataclass
class StreamingTtsSession:
    voice: str
    cancel_event: threading.Event
    state: object | None = None
    on_start: Optional[Callable[[], None]] = None
    on_end: Optional[Callable[[], None]] = None
    max_chunk_chars: int = 140

    def __post_init__(self) -> None:
        self._chunker = _TextChunker(max_chars=self.max_chunk_chars)
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._started = False
        self._player = _pick_player()
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def feed(self, text: str) -> None:
        if self.cancel_event.is_set():
            return
        for chunk in self._chunker.feed(text):
            self._queue.put(chunk)

    def finish(self) -> None:
        if not self.cancel_event.is_set():
            remainder = self._chunker.flush()
            if remainder:
                self._queue.put(remainder)
        self._queue.put(None)
        self._worker.join()

    def cancel(self) -> None:
        self.cancel_event.set()
        self._queue.put(None)
        self._worker.join(timeout=1.0)

    def _set_state(self, speaking: bool) -> None:
        if self.state is not None and hasattr(self.state, "mark_speaking"):
            self.state.mark_speaking(speaking)

    def _play_chunk(self, text: str) -> None:
        if not text.strip() or self.cancel_event.is_set():
            return

        fd, path = tempfile.mkstemp(suffix=".mp3", prefix="jarvis_tts_")
        os.close(fd)
        try:
            asyncio.run(_save_edge_tts(text, self.voice, path))
            if self.cancel_event.is_set():
                return

            if not self._started:
                self._started = True
                self._set_state(True)
                if self.on_start is not None:
                    self.on_start()

            process = subprocess.Popen(self._player + [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                while process.poll() is None:
                    if self.cancel_event.wait(0.05):
                        process.kill()
                        break
            finally:
                if process.poll() is None:
                    process.kill()
        finally:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass

    def _run(self) -> None:
        try:
            while not self.cancel_event.is_set():
                try:
                    chunk = self._queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                if chunk is None:
                    break
                try:
                    self._play_chunk(chunk)
                except Exception as e:
                    print(f"[ERROR] TTS playback failed: {e}")
                    import traceback
                    traceback.print_exc()
        except Exception as e:
            print(f"[ERROR] TTS session worker crashed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._set_state(False)
            if self.on_end is not None:
                self.on_end()


class ChunkedEdgeTTSPlayer:
    def __init__(self, voice: str = "en-US-GuyNeural"):
        self.voice = voice

    def start_session(
        self,
        cancel_event: threading.Event,
        state: object | None = None,
        on_start: Optional[callable] = None,
        on_end: Optional[callable] = None,
    ) -> StreamingTtsSession:
        return StreamingTtsSession(
            voice=self.voice,
            cancel_event=cancel_event,
            state=state,
            on_start=on_start,
            on_end=on_end,
        )

    def speak_text(self, text: str) -> None:
        cancel_event = threading.Event()
        session = self.start_session(cancel_event)
        try:
            session.feed(text)
            session.finish()
        finally:
            session.cancel()