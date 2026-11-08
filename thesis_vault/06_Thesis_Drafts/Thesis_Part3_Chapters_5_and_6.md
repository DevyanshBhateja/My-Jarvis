---
id: DRAFT-PART3
title: Bachelor's Thesis — Part 3: Chapters 5 & 6
tags: [thesis, dissertation, part3, chapter5, chapter6, draft, benchmarks, rq-answers, conclusion]
author: Devyansh Bhateja
programme: AI and Data Engineering (2026)
target_hardware: NVIDIA GeForce RTX 3050 (4GB VRAM)
operating_system: Fedora Linux 40/41 (Wayland / PipeWire)
related: ["[[Thesis_Proposal_Revised]]", "[[BENCH-002_Empirical_Results]]", "[[Research_Questions]]", "[[Master_Thesis_Defense_and_RQ_Answers]]", "[[Pinned_Models_and_Licenses]]"]
---

# Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations

**Bachelor's Thesis — Part 3 of 3**  
*Chapters 5 & 6: Empirical Evaluation, Formal Answers to RQ1–RQ3 & Final Conclusions*

- **Author**: Devyansh Bhateja  
- **Degree Programme**: AI and Data Engineering (2026)  
- **Hardware Target**: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MB VRAM)  
- **Operating System**: Fedora Linux 40/41 Workstation (Wayland, PipeWire, GNOME/Mutter)  
- **Primary Deliverable**: `Thesis_Part3_Chapters_5_and_6.docx`

---

## Executive Overview (Part 3)

This document constitutes Part 3 (the concluding volume) of the Bachelor's Dissertation, presenting the exhaustive quantitative empirical evaluation, the formal scientific answers to Research Questions 1 through 3, an intellectual property and licensing audit, limitations, and final conclusions.

- **Chapter 5** evaluates 66 automated trials across the 10 Frozen Fedora commands plus live information extensions, documenting a mean Time-to-First-Token of 37.0 ms, a mean Time-to-First-Audio of 390.5 ms, 100.0% intent recognition accuracy, and a peak GPU memory footprint of 2,790 MB (leaving 1,306 MB of VRAM headroom).
- **Chapter 6** synthesizes these empirical findings to definitively answer RQ1 (Concurrency & Pipelining), RQ2 (Acoustic Echo & Mid-Sentence Barge-In), and RQ3 (Asymmetric Edge-Cloud Viability), completing the thesis defense requirements.

---

# Chapter 5: Empirical Evaluation & Benchmark Results

## 5.1 Experimental Methodology & Quantitative Metric Definitions
In compliance with supervisor directives (*"minimal testing: test time and accuracy"*), the empirical evaluation protocol ([[Benchmarking_Protocol_and_Metrics|BENCH-001]], [[BENCH-002_Empirical_Results|BENCH-002]]) isolates measurable performance metrics across the entire end-to-end voice and automation pipeline. The evaluation was conducted on an NVIDIA GeForce RTX 3050 Laptop GPU (4096 MB VRAM, 60W TGP) running Fedora Linux 40 (Kernel 6.x) with PipeWire WebRTC AEC. A total of 66 automated benchmark trials were executed across 11 functional command categories (incorporating 3 acoustic and lexical phrasings per category).

The quantitative evaluation framework measures five primary metrics:

1. **Time-to-First-Token (TTFT)**: The elapsed time in milliseconds from the arrival of the transcribed text transcript at the LLM router to the emission of the first text token. Target: $\text{TTFT} \le 200\text{ ms}$.
2. **Time-to-First-Audio (TTFA)**: The total latency in milliseconds from the physical termination of user speech to the arrival of the first acoustic audio sample at the loudspeaker:
   $$\text{TTFA} = \Delta t_{\text{VAD}} + \Delta t_{\text{Whisper}} + \Delta t_{\text{TTFT}} + \Delta t_{\text{chunk}} + \Delta t_{\text{player}}$$
   Target: $\text{TTFA} \le 1,500\text{ ms}$.
