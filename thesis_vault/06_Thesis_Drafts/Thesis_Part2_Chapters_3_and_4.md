---
id: DRAFT-PART2
title: Bachelor's Thesis — Part 2: Chapters 3 & 4
tags: [thesis, dissertation, part2, chapter3, chapter4, draft, architecture, failure-modes]
author: Devyansh Bhateja
programme: AI and Data Engineering (2026)
target_hardware: NVIDIA GeForce RTX 3050 (4GB VRAM)
operating_system: Fedora Linux 40/41 (Wayland / PipeWire)
related: ["[[Thesis_Proposal_Revised]]", "[[00_Map_of_Content]]", "[[ADR-001_VRAM_Budget_Allocation]]", "[[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]]", "[[ADR-003_Double_AI_Asymmetric_Duplex]]", "[[ADR-004_Token_Level_Streaming_TTS_Chunking]]", "[[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]]"]
---

# Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations

**Bachelor's Thesis — Part 2 of 3**  
*Chapters 3 & 4: System Architecture, Concurrent Pipelining Design & The 16 Engineering Challenges*

- **Author**: Devyansh Bhateja  
- **Degree Programme**: AI and Data Engineering (2026)  
- **Hardware Target**: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MB VRAM)  
- **Operating System**: Fedora Linux 40/41 Workstation (Wayland, PipeWire, GNOME/Mutter)  
- **Primary Deliverable**: `Thesis_Part2_Chapters_3_and_4.docx`

---

## Executive Overview (Part 2)

This document constitutes Part 2 of the formal Bachelor's Dissertation, detailing the technical implementation, asynchronous concurrency architecture, and empirical engineering challenges encountered while building a real-time full-duplex conversational voice assistant within a 4GB VRAM envelope.

- **Chapter 3** introduces the multi-threaded interaction orchestrator, the Asymmetric "Double-AI" duplex model, the sentence-bounded streaming token chunker, PipeWire WebRTC digital signal processing, two-tier command safety containment, and deterministic process lifecycle tracking under Wayland.
- **Chapter 4** provides a comprehensive academic analysis of the **16 real-world engineering failures and negative results** discovered during development and live demonstration—ranging from speaker acoustic bleed and Whisper short-utterance hallucinations to Mutter Wayland security dialogs, host terminal suicide process teardown, and PortAudio C-thread deadlocks.

---

# Chapter 3: System Architecture & Implementation

## 3.1 Architectural Principles: The Modular Full-Duplex Philosophy
Building a conversational voice agent capable of executing desktop actions on memory-constrained hardware requires departing from monolithic end-to-end architectures. The primary architectural objective of MY_JARVIS is the complete decoupling of perceptual responsiveness (speech recognition, token streaming, and vocalization) from symbolic tool planning and operating system execution. The system operates according to three core design invariants:

1. **Continuous Acoustic Presence**: A conversational voice agent must never enforce half-duplex turn-taking. The microphone capture pipeline must remain active, filtering audio and evaluating speech boundaries even while the assistant's speech synthesizer is actively driving physical loudspeakers.
2. **Sub-Second Time-to-First-Audio (TTFA)**: The user must never wait for an entire language model generation to finish before hearing audio output. Streaming tokens must be transformed into spoken acoustic units in small, natural phonological increments as early as token reception permits.
3. **Deterministic Memory Budgeting**: The combined GPU VRAM allocation of the transcription model, language model, speech synthesis model, and operating system display server must remain strictly below 3,500 MB at all times, guaranteeing at least 500 MB of VRAM headroom for host desktop multitasking.

---

## 3.2 The Four-Thread Concurrent Pipelining Model
To achieve full-duplex responsiveness without race conditions, the runtime is organized as an asynchronous four-worker pipeline managed by a central Interaction Orchestrator (`jarvis_rt/interaction_orchestrator.py`). Each worker runs as an independent daemon thread communicating across bounded, thread-safe FIFO queues:

