---
id: DRAFT-PART1
title: Bachelor's Thesis — Part 1: Chapters 1 & 2
tags: [thesis, dissertation, part1, chapter1, chapter2, draft]
author: Devyansh Bhateja
programme: AI and Data Engineering (2026)
target_hardware: NVIDIA GeForce RTX 3050 (4GB VRAM)
operating_system: Fedora Linux 40/41 (Wayland / PipeWire)
related: ["[[Thesis_Proposal_Revised]]", "[[Supervisor_Guidelines]]", "[[Research_Questions]]", "[[Pinned_Models_and_Licenses]]", "[[Frozen_Fedora_Commands]]"]
---

# Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations

**Bachelor's Thesis — Part 1 of 3**  
*Chapters 1 & 2: Introduction, Problem Formulation, Theoretical Foundations & Related Work*

- **Author**: Devyansh Bhateja  
- **Degree Programme**: AI and Data Engineering (2026)  
- **Hardware Target**: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MB VRAM)  
- **Operating System**: Fedora Linux 40/41 Workstation (Wayland, PipeWire, GNOME/Mutter)  
- **Primary Deliverable**: `Thesis_Part1_Chapters_1_and_2.docx`

---

## Executive Overview (Part 1)

This document constitutes Part 1 of the formal Bachelor's Dissertation, establishing the rigorous theoretical, algorithmic, and system-level foundations for real-time full-duplex conversational voice interaction and deterministic desktop automation under a strict 4096 MB VRAM hardware boundary.

- **Chapter 1** formalizes the technical motivation, the breakdown of the classical half-duplex walkie-talkie paradigm, the mathematical memory budget constraints on consumer edge hardware, the formal Research Questions ([[Research_Questions|RQ1–RQ3]]), and the strictly contained 10-command Fedora automation catalog ([[Frozen_Fedora_Commands]]).
- **Chapter 2** delivers a systematic review of the state-of-the-art across five critical engineering domains: digital signal processing (DSP) for Linux audio echo cancellation (PipeWire WebRTC AEC), low-latency edge speech recognition (OpenAI Whisper), quantized small language models (Qwen 2.5 3B via GGUF/Ollama), memory-constrained neural speech synthesis (Coqui VITS vs. XTTS v2), and modern display server automation security under Wayland and GNOME/Mutter.

---

# Chapter 1: Introduction & Problem Formulation

## 1.1 Context and Technical Motivation
Over the past decade, conversational voice assistants have transitioned from simple keyword-spotted command parsers into sophisticated dialogue agents powered by large-scale deep neural networks. Commercial cloud-hosted ecosystems—such as Apple Siri, Amazon Alexa, and Google Assistant—have established voice as a mainstream modality for user interaction. More recently, the emergence of large language models (LLMs) and end-to-end multimodal systems (e.g., GPT-4o, Gemini Live) has demonstrated the dramatic ergonomic benefits of natural, flexible, human-like voice communication. However, these systems universally depend on multi-gigawatt hyperscale cloud data centers, transmitting uncompressed or lightly compressed user audio across wide-area networks (WAN) to remote server clusters.

While cloud-anchored architectures deliver massive parameter capacity, they introduce severe architectural and operational liabilities:

1. **Latency Jitter & Lack of Determinism**: Cloud voice transmission introduces inherent network latency jitter ranging from 250 milliseconds to multiple seconds, fundamentally prohibiting deterministic, conversational turn-taking rhythms.
2. **Privacy and Data Sovereignty**: Streaming raw, continuous room acoustics to external corporate third parties creates acute privacy and security risks, rendering cloud assistants non-compliant with strict corporate, healthcare, and academic data governance standards (such as GDPR).
3. **Economic Unviability**: Commercial cloud conversational APIs impose recurring per-token or per-minute financial costs, creating unsustainable economic overhead for continuous, background desktop monitoring and workstation automation.
4. **Desktop Isolation**: A desktop agent must interact with local operating system primitives (process managers, audio mixers, display servers, and file systems). Cloud models lack direct low-latency hooks into local kernel interfaces and must operate through complex, fragile remote RPC bridges.

Consequently, there is an urgent academic and engineering need for entirely self-contained, edge-resident voice assistants capable of executing full-duplex conversational reasoning and operating system automation directly on local personal workstations.

---

