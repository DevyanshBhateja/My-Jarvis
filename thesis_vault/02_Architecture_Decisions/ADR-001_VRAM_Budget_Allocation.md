---
id: ADR-001
title: VRAM Budget Allocation on 4GB RTX 3050
tags: [adr, architecture, vram, models, decision]
status: Accepted
related: ["[[Pinned_Models_and_Licenses]]", "[[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]]", "[[Research_Questions]]"]
---

# 🏛️ ADR-001: VRAM Budget Allocation on 4GB RTX 3050

## Context & Problem Statement
The target edge hardware for this thesis is an **NVIDIA GeForce RTX 3050 Laptop/Desktop GPU with exactly 4096 MB VRAM**. In modern voice systems, running an Automatic Speech Recognition model (Whisper), a quantized Large/Small Language Model (Ollama), and a Neural Text-to-Speech synthesis model (Coqui) simultaneously on a single GPU frequently exhausts available memory, triggering CUDA out-of-memory errors (`CUDA error: out of memory`) or system process evictions.

## Decision Drivers
1. **Total Available VRAM**: 4096 MB.
2. **Display Server & Desktop Overhead**: GNOME Shell / Wayland / X11 consumes approximately 400 MB to 700 MB of VRAM simply rendering the desktop and active windows.
3. **Usable VRAM for AI Pipeline**: $\le 3300\text{ MB}$.
4. **Latency Requirement**: STT and SLM must remain memory-resident (no dynamic loading/unloading from disk during live turns).

## Considered Options
1. **Option A (Heavy Pipeline)**: Whisper Base (~250MB) + Ollama Qwen 2.5 3B (~1900MB) + Coqui XTTS v2 (~1600MB) = **3750 MB**.
2. **Option B (Lightweight Pipeline - Accepted)**: Whisper Base (~250MB) + Ollama Qwen 2.5 3B (~1900MB) + Coqui VITS (~300MB) = **2450 MB**.
3. **Option C (Cloud Offload)**: Whisper on GPU (~250MB) + Cloud LLM (0MB) + Cloud TTS (0MB).

## Decision & Rationale
We adopt **Option B** as the primary research baseline:
- Whisper `base.en` resides on GPU (~250 MB).
- Ollama `qwen2.5:3b-instruct-q4_K_M` resides on GPU (~1.90 GB).
- Coqui VITS (`vits_ljspeech`) resides on GPU (~300 MB).
- Total AI memory footprint is **~2.45 GB**, leaving **~1.55 GB buffer** for display servers and application launching (e.g. Firefox).
- **Coqui XTTS v2** is preserved in the repository as a comparison benchmark to document failure boundaries (see [[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]]).

## Consequences & Thesis Contribution
- **Positive**: Zero risk of CUDA OOM during multi-turn continuous conversation; sub-second synthesis times with VITS.
- **Negative**: VITS lacks zero-shot voice cloning capabilities present in XTTS v2.
- **Academic Discussion**: Validates how memory-constrained edge hardware dictates architectural compromises between acoustic expressiveness and pipeline stability.
