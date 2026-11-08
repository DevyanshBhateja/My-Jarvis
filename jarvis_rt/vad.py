"""Voice-activity detection and utterance collection."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
import math
from typing import Callable, Deque, Optional

import numpy as np

try:
    import webrtcvad  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    webrtcvad = None


class AudioEventKind(str, Enum):
    SPEECH_START = "speech_start"
    SPEECH_END = "speech_end"


@dataclass(slots=True)
class AudioEvent:
    kind: AudioEventKind
    audio: bytes = b""


@dataclass(slots=True)
class VadConfig:
    sample_rate: int = 16_000
    frame_duration_ms: int = 30
    prefix_padding_ms: int = 300
    speech_start_ms: int = 240
    silence_duration_ms: int = 800
    speech_end_debounce_ms: int = 250
    min_utterance_ms: int = 240
    max_utterance_ms: int = 15000
    web_rtc_mode: int = 2
    energy_threshold: float = 0.012

    @property
    def frame_samples(self) -> int:
        return int(self.sample_rate * self.frame_duration_ms / 1000)

    @property
    def prefix_frames(self) -> int:
        return max(1, math.ceil(self.prefix_padding_ms / self.frame_duration_ms))

    @property
    def speech_start_frames(self) -> int:
        return max(1, math.ceil(self.speech_start_ms / self.frame_duration_ms))

    @property
    def silence_frames(self) -> int:
        return max(1, math.ceil(self.silence_duration_ms / self.frame_duration_ms))

    @property
    def speech_end_debounce_frames(self) -> int:
        return max(1, math.ceil(self.speech_end_debounce_ms / self.frame_duration_ms))

    @property
    def min_utterance_frames(self) -> int:
        return max(1, math.ceil(self.min_utterance_ms / self.frame_duration_ms))

    @property
    def max_utterance_frames(self) -> int:
        return max(1, math.ceil(self.max_utterance_ms / self.frame_duration_ms))


class _BaseSpeechDetector:
    def is_speech(self, frame: bytes) -> bool:
        raise NotImplementedError


class _WebRtcSpeechDetector(_BaseSpeechDetector):
    def __init__(self, config: VadConfig):
        self._vad = webrtcvad.Vad(config.web_rtc_mode)
        self._sample_rate = config.sample_rate
        self._threshold = config.energy_threshold

    def is_speech(self, frame: bytes) -> bool:
        if not self._vad.is_speech(frame, self._sample_rate):
            return False
        # Dual-gate: check RMS energy to prevent triggering on quiet room hum / mic static
        samples = np.frombuffer(frame, dtype=np.int16).astype(np.float32) / 32768.0
        if samples.size == 0:
            return False
        rms = float(np.sqrt(np.mean(np.square(samples))))
        return rms >= self._threshold


class _EnergySpeechDetector(_BaseSpeechDetector):
    def __init__(self, config: VadConfig):
        self._threshold = config.energy_threshold
        self._noise_floor = config.energy_threshold / 2

    def is_speech(self, frame: bytes) -> bool:
        if not frame:
            return False
        samples = np.frombuffer(frame, dtype=np.int16).astype(np.float32) / 32768.0
        if samples.size == 0:
            return False
        rms = float(np.sqrt(np.mean(np.square(samples))))
        self._noise_floor = 0.98 * self._noise_floor + 0.02 * rms
        adaptive_threshold = max(self._threshold, self._noise_floor * 2.5)
        return rms >= adaptive_threshold


class VoiceActivityCollector:
    """Collects continuous PCM frames and emits speech-turn events."""

    def __init__(
        self,
        config: Optional[VadConfig] = None,
        on_speech_start: Optional[Callable[[], None]] = None,
        on_speech_end: Optional[Callable[[bytes], None]] = None,
    ):
        self.config = config or VadConfig()
        self.on_speech_start = on_speech_start
        self.on_speech_end = on_speech_end
        if webrtcvad is not None:
            self._detector: _BaseSpeechDetector = _WebRtcSpeechDetector(self.config)
            print("[VAD] Using WebRTC VAD (Dual-Gate Energy Protected)")
        else:
            self._detector = _EnergySpeechDetector(self.config)
            print("[VAD] Using energy-based VAD (WebRTC not available)")
        self._prefix: Deque[bytes] = deque(maxlen=self.config.prefix_frames)
        self._utterance: list[bytes] = []
        self._triggered = False
        self._speech_frames = 0
        self._silence_frames = 0
        self._pending_end_frames = 0

    def reset(self) -> None:
        self._prefix.clear()
        self._utterance.clear()
        self._triggered = False
        self._speech_frames = 0
        self._silence_frames = 0
        self._pending_end_frames = 0

    def process(self, frame: bytes) -> list[AudioEvent]:
        events: list[AudioEvent] = []
        if not frame:
            return events

        speech = self._detector.is_speech(frame)

        if self._triggered:
            self._utterance.append(frame)

            # Safeguard: prevent runaway utterance buffer from hanging indefinitely
            if len(self._utterance) >= self.config.max_utterance_frames:
                audio = b"".join(self._utterance)
                self.reset()
                print(f"[VAD] Max speech duration reached ({self.config.max_utterance_ms}ms), finalizing speech")
                events.append(AudioEvent(AudioEventKind.SPEECH_END, audio))
                if self.on_speech_end is not None:
                    self.on_speech_end(audio)
                return events

            if speech:
                self._silence_frames = 0
                self._pending_end_frames = 0
            else:
                self._silence_frames += 1
                if self._silence_frames >= self.config.silence_frames:
                    self._pending_end_frames += 1
                    if self._pending_end_frames >= self.config.speech_end_debounce_frames:
                        audio = b"".join(self._utterance)
                        self.reset()
                        min_bytes = self.config.min_utterance_frames * self.config.frame_samples * 2
                        if len(audio) >= min_bytes:
                            samples = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
                            if samples.size > 0:
                                peak = float(np.max(np.abs(samples)))
                                rms = float(np.sqrt(np.mean(np.square(samples))))
                                if peak >= 0.025 and rms >= 0.006:
                                    events.append(AudioEvent(AudioEventKind.SPEECH_END, audio))
                                    if self.on_speech_end is not None:
                                        self.on_speech_end(audio)
                                else:
                                    print(f"[VAD] Discarded low-energy sound (peak={peak:.3f}, rms={rms:.4f})")
                        else:
                            print(f"[VAD] Discarded short sound ({len(audio)} bytes)")
            return events

        self._prefix.append(frame)
        if speech:
            self._speech_frames += 1
            if self._speech_frames >= self.config.speech_start_frames:
                self._triggered = True
                self._utterance = list(self._prefix)
                self._speech_frames = 0
                self._silence_frames = 0
                events.append(AudioEvent(AudioEventKind.SPEECH_START))
                if self.on_speech_start is not None:
                    self.on_speech_start()
        else:
            self._speech_frames = 0

        return events