## 1.2 The Half-Duplex Bottleneck vs. Full-Duplex Conversational Dynamics
Existing open-source edge voice assistants almost universally implement a rigid, sequential, half-duplex interaction pipeline. Under this classical paradigm, interaction proceeds through strictly discrete, non-overlapping phases:

$$\text{Speech Capture} \longrightarrow \text{VAD} \longrightarrow \text{ASR} \longrightarrow \text{LLM Inference} \longrightarrow \text{Neural TTS Synthesis} \longrightarrow \text{Audio Playback}$$

This sequential pipeline imposes two crippling flaws on human-machine dialogue:

### A. The Turn-Taking Latency Penalty
In a sequential architecture, speech synthesis cannot begin until the language model has finished generating its entire textual response. For an autoregressive model generating a 60-token reply at 30 tokens/second, this incurs a mandatory 2,000 ms delay before speech synthesis even starts. Coupled with ASR transcription overhead (300–600 ms) and TTS vocoder latency (400–800 ms), the user experiences a jarring 3.0 to 4.5 second pause between speaking and hearing the assistant's first word. Psychoacoustic and sociolinguistic research in human-computer interaction (HCI) demonstrates that conversational silences exceeding 1,000 ms disrupt natural conversational rhythm, causing users to perceive the agent as sluggish, unresponsive, or frozen.

### B. The Acoustic Feedback & Barge-In Dilemma
In human speech, conversation is inherently full-duplex: both participants listen continuously, even while speaking. In contrast, naive edge systems suffer from fatal acoustic feedback loops. If the microphone remains active while the speaker is outputting synthesized voice, the assistant ingests its own speech, interprets it as a new user command, and enters an infinite self-triggering feedback loop. To prevent this, naive implementations simply mute the microphone (`mic.pause()`) during audio playback. However, software muting degrades the assistant into a primitive "walkie-talkie": if the assistant begins speaking an incorrect, verbose, or outdated response, the user is completely powerless to interrupt mid-sentence ("barge-in"). The user must passively wait for audio playback to terminate before issuing a correction.

---

## 1.3 The Extreme Memory Constraint: The 4GB VRAM Hardware Boundary
While full-duplex conversational systems are theoretically achievable by running massive multi-billion parameter neural networks in parallel, deploying such architectures on consumer-grade edge hardware encounters an unyielding physical bottleneck: Video Random-Access Memory (VRAM).

The target hardware evaluation platform for this thesis is an **NVIDIA GeForce RTX 3050 Laptop GPU** equipped with exactly **4096 MB of GDDR6 VRAM**. The RTX 3050 represents the dominant entry-level discrete GPU deployed across millions of student, developer, and engineering laptops globally. Operating within a 4GB VRAM envelope is qualitatively distinct from datacenter environments:

| Component / Pipeline Stage | Model / Architecture | VRAM Allocation | Memory Footprint (% of 4GB) |
| :--- | :--- | :---: | :---: |
| **Speech-to-Text (STT)** | OpenAI Whisper (`base.en`, FP16) | **250 MB** | 6.1% |
| **Edge Small Language Model (SLM)** | Qwen 2.5 3B (Ollama `Q4_K_M`) | **1,900 MB** | 46.4% |
| **Neural Speech Synthesis (TTS)** | Coqui VITS (`vits_ljspeech`) | **300 MB** | 7.3% |
| **Host OS & Display Server** | Fedora GNOME / Mutter (Wayland Buffers) | **350 – 500 MB** | 8.5% – 12.2% |
| **Total Baseline Allocation** | **Whisper + Qwen-3B + VITS + Desktop** | **~2,950 MB** | **~72.0%** |

Under this primary baseline allocation, the combined static neural footprint totals 2,450 MB. Adding the ~500 MB required by the Fedora Wayland display server leaves exactly 1,146 MB of physical headroom. This safety margin is vital: when the assistant executes desktop commands (such as launching Firefox or VS Code), application window buffers demand GPU memory. If the model footprint exceeds 3,500 MB, desktop multitasking triggers fatal CUDA Out-Of-Memory (OOM) exceptions and crashes the host session.

---

## 1.4 Research Questions & Formal Hypotheses
To rigorously investigate this engineering domain, the research is organized around three foundational Research Questions:

### RQ1: Concurrency, Streaming Pipelining & Latency Minimization
> **Question**: *How can an asynchronous multi-threaded pipeline (`Listen`, `Converse`, `Speak`, `Action`) minimize Time-to-First-Audio (TTFA) while strictly separating real-time conversational dialogue from structured tool calls?*
> 
> **Formal Hypothesis (H1)**: By coupling streaming LLM token generation directly with sentence-bounded TTS chunking (10–15 tokens per chunk), Time-to-First-Audio can be compressed under 1.0 second on local edge GPUs, reducing turn-taking latency by over 60% compared to sequential execution.

### RQ2: Acoustic Echo Cancellation & Mid-Sentence Barge-In
> **Question**: *What combination of system-level digital signal processing (PipeWire WebRTC AEC) and application-level audio state management is required to support reliable mid-sentence barge-in without acoustic self-triggering?*
> 
> **Formal Hypothesis (H2)**: Software microphone muting eliminates feedback but destroys conversational ergonomics. A system-level PipeWire WebRTC Acoustic Echo Cancellation (AEC) filter chain coupled with post-playback buffer flushing is necessary and sufficient to permit continuous listening during audio output, achieving mid-sentence barge-in cancellation latency under 200 ms with a false-trigger rate under 2%.

### RQ3: Asymmetric Edge-Cloud Viability & Workstation Automation
> **Question**: *How effectively can an asymmetric "Double-AI" architecture, coupling a local 4GB VRAM edge workstation with free-tier cloud APIs, replicate the responsiveness of high-end commercial assistants while maintaining hands-free desktop control?*
> 
> **Formal Hypothesis (H3)**: An asymmetric architecture—in which a fast edge SLM (Qwen 2.5 3B) provides deterministic, zero-jitter conversational replies (TTFT < 100 ms) while an asynchronous cloud model (Llama 3.3 70B via NVIDIA NIM) handles multi-step reasoning—satisfies sub-second conversational ergonomics without exceeding the 4GB edge VRAM ceiling.

---

## 1.5 Scope Containment: The Frozen Fedora Benchmark Suite
A critical vulnerability in desktop automation research is "scope creep"—the uncontrolled expansion of ad-hoc system commands that compromise reproducibility and test validity. In strict compliance with supervisor directives (*"make a list what I can do, test that nothing more"*), the operating system automation capability of this thesis is strictly confined to a frozen benchmark catalog of exactly ten deterministic commands:

| ID | Category | Spoken Prompt Example | Target Linux System Primitive |
| :---: | :--- | :--- | :--- |
| **CMD-01** | Application Management | *"Launch Firefox"* / *"Open browser"* | `subprocess.Popen(['firefox'])` |
| **CMD-02** | Application Management | *"Open file manager"* | `subprocess.Popen(['nautilus'])` |
| **CMD-03** | Application Management | *"Open terminal"* | `subprocess.Popen(['gnome-terminal'])` |
| **CMD-04** | Window Management | *"Close this window"* | Process Lifecycle Manager (audited `SIGTERM`) |
| **CMD-05** | Audio / Workspace | *"Mute sound"* / *"Unmute audio"* | `wpctl set-mute @DEFAULT_SINK@ toggle` |
| **CMD-06** | Audio / Workspace | *"Turn volume up"* / *"Set volume to 80%"* | `wpctl set-volume -l 1.0 @DEFAULT_SINK@ 5%+` |
| **CMD-07** | Audio / Workspace | *"Turn volume down"* | `wpctl set-volume @DEFAULT_SINK@ 5%-` |
| **CMD-08** | Hardware Diagnostics | *"Check CPU usage"* | `top -b -n1 \| head -5` |
| **CMD-09** | Hardware Diagnostics | *"Check battery level"* | `upower -i $(upower -e \| grep BAT)` |
| **CMD-10** | System Information | *"What is my IP address?"* | `hostname -I` |

---

## 1.6 Summary of Academic & Practical Contributions
The primary contributions of this thesis are summarized as follows:
1. **Edge Architecture on Constrained Hardware**: Demonstrates a fully functional full-duplex conversational voice assistant running entirely within a 4GB VRAM envelope, achieving a mean Time-to-First-Audio under 400 milliseconds and sub-200ms barge-in interruption latency.
2. **The "Double-AI" Asymmetric Duplex Model**: Presents an asymmetric pipeline decoupling immediate edge voice generation from background asynchronous cloud reasoning, guaranteeing conversational ergonomics while unlocking deep tool planning.
3. **Comprehensive Failure Mode Taxonomy**: Provides an exhaustive empirical study of 16 distinct engineering challenges and negative results—spanning acoustic feedback loops, Whisper short-burst hallucinations, Wayland client isolation boundaries, and PortAudio C-thread deadlocks.
4. **Rigorous Empirical Benchmark**: Evaluates the 10 frozen Fedora commands across extensive trials, proving 100% intent recognition accuracy and deterministic execution under modern Linux display and audio servers.