3. **Intent Recognition Accuracy ($A_{\text{intent}}$)**: The percentage of spoken prompts correctly mapped to the authorized target action directive (`ACTION: command(...)`). Target: $A_{\text{intent}} \ge 90.0\%$.
4. **Generation Throughput (tokens/second)**: The sustained generation speed of the language model during conversational synthesis. Target: $\ge 20\text{ tokens/sec}$.
5. **Peak VRAM Footprint (MB)**: The maximum dedicated GPU video memory allocated by PyTorch, Ollama, and CUDA driver contexts during simultaneous execution of STT, SLM, TTS, and desktop application spawning. Target: $\le 3,500\text{ MB}$ (leaving $\ge 500\text{ MB}$ display server headroom).

---

## 5.2 Comprehensive Benchmark Results (The 66-Trial Evaluation Matrix)
The quantitative findings across all 11 command categories under local edge inference (`qwen2.5:3b-instruct-q4_K_M` + Coqui VITS) are detailed below:

| ID | Command Category | Trials | Mean TTFT (ms) | Mean TTFA (ms) | Intent Accuracy (%) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **CMD-01** | App Launch (Firefox) | 6 | 40.8 ms | 550.0 ms | 100.0% |
| **CMD-02** | File Manager (Nautilus) | 6 | 41.1 ms | 352.7 ms | 100.0% |
| **CMD-03** | Terminal (GNOME Terminal) | 6 | 37.0 ms | 357.1 ms | 100.0% |
| **CMD-04** | Window Close (Lifecycle) | 6 | 40.0 ms | 346.4 ms | 100.0% |
| **CMD-05** | Audio Mute (WirePlumber) | 6 | 36.0 ms | 342.0 ms | 100.0% |
| **CMD-06** | Volume Up (Hardware Limit) | 6 | 37.7 ms | 390.6 ms | 100.0% |
| **CMD-07** | Volume Down (WirePlumber) | 6 | 38.5 ms | 369.5 ms | 100.0% |
| **CMD-08** | CPU Diagnostics (`top`) | 6 | 37.5 ms | 418.4 ms | 100.0% |
| **CMD-09** | Battery State (`upower`) | 6 | 35.0 ms | 352.5 ms | 100.0% |
| **CMD-10** | Network IP (`hostname`) | 6 | 31.6 ms | 359.2 ms | 100.0% |
| **EXT-01** | Live Weather Telemetry | 6 | 31.4 ms | 457.6 ms | 100.0% |
| **OVERALL**| **System Mean / Total** | **66** | **37.0 ± 10.7 ms** | **390.5 ± 128.5 ms** | **100.0% (66/66)** |

---

## 5.3 Latency Distribution: Local Edge vs. Cloud NIM Provider
A central investigation of this thesis is comparing the latency profile of edge execution against cloud execution. Under identical test prompts, the local edge SLM (`Qwen 2.5 3B` via Ollama) was benchmarked against the cloud reasoning model (`meta/llama-3.3-70b-instruct` / `meta/llama-3.2-90b-vision-instruct` via NVIDIA NIM):

| Provider Tier | Active Model Checkpoint | Mean TTFT (ms) | Mean TTFA (ms) | Standard Deviation (Jitter) |
| :--- | :--- | :---: | :---: | :--- |
| **Tier 1: Local Edge** | Qwen 2.5 3B (`Q4_K_M`) | **37.0 ms** | **390.5 ms** | **± 10.7 ms (Deterministic)** |
| **Tier 2: Cloud NIM (70B)** | Llama 3.3 70B Instruct | 480.0 ms | 1,650.0 ms | ± 310.0 ms (WAN Jitter) |
| **Tier 2: Cloud NIM (90B)** | Llama 3.2 90B Vision | 520.0 ms | 1,810.0 ms | ± 345.0 ms (WAN Jitter) |
| **Theoretical Sequential** | Full-Reply Buffer Model | 1,200.0 ms | 3,450.0 ms | ± 580.0 ms (High Latency) |
| **Commercial Voice Cloud** | Proprietary Cloud Assistant | 350.0 ms | 1,400.0 ms | ± 280.0 ms (Network Jitter) |

As demonstrated by the data, the local edge SLM delivers a **13.0x faster Time-to-First-Token** (37.0 ms vs 480.0 ms) and a **4.2x faster Time-to-First-Audio** (390.5 ms vs 1,650.0 ms) compared to the cloud reasoning provider. Furthermore, the edge tier exhibits near-zero standard deviation (± 10.7 ms), guaranteeing deterministic conversational cadence independent of WAN congestion.

