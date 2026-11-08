"""Real-time, interruptible Jarvis voice assistant components."""

from .controller import AssistantController, listen_once, run_assistant
from .interaction_orchestrator import InteractionOrchestrator
from .coqui_tts import CoquiXTTSPlayer, StreamingCoquiTtsSession
from .llm_stream import LocalOllamaClient, NvidiaNimClient
from .transcription import WhisperTranscriber
from .tts_stream import ChunkedEdgeTTSPlayer
from .vad import AudioEvent, VadConfig, VoiceActivityCollector

__all__ = [
    "AssistantController",
    "AudioEvent",
    "ChunkedEdgeTTSPlayer",
    "CoquiXTTSPlayer",
    "InteractionOrchestrator",
    "LocalOllamaClient",
    "NvidiaNimClient",
    "StreamingCoquiTtsSession",
    "VadConfig",
    "VoiceActivityCollector",
    "WhisperTranscriber",
    "listen_once",
    "run_assistant",
]