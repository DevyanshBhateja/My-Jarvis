"""Full-duplex interaction orchestrator for streaming, interruptible Jarvis."""

from __future__ import annotations

import asyncio
import queue
import re
import threading
import time
import traceback
from dataclasses import dataclass, field
from typing import Callable, Optional
from threading import RLock, Event

from .action_executor import confirm_and_execute, format_action_result_speech
from .action_protocol import ActionRequest, parse_action_from_llm
from .coqui_tts import CoquiXTTSPlayer, StreamingCoquiTtsSession
from .llm_stream import LLMRouter
from .mic_stream import MicrophoneStream
from .state import AssistantState
from .transcription import WhisperTranscriber
from .vad import AudioEventKind, VadConfig, VoiceActivityCollector

try:
    from jarvis_ui.state_bridge import ui_bridge
except ImportError:
    class _DummyUIBridge:
        def set_state(self, *a, **k): pass
        def set_engine(self, *a, **k): pass
        def post_user_speech(self, *a, **k): pass
        def post_jarvis_speech(self, *a, **k): pass
        def post_action(self, *a, **k): pass
        def clear_dialogue(self, *a, **k): pass
    ui_bridge = _DummyUIBridge()


@dataclass
class OrchestrationState:
    """Thread-safe shared state for orchestrator."""
    
    is_listening: bool = True
    is_speaking: bool = False
    user_interrupt_requested: bool = False
    current_utterance_id: str = ""
    actions_in_progress: list = field(default_factory=list)
    _lock: RLock = field(default_factory=RLock)

    def acquire(self) -> RLock:
        """Get lock for safe state updates."""
        return self._lock

    def set_speaking(self, speaking: bool) -> None:
        with self._lock:
            self.is_speaking = speaking
            self.is_listening = not speaking

    def request_interrupt(self) -> None:
        with self._lock:
            self.user_interrupt_requested = True

    def clear_interrupt(self) -> None:
        with self._lock:
            self.user_interrupt_requested = False

    def is_interrupted(self) -> bool:
        with self._lock:
            return self.user_interrupt_requested

    def new_utterance(self, uid: str) -> None:
        with self._lock:
            self.current_utterance_id = uid
            self.user_interrupt_requested = False


@dataclass
class TTSChunk:
    """Text chunk to synthesize and play."""
    text: str
    utterance_id: str