---

## 1.7 Dissertation Structure Across the Three Parts
- **Part 1 (Current Document)**: Chapters 1 & 2: Introduction, Problem Formulation, Theoretical Background, and Literature Review.
- **Part 2**: Chapters 3 & 4: System Architecture, Concurrent Pipelining Design, and In-Depth Failure Mode Analysis (The 16 Engineering Challenges).
- **Part 3**: Chapters 5 & 6: Quantitative Empirical Benchmark Results (Latency, Accuracy, VRAM Profiles), Formal Answers to RQ1–RQ3, and Conclusion.

---

# Chapter 2: Theoretical Foundations & Related Work

## 2.1 Evolution of Conversational Architectures: Cascaded vs. End-to-End Multimodal
Conversational AI architectures have historically followed two distinct paradigms: cascaded modular pipelines and native end-to-end multimodal networks.

### A. The Cascaded Paradigm
Cascaded pipelines divide speech interaction into three discrete, specialized components: Automatic Speech Recognition (ASR), Natural Language Processing (NLP/LLM), and Text-to-Speech (TTS). This modularity offers significant engineering advantages: each model can be independently updated, quantized, audited, and debugged. Furthermore, system developers maintain full transparency over intermediate representations, enabling deterministic regex parsing and safety guardrails on LLM text output before actions are executed.

### B. The End-to-End Multimodal Frontier
Recently, native multimodal models (such as GPT-4o, Google Gemini Live, and Moshi) process raw audio tokens directly into text and audio waveforms without intermediate transcription. While native multimodal models achieve remarkable prosody and sub-300ms turn-taking latencies, they are fundamentally unsuitable for edge workstations with 4GB VRAM. These models require tens of billions of parameters, demanding specialized server-grade GPUs with 48GB to 80GB VRAM. Compressing such monolithic networks to fit into 2.5 GB of edge VRAM results in catastrophic degradation of reasoning ability and phonetic clarity. Consequently, an optimized, pipelined cascaded architecture remains the only viable mechanism for achieving real-time conversational AI on memory-constrained edge hardware.

---

## 2.2 Digital Signal Processing (DSP) & Acoustic Echo Cancellation in Linux Audio
The fundamental prerequisite for full-duplex voice interaction is Acoustic Echo Cancellation (AEC). When an assistant vocalizes responses through physical loudspeakers, sound waves propagate through the room and enter the microphone capsule at amplitudes often 20 to 40 dB higher than incoming human speech. Without cancellation, the microphone stream captures the synthesized output, creating a destructive feedback loop.

In modern Linux distributions, audio management has transitioned from legacy ALSA and PulseAudio to PipeWire. PipeWire is a low-latency multimedia routing framework built around a graph-based processing pipeline. PipeWire achieves acoustic echo cancellation through its `libpipewire-module-echo-cancel` plugin, which integrates Google's battle-tested WebRTC AEC engine into the native audio graph.

The WebRTC AEC algorithm operates in the frequency domain using adaptive finite impulse response (FIR) filtering. It correlates the far-end reference signal (audio sent to the speaker sink) with the near-end microphone signal (audio captured by the physical source). By dynamically modeling the acoustic room impulse response (RIR), the filter subtracts the predicted echo signal from the microphone input in real time. As established in this thesis, relying on software-level microphone muting is an architectural antipattern: it converts the system into a half-duplex walkie-talkie. A system-level PipeWire WebRTC AEC filter chain is mandatory to enable true mid-sentence barge-in.

---

## 2.3 Automatic Speech Recognition (ASR) Under Resource Limits
Speech recognition on edge workstations requires balancing transcription accuracy, computational throughput, and memory residency. OpenAI's Whisper represents the current state of the art in open-weight robust speech recognition. Whisper is built on an encoder-decoder Transformer architecture trained on 680,000 hours of weakly supervised multilingual audio.

