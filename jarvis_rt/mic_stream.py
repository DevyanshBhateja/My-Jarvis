"""Continuous microphone capture with small fixed-size frames."""

from __future__ import annotations

import queue
import threading
from typing import Optional

import sounddevice as sd

from .vad import VadConfig


class MicrophoneStream:
    def __init__(self, config: Optional[VadConfig] = None, device: int | None = None):
        self.config = config or VadConfig()
        self.device = device
        self._frames: queue.Queue[bytes] = queue.Queue(maxsize=128)
        self._stream: sd.InputStream | None = None
        self._started = threading.Event()
        self._paused = threading.Event()

    @property
    def frame_samples(self) -> int:
        return self.config.frame_samples

    @property
    def is_paused(self) -> bool:
        return self._paused.is_set()

    def _callback(self, indata, frames, time, status) -> None:  # pragma: no cover - sounddevice callback
        if status:
            print(f"[MIC] Status: {status}")
        if self._paused.is_set():
            return
        frame = bytes(indata)
        try:
            self._frames.put_nowait(frame)
        except queue.Full:
            try:
                self._frames.get_nowait()
            except queue.Empty:
                pass
            try:
                self._frames.put_nowait(frame)
            except queue.Full:
                print("[WARN] Microphone frame queue overflow")

    def start(self) -> None:
        if self._stream is not None:
            return
        print(f"[MIC] Starting stream: sr={self.config.sample_rate}Hz, blocksize={self.frame_samples}, device={self.device}")
        try:
            self._stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=1,
                dtype="int16",
                blocksize=self.frame_samples,
                device=self.device,
                callback=self._callback,
            )
            self._stream.start()
            self._started.set()
            print("[MIC] Stream started successfully")
        except Exception as e:
            print(f"[ERROR] Failed to start microphone stream: {e}")
            raise

    def stop(self) -> None:
        if self._stream is None:
            return
        try:
            self._stream.stop()
        finally:
            self._stream.close()
            self._stream = None
            self._started.clear()
            self._paused.clear()

    def pause(self) -> None:
        if not self._started.is_set() or self._paused.is_set():
            return
        print("[MIC] Pausing microphone capture during TTS")
        self._paused.set()
        # Drop buffered input to avoid replaying stale frames when resuming.
        while True:
            try:
                self._frames.get_nowait()
            except queue.Empty:
                break

    def flush(self) -> int:
        """Discard all pending microphone frames in queue to clear stale audio."""
        dropped = 0
        while True:
            try:
                self._frames.get_nowait()
                dropped += 1
            except queue.Empty:
                break
        return dropped

    def resume(self) -> None:
        if not self._started.is_set() or not self._paused.is_set():
            return
        self._paused.clear()
        print("[MIC] Resumed microphone capture")

    def close(self) -> None:
        self.stop()

    def read_frame(self, timeout: float = 0.1) -> bytes | None:
        if not self._started.is_set():
            raise RuntimeError("MicrophoneStream.start() must be called first")
        try:
            return self._frames.get(timeout=timeout)
        except queue.Empty:
            return None