class InteractionOrchestrator:
    """Orchestrates full-duplex conversation with streaming TTS, barge-in, and parallel action execution."""

    def __init__(
        self,
        mic: MicrophoneStream,
        vad: VoiceActivityCollector,
        transcriber: WhisperTranscriber,
        llm_router: LLMRouter,
        tts_client: CoquiXTTSPlayer,
        assistant_state: AssistantState,
    ):
        self.mic = mic
        self.vad = vad
        self.transcriber = transcriber
        self.llm_router = llm_router
        self.tts_client = tts_client
        self.assistant_state = assistant_state

        self.orch_state = OrchestrationState()
        self.stop_event = Event()

        # Queues for inter-loop communication
        self.utterance_queue: queue.Queue[str | None] = queue.Queue(maxsize=10)
        self.tts_chunk_queue: queue.Queue[TTSChunk | None] = queue.Queue(maxsize=50)
        self.action_queue: queue.Queue[ActionRequest | None] = queue.Queue(maxsize=20)

        # TTS state
        self._current_tts_session: Optional[StreamingCoquiTtsSession] = None
        self._tts_session_lock = RLock()

        # LLM state
        self._llm_cancel_event = Event()
        self._speaking_since: float | None = None

        # Threads
        self._threads: dict[str, threading.Thread] = {}

    def start_conversation_loop(self) -> None:
        """Start the full-duplex conversation orchestrator."""
        print("[ORCH] Starting full-duplex orchestrator...")
        self.stop_event.clear()

        try:
            self.mic.start()
            print("[ORCH] Microphone stream started")
        except Exception as e:
            print(f"[ERROR] Failed to start microphone: {e}")
            traceback.print_exc()
            return

        # Start all worker threads
        threads_config = [
            ("listen", self._listen_loop),
            ("converse", self._converse_loop),
            ("speak", self._speak_loop),
            ("action", self._action_loop),
        ]

        for name, target in threads_config:
            thread = threading.Thread(target=target, daemon=True, name=f"Orch{name.capitalize()}")
            thread.start()
            self._threads[name] = thread
            print(f"[ORCH] {name.capitalize()} loop started")

        print("[ORCH] All loops started. Listening for speech...")

        try:
            while not self.stop_event.is_set():
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n[ORCH] Interrupt received, shutting down...")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Gracefully shut down orchestrator."""
        with self.orch_state.acquire():
            if getattr(self, "_shutdown_done", False):
                return
            self._shutdown_done = True

        print("[ORCH] Shutting down...")
        self.stop_event.set()

        # Cancel current TTS session immediately
        self._cancel_tts_session()

        # Signal queues to stop
        try:
            self.utterance_queue.put_nowait(None)
            self.tts_chunk_queue.put_nowait(None)
            self.action_queue.put_nowait(None)
        except Exception:
            pass

        # Close microphone
        try:
            self.mic.close()
        except Exception as e:
            print(f"[WARN] Error closing microphone: {e}")

        # Wait briefly for threads
        for name, thread in self._threads.items():
            try:
                thread.join(timeout=0.5)
            except Exception:
                pass

        print("[ORCH] Shutdown complete")

    def request_interrupt(self) -> None:
        """Request interrupt of current speech and LLM."""
        print("[ORCH] User interrupt requested")
        ui_bridge.set_state("listening")
        self.orch_state.request_interrupt()
        self._cancel_tts_session()
        self._clear_tts_chunk_queue()
        self._llm_cancel_event.set()

    def _clear_tts_chunk_queue(self) -> None:
        """Drop queued audio from the interrupted turn."""
        while True:
            try:
                self.tts_chunk_queue.get_nowait()
                self.tts_chunk_queue.task_done()
            except queue.Empty:
                break

    def enqueue_utterance(self, text: str) -> None:
        """Enqueue user utterance for processing."""
        try:
            self.utterance_queue.put_nowait(text)
        except queue.Full:
            print("[WARN] Utterance queue full, dropping input")

    def _listen_loop(self) -> None:
        """Continuously listen for speech, even while speaking (for barge-in)."""
        print("[LISTEN] Loop started")
        try:
            while not self.stop_event.is_set():
                frame = self.mic.read_frame(timeout=0.1)
                if frame is None:
                    continue

                for event in self.vad.process(frame):
                    if event.kind == AudioEventKind.SPEECH_START:
                        ui_bridge.set_state("listening")
                        speaking_long_enough = (
                            self._speaking_since is not None
                            and time.monotonic() - self._speaking_since >= 0.3
                        )
                        if self.orch_state.is_speaking and speaking_long_enough:
                            print("[LISTEN] Speech detected during speak (barge-in)")
                            self.request_interrupt()
                        elif not self.orch_state.is_speaking:
                            print("[LISTEN] User speech detected, listening...")

                    elif event.kind == AudioEventKind.SPEECH_END:
                        print(f"[LISTEN] Speech ended ({len(event.audio)} bytes)")
                        try:
                            user_text = self.transcriber.transcribe_pcm16(
                                event.audio, sample_rate=16_000
                            )
                            if user_text.strip():
                                print(f"[LISTEN→USER] {user_text}")
                                ui_bridge.post_user_speech(user_text)
                                self.enqueue_utterance(user_text)
                            else:
                                print("[LISTEN] Empty transcription, skipping")
                        except Exception as e:
                            print(f"[ERROR] ASR failed: {e}")
                            traceback.print_exc()

        except Exception as e:
            print(f"[ERROR] Listen loop crashed: {e}")
            traceback.print_exc()
            self.stop_event.set()

    def _converse_loop(self) -> None:
        """Process user utterances and stream LLM responses."""
        print("[CONVERSE] Loop started")
        try:
            while not self.stop_event.is_set():
                try:
                    user_text = self.utterance_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if user_text is None:
                    break

                self._handle_user_utterance(user_text)

        except Exception as e:
            print(f"[ERROR] Converse loop crashed: {e}")
            traceback.print_exc()
            self.stop_event.set()

    def _handle_user_utterance(self, user_text: str) -> None:
        """Process one user utterance with LLM streaming."""
        clean_prompt = user_text.strip().lower().rstrip(".!?,")
        exit_phrases = {
            "exit",
            "quit",
            "shutdown",
            "shut down",
            "turn off",
            "power off",
            "close assistant",
            "exit assistant",
            "stop assistant",
            "goodbye",
            "bye",
            "bye bye",
        }
        if clean_prompt in exit_phrases or any(clean_prompt.endswith(phrase) for phrase in exit_phrases if len(phrase) >= 4):
            print(f"[CONVERSE] Exit voice command received: '{user_text}'. Shutting down.")
            ui_bridge.post_jarvis_speech("Shutting down. Goodbye.")
            try:
                self.tts_client.speak("Shutting down. Goodbye.")
            except Exception:
                pass
            self.stop_event.set()
            return

        utterance_id = f"u_{int(time.time() * 1000)}"
        self.orch_state.new_utterance(utterance_id)

        print(f"[CONVERSE] Processing utterance {utterance_id}: {user_text}")
        ui_bridge.post_user_speech(user_text)
        ui_bridge.set_state("thinking")
        ui_bridge.set_engine(getattr(self.llm_router, "last_provider", "local"))

        # Clear interrupt flag and cancel events for new utterance
        self.orch_state.clear_interrupt()
        self._llm_cancel_event.clear()

        # Initialize TTS session
        cancel_event = Event()
        
        def on_tts_start():
            print(f"[SPEAK] Playback started for {utterance_id}")
            self._speaking_since = time.monotonic()
            self.orch_state.set_speaking(True)
            ui_bridge.set_state("speaking")
        
        def on_tts_end():
            print(f"[SPEAK] Playback ended for {utterance_id}")
            self._speaking_since = None
            self.orch_state.set_speaking(False)
            ui_bridge.set_state("idle")
            # Clear stale audio frames that captured speaker output and reset VAD
            self.vad.reset()
            self.mic.flush()
        
        tts_session = self.tts_client.start_session(
            cancel_event=cancel_event,
            state=self.assistant_state,
            on_start=on_tts_start,
            on_end=on_tts_end,
        )

        with self._tts_session_lock:
            self._current_tts_session = tts_session

        response_text = ""
        try:
            response_parts: list[str] = []
            current_line_buffer = ""
            speech_buffer = ""
            pending_actions: list[ActionRequest] = []

            def _flush_speech():
                nonlocal speech_buffer
                clean = speech_buffer.strip()
                if clean and not self.orch_state.is_interrupted():
                    print(f"[CONVERSE→TTS] Enqueued chunk: {clean[:80]}")
                    ui_bridge.post_jarvis_speech(clean)
                    try:
                        self.tts_chunk_queue.put_nowait(TTSChunk(text=clean, utterance_id=utterance_id))
                    except queue.Full:
                        print("[WARN] TTS queue full, dropping chunk")
                speech_buffer = ""

            def _handle_action_line(action_str: str):
                nonlocal speech_buffer
                stripped = action_str.strip()
                payload = stripped.removeprefix("ACTION:").strip()
                if payload.upper() in {"NONE", "ACTION_NONE", "ACTION_NOT_NEEDED"}:
                    return
                # If LLM hallucinates an ACTION: speak("..."), route it to spoken text
                if payload.startswith(("speak(", "say(")) and payload.endswith(")"):
                    import ast
                    try:
                        parsed = ast.parse(payload, mode="eval")
                        if isinstance(parsed.body, ast.Call) and parsed.body.args:
                            spoken = ast.literal_eval(parsed.body.args[0])
                            speech_buffer += (" " if speech_buffer else "") + str(spoken)
                            _flush_speech()
                            return
                    except Exception:
                        pass
                try:
                    action_req = parse_action_from_llm(stripped)
                    if action_req:
                        action_req.done_event = Event()
                        pending_actions.append(action_req)
                        ui_bridge.post_action(action_req.name, " ".join(str(a) for a in action_req.args))
                        self._enqueue_action(action_req, utterance_id)
                except Exception as e:
                    print(f"[WARN] Failed to parse action '{stripped}': {e}")

            for token in self.llm_router.stream_reply(user_text):
                if self.orch_state.is_interrupted():
                    print(f"[CONVERSE] Interrupted, stopping {utterance_id}")
                    break
                if self._llm_cancel_event.is_set():
                    print(f"[CONVERSE] Cancel requested for {utterance_id}")
                    break

                response_parts.append(token)
                current_line_buffer += token

                # If full line has arrived, check if it's an ACTION or regular speech
                while "\n" in current_line_buffer:
                    line, current_line_buffer = current_line_buffer.split("\n", 1)
                    if line.strip().startswith("ACTION:"):
                        _handle_action_line(line)
                    else:
                        speech_buffer += (" " if speech_buffer else "") + line.strip()
                        _flush_speech()

                # If current line does not start with ACTION, chunk eagerly on sentence boundaries
                if not current_line_buffer.lstrip().startswith("ACTION"):
                    match = re.search(r"([.!?]+)(?:\s|$)", current_line_buffer)
                    if match:
                        sentence = current_line_buffer[:match.end()].strip()
                        current_line_buffer = current_line_buffer[match.end():]
                        speech_buffer += (" " if speech_buffer else "") + sentence
                        _flush_speech()
                    elif len(current_line_buffer.split()) >= 12:
                        split_at = current_line_buffer.rfind(" ")
                        if split_at > 0:
                            chunk = current_line_buffer[:split_at].strip()
                            current_line_buffer = current_line_buffer[split_at:].lstrip()
                            speech_buffer += (" " if speech_buffer else "") + chunk
                            _flush_speech()

            # Flush any remaining text in buffer after stream completes
            if current_line_buffer.strip():
                if current_line_buffer.strip().startswith("ACTION:"):
                    _handle_action_line(current_line_buffer)
                else:
                    speech_buffer += (" " if speech_buffer else "") + current_line_buffer.strip()

            _flush_speech()
            response_text = "".join(response_parts)

            # Wait for any pending actions to complete so their spoken telemetry is queued before ending session
            for act in pending_actions:
                if act.done_event:
                    while not act.done_event.wait(timeout=0.1):
                        if self.orch_state.is_interrupted() or self.stop_event.is_set():
                            break

            # Mark end of session for the speaker loop and wait for completion
            if not self.orch_state.is_interrupted():
                self.tts_chunk_queue.put_nowait(None)
                self.tts_chunk_queue.join()
                tts_session.finish()

        except Exception as e:
            print(f"[ERROR] Utterance processing failed: {e}")
            traceback.print_exc()
        finally:
            ui_bridge.set_state("idle")
            if response_text:
                self.llm_router.remember_turn(user_text, response_text)
            with self._tts_session_lock:
                self._current_tts_session = None
            self.orch_state.set_speaking(False)
            self.vad.reset()
            self.mic.flush()
            print(f"[CONVERSE] Completed utterance {utterance_id}")
            print("[CONVERSE] Ready and listening for your next command...")

    def _speak_loop(self) -> None:
        """Play TTS chunks as they arrive."""
        print("[SPEAK] Loop started")
        try:
            while not self.stop_event.is_set():
                try:
                    chunk = self.tts_chunk_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if chunk is None:
                    # End of session signal
                    print("[SPEAK] End-of-session marker received")
                    self.tts_chunk_queue.task_done()
                    continue

                try:
                    # Check if this chunk is for the current utterance (not interrupted)
                    if chunk.utterance_id != self.orch_state.current_utterance_id:
                        print(f"[SPEAK] Skipping chunk from old utterance {chunk.utterance_id}")
                        continue

                    print(f"[SPEAK] Synthesizing: {chunk.text[:80]}")

                    with self._tts_session_lock:
                        session = self._current_tts_session

                    if session is None:
                        print("[SPEAK] No active TTS session, skipping chunk")
                        continue

                    session.feed(chunk.text)
                finally:
                    self.tts_chunk_queue.task_done()

        except Exception as e:
            print(f"[ERROR] Speak loop crashed: {e}")
            traceback.print_exc()
            self.stop_event.set()

    def _action_loop(self) -> None:
        """Execute actions in parallel with speech."""
        print("[ACTION] Loop started")
        try:
            while not self.stop_event.is_set():
                try:
                    action_req = self.action_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if action_req is None:
                    break

                print(f"[ACTION] Executing: {action_req.name}")

                try:
                    # Execute action (with confirmation)
                    result = confirm_and_execute(
                        request=action_req,
                    )

                    if result:
                        print(f"[ACTION] Completed: {action_req.name} → {result}")
                        spoken = format_action_result_speech(action_req, result)
                        if spoken and not self.orch_state.is_interrupted() and not self.stop_event.is_set():
                            print(f"[ACTION→VOICE] Enqueuing spoken telemetry: {spoken}")
                            try:
                                self.tts_chunk_queue.put_nowait(
                                    TTSChunk(text=spoken, utterance_id=action_req.utterance_id)
                                )
                            except queue.Full:
                                print("[WARN] TTS queue full, dropping action voice telemetry")
                    else:
                        print(f"[ACTION] Denied: {action_req.name}")

                except Exception as e:
                    print(f"[ERROR] Action execution failed: {e}")
                    traceback.print_exc()
                finally:
                    if hasattr(action_req, "done_event") and action_req.done_event is not None:
                        action_req.done_event.set()

        except Exception as e:
            print(f"[ERROR] Action loop crashed: {e}")
            traceback.print_exc()
            self.stop_event.set()

    def _enqueue_action(self, action_req, utterance_id: str) -> None:
        """Enqueue an action for execution."""
        action_req.utterance_id = utterance_id
        try:
            self.action_queue.put_nowait(action_req)
            print(f"[ORCH] Action enqueued: {action_req.name}")
        except queue.Full:
            print("[WARN] Action queue full, dropping action")

    def _cancel_tts_session(self) -> None:
        """Cancel current TTS session."""
        with self._tts_session_lock:
            if self._current_tts_session is not None:
                print("[ORCH] Cancelling TTS session")
                self._current_tts_session.cancel()
                self._current_tts_session = None