Whisper encodes log-mel spectrogram representations of 30-second audio windows into continuous feature vectors, which the autoregressive decoder maps into textual token sequences. To operate within our 4GB VRAM ceiling, this thesis pins Whisper to the `base.en` checkpoint (74 million parameters, ~250 MB VRAM footprint in FP16). The `base.en` model executes inference in under 180 ms on the RTX 3050 Tensor Cores, satisfying our real-time budget.

However, this thesis uncovers a critical theoretical challenge in edge ASR: **Whisper Short-Utterance Hallucination** ([[PRB-002_Whisper_Short_Utterance_Hallucination]]). Whisper was architected for long-form, continuous speech. When presented with sub-500ms audio clips containing monosyllabic desktop confirmations (*"yes"*, *"stop"*, *"ok"*), the attention mechanisms in the decoder lack sufficient acoustic context. Under standard decoding parameters (`condition_on_previous_text=True`), the model hallucinated repetitive phrases from earlier conversation turns or generated phantom YouTube closing tokens (*"Thank you for watching!"*). Overcoming this failure mode required enforcing 300 ms pre-speech acoustic padding, disabling prior-text conditioning, and applying digital audio peak normalization before dispatching frames to the model.

---

## 2.4 Small Language Models (SLMs) and Low-Bit Quantization
Until recently, executing conversational reasoning required models exceeding 70 billion parameters, strictly confining language models to cloud servers. The release of high-density Small Language Models (SLMs)—specifically the Qwen 2.5 series—has fundamentally altered edge AI feasibility. The `Qwen 2.5 3B` model possesses 3.09 billion parameters, offering reasoning and tool-calling capabilities that rival previous 13B parameter architectures.

To fit within our 1.9 GB SLM memory allocation, the model is quantized using 4-bit Post-Training Quantization (PTQ) via the GGUF `Q4_K_M` format, executed through the Ollama runtime. In `Q4_K_M` quantization, attention weights and feed-forward layers are quantized to 4-bit integers with specialized block-level scaling factors, preserving critical attention heads at higher precision. On the RTX 3050, `qwen2.5:3b-instruct-q4_K_M` achieves a generation throughput exceeding 60 tokens per second with an initial Time-to-First-Token (TTFT) under 40 milliseconds, providing the ultra-low latency foundation required for natural dialogue.

---

## 2.5 Neural Text-to-Speech (TTS) Synthesis: Latency vs. Memory Trade-Offs
Neural speech synthesis represents the final acoustic output stage of the pipeline. On edge hardware, TTS engines face a severe trade-off between voice cloning naturalness and memory consumption. This thesis investigates two contrasting neural architectures within the Coqui TTS ecosystem:

| Attribute | Coqui VITS (`vits_ljspeech`) | Coqui XTTS v2 (`xtts_v2`) | Architectural Impact on Thesis |
| :--- | :--- | :--- | :--- |
| **Synthesis Architecture** | Non-autoregressive (Flow + VAE) | Autoregressive + Diffusion Vocoder | VITS synthesizes speech in a single forward pass. |
| **VRAM Footprint** | **300 MB** | **1,600 MB** | XTTS v2 consumes 40% of the entire 4GB VRAM budget. |
| **Real-Time Factor (RTF)** | **0.08** (12x faster than real-time) | 0.65 – 0.85 (Marginal real-time) | VITS enables sub-second TTFA chunk streaming. |
| **Licensing & Terms** | **MIT License** (Permissive Open Source) | **CPML** (Coqui Public Model License) | XTTS v2 is legally restricted from commercial use. |

As formalized in Architectural Decision Record 001 ([[ADR-001_VRAM_Budget_Allocation]]), deploying XTTS v2 alongside Whisper and Ollama elevates total static VRAM consumption to 3,750 MB, leaving only 346 MB of headroom. Under standard desktop operations, GPU memory allocation requests from the display server cause immediate CUDA Out-Of-Memory aborts ([[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]]). Therefore, Coqui VITS is selected as the primary operational engine, guaranteeing rock-solid stability while preserving sub-second speech synthesis.

---

## 2.6 Linux Desktop Automation & Wayland Security Architecture
A critical area where academic literature frequently lags practical systems engineering is the security boundary of modern Linux display servers. For three decades, desktop automation on Unix-like systems relied on the X11 display server. Under X11, the display server is fundamentally unconfined: any unprivileged application can capture global keystrokes (keylogging) or inject arbitrary synthetic keyboard and mouse events into any target window. Popular Python automation libraries (such as `pyautogui`) rely entirely on this unconfined X11 architecture.

