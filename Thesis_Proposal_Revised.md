# Bachelor’s Thesis Proposal (Revised)

# Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations

**Author:** Devyansh Bhateja  
**Degree Programme:** AI and Data Engineering  
**Academic Year:** 2026  
**Target Hardware:** NVIDIA GeForce RTX 3050 (4GB VRAM)  
**Operating System:** Fedora Linux 40/41  

---

## Table of Contents
1. [Executive Summary & Scope](#1-executive-summary--scope)
2. [Problem Statement & Technical Motivation](#2-problem-statement--technical-motivation)
3. [Proposed Architecture: The Asymmetric "Double-AI" Hybrid Duplex](#3-proposed-architecture-the-asymmetric-double-ai-hybrid-duplex)
4. [Research Questions & Formal Hypotheses](#4-research-questions--formal-hypotheses)
5. [Strict Scope Containment: The Frozen Fedora Benchmark Suite](#5-strict-scope-containment-the-frozen-fedora-benchmark-suite)
6. [Pinned Model Specifications & VRAM Memory Budget](#6-pinned-model-specifications--vram-memory-budget)
7. [Minimal Testing Protocol: Time, Accuracy & Known Failure Modes](#7-minimal-testing-protocol-time-accuracy--known-failure-modes)
8. [Comprehensive Licensing & Intellectual Property Audit](#8-comprehensive-licensing--intellectual-property-audit)
9. [Prerequisites for Practical Reproduction](#9-prerequisites-for-practical-reproduction)
10. [Nomenclature & Abbreviations Glossary](#10-nomenclature--abbreviations-glossary)
11. [Deliverables & Milestone Timeline](#11-deliverables--milestone-timeline)

---

## 1. Executive Summary & Scope

This thesis addresses an applied software systems and AI engineering challenge: **achieving real-time, full-duplex conversational voice interaction and deterministic desktop automation on consumer-grade edge workstations with tight memory limits (NVIDIA GeForce RTX 3050 with 4GB VRAM)**.

Rather than training foundational neural network weights from scratch, the research focuses on pipeline concurrency, asynchronous edge-cloud orchestration, digital signal processing (DSP) echo cancellation, and low-latency full-duplex communication. The engineering goal is to replace rigid, half-duplex "walkie-talkie" turn-taking with a natural, interruptible voice interface capable of hands-free operating system control on Fedora Linux at zero marginal API cost.

---

## 2. Problem Statement & Technical Motivation

Current consumer voice assistants process interactions through a rigid, sequential half-duplex pipeline:
$$\text{Speech Capture} \longrightarrow \text{VAD} \longrightarrow \text{STT} \longrightarrow \text{LLM Generation} \longrightarrow \text{TTS Synthesis} \longrightarrow \text{Audio Playback}$$

This sequential structure produces three fundamental bottlenecks on edge workstations:

1. **Unacceptable Perceptible Latency:** End-to-end response times routinely sit between 2.5 and 5.0 seconds. Waiting for full LLM generation before starting speech synthesis destroys conversational cadence.
2. **Barge-In Failure & Acoustic Feedback:** When speakers are active, incoming microphone frames capture the assistant's own voice. Naive systems either mute the microphone (preventing mid-sentence user interruptions) or suffer acoustic feedback loops where the assistant self-interrupts.
3. **Severe Edge Memory Constraints (4GB VRAM):** Running Automatic Speech Recognition (Whisper), an autoregressive Small Language Model (SLM), and a Neural Text-to-Speech (TTS) engine simultaneously on an NVIDIA RTX 3050 (4096 MB VRAM) routinely triggers fatal CUDA Out-Of-Memory (OOM) crashes, especially when desktop applications (e.g., Firefox) demand GPU framebuffer memory.
4. **Unpredictable Cloud Jitter:** Relying purely on cloud APIs introduces variable WAN latency (300–1200ms jitter) and recurring per-token financial costs.

---

## 3. Proposed Architecture: The Asymmetric "Double-AI" Hybrid Duplex

To resolve the tension between edge memory limits and deep reasoning requirements, the system decouples conversational responsiveness from complex task planning:

```
                            USER SPEECH
                                 │
                                 ▼
                     [PipeWire WebRTC AEC]
                   (Acoustic Echo Cancellation)
                                 │
                                 ▼
                    [OpenAI Whisper (base.en)]
                                 │
                                 ▼
                 [Interaction Orchestrator Queue]
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
 [Tier 1: Edge Dialogue Loop]               [Tier 2: Cloud Reasoning Worker]
  • Model: Qwen 2.5 3B (Ollama)              • Model: Llama 3.3 70B (NVIDIA NIM)
  • Role: Instant conversational reply        • Role: Multi-step OS tool planning
  • Latency: TTFT < 200ms                    • Latency: Async background execution
  • Footprint: ~1.9 GB VRAM                  • Footprint: 0 MB VRAM
         │                                               │
         ▼                                               ▼
 [Sentence-Bounded TTS Chunker]             [Action Execution Engine]
  (Flushes every 10-15 tokens)               (Human-in-the-Loop Confirmation)
         │                                               │
         ▼                                               ▼
  [Coqui VITS Synthesis]                     [10 Frozen Fedora Commands]
  (Hardware Playback via pw-play)                        │
         ▲                                               │
         └───────────────────────────────────────────────┘
                     Task Completion Feedback
```

### 3.1 The Local Edge Tier (Low Latency Loop)
- **Runtime & Models:** Runs 100% locally on the RTX 3050 GPU using Whisper `base.en`, Ollama-quantized `Qwen 2.5 3B`, and Coqui VITS.
- **Audio Infrastructure:** Linux PipeWire WebRTC Acoustic Echo Cancellation (`libpipewire-module-echo-cancel`).
- **Core Function:** Guarantees sub-second Time-to-First-Audio (TTFA), immediate spoken backchanneling (*"Checking that for you now..."*), and hardware-level barge-in cancellation under 200ms.

### 3.2 The Cloud Worker Tier (Asynchronous Reasoning Loop)
- **Infrastructure:** NVIDIA NIM developer endpoints (hosting `meta/llama-3.3-70b-instruct`) operating under developer free-tier quotas.
- **Core Function:** Operates asynchronously in the background on complex queries. It handles multi-step tool parameter extraction and complex diagnostic reasoning without blocking the audio output of the local dialogue loop.

### 3.3 The OS Automation & Execution Layer (Fedora Linux)
- **Integration:** Bridges parsed high-level intent (`ACTION: command(...)`) directly into native Fedora system utilities (`wpctl`, `upower`, `top`, `subprocess`).
- **Safety Protocol:** Strictly enforces a voice/terminal confirmation prompt (*"Approve action? (yes/no)"*) before triggering operating system state mutations.

---

## 4. Research Questions & Formal Hypotheses

### RQ1 (Concurrency & Pipelining)
> **Question:** *How can an asynchronous multi-threaded pipeline (`Listen`, `Converse`, `Speak`, `Action`) minimize Time-to-First-Audio (TTFA) while separating real-time dialogue from structured tool calls?*
- **Hypothesis:** By coupling streaming LLM token generation directly with sentence-bounded TTS chunking (10–15 tokens per chunk), Time-to-First-Audio can be compressed under 1.5 seconds, even on local edge GPUs.

### RQ2 (Acoustic Echo & Mid-Sentence Barge-In)
> **Question:** *What combination of system-level acoustic echo cancellation (PipeWire WebRTC AEC) and soft audio state management is required to support reliable mid-sentence barge-in without self-triggering?*
- **Hypothesis:** Software-only microphone muting eliminates feedback but destroys full-duplex responsiveness. A system-level PipeWire WebRTC AEC filter chain is necessary and sufficient to permit continuous listening during playback with barge-in interruption latency under 200ms.

### RQ3 (Asymmetric Edge-Cloud Viability)
> **Question:** *How effectively can an asymmetric architecture, coupling a local 4GB VRAM edge device with free-tier cloud APIs, replicate the responsiveness of commercial, high-end voice assistants while maintaining hands-free desktop control?*
- **Hypothesis:** An asymmetric "Double-AI" model—where a fast local SLM (Qwen 2.5 3B) provides instant conversational backchanneling while a cloud worker (Llama 3.3 70B via NVIDIA NIM) asynchronously plans and verifies OS actions—satisfies sub-second conversational ergonomics without exceeding a 4GB VRAM ceiling.

---

## 5. Strict Scope Containment: The Frozen Fedora Benchmark Suite

Per the supervisor's instruction (*"make a list what i can do, test that nothing more"*), desktop automation is strictly confined to a **frozen catalog of 10 deterministic commands**:

| ID | Category | Voice Prompt Trigger | Internal Implementation | Target OS Utility | Expected Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CMD-01** | App Management | *"Launch Firefox"* / *"Open browser"* | `open_app("firefox")` | `subprocess.Popen(["firefox"])` | Spawns browser window |
| **CMD-02** | App Management | *"Open file manager"* | `open_app("nautilus")` | `subprocess.Popen(["nautilus"])` | Spawns Nautilus explorer |
| **CMD-03** | App Management | *"Open terminal"* | `open_app("gnome-terminal")` | `subprocess.Popen(["gnome-terminal"])`| Spawns terminal window |
| **CMD-04** | Window Management | *"Close active window"* | `hotkey("alt", "f4")` | `pyautogui.hotkey('alt', 'f4')` | Terminates active window |
| **CMD-05** | Workspace Audio | *"Mute audio"* / *"Unmute sound"* | `run_command("wpctl set-mute @DEFAULT_SINK@ toggle")` | `wpctl` (WirePlumber) | Toggles mute state on default sink |
| **CMD-06** | Workspace Audio | *"Turn volume up"* | `run_command("wpctl set-volume @DEFAULT_SINK@ 5%+")` | `wpctl` | Increases sink volume by 5% |
| **CMD-07** | Workspace Audio | *"Turn volume down"* | `run_command("wpctl set-volume @DEFAULT_SINK@ 5%-")` | `wpctl` | Decreases sink volume by 5% |
| **CMD-08** | System Diagnostics | *"Check CPU usage"* | `run_command("top -b -n1 \| head -5")` | `top` utility | Extracts CPU idle and load metrics |
| **CMD-09** | Hardware State | *"Check battery level"* | `run_command("upower -i $(upower -e \| grep BAT)")` | `upower` daemon | Returns battery charge % and state |
| **CMD-10** | System Info | *"What is my IP address?"* | `run_command("hostname -I")` | `hostname` utility | Returns local network IPv4 address |

*Constraint:* Zero unlisted desktop actions or arbitrary web browsing tasks will be tested or evaluated in the thesis.

---

## 6. Pinned Model Specifications & VRAM Memory Budget

To guarantee academic reproducibility, all model versions and precision formats are fixed:

| Pipeline Stage | Model Identifier & Checkpoint | Parameter Count | Precision / Quantization | VRAM Footprint |
| :--- | :--- | :--- | :--- | :--- |
| **STT** | `openai-whisper:base.en` | 74M | PyTorch FP32/FP16 Checkpoint | ~250 MB |
| **Edge SLM** | `Qwen/Qwen2.5-3B-Instruct` | 3.09B | Ollama `qwen2.5:3b-instruct-q4_K_M` | ~1,900 MB |
| **Cloud Worker** | `meta/llama-3.3-70b-instruct` | 70B | NVIDIA NIM Cloud API | 0 MB (Cloud) |
| **Local TTS (Primary)** | Coqui VITS (`vits_ljspeech`) | ~30M | PyTorch Checkpoint | ~300 MB |
| **Local TTS (Comparison)**| Coqui XTTS v2 (`xtts_v2`) | ~460M | PyTorch Checkpoint (Diffusion/Autoreg)| ~1,600 MB |
| **VAD** | Google WebRTC VAD | N/A | C Library (`webrtcvad` Mode 1) | 0 MB (Host CPU) |
| **AEC** | PipeWire WebRTC AEC | N/A | PipeWire DSP Module | 0 MB (Host CPU) |

### Memory Budget Analysis on 4096 MB VRAM Ceiling
- **Primary Operational Baseline (Whisper + Qwen-3B + VITS):**
  $$\text{Total VRAM} = 250\text{ MB} + 1,900\text{ MB} + 300\text{ MB} = \mathbf{2,450\text{ MB}}$$
  *Available Headroom:* $\mathbf{1,646\text{ MB}}$ remaining for GNOME display server buffers, Wayland compositing, and application windows (Firefox). **Zero OOM risk.**
- **Heavy Comparison Baseline (Whisper + Qwen-3B + XTTS v2):**
  $$\text{Total VRAM} = 250\text{ MB} + 1,900\text{ MB} + 1,600\text{ MB} = \mathbf{3,750\text{ MB}}$$
  *Available Headroom:* Only $\mathbf{346\text{ MB}}$ remaining. Launching Firefox triggers immediate CUDA memory allocation failures. Documented in thesis as an empirical failure threshold.

---

## 7. Minimal Testing Protocol: Time, Accuracy & Known Failure Modes

In compliance with supervisor guidance (*"minimal testing: test time and accuracy, mention the problems"*), testing focuses strictly on quantifiable latency, accuracy, and failure modes:

### 7.1 Latency Benchmarks (Time)
1. **Time-to-First-Token (TTFT):** Milliseconds from user speech transcript arrival to first token emission by the language model.
2. **Time-to-First-Audio (TTFA):** Total elapsed milliseconds from user speech termination to first audio sample emitted by speaker:
   $$\text{TTFA} = \Delta t_{\text{VAD\_debounce}} + \Delta t_{\text{Whisper\_ASR}} + \Delta t_{\text{TTFT}} + \Delta t_{\text{TTS\_chunk\_synthesis}} + \Delta t_{\text{player\_buffer}}$$
3. **Barge-In Interruption Latency ($L_{\text{barge}}$):** Milliseconds from user interruption onset to active audio process termination (`SIGKILL`). Target: $\le 200\text{ ms}$.

### 7.2 Accuracy Benchmarks
1. **Intent Recognition Accuracy ($A_{\text{intent}}$):** Percentage of spoken commands correctly mapped to the target action across 50 trials per command ($N = 500$ total trials).
2. **Action Execution Success Rate ($S_{\text{exec}}$):** Percentage of approved OS commands exiting with status code `0`.
3. **False Barge-In Rate ($R_{\text{false}}$):** Rate at which the assistant falsely self-interrupts due to acoustic echo bleed. Target: $\le 2.0\%$.

### 7.3 Explicitly Documented Problems & Real-World Failure Modes
The thesis report will dedicate Chapter 4 to analyzing the following technical failures:
1. **Acoustic Bleed & AEC Failure:** How physical speaker volume, microphone proximity, and room reverberation challenge WebRTC AEC algorithms.
2. **ASR Hallucination on Confirmation Tokens:** Whisper's tendency to hallucinate (*"Thank you for watching"*) on sub-500ms monosyllabic words (*"yes"*, *"no"*) when pre-speech padding and audio peak normalization are omitted.
3. **VRAM Eviction Under Desktop Multitasking:** System instability caused when GPU-accelerated desktop applications contest GPU VRAM alongside heavy neural TTS models (XTTS v2).
4. **Cloud WAN Latency Jitter:** Fluctuations in external developer endpoint response times compared against deterministic local edge inference.

---

## 8. Comprehensive Licensing & Intellectual Property Audit

| Component | Upstream Project | License Type | Academic Research Terms | Commercial Terms |
| :--- | :--- | :--- | :--- | :--- |
| **STT** | OpenAI Whisper | **MIT License** | Unrestricted open access | Permitted |
| **Edge SLM** | Qwen 2.5 3B | **Apache 2.0** | Unrestricted open access | Permitted |
| **Local TTS (VITS)**| Coqui Community | **MIT License** | Unrestricted open access | Permitted |
| **Local TTS (XTTS)**| Coqui AI | **CPML** (Coqui Public Model License) | **Permitted for non-commercial academic research** | Prohibited without commercial license |
| **Cloud Worker** | NVIDIA NIM | **NVIDIA Developer Terms** | Free evaluation tier granted for prototyping | Subject to enterprise licensing |
| **Audio Routing** | PipeWire & WebRTC | **LGPL 2.1+ / BSD 3-Clause** | Open-source system software | Permitted |
| **Assistant Code** | MY_JARVIS | **MIT License** | Author's original research codebase | Permitted |

*Thesis Note:* The legal distinction between Coqui VITS (MIT) and XTTS v2 (CPML) is formally analyzed in the thesis when discussing the real-world deployment viability of edge AI assistants.

---

## 9. Prerequisites for Practical Reproduction

Any evaluator can reproduce the empirical benchmarks using the following specification:

### A. Workstation Hardware
- **GPU:** NVIDIA GeForce RTX 3050 (Laptop or Desktop, 4096 MB GDDR6 VRAM, CUDA Compute Capability 8.6).
- **CPU & Host RAM:** Intel Core i5/i7 (11th Gen+) or AMD Ryzen 5/7 (5000 series+), $\ge 16\text{ GB}$ system RAM.
- **Audio Gear:** Integrated/USB microphone + external stereo speakers.

### B. Operating System & Linux Packages
- **Distribution:** Fedora Linux 40 or 41 (Workstation Edition).
- **Core System Dependencies:**
  ```bash
  sudo dnf install -y pipewire-plugin-echo-cancel pipewire-utils alsa-utils mpg123
  ```
- **Local Inference Engine:**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ollama pull qwen2.5:3b
  ```

### C. Python 3.11 Virtual Environment
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install openai-whisper TTS sounddevice webrtcvad openai pyautogui python-docx
```

---

## 10. Nomenclature & Abbreviations Glossary

| Abbreviation | Expanded Full Name | Definition in Context of the Thesis |
| :--- | :--- | :--- |
| **AEC** | **Acoustic Echo Cancellation** | DSP algorithm removing speaker playback from microphone capture to avoid feedback loops. |
| **ASR** | **Automatic Speech Recognition** | Algorithmic conversion of spoken acoustic signals into textual transcripts. |
| **CPML** | **Coqui Public Model License** | Restrictive license permitting non-commercial research while prohibiting unlicensed commercial distribution. |
| **CUDA** | **Compute Unified Device Architecture** | NVIDIA's parallel computing platform and programming interface for GPU execution. |
| **D-Bus** | **Desktop Bus** | Standard Linux inter-process communication mechanism for desktop and system daemon management. |
| **FP16 / FP32**| **Floating-Point 16 / 32-bit** | Numerical precision representations balancing computational throughput against memory consumption. |
| **HCI** | **Human-Computer Interaction** | Academic discipline studying the ergonomics and interaction paradigms between humans and machines. |
| **LLM** | **Large Language Model** | High-parameter transformer neural networks ($\ge 70\text{B}$ parameters) hosted on cloud clusters for deep reasoning. |
| **NIM** | **NVIDIA Inference Microservice** | Containerized deployment microservice and cloud API providing optimized inference execution. |
| **OOM** | **Out-Of-Memory** | Exception condition triggered when software attempts to allocate more VRAM or RAM than physically available. |
| **PCM** | **Pulse-Code Modulation** | Uncompressed digital encoding of analog audio waveforms sampled at discrete intervals (16 kHz 16-bit). |
| **RMS** | **Root Mean Square** | Statistical measure of varying audio signal amplitude used in energy-based speech detection. |
| **SLM** | **Small Language Model** | Quantized neural language models ($\le 3\text{B}$ parameters) optimized for edge GPU execution. |
| **STT** | **Speech-to-Text** | The pipeline component transcribing human voice audio into textual tokens. |
| **TTFA** | **Time-to-First-Audio** | Latency metric: elapsed time from user speech termination to first acoustic output from the speaker. |
| **TTFT** | **Time-to-First-Token** | Latency metric: elapsed time from prompt dispatch to first token emission by the language model. |
| **TTS** | **Text-to-Speech** | The pipeline component synthesizing natural spoken waveforms from text strings. |
| **VAD** | **Voice Activity Detection** | Algorithmic classifier detecting the boundary transitions between speech and ambient silence. |
| **VITS** | **Variational Inference TTS** | Lightweight, non-autoregressive neural speech synthesis architecture characterized by low VRAM footprint. |
| **VRAM** | **Video Random-Access Memory** | High-speed dedicated physical memory mounted directly on the GPU board. |
| **XTTS** | **Extended Text-to-Speech** | Autoregressive and diffusion-based neural TTS architecture supporting zero-shot voice cloning. |

---

## 11. Deliverables & Milestone Timeline

1. **Reference Implementation:** A fully functional, full-duplex conversational voice assistant running on Fedora Linux and an RTX 3050 (4GB VRAM) supporting mid-sentence barge-in and the 10 frozen desktop automation commands.
2. **Empirical Benchmarking Dataset:** Documented latency measurements (TTFT, TTFA, $L_{\text{barge}}$) and accuracy metrics across 500 standardized command trials.
3. **Completed Bachelor's Thesis Report:** A formal academic dissertation detailing architectural trade-offs, negative results/engineering failures, and findings addressing RQ1, RQ2, and RQ3.
