# Thesis Steering & Empirical Research Protocol

This rule governs all development in the `MY_JARVIS` workspace.

## Mandates:
1. **Target Envelope**: NVIDIA RTX 3050 (4GB VRAM), Fedora Linux, PipeWire audio.
2. **Pinned Models**:
   - STT: OpenAI Whisper `base.en`
   - Edge SLM: `qwen2.5:3b-instruct-q4_K_M` via local Ollama
   - Cloud Worker: `meta/llama-3.3-70b-instruct` via NVIDIA NIM (free tier)
   - Edge TTS: Coqui VITS `vits_ljspeech` (lightweight) / Coqui XTTS v2 (comparison)
   - VAD / AEC: Google WebRTC VAD + PipeWire WebRTC Echo Cancel
3. **Frozen Command Suite**: Only test the 10 approved commands defined in `thesis_vault/01_Specification/Frozen_Fedora_Commands.md`.
4. **Obsidian Research Logging**:
   - Every bug, failure, or trade-off must be logged into `thesis_vault/03_Problem_Log/` using wikilinks `[[Note]]` and tags (`#failed-attempt`, `#solution`, `#problem`, `#benchmark`).
   - Failed attempts are considered high-value thesis material and must never be discarded without documentation.