| Worker Thread | Core Functionality | Input / Output Boundary | Concurrency Primitives |
| :--- | :--- | :--- | :--- |
| **The Listen Thread** | Captures 16 kHz 16-bit PCM frames from PortAudio; evaluates dual-gate WebRTC VAD; detects speech start and end boundaries. | Audio Stream $\longrightarrow$ VAD Queue $\longrightarrow$ Transcriber Queue | Atomic boolean `is_listening`; dynamic energy threshold. |
| **The Converse Thread** | Consumes transcribed text from Whisper; dispatches prompt to LLM Router; streams tokens into text chunker. | Transcriber Queue $\longrightarrow$ LLM Stream $\longrightarrow$ TTS Chunk Queue | Thread-safe `ChatHistory`; non-blocking token generator. |
| **The Speak Thread** | Consumes text chunks; executes neural TTS synthesis via Coqui VITS; spawns `pw-play` subprocess for acoustic playback. | TTS Chunk Queue $\longrightarrow$ Audio Subprocess $\longrightarrow$ Loudspeakers | Atomic `interrupt_requested` flag; `subprocess.Popen.kill()`. |
| **The Action Thread** | Parses structured `ACTION:` blocks; evaluates security whitelist; executes POSIX primitives or launches background cloud reasoning. | Action Directive Queue $\longrightarrow$ OS Primitive / Cloud NIM | Two-tier approval barrier; `RECENT_PROCESSES` tracking stack. |

---

## 3.3 Asymmetric "Double-AI" Hybrid Duplex Architecture
A central innovation of this thesis is the Asymmetric "Double-AI" Duplex model (formalized in [[ADR-003_Double_AI_Asymmetric_Duplex]]). Edge workstations face a fundamental dilemma: local models small enough to fit in edge VRAM (e.g. 3B parameters) possess limited multi-step tool reasoning, while massive models (70B+ parameters) require cloud hosting and suffer from unpredictable network latency jitter.

Our architecture reconciles this tension by decoupling the conversational voice loop from the reasoning planning loop:

- **Tier 1: The Local Edge Conversational Loop**: A quantized `Qwen 2.5 3B Instruct` model running locally in GPU VRAM via Ollama. It evaluates every user utterance with a mean Time-to-First-Token under 40 milliseconds. For standard conversational queries and direct desktop commands, Tier 1 directly streams tokens to the TTS engine. For complex queries requiring deep planning, Tier 1 immediately synthesizes natural spoken backchanneling tokens (*"Analyzing your request now..."*, *"Checking system performance..."*), completely masking cloud latency.
- **Tier 2: The Asynchronous Cloud Reasoning Worker**: A high-parameter model (`meta/llama-3.3-70b-instruct` or `meta/llama-3.2-90b-vision-instruct`) hosted on NVIDIA NIM cloud developer endpoints. Tier 2 executes asynchronously in the background. It consumes complex diagnostic prompts or multi-step action scripts, returning structured actions back to the Action Worker without consuming a single megabyte of local edge VRAM.

---

## 3.4 Token-Level Streaming and Sentence-Bounded TTS Chunking
To achieve sub-second Time-to-First-Audio (TTFA), the assistant implements a dual-trigger sentence-bounded text chunker (`jarvis_rt/tts_stream.py`, [[ADR-004_Token_Level_Streaming_TTS_Chunking]]). Rather than waiting for the entire LLM response to complete, the chunker evaluates tokens as they arrive from the generator stream:

1. **Trigger 1: Clause Boundary Punctuation**: If an incoming token contains terminating punctuation (`.`, `!`, `?`, or `\n`), the buffered text is immediately flushed to the TTS queue. This guarantees that the speech synthesizer receives complete semantic clauses, preserving natural prosody and intonation.
2. **Trigger 2: Token Count Ceiling (12–18 Tokens)**: If a clause is unusually long, waiting for a full stop would reintroduce perceptible latency. Therefore, if the token buffer reaches 12 tokens and encounters an intermediate pause (comma, semicolon, colon, or dash), it immediately dispatches the chunk. If the buffer exceeds 18 tokens without any punctuation, it forces a chunk boundary at the nearest word boundary.

