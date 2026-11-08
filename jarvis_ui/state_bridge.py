"""Thread-safe event bridge connecting Jarvis runtime to the HUD interface."""

from __future__ import annotations

import json
import queue
import threading
import time
from typing import Any, Dict, List, Optional


class UIBridge:
    """Pub/Sub event broadcaster for the Jarvis HUD."""

    _instance: Optional[UIBridge] = None
    _lock = threading.Lock()

    def __new__(cls) -> UIBridge:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_bridge()
            return cls._instance

    def _init_bridge(self) -> None:
        self._subscribers: List[queue.Queue] = []
        self._sub_lock = threading.Lock()
        self._current_state = "idle"
        self._current_engine = "local"
        self._current_action = ""
        self._user_text = ""
        self._jarvis_text = ""
        self._vram_mb = 0.0
        self._is_active = False

    def activate(self) -> None:
        self._is_active = True

    @property
    def is_active(self) -> bool:
        return self._is_active

    def subscribe(self) -> queue.Queue:
        """Subscribe to the event stream."""
        q: queue.Queue = queue.Queue(maxsize=100)
        with self._sub_lock:
            self._subscribers.append(q)
            # Send initial snapshot immediately
            initial_event = {
                "type": "snapshot",
                "state": self._current_state,
                "engine": self._current_engine,
                "action": self._current_action,
                "user_text": self._user_text,
                "jarvis_text": self._jarvis_text,
                "timestamp": time.time(),
            }
            try:
                q.put_nowait(initial_event)
            except queue.Full:
                pass
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self._sub_lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def _broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        event = {
            "type": event_type,
            "timestamp": time.time(),
            **data,
        }
        with self._sub_lock:
            dead = []
            for q in self._subscribers:
                try:
                    q.put_nowait(event)
                except queue.Full:
                    # Drop oldest item to keep real-time freshness
                    try:
                        q.get_nowait()
                        q.put_nowait(event)
                    except Exception:
                        dead.append(q)
            for q in dead:
                if q in self._subscribers:
                    self._subscribers.remove(q)

    def set_state(self, state: str) -> None:
        """Update active operational state: 'idle', 'listening', 'thinking', 'speaking', 'interrupted'."""
        self._current_state = state
        self._broadcast("state", {"state": state})

    def set_engine(self, engine: str, model_name: str = "") -> None:
        """Set current LLM engine: 'local' (Ollama) or 'nvidia' (Cloud NIM)."""
        self._current_engine = engine
        self._broadcast("engine", {"engine": engine, "model": model_name})

    def post_user_speech(self, text: str) -> None:
        """Publish transcribed user utterance."""
        self._user_text = text
        self._broadcast("user_speech", {"text": text})

    def post_jarvis_speech(self, text: str, append: bool = True) -> None:
        """Publish assistant synthesized speech or sentence chunk."""
        if append and self._jarvis_text:
            self._jarvis_text += " " + text
        else:
            self._jarvis_text = text
        self._broadcast("jarvis_speech", {"text": text, "full_text": self._jarvis_text})

    def clear_dialogue(self) -> None:
        self._user_text = ""
        self._jarvis_text = ""
        self._broadcast("clear_dialogue", {})

    def post_action(self, name: str, description: str = "", status: str = "running") -> None:
        """Publish action invocation or completion."""
        self._current_action = f"{name}: {description}" if description else name
        self._broadcast("action", {"name": name, "description": description, "status": status})

    def post_audio_level(self, level: float) -> None:
        """Broadcast live audio volume level (0.0 to 1.0) for visualizer pulse."""
        self._broadcast("audio_level", {"level": max(0.0, min(1.0, level))})


# Global singleton bridge
ui_bridge = UIBridge()
