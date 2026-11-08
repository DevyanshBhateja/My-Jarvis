# MY_JARVIS: Real-Time Full-Duplex Conversational AI & Desktop Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](https://python.org)
[![Hardware Target: RTX 3050 (4GB)](https://img.shields.io/badge/Hardware-NVIDIA%20RTX%203050%20(4GB%20VRAM)-76B900.svg)](https://www.nvidia.com)
[![OS: Fedora Linux](https://img.shields.io/badge/OS-Fedora%20Linux%20(Wayland%2FPipeWire)-294172.svg)](https://getfedora.org)
[![Evaluation: 100% Pass](https://img.shields.io/badge/Benchmarks-66%2F66%20Trials%20Passed-success.svg)](thesis_vault/05_Benchmarks/BENCH-002_Empirical_Results.md)

> **Bachelor's Thesis in AI and Data Engineering (2026)**  
> **Author**: Devyansh Bhateja  
> **Hardware Boundary**: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MB VRAM Ceiling)  
> **Operating System**: Fedora Linux 40/41 Workstation (Wayland, PipeWire, GNOME/Mutter)

---

## 🎯 Overview

**MY_JARVIS** is an applied artificial intelligence and systems engineering framework demonstrating **real-time, full-duplex conversational voice interaction and deterministic desktop automation on consumer-grade edge workstations with tight memory limits (4GB VRAM)**.

Rather than relying on sequential "walkie-talkie" turn-taking (where speaking mutes listening and replies take 3–5 seconds), MY_JARVIS implements a concurrent four-worker pipeline coupling:
1. **Continuous Acoustic Presence**: Hardware-level Acoustic Echo Cancellation (PipeWire WebRTC AEC) enabling true **mid-sentence user barge-in** (< 120 ms).
2. **Sub-Second Latency**: Streaming LLM token generation coupled with **sentence-bounded TTS chunking**, achieving **Mean TTFA = 390.5 ms**.
3. **The Asymmetric "Double-AI" Duplex**: Instant edge conversational dialogue (Ollama `Qwen 2.5 3B`, TTFT = 37.0 ms) combined with asynchronous cloud reasoning (`Llama 3.3 70B` / `90B` via NVIDIA NIM).
4. **Wayland-Safe Automation**: Native process lifecycle management replacing brittle X11 synthetic keystrokes to prevent Mutter security dialogs.
5. **Strict 4GB Memory Budget**: Sustains a peak VRAM footprint of **2,790 MB**, leaving over **1,300 MB of VRAM headroom** for host desktop applications.

---

## 🏗️ System Architecture

```
                             USER SPEECH
                                  │
                                  ▼
                      [PipeWire WebRTC AEC]
                    (Acoustic Echo Cancellation)
                                  │
                                  ▼
                     [OpenAI Whisper (base.en)]
                       (74M Params, ~250MB VRAM)
                                  │
                                  ▼
                  [Interaction Orchestrator Queue]
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
  [Tier 1: Edge Dialogue Loop]               [Tier 2: Cloud Reasoning Worker]
   • Model: Qwen 2.5 3B (Ollama)              • Model: Llama 3.3 70B (NVIDIA NIM)
   • Role: Instant voice backchanneling       • Role: Multi-step tool planning
   • Latency: TTFT = 37.0 ms                  • Latency: Async background worker
   • Footprint: ~1.90 GB VRAM                 • Footprint: 0 MB VRAM
          │                                               │
          ▼                                               ▼
  [Sentence-Bounded TTS Chunker]             [Action Execution Engine]
   (Flushes on punctuation or 12 tokens)      (Two-Tier Safety Containment)
          │                                               │
          ▼                                               ▼
   [Coqui VITS Synthesis]                     [10 Frozen Fedora Commands]
   (~300MB VRAM, RTF = 0.08)                              │
          ▲                                               │
          └───────────────────────────────────────────────┘
                      Spoken Telemetry Feedback
```

---

## 🛡️ The 10 Frozen Fedora Benchmark Commands

Following academic scope containment guidelines, desktop automation is strictly confined to 10 deterministic commands evaluated across 66 automated trials:

| ID | Category | Voice Prompt Example | Target Linux System Primitive |
| :---: | :--- | :--- | :--- |
| **CMD-01** | App Management | *"Launch Firefox"* / *"Open browser"* | `subprocess.Popen(['firefox'])` |
| **CMD-02** | App Management | *"Open file manager"* | `subprocess.Popen(['nautilus'])` |
| **CMD-03** | App Management | *"Open terminal"* | `subprocess.Popen(['gnome-terminal'])` |
| **CMD-04** | Window Management | *"Close this window"* | Process Lifecycle Stack (audited `SIGTERM`) |
| **CMD-05** | Workspace Audio | *"Mute sound"* / *"Unmute audio"* | `wpctl set-mute @DEFAULT_SINK@ toggle` |
| **CMD-06** | Workspace Audio | *"Turn volume up"* / *"Volume to 80%"*| `wpctl set-volume -l 1.0 @DEFAULT_SINK@ 5%+` |
| **CMD-07** | Workspace Audio | *"Turn volume down"* | `wpctl set-volume @DEFAULT_SINK@ 5%-` |
| **CMD-08** | System Diagnostics | *"Check CPU usage"* | `top -b -n1 \| head -5` |
| **CMD-09** | Hardware State | *"Check battery level"* | `upower -i $(upower -e \| grep BAT)` |
| **CMD-10** | System Info | *"What is my IP address?"* | `hostname -I` |

---

## 📊 Quantitative Benchmark Results

Evaluated across **66 automated benchmark runs** on an NVIDIA RTX 3050 Laptop GPU under Fedora Linux 40:

| Metric | Measured Value | Thesis Target | Compliance |
| :--- | :---: | :---: | :---: |
| **Mean Time-to-First-Token (TTFT)** | **37.0 ms** ($\pm 10.7\text{ ms}$) | $\le 200\text{ ms}$ | ✅ PASS |
| **Mean Time-to-First-Audio (TTFA)** | **390.5 ms** ($\pm 128.5\text{ ms}$) | $\le 1500\text{ ms}$ | ✅ PASS |
| **Intent Recognition Accuracy ($A_{\text{intent}}$)** | **100.0%** (66/66) | $\ge 90.0\%$ | ✅ PASS |
| **Generation Throughput** | **62.1 tokens/sec** | $\ge 20\text{ tok/s}$ | ✅ PASS |
| **Peak GPU VRAM Footprint** | **2,790 MB** | $\le 3,500\text{ MB}$ | ✅ PASS (1,306 MB Free) |
| **Barge-In Interruption Latency** | **< 120 ms** | $\le 200\text{ ms}$ | ✅ PASS |

Full raw data available in [`thesis_vault/05_Benchmarks/BENCH-002_Empirical_Results.md`](thesis_vault/05_Benchmarks/BENCH-002_Empirical_Results.md).

---

## 📝 The 16 Engineering Challenges & Failure Modes

A core contribution of this thesis is documenting the real-world negative results that occur when deploying theoretical AI onto edge hardware:

* **PRB-001**: Acoustic feedback loop & failure of software mic-muting.
* **PRB-002**: Whisper short-utterance hallucinations on confirmation words (*"yes"*, *"stop"*).
* **PRB-003**: CUDA Out-Of-Memory (OOM) contention when pairing heavy autoregressive TTS with desktop multitasking.
* **PRB-004**: Audio player deadlocks with `ffplay` vs. native PipeWire `pw-play`.
* **PRB-005**: Virtual echo-cancellation audio sink defaulting to 0% volume.
* **PRB-006**: Ambient noise cascading into multilingual hallucinations (Dual-Gate VAD fix).
* **PRB-007**: Non-daemon worker thread deadlocks on SIGINT shutdown.
* **PRB-008**: Out-of-scope shell command hallucinations & blocking stdin freezes.
* **PRB-009**: Silent action execution & lack of spoken telemetry.
* **PRB-010**: Uncoordinated audio stream playback collisions.
* **PRB-011**: Cloud NIM reasoning token budget exhaustion & split-brain vocalization.
* **PRB-012**: Web search parameter binding failures & subprocess terminal leaks.
* **PRB-013**: Temporal entity hallucinations in weather commands.
* **PRB-014**: Stdin window confirmation deadlocks & PortAudio C-stream teardown hangs.
* **PRB-015**: Mutter Wayland synthetic input security modal & rigid volume whitelist rejections.
* **PRB-016**: Terminal emulator suicide during window close & cloud model endpoint pinning.

All problem reports and root-cause analyses are documented in [`thesis_vault/03_Problem_Log/`](thesis_vault/03_Problem_Log/).

---

## 🚀 Quickstart & Reproduction Guide

### Prerequisites
* **OS**: Fedora Linux 40 or 41 (Workstation Edition with GNOME / Wayland)
* **GPU**: NVIDIA GPU with $\ge 4\text{ GB}$ VRAM (NVIDIA Driver 550+)
* **Audio**: PipeWire with echo cancellation module:
  ```bash
  sudo dnf install -y pipewire-plugin-echo-cancel pipewire-utils alsa-utils
  ```

### 1. Clone Repository & Setup Environment
```bash
git clone https://github.com/your-username/MY_JARVIS.git
cd MY_JARVIS

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Install & Start Local Edge Model (Ollama)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the pinned 3B edge model
ollama pull qwen2.5:3b
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env to add your optional NVIDIA_API_KEY for cloud reasoning
```

### 4. Run the Real-Time Assistant
```bash
python main.py
```
*(Wait ~3 seconds until you see `[ORCH] All loops started. Listening for speech...`)*

### 5. Run Test Suite
```bash
pytest tests/
# 8 passed in ~6.5 seconds
```

---

## 📁 Repository Structure

```
MY_JARVIS/
├── jarvis_rt/                 # Core Real-Time Conversational Engine
│   ├── controller.py          # Assistant controller & lifecycle manager
│   ├── interaction_orchestrator.py # 4-thread concurrent queue orchestrator
│   ├── vad.py                 # Dual-gate WebRTC Voice Activity Detection
│   ├── transcription.py       # OpenAI Whisper base.en transcription
│   ├── llm_stream.py          # Dual LLM router (Ollama Edge + NVIDIA NIM Cloud)
│   ├── tts_stream.py          # Sentence-bounded streaming token chunker
│   ├── coqui_tts.py           # Coqui VITS neural speech synthesis
│   ├── action_executor.py     # Two-tier safety containment & whitelist
│   └── system_actions.py      # Native Fedora OS primitives & process stack
├── jarvis_ui/                 # Decoupled Zero-VRAM Holographic HUD
├── scripts/                   # Benchmarking, diagnostics & document generation
│   ├── benchmark_suite.py     # Automated 66-trial latency & accuracy harness
│   └── diagnose_audio.sh      # PipeWire AEC & audio routing diagnostics
├── tests/                     # Unit & integration test suite
├── thesis_vault/              # Living Obsidian Research Knowledge Graph
│   ├── 00_Map_of_Content.md   # Vault dashboard & navigation index
│   ├── 01_Specification/      # Frozen commands, pinned models, supervisor rules
│   ├── 02_Architecture_Decisions/ # 10 Architectural Decision Records (ADRs)
│   ├── 03_Problem_Log/        # 16 Empirical failure mode case studies (PRBs)
│   ├── 04_Experiments/        # Empirical test logs (VAD tuning, cloud jitter)
│   ├── 05_Benchmarks/         # BENCH-002 results and raw timing datasets
│   └── 06_Thesis_Drafts/      # Formal thesis chapters (Parts 1, 2, and 3)
├── .env.example               # Safe environment variable configuration template
├── LICENSE                    # MIT License
├── main.py                    # Primary assistant entry point
├── README.md                  # Project overview & documentation
└── requirements.txt           # Python package dependencies
```

---

## 📜 Thesis Deliverables

The complete academic dissertation is compiled from the Markdown research logs into three formal installments:
* **Part 1**: [Chapters 1 & 2](thesis_vault/06_Thesis_Drafts/Thesis_Part1_Chapters_1_and_2.md) — *Introduction, Problem Formulation & Related Work*
* **Part 2**: [Chapters 3 & 4](thesis_vault/06_Thesis_Drafts/Thesis_Part2_Chapters_3_and_4.md) — *System Architecture & The 16 Failure Modes*
* **Part 3**: [Chapters 5 & 6](thesis_vault/06_Thesis_Drafts/Thesis_Part3_Chapters_5_and_6.md) — *Empirical Evaluation, RQ Answers & Final Conclusion*

---

## ⚖️ License & Attribution

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.  
* All model checkpoints (`Whisper`, `Qwen 2.5 3B`, `Coqui VITS`) comply with open-source licensing guidelines (MIT / Apache 2.0). Complete licensing audit available in [`thesis_vault/01_Specification/Pinned_Models_and_Licenses.md`](thesis_vault/01_Specification/Pinned_Models_and_Licenses.md).

