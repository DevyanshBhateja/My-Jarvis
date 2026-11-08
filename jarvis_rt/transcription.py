"""Whisper transcription helpers."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import whisper


@lru_cache(maxsize=4)
def _load_whisper_model(model_name: str):
    return whisper.load_model(model_name)


_HALLUCINATION_BLACKLIST = {
    "thank you for watching.",
    "thank you for watching",
    "thanks for watching.",
    "thanks for watching",
    "please subscribe.",
    "please subscribe",
    "subtitles by",
    "you",
    "bye.",
    "bye",
    "goodbye.",
    "goodbye",
    "silence",
    "[silence]",
    "[applause]",
    "[music]",
}


class WhisperTranscriber:
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name

    def transcribe_pcm16(self, pcm_audio: bytes, sample_rate: int = 16_000) -> str:
        if not pcm_audio:
            return ""

        audio = np.frombuffer(pcm_audio, dtype=np.int16).astype(np.float32) / 32768.0
        if audio.size == 0:
            return ""

        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(np.square(audio))))

        # Silence / background noise rejection gate: do not transcribe low energy hiss
        if peak < 0.035 or rms < 0.008:
            return ""

        # Gentle normalization: prevent 100x amplification of background noise
        if peak < 0.8:
            gain = min(1.0 / peak, 3.0)
            audio = audio * gain

        model = _load_whisper_model(self.model_name)
        result = model.transcribe(
            audio,
            fp16=False,
            language="en",
            temperature=0.0,
            no_speech_threshold=0.6,
            logprob_threshold=-1.0,
            compression_ratio_threshold=2.4,
            condition_on_previous_text=False,
        )
        text = (result.get("text") or "").strip()

        # Filter out known Whisper subtitle hallucinations
        clean_lower = text.lower().strip()
        if clean_lower in _HALLUCINATION_BLACKLIST or clean_lower.startswith("subtitles by"):
            return ""

        return text