"""Entry point for the real-time Jarvis voice assistant."""

from __future__ import annotations

import os
import signal
import sys

from jarvis_rt.controller import AssistantConfig, AssistantController


def _load_env() -> None:
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip().strip("\"'")


def main() -> None:
    _load_env()

    config = AssistantConfig(
        llm_route_mode=os.getenv("JARVIS_LLM_ROUTE", "auto"),
        local_model=os.getenv("JARVIS_LOCAL_MODEL", "qwen2.5:3b"),
        local_base_url=os.getenv("JARVIS_OLLAMA_URL", "http://127.0.0.1:11434"),
        tts_model=os.getenv("JARVIS_TTS_MODEL", "tts_models/en/ljspeech/vits"),
        nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
        nvidia_model=os.getenv("JARVIS_NVIDIA_MODEL", "meta/llama-3.2-90b-vision-instruct"),
        nvidia_base_url=os.getenv("JARVIS_NVIDIA_URL", "https://integrate.api.nvidia.com/v1"),
    )

    controller = AssistantController(config=config)

    enable_ui = "--no-ui" not in sys.argv and os.getenv("JARVIS_ENABLE_UI", "true").lower() in ("true", "1", "yes")
    hud_server = None
    hud_launcher = None

    if enable_ui:
        try:
            from jarvis_ui import HUDServer, HUDLauncher
            hud_server = HUDServer(port=5055)
            url = hud_server.start()
            hud_launcher = HUDLauncher(url)
            hud_launcher.launch()
        except Exception as exc:
            print(f"[WARN] Failed to initialize Jarvis HUD ({exc}). Continuing in headless voice mode.")

    def _sig_handler(signum, frame) -> None:
        print("\n[MAIN] Caught interrupt signal, shutting down Jarvis cleanly...")
        if hud_launcher:
            try:
                hud_launcher.close()
            except Exception:
                pass
        if hud_server:
            try:
                hud_server.stop()
            except Exception:
                pass
        try:
            controller.shutdown()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, _sig_handler)
    signal.signal(signal.SIGTERM, _sig_handler)

    try:
        controller.run()
    except KeyboardInterrupt:
        _sig_handler(signal.SIGINT, None)
    finally:
        if hud_launcher:
            try:
                hud_launcher.close()
            except Exception:
                pass
        if hud_server:
            try:
                hud_server.stop()
            except Exception:
                pass
        try:
            controller.shutdown()
        except Exception:
            pass
        os._exit(0)


if __name__ == "__main__":
    main()