"""Simplified controller that delegates to InteractionOrchestrator."""

from __future__ import annotations

from dataclasses import dataclass
import os
import traceback
from typing import Optional

from .interaction_orchestrator import InteractionOrchestrator
from .llm_stream import LocalOllamaClient, LLMRouter, NvidiaNimClient, RoutePolicy
from .mic_stream import MicrophoneStream
from .state import AssistantState
from .transcription import WhisperTranscriber
from .vad import VadConfig, VoiceActivityCollector, AudioEventKind
from .coqui_tts import CoquiXTTSPlayer


@dataclass(slots=True)
class AssistantConfig:
    sample_rate: int = 16_000
    frame_duration_ms: int = 30
    whisper_model: str = "base"
    local_model: str = "qwen2.5:3b"
    nvidia_model: str = "nvidia/nemotron-3-super-120b-a12b"
    audio_device: int | None = None
    local_base_url: str = "http://127.0.0.1:11434"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    llm_route_mode: str = "local"  # auto | local | nvidia
    tts_model: str = "tts_models/en/ljspeech/vits"
    nvidia_api_key: str | None = None
    complexity_chars: int = 180
    complexity_words: int = 35


class AssistantController:
    """Simple controller that orchestrates full-duplex voice assistant via InteractionOrchestrator."""

    def __init__(self, config: Optional[AssistantConfig] = None):
        self.config = config or AssistantConfig()
        
        # Initialize components
        vad_config = VadConfig(
            sample_rate=self.config.sample_rate,
            frame_duration_ms=self.config.frame_duration_ms
        )
        self.state = AssistantState()
        self.mic = MicrophoneStream(vad_config, device=self.config.audio_device)
        self.vad = VoiceActivityCollector(vad_config)
        self.transcriber = WhisperTranscriber(self.config.whisper_model)
        
        # Initialize LLM routing
        route_mode = self.config.llm_route_mode.lower().strip()
        self.local_llm = LocalOllamaClient(
            base_url=self.config.local_base_url,
            model=self.config.local_model,
        )
        print(f"[ROUTER] Local Ollama client enabled ({self.config.local_model})")
        # Preload Ollama model into GPU VRAM concurrently during startup
        import threading
        threading.Thread(target=self.local_llm.warmup, name="OllamaWarmupThread", daemon=True).start()
        
        nvidia_key = self.config.nvidia_api_key or os.getenv("NVIDIA_API_KEY")
        self.nvidia_llm = None
        if nvidia_key:
            self.nvidia_llm = NvidiaNimClient(
                api_key=nvidia_key,
                model=self.config.nvidia_model,
                base_url=self.config.nvidia_base_url,
            )
            print("[ROUTER] NVIDIA NIM client enabled")
        else:
            print("[ROUTER] NVIDIA NIM client disabled (missing NVIDIA_API_KEY)")

        if route_mode == "nvidia" and self.nvidia_llm is None:
            raise RuntimeError("NVIDIA-only mode requested but NVIDIA_API_KEY is not set")

        self.router = LLMRouter(
            local_llm=self.local_llm,
            nvidia_llm=self.nvidia_llm,
            policy=RoutePolicy(
                mode=self.config.llm_route_mode,
                complexity_chars=self.config.complexity_chars,
                complexity_words=self.config.complexity_words,
            ),
        )
        
        # Initialize Coqui TTS (pinned to VITS for 4GB VRAM per ADR-001)
        print(f"[COQUI-TTS] Initializing Coqui TTS ({self.config.tts_model})...")
        self.tts = CoquiXTTSPlayer(
            model_name=self.config.tts_model,
            gpu=True,
            language="en"
        )
        
        # Create orchestrator
        self.orchestrator = InteractionOrchestrator(
            mic=self.mic,
            vad=self.vad,
            transcriber=self.transcriber,
            llm_router=self.router,
            tts_client=self.tts,
            assistant_state=self.state,
        )

    def run(self) -> None:
        """Start the full-duplex voice assistant."""
        print("[CONTROLLER] Starting full-duplex assistant...")
        try:
            self.orchestrator.start_conversation_loop()
        except KeyboardInterrupt:
            print("\n[CONTROLLER] Interrupt received")
        except Exception as e:
            print(f"[ERROR] Controller crashed: {e}")
            traceback.print_exc()
        finally:
            self.orchestrator.shutdown()

    def shutdown(self) -> None:
        """Gracefully shut down the controller."""
        self.orchestrator.shutdown()

    def listen_once(self) -> str:
        """Listen for a single utterance (utility method)."""
        self.mic.start()
        try:
            while True:
                frame = self.mic.read_frame(timeout=0.1)
                if frame is None:
                    continue
                for event in self.vad.process(frame):
                    if event.kind == AudioEventKind.SPEECH_END:
                        return self.transcriber.transcribe_pcm16(
                            event.audio, sample_rate=self.config.sample_rate
                        )
        finally:
            self.mic.close()


def listen_once() -> str:
    """Utility: listen for one utterance."""
    controller = AssistantController()
    return controller.listen_once()


def run_assistant(config: Optional[AssistantConfig] = None) -> None:
    """Run the full-duplex Jarvis assistant."""
    controller = AssistantController(config=config)
    controller.run()