This dual-trigger mechanism compresses the delay between LLM token generation and speech playback to the duration of synthesizing a single clause (~150–250 ms), enabling a total system TTFA consistently under 400 milliseconds.

---

## 3.5 System-Level Digital Signal Processing & PipeWire WebRTC AEC Integration
Achieving continuous listening during assistant speech output requires robust Acoustic Echo Cancellation (AEC). As established in [[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]], software-level muting converts the system into a half-duplex walkie-talkie. MY_JARVIS interfaces directly with Linux PipeWire's graph-based audio processing subsystem using `libpipewire-module-echo-cancel`.

The filter chain creates two virtual audio nodes in the PipeWire graph: an `echo-cancel-sink` and an `echo-cancel-source`. When the speech player outputs audio, the synthesized PCM samples are routed to the echo-cancel sink, which serves as the reference signal. The WebRTC AEC filter continuously cross-correlates the physical microphone input with the reference signal, performing frequency-domain adaptive filtering to subtract speaker acoustic bleed. Furthermore, `action_executor.py` automatically injects hardware-safe ceiling limiters (`wpctl set-volume -l 1.0 @DEFAULT_SINK@`, [[ADR-006_Hardware_Bounded_Audio_Limits_and_State_Inspection]]) to guarantee that speaker audio never exceeds 100% gain, preventing digital clipping and nonlinear speaker distortions that would break AEC filter convergence.

---

## 3.6 Two-Tier Desktop Action Containment & Safety Policy
Autonomous operating system automation introduces severe safety hazards. If an unconstrained language model is granted raw shell execution privileges, hallucinated commands can corrupt the file system or terminate critical processes. To resolve this, MY_JARVIS implements a strict Two-Tier Command Containment Architecture ([[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]]):

- **Tier 1 (Auto-Approved Actions)**: Safe, read-only system diagnostic utilities (`top -b -n1`, `upower -i`, `hostname -I`, `free -h`) and sandboxed application launchers (`open_app("firefox")`, `open_app("nautilus")`). These commands mutate no permanent state and execute instantly with zero user confirmation overhead.
- **Tier 2 (Human-in-the-Loop Confirmation)**: State-mutating system operations (closing active applications, adjusting system volume, or locking the workstation). Tier 2 actions require explicit confirmation. The assistant prompts the user (*"Approve action: [command]?"*), which can be confirmed by voice (*"yes"*, *"proceed"*) or terminal input (`[y/N]`) within a 10-second timeout window.

In addition, `action_executor.py` enforces a strict whitelist and regex-validated boundary: any command string not matching the authorized Frozen Fedora catalog is rejected with an explicit vocal telemetry message (*"I cannot execute that command; it is outside my authorized capabilities."*).

---

## 3.7 Process Lifecycle Tracking vs. Wayland Synthetic Keystrokes
A critical systems-level contribution of this thesis is resolving the Wayland client isolation barrier ([[PRB-015_Wayland_Synthetic_Input_Portal_and_Dynamic_Volume_Whitelist]]). Under modern Fedora GNOME/Wayland, injecting synthetic keystrokes via X11 automation libraries (`pyautogui.hotkey('alt', 'f4')`) is intercepted by Mutter as an unauthorized remote desktop intrusion, presenting a blocking permission dialog.