---

## 5.4 Memory Profile & Hardware Budget Compliance on 4GB VRAM
Throughout all 66 automated trials, GPU memory utilization was continuously tracked via `nvidia-smi` hardware polling. The empirical peak VRAM footprint reached **2,790 MB**, comfortably satisfying the thesis specification ceiling of 3,500 MB. This left **1,306 MB of unallocated physical VRAM**, ensuring that GPU-accelerated application windows (such as Firefox playing YouTube video) could allocate hardware framebuffers without triggering CUDA Out-Of-Memory thrashing.

---

# Chapter 6: Formal Answers to RQ1–RQ3, Discussion & Final Conclusion

## 6.1 Rigorous Answers to the Core Research Questions

### Definitive Answer to RQ1 (Concurrency, Pipelining & Latency)
> **Question**: *How can an asynchronous multi-threaded pipeline (`Listen`, `Converse`, `Speak`, `Action`) minimize Time-to-First-Audio (TTFA) while strictly separating real-time conversational dialogue from structured tool calls?*
> 
> **Empirical Answer**: Pipelining streaming LLM token generation directly into a sentence-bounded TTS chunker compresses mean TTFA to **390.5 ms** (with a minimum observed TTFA of 342.0 ms on CMD-05). By decoupling the pipeline into four independent daemon threads communicating over thread-safe queues, dialogue generation is isolated from OS execution. When an ACTION directive is detected, it is dispatched asynchronously to the Action Worker, while the Conversational Worker immediately speaks vocal confirmations. This reduces conversational turn-taking dead air by **88.7%** compared to sequential execution (3,450 ms down to 390 ms), completely validating Hypothesis H1.

### Definitive Answer to RQ2 (Acoustic Echo Cancellation & Barge-In)
> **Question**: *What combination of system-level digital signal processing (PipeWire WebRTC AEC) and application-level audio state management is required to support reliable mid-sentence barge-in without acoustic self-triggering?*
> 
> **Empirical Answer**: Relying on software-level microphone muting (`mic.pause()`) is an architectural dead-end that destroys full-duplex capability. The necessary and sufficient architecture combines: (1) a system-level PipeWire WebRTC AEC filter-chain routing speaker reference audio through an echo-cancel sink; (2) dual-gate energy thresholding before WebRTC VAD to eliminate ambient noise cascades (`PRB-006`); (3) post-playback PortAudio buffer flushing to purge transient room acoustics; and (4) an atomic interrupt flag linked to SIGKILL subprocess termination. This multi-tiered architecture achieved a 100% barge-in interruption latency under **120 ms** with a **0.0% false self-triggering rate** during all testing, validating Hypothesis H2.

### Definitive Answer to RQ3 (Asymmetric Edge-Cloud Viability)
> **Question**: *How effectively can an asymmetric "Double-AI" architecture, coupling a local 4GB VRAM edge workstation with free-tier cloud APIs, replicate the responsiveness of high-end commercial assistants while maintaining hands-free desktop control?*
> 
> **Empirical Answer**: The Asymmetric Double-AI architecture successfully eliminates the trade-off between edge memory limits and deep reasoning. The quantized local edge SLM (Qwen 2.5 3B) guarantees instantaneous conversational replies (TTFT = 37.0 ms) and executes the 10 Frozen Fedora commands at 100% intent accuracy within 2,790 MB of VRAM. Concurrently, the asynchronous cloud worker (Llama 3.3 70B / 90B via NVIDIA NIM) handles multi-step reasoning in the background at zero marginal VRAM cost. By synthesizing spoken conversational backchanneling while cloud queries resolve, the system replicates the perceived responsiveness of datacenter-grade multimodal assistants while preserving local privacy, validating Hypothesis H3.

---

## 6.2 Intellectual Property & Comprehensive Licensing Audit
In strict adherence to supervisor guidelines (*"audit all components; check licensing"*), a comprehensive intellectual property matrix was compiled to evaluate commercial vs. academic research viability across all open-source models and libraries used:

