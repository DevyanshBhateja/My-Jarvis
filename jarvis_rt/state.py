"""Thread-safe shared assistant state."""

from __future__ import annotations

from dataclasses import dataclass, field
import threading


@dataclass
class AssistantState:
    lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)
    is_listening: bool = True
    is_speaking: bool = False
    interrupt_requested: bool = False

    def mark_listening(self, value: bool) -> None:
        with self.lock:
            self.is_listening = value

    def mark_speaking(self, value: bool) -> None:
        with self.lock:
            self.is_speaking = value

    def request_interrupt(self) -> None:
        with self.lock:
            self.interrupt_requested = True

    def clear_interrupt(self) -> None:
        with self.lock:
            self.interrupt_requested = False