MY_JARVIS replaces synthetic input with a deterministic **Process Lifecycle Management Stack** (`RECENT_PROCESSES` in `system_actions.py`). Whenever the assistant launches an application (`CMD-01` to `CMD-03`), the spawned `subprocess.Popen` handle is registered into an active process stack. When the user commands *"Close this window"* (`CMD-04`), the system pops the most recent process handle and issues a graceful POSIX `SIGTERM`. Furthermore, to guarantee host environment stability ([[PRB-016_Terminal_Suicide_Process_Teardown_and_Cloud_NIM_90B_Pinning]]), critical development processes (`ptyxis`, `gnome-terminal`, `bash`, `python`, `code`) are hardcoded into an immune system list: the action executor permanently refuses to terminate any process belonging to the assistant's own process hierarchy.

---

## 3.8 Decoupled Zero-VRAM Holographic HUD Architecture
To provide rich visual telemetry (Arc Reactor core status, audio reactive waveforms, token-by-token streaming, and GPU VRAM monitoring) without consuming scarce edge VRAM, MY_JARVIS implements a decoupled Holographic HUD (`jarvis_ui/`, [[ADR-009_Decoupled_Zero_VRAM_Holographic_HUD]]). The HUD runs as a standalone lightweight browser-anchored client communicating with the backend over local inter-process WebSocket streams. Because the UI renders via hardware-accelerated browser canvas without bundling separate PyTorch dependencies, it imposes zero additional VRAM overhead on the assistant runtime.

---

# Chapter 4: Practical Engineering Challenges & The 16 Empirical Failure Modes

## 4.1 The Methodology of Negative Results in Applied Edge AI
Academic literature in artificial intelligence frequently suffers from publication bias: papers showcase idealized benchmarks while omitting the myriad practical engineering failures that occur when deploying theoretical models onto real hardware. In edge-based full-duplex conversational systems, however, system stability is entirely determined by how gracefully the architecture handles physical audio bleed, thread deadlocks, and memory thrashing.

In strict adherence to supervisor guidelines (*"minimal testing: test time and accuracy, mention the problems"*), this chapter documents all 16 empirical failure modes discovered, diagnosed, and resolved during the research:

| ID | Failure Mode Category | Observed Symptom / Negative Result | Engineered Resolution |
| :---: | :--- | :--- | :--- |
| **PRB-001** | Acoustic Feedback | Assistant replied to its own voice in an infinite loop. | Integrated PipeWire WebRTC AEC filter graph (`ADR-002`). |
| **PRB-002** | ASR Hallucination | Whisper hallucinated YouTube tags on *"yes"*/*"stop"*. | Enforced 300ms pre-padding, disabled prior text condition. |
| **PRB-003** | VRAM Contention | Coqui XTTS v2 caused CUDA OOM when opening Firefox. | Pinned Coqui VITS (300MB) as primary operational engine (`ADR-001`). |
| **PRB-004** | Audio Subprocess Hang | Playback deadlocked with `ffplay` on PipeWire. | Migrated to native PipeWire `pw-play` with non-blocking stream. |
| **PRB-005** | Virtual Source Attenuation | AEC source defaulted to 0% volume (-inf dB). | Scripted automated WirePlumber sink/source initialization volume. |
| **PRB-006** | VAD Noise Cascade | Ambient room noise triggered multilingual hallucinations. | Implemented dual-gate energy thresholding before WebRTC VAD. |
| **PRB-007** | Thread Deadlock | Non-daemon worker threads prevented Ctrl+C shutdown. | Strictly daemonized all audio/LLM workers; added shutdown hooks. |
| **PRB-008** | Command Hallucination | SLM hallucinated *"shutdown now"*; hung on stdin. | Enforced strict whitelist barrier and non-blocking select input. |
| **PRB-009** | Silent Action Execution | Actions executed without user spoken feedback. | Added spoken vocal telemetry formatting for all actions (`ADR-005`). |
| **PRB-010** | Audio Stream Collision | Multiple audio playback streams overlapped simultaneously. | Added central playback mutex and atomic process kill. |
| **PRB-011** | Cloud Token Exhaustion | Reasoning tokens exhausted NIM budget; split-brain. | Pinned `max_tokens=1024` and unified edge vocal synthesis (`ADR-007`). |
| **PRB-012** | Subprocess Terminal Leak | GUI browser launch flooded terminal with stderr logs. | Redirected subprocess stdout/stderr to `/dev/null`. |
| **PRB-013** | Temporal Entity Hallucination | SLM hallucinated day of week in weather commands. | Injected real-time system date anchor into system prompt. |
| **PRB-014** | PortAudio Shutdown Freeze | C-level PortAudio stream blocked process termination. | Added explicit `stream.abort()` and C-stream cleanup handlers. |
| **PRB-015** | Wayland Keystroke Security | GNOME showed *"Remote Desktop"* dialog on window close. | Replaced synthetic keys with native Process Lifecycle Stack. |
| **PRB-016** | Terminal Process Suicide | Browser close fallback killed parent `ptyxis` terminal. | Immunized host terminal processes; pinned stable Cloud 90B model. |

---

## 4.2 Detailed Analysis: Acoustic Feedback & The Failure of Software Mic-Muting (PRB-001)
During initial end-to-end testing, the assistant entered a runaway feedback loop within 200 milliseconds of initiating speech. Because the physical microphone capsule remained open, the synthesized speech emitted by the laptop speakers was captured as new input. Whisper transcribed the assistant's own voice, the SLM generated a follow-up response, and the system spoke again indefinitely.

Attempting to solve this by temporarily pausing microphone input (`mic.pause()`) proved to be an architectural failure: while eliminating echo, it reduced the system to a half-duplex walkie-talkie. If the assistant began speaking an inaccurate answer, the user could not interrupt mid-sentence. The working solution required integrating system-level Acoustic Echo Cancellation via PipeWire's `libpipewire-module-echo-cancel` ([[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]]), which continuously subtracts speaker reference audio from the microphone stream in real time, permitting continuous listening and sub-200ms barge-in.

---

## 4.3 Detailed Analysis: Whisper Short-Utterance Hallucination (PRB-002)
In desktop automation, voice confirmation dialogues require high precision on monosyllabic words (*"yes"*, *"stop"*, *"no"*). Standard Whisper models, optimized for long-form continuous speech, exhibited acute hallucinations when transcribing audio bursts under 500 ms. When a user whispered *"yes"*, Whisper routinely emitted phantom phrases such as *"Thank you for watching!"*, *"Subtitles by..."*, or repeated fragments from prior conversational turns.

The root cause was two-fold: (1) aggressive VAD trimming clipped initial plosive consonants, leaving insufficient spectral context, and (2) enabling `condition_on_previous_text=True` biased the autoregressive decoder toward prior dialogue history. The fix required enforcing 300 ms pre-speech acoustic padding, disabling prior-text conditioning, and applying digital peak normalization prior to inference.

---

## 4.4 Detailed Analysis: VRAM Contention on 4GB Edge Workstations (PRB-003)
Consumer laptops featuring the NVIDIA RTX 3050 impose an unyielding 4096 MB VRAM ceiling. While modern autoregressive and diffusion-based TTS models (such as Coqui XTTS v2) offer superior voice naturalness, their ~1.6 GB footprint, combined with local SLM execution (1.9 GB) and Whisper (250 MB), leaves less than 250 MB of VRAM headroom. Under standard desktop operations—such as executing `CMD-01` to open Firefox—the Wayland display server allocated GPU memory buffers that triggered fatal CUDA Out-Of-Memory exceptions (`RuntimeError: CUDA out of memory. Tried to allocate 128.00 MiB`).

The resolution required adopting a dual-model strategy ([[ADR-001_VRAM_Budget_Allocation]]): deploying lightweight non-autoregressive models (Coqui VITS, ~300 MB) for real-time memory stability (total model footprint: 2,450 MB; 1,646 MB headroom) while preserving XTTS v2 strictly as an isolated off-line benchmark.

---

## 4.5 Detailed Analysis: Wayland Synthetic Keystroke Rejection & Dynamic Volume Whitelist (PRB-015)
During live demonstration, two significant edge automation barriers emerged:
1. **Wayland Synthetic Input Rejection**: When executing `CMD-04` (*"Close this window"*), the assistant initially called `pyautogui.hotkey('alt', 'f4')`. Under Fedora GNOME, Mutter's Wayland security portal intercepted the synthetic key event and generated a blocking security modal: *`Remote Desktop: Allow Remote Interaction`*. This completely halted the pipeline until manual mouse consent was granted.
2. **Rigid String Matching Rejection**: When the user asked *"Can you set the volume to 50%?"*, the SLM emitted `ACTION: run_command('wpctl set-volume -l 1.0 @DEFAULT_SINK@ 50%+')`. Because the safety catalog only matched rigid fixed increments (`5%+`, `5%-`), the command was rejected as an unauthorized capability.

The fixes directly established key thesis contributions: (1) replacing synthetic keystrokes with native process lifecycle management (`proc.terminate()`), completely eliminating the Wayland modal dialog; and (2) implementing safe regex matching for arbitrary volume percentages with hardware ceiling limiters (`-l 1.0`) enforced by default.

---

## 4.6 Detailed Analysis: Host Terminal Suicide & Cloud NIM Endpoint Pinning (PRB-016)
In a live demonstration test, the assistant opened a browser window and the user commanded *"Close the opened brave window"*. Because the browser process was launched via `xdg-open` without being registered into `RECENT_PROCESSES`, the queue was empty. The fallback loop iterated through approved process names and executed `pkill -f ptyxis`. Because the assistant, IDE server, and terminal session were all running inside Ptyxis (Fedora's default terminal emulator), the assistant terminated its own parent process, crashing the entire session.

In addition, dispatching background reasoning to NVIDIA NIM failed with HTTP 404 (`Function not found for account`) because the preview endpoint had been retired on developer accounts. The resolution established two critical safeguards: (1) hardcoded terminal immunization permanently forbidding termination of `ptyxis`, `gnome-terminal`, `bash`, `python`, or `code`; and (2) pinning verified stable cloud models (`meta/llama-3.2-90b-vision-instruct`) benchmarked live across 84 available endpoints.

---

## 4.7 Summary & Transition to Empirical Evaluation
The 16 engineering challenges documented in this chapter illustrate the profound divergence between theoretical AI models and real-world system engineering. By identifying, root-causing, and resolving each failure mode, MY_JARVIS achieved deterministic full-duplex conversational interaction on constrained edge hardware.

With the system architecture and engineering safeguards fully described, Part 3 of this thesis (Chapters 5 & 6) presents the comprehensive quantitative empirical benchmark evaluation—measuring TTFT, TTFA, intent recognition accuracy, and VRAM utilization across the 10 Frozen Fedora commands.

---

## References (Chapters 3 & 4)
1. **Coqui Community. (2023)**. Coqui TTS: Fast, Multi-Speaker Neural Text-to-Speech Engine. https://github.com/coqui-ai/TTS.
2. **FreeDesktop.org. (2024)**. Desktop Linux Inter-Process Communication and D-Bus Specification. https://freedesktop.org.
3. **Google. (2022)**. WebRTC Voice Engine and Echo Cancellation 3. Google Technical Documentation.
4. **NVIDIA Corporation. (2024)**. NVIDIA Inference Microservices (NIM) Architecture Overview and API Reference. NVIDIA Developer Documentation.
5. **Ollama Project. (2024)**. Ollama: Run Large Language Models Locally. https://ollama.com.
6. **PipeWire Project. (2023)**. PipeWire Filter-Chain and Echo-Cancel Module Architecture. https://docs.pipewire.org.
7. **Red Hat Inc. (2024)**. Fedora Workstation 40 Systems Administration Guide: GNOME, Mutter, and Wayland Security Protocols.

