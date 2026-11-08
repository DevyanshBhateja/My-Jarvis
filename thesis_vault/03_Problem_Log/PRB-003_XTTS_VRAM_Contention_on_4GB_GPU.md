---
id: PRB-003
title: Coqui XTTS v2 VRAM Contention and CUDA OOM on 4GB RTX 3050
research_question: "[[Research_Questions|RQ3]]"
status: Solved
tags: [problem, failed-attempt, solution, rq3, vram, cuda, oom, xtts]
related: ["[[ADR-001_VRAM_Budget_Allocation]]", "[[Pinned_Models_and_Licenses]]"]
---

# ⚠️ PRB-003: Coqui XTTS v2 VRAM Contention & CUDA OOM on 4GB RTX 3050

## 1. Problem Description & Symptoms
When running the full stack on the NVIDIA RTX 3050 (Whisper `base.en` on CUDA + Ollama Qwen 2.5 3B on CUDA + Coqui XTTS v2 on CUDA), total allocated GPU VRAM exceeded **3800 MB**. 

When the user launched an external application (e.g. `CMD-01: open_app("firefox")`), the desktop window manager (Wayland/X11) requested additional GPU framebuffer memory, causing PyTorch in Coqui to crash immediately with:
```
RuntimeError: CUDA out of memory. Tried to allocate 256.00 MiB (GPU 0; 4.00 GiB total capacity; 3.72 GiB already allocated)
```

---

## 2. Failed Attempts & Negative Results (Thesis Goldmine)

### Failed Attempt 1: Running XTTS v2 Entirely on CPU (`gpu=False`)
- **What was tried**: Initialized Coqui with `gpu=False` in [[coqui_tts.py]] to spare VRAM.
- **Negative Result**: While VRAM dropped to ~2.2 GB, CPU synthesis latency skyrocketed. Synthesizing a single 10-word sentence on an Intel Core i5 CPU took **4.8 to 6.2 seconds** ($\text{RTF} > 1.8$). Time-to-First-Audio became unbearable.
- **Why it failed**: Autoregressive transformer neural TTS architectures cannot achieve real-time factor ($\text{RTF} < 1.0$) on consumer laptop CPUs.

### Failed Attempt 2: Dynamic CUDA Memory Deallocation (`torch.cuda.empty_cache()`)
- **What was tried**: Called `torch.cuda.empty_cache()` and `gc.collect()` between turns.
- **Negative Result**: Did not reclaim weights memory (only freed unused PyTorch cache blocks). Base weight allocation of XTTS v2 (~1.6 GB) remained resident, leaving zero cushion against external GPU bursts.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Model Swap to Coqui VITS**: Replaced heavy XTTS v2 (~460M parameters, 1.6 GB VRAM) with **Coqui VITS LJSpeech** (~30M parameters, ~300 MB VRAM) for the primary conversational loop.
2. **Resulting Memory Profile**:
   $$\text{Whisper (250MB)} + \text{Ollama Qwen-3B (1900MB)} + \text{Coqui VITS (300MB)} = \mathbf{2450\text{ MB}}$$
3. **Headroom Maintained**: Left **~1.6 GB of unallocated VRAM**, completely eliminating OOM crashes even when launching heavy 3D or browser applications.

---

## 4. Academic Thesis Contribution
- Directly answers **RQ3**: Demonstrates the physical ceiling of consumer edge hardware (4GB VRAM). Proves that while heavy zero-shot diffusion TTS models (XTTS v2) are superior in voice cloning fidelity, lightweight non-autoregressive models (VITS) are mandatory for production stability when co-located with local STT and SLM instances.