However, modern distributions (including Fedora 40/41, Ubuntu 24.04, and RHEL 9) have replaced X11 with Wayland and modern compositors (GNOME/Mutter). Wayland enforces strict client isolation: application windows operate in secure sandboxes and are completely isolated from one another. When an agent attempts to simulate keystrokes (such as `Alt + F4` via `pyautogui`) to close a window, Mutter intercepts the synthetic input as an unauthorized remote control attempt and generates a blocking security dialog: *`Remote Desktop: Allow Remote Interaction`* ([[PRB-015_Wayland_Synthetic_Input_Portal_and_Dynamic_Volume_Whitelist]]). This modal blocks the automation pipeline until manual mouse intervention occurs, completely defeating the goal of hands-free voice control.

This thesis establishes that voice assistants on modern Linux workstations cannot rely on synthetic keystrokes. Instead, automation must be implemented through native process lifecycle management—tracking active process handles (`RECENT_PROCESSES` stack) and issuing audited POSIX `SIGTERM` signals, integrated with D-Bus desktop IPC and WirePlumber (`wpctl`) APIs.

---

## 2.7 Asymmetric Edge-Cloud Collaboration (Double-AI Paradigms)
Edge computing and cloud computing are frequently presented as mutually exclusive paradigms. In conversational automation, however, an asymmetric "Double-AI" hybrid architecture unlocks synergies that neither paradigm can achieve in isolation. The core concept of asymmetric duplexing is the strict separation of concerns between conversational pacing and deep symbolic reasoning.

Human conversational ergonomics mandate that voice responses begin within 500 to 1,000 milliseconds. The local edge SLM (Qwen 2.5 3B) satisfies this requirement with deterministic sub-40ms TTFT. Concurrently, complex multi-step reasoning tasks (e.g., cross-referencing system diagnostics or formulating multi-stage scripts) require high parameter capacity (70B+ parameters). By dispatching complex queries asynchronously to a cloud inference worker (Llama 3.3 70B via NVIDIA NIM) while the local edge model immediately speaks conversational backchanneling tokens (*"Checking system status for you now..."*), the assistant eliminates perceived dead air without violating local edge memory boundaries ([[ADR-003_Double_AI_Asymmetric_Duplex]], [[EXP-002_Local_vs_Cloud_Routing_Latency]]).

---

## 2.8 Summary & Transition to System Design
This chapter reviewed the theoretical foundations and state-of-the-art across audio DSP, neural ASR, quantized edge SLMs, neural TTS, Wayland security boundaries, and asymmetric hybrid orchestration. The literature establishes that while individual components exist, no prior work has unified them into a fully concurrent, interruptible, full-duplex desktop assistant operating within a strict 4096 MB VRAM envelope.

With these theoretical foundations established, Part 2 of this thesis (Chapters 3 & 4) will detail the system architecture, the multi-threaded interaction orchestrator, sentence-bounded token chunking algorithms, and the comprehensive taxonomy of 16 empirical failure modes discovered and resolved during system evaluation.

---

## References (Chapters 1 & 2)
1. **Kim, J., Kong, J., & Son, J. (2021)**. Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech. *Proceedings of the 38th International Conference on Machine Learning (ICML 2021)*, PMLR 139, 5530-5540.
2. **Qwen Team. (2024)**. Qwen2.5: A Party of Foundation Models. *Alibaba Group Technical Report*. arXiv:2412.15115.
3. **Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2022)**. Robust Speech Recognition via Large-Scale Weak Supervision. *OpenAI Technical Report*. arXiv:2212.04356.
4. **Taymans, W. (2020)**. PipeWire: A Multimedia Framework for Linux. *Technical Documentation, Red Hat Inc*. https://pipewire.org.
5. **Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017)**. Attention Is All You Need. *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30, 5998-6008.
6. **WebRTC Project Authors. (2021)**. WebRTC Acoustic Echo Cancellation 3 (AEC3) Architecture and Processing Principles. *Google Open Source Documentation*. https://webrtc.org.
7. **Wayland Protocol Architecture Group. (2023)**. Wayland Security Model and Desktop Portals Specification. *FreeDesktop.org Technical Standards*.

