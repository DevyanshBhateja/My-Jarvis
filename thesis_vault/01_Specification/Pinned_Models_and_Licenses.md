---
id: SPEC-002
title: Pinned Models, Licensing Matrix & System Prerequisites
tags: [specification, models, licensing, prerequisites, vram]
related: ["[[Supervisor_Guidelines]]", "[[ADR-001_VRAM_Budget_Allocation]]", "[[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]]"]
---

# 🎯 Pinned Models, Licensing Matrix & Prerequisites

## 1. Pinned Model Specifications

To ensure reproducibility across all thesis benchmarks, all model weights and quantizations are strictly pinned:

| Pipeline Stage | Model Name & Version | Parameter Count | Quantization / Format | VRAM Footprint |
| :--- | :--- | :--- | :--- | :--- |
| **STT (Speech-to-Text)** | `openai-whisper:base.en` | 74M | FP32 / FP16 PyTorch Checkpoint | ~250 MB |
| **Local Edge SLM** | `Qwen/Qwen2.5-3B-Instruct` | 3.09B | Ollama `qwen2.5:3b-instruct-q4_K_M` | ~1.90 GB |
| **Cloud Worker LLM** | `meta/llama-3.3-70b-instruct` | 70B | NVIDIA NIM Cloud Endpoint | 0 MB (Cloud) |
| **Primary Local TTS** | Coqui VITS (`vits_ljspeech`) | ~30M | PyTorch Checkpoint (`tts_models/en/ljspeech/vits`) | ~300 MB |
| **Secondary Local TTS** | Coqui XTTS v2 (`xtts_v2`) | ~460M | PyTorch Checkpoint (`tts_models/multilingual/multi-dataset/xtts_v2`) | ~1.60 GB |
| **VAD** | Google WebRTC VAD | N/A (Algorithmic) | C library wrapper (`webrtcvad` Mode 1) | 0 MB (CPU) |
| **AEC** | PipeWire WebRTC AEC | N/A (DSP module) | `libpipewire-module-echo-cancel` | 0 MB (CPU/DSP) |

### Memory Budget on RTX 3050 (4.0 GB Maximum)
- **Primary Setup (Whisper + Qwen-3B + VITS)**:
  $$\text{VRAM}_{\text{total}} = 250\text{MB} + 1900\text{MB} + 300\text{MB} = \mathbf{2.45\text{ GB}}$$
  *Headroom for display server / desktop: ~1.55 GB (Extremely stable, zero OOM).*
- **Heavy Comparison Setup (Whisper + Qwen-3B + XTTS v2)**:
  $$\text{VRAM}_{\text{total}} = 250\text{MB} + 1900\text{MB} + 1600\text{MB} = \mathbf{3.75\text{ GB}}$$
  *Headroom: ~250 MB (High risk of OOM when launching GPU-accelerated applications like Firefox).* See [[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]].

---

## 2. Licensing Audit & Compliance Matrix

Academic integrity requires explicit audit of all component licenses:

| Component | Software / Model | License Type | Academic / Commercial Terms |
| :--- | :--- | :--- | :--- |
| **Whisper** | OpenAI Whisper | **MIT License** | Completely open; free for academic and commercial use. |
| **Qwen 2.5 3B** | Alibaba Qwen Team | **Apache 2.0** | Permissive open-source; free research and commercial distribution. |
| **Coqui VITS** | Coqui Community | **MIT License** | Completely open source and unrestricted. |
| **Coqui XTTS v2**| Coqui AI | **CPML** (Coqui Public Model License) | **Restricted to non-commercial academic research.** Commercial use requires separate commercial licensing. |
| **NVIDIA NIM** | NVIDIA Corporation | **NVIDIA Developer Agreement** | Free developer evaluation tier granted for prototyping and academic benchmarking. |
| **PipeWire** | PipeWire Project | **LGPL 2.1+ / MIT** | Standard GNU Linux audio routing libraries. |
| **MY_JARVIS Codebase** | Devyansh Bhateja | **MIT License** | Author's original research implementation. |

> **Thesis Note on CPML**: In the thesis discussion, the distinction between **Coqui VITS (permissive MIT)** and **XTTS v2 (non-commercial CPML)** must be highlighted when analyzing the legal viability of consumer edge assistants.

---

## 3. Practical Prerequisites for Reproducing the Test Bench

To follow and reproduce this thesis implementation on hardware, the following environment must be configured:

### A. Hardware
- **GPU**: NVIDIA GeForce RTX 3050 Laptop/Desktop GPU (4GB GDDR6 VRAM, CUDA Compute Capability 8.6).
- **CPU**: Intel Core i5/i7 (11th Gen or newer) or AMD Ryzen 5/7 (5000 series or newer), 4+ cores.
- **RAM**: 16 GB DDR4/DDR5 system memory.
- **Audio Setup**: Built-in or USB microphone + external speakers (for acoustic echo cancellation testing).

### B. Operating System & System Libraries
- **OS**: Fedora Linux 40 or 41 (GNOME on Wayland or X11).
- **Core System Packages**:
  ```bash
  sudo dnf install -y pipewire-plugin-echo-cancel pipewire-utils alsa-utils mpg123 ffmpeg
  ```
- **Ollama Engine**:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ollama pull qwen2.5:3b
  ```

### C. Python 3.11 Virtual Environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install openai-whisper TTS sounddevice webrtcvad openai pyautogui
```

### D. Environment Configuration
```bash
export JARVIS_OLLAMA_URL="http://127.0.0.1:11434"
export JARVIS_LOCAL_MODEL="qwen2.5:3b"
export JARVIS_LLM_ROUTE="auto"
export NVIDIA_API_KEY="nvapi-your-key-here"
```