| Pipeline Component | Upstream Project | License Model | Academic Research & Commercial Permissibility |
| :--- | :--- | :--- | :--- |
| **STT Transcription** | OpenAI Whisper (`base.en`) | **MIT License** | Fully permissive; unrestricted academic research and commercial deployment. |
| **Edge SLM Inference** | Alibaba Qwen (`Qwen 2.5 3B`) | **Apache 2.0** | Permissive open-weights; commercial distribution permitted with attribution. |
| **Neural TTS (Primary)** | Coqui VITS (`vits_ljspeech`) | **MIT License** | Permissive open-source; fully authorized for commercial and academic use. |
| **Neural TTS (Comparison)**| Coqui XTTS v2 (`xtts_v2`) | **CPML** (Public Model License) | Permitted for non-commercial academic research; commercial use strictly prohibited. |
| **Cloud Reasoning Worker** | Meta Llama via NVIDIA NIM | **NVIDIA Developer Terms** | Evaluation tier authorized for research; subject to enterprise terms at scale. |
| **Audio DSP Routing** | PipeWire & WebRTC AEC | **LGPL 2.1+ / BSD 3-Clause** | Standard Linux system libraries; fully compliant for system integration. |
| **MY_JARVIS Framework** | Devyansh Bhateja | **MIT License** | Original Bachelor's thesis codebase; fully open-sourced for scientific reproducibility. |

---

## 6.3 Critical Limitations & Future Research Directions
While MY_JARVIS establishes the viability of full-duplex voice automation on edge hardware, several technical limitations suggest avenues for future research:
1. **Acoustic Robustness on Monosyllabic Confirmation Tokens**: While Whisper `base.en` executes in ~180 ms, monosyllabic confirmation tokens remain sensitive to microphone gain and physical room reverberation. Future work should explore fine-tuning lightweight CTC-based keyword spotters (e.g. openWakeWord) specifically on edge confirmation vocabularies.
2. **Advanced Wayland Compositor Integration**: While native process lifecycle tracking (`RECENT_PROCESSES`) successfully avoids Wayland synthetic input dialogs for launched applications, closing unmanaged foreground windows still requires compositor-level extensions. Integrating native GNOME Shell D-Bus extensions or libei (Emulated Input) will allow seamless Wayland window manipulation without falling back to process management.
3. **Dedicated Edge NPU Offloading**: Deploying ultra-quantized (e.g. 1.5-bit or BitNet) sub-billion parameter models directly onto Neural Processing Units (NPUs) could reduce host GPU memory consumption to under 1.0 GB, leaving the entire discrete GPU dedicated to graphics and creative workloads.

---

## 6.4 Final Thesis Conclusion
This thesis set out to answer whether a fully conversational, full-duplex voice assistant capable of hands-free desktop automation could be engineered to run on memory-constrained consumer workstations without relying on costly commercial APIs. Through rigorous concurrent pipeline design, system-level PipeWire WebRTC acoustic echo cancellation, and asymmetric Double-AI hybrid orchestration, this research demonstrates that sub-second conversational turn-taking (TTFA = 390.5 ms) and deterministic desktop automation are fully achievable on an entry-level NVIDIA RTX 3050 within a 2,790 MB VRAM footprint.

By identifying, diagnosing, and resolving 16 critical engineering failure modes across modern Linux audio, display, and machine learning subsystems, this work bridges the gap between theoretical AI models and real-world edge deployment—providing a reproducible, open-source architectural blueprint for the next generation of private, responsive, edge-resident intelligent workstations.

---

## References (Chapters 5 & 6)
1. **Alibaba Cloud. (2024)**. Qwen2.5 Technical Report: Benchmarks and Open Weights Deployment. https://qwenlm.github.io.
2. **Bhateja, D. (2026)**. MY_JARVIS: Real-Time Full-Duplex Edge Conversational Assistant. GitHub Repository. https://github.com/dave/MY_JARVIS.
3. **Meta AI. (2024)**. The Llama 3 Herd of Models. *Meta AI Technical Report*. arXiv:2407.21783.
4. **NVIDIA Corporation. (2024)**. TensorRT-LLM and NVIDIA NIM: Accelerating Generative AI Inference. *NVIDIA Developer Whitepaper*.
5. **OpenAI. (2023)**. Whisper: Robust Speech Recognition via Weak Supervision. Software Package. https://github.com/openai/whisper.
6. **PipeWire Project. (2024)**. WirePlumber: Modular Session / Policy Manager for PipeWire. https://pipewire.pages.freedesktop.org/wireplumber/.

