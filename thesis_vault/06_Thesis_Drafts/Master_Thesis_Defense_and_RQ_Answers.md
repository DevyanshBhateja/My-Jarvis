---
id: DEFENSE-001
title: Master Thesis Defense Script, Research Question Answers & Supervisor Q&A Bank
tags: [defense, script, rq1, rq2, rq3, supervisor, presentation, benchmark, thesis]
related: ["[[Supervisor_Guidelines]]", "[[Research_Questions]]", "[[BENCH-002_Empirical_Results]]", "[[Frozen_Fedora_Commands]]", "[[Live_Demo_Protocol_and_Defense_Guide]]"]
---

# 🎓 Master Thesis Defense Script & Research Question Answers

> **Thesis Title**: Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations  
> **Author**: Devyansh Bhateja  
> **Target Hardware**: NVIDIA GeForce RTX 3050 Laptop GPU (4GB VRAM) on Fedora Linux  
> **Primary Document Purpose**: All-in-one cheat-sheet for the live demonstration and oral defense.

---

## 🧭 Master Vault Index (Where Every Answer Lives)

If the supervisor asks to inspect code, architecture decisions, or empirical data, point them to these exact documents:
- **Supervisor Directives & Compliance**: [[Supervisor_Guidelines]] (`SPEC-001`)
- **Pinned Models & Licensing Audit (MIT / Apache / CPML)**: [[Pinned_Models_and_Licenses]] (`SPEC-002`)
- **10 Frozen Fedora Commands Specification**: [[Frozen_Fedora_Commands]] (`SPEC-003`)
- **Formal Abbreviations Glossary**: [[Abbreviations_Glossary]] (`SPEC-004`)
- **Empirical Benchmark Protocol**: [[Benchmarking_Protocol_and_Metrics]] (`BENCH-001`)
- **Quantitative Benchmark Dataset**: [[BENCH-002_Empirical_Results]] (`BENCH-002`)
- **VRAM Budget Allocation**: [[ADR-001_VRAM_Budget_Allocation]] (`ADR-001`)
- **PipeWire WebRTC AEC Architecture**: [[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]] (`ADR-002`)
- **Token-Level Streaming TTS Chunking**: [[ADR-004_Token_Level_Streaming_TTS_Chunking]] (`ADR-004`)
- **Two-Tier Action Containment Policy**: [[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]] (`ADR-005`)
- **Complete Log of 16 Engineering Failures & Solutions**: `thesis_vault/03_Problem_Log/` ([[PRB-001_VAD_Self_Triggering_Acoustic_Feedback|PRB-001]] to [[PRB-016_Terminal_Suicide_Process_Teardown_and_Cloud_NIM_90B_Pinning|PRB-016]])

---

## 🎬 Section 1: The Step-by-Step Live Demo Script (3–4 Minutes)

### Pre-Launch Setup (Do this before supervisor looks at screen)
1. Split screen:
   - **Left half**: Terminal ready to run `python main.py`, with a lower pane running `watch -n 1 nvidia-smi`.
   - **Right half**: Brave browser ready to display HUD.
2. Ensure `.env` is set to `JARVIS_LLM_ROUTE="local"` for zero network jitter.
3. Start the system:
   ```bash
   python main.py
   ```
   *(Wait ~3 seconds until you see `[ORCH] All loops started. Listening for speech...`)*

---

### Act 1: Instant Edge Conversational Loop (Proving RQ1)
* **What you say**:  
  > *"Hello Jarvis, can you hear me?"*
* **What Jarvis does**:  
  Spoken response starts within **~300 ms**: *"Yes, I can hear you clearly. How can I assist you today?"*
* **What you explain to supervisor**:  
  > *"Notice the voice response begins in approximately 300 milliseconds. Whisper STT, Qwen2.5-3B SLM, and Coqui VITS TTS are running concurrently on this 4GB laptop GPU using token-level streaming chunking."*
  > *(Point to `nvidia-smi` showing ~2.4GB VRAM active).*

---

### Act 2: Deterministic Desktop Automation (Proving SPEC-003)
* **Step 2A: Hardware Diagnostics (`CMD-09`)**:  
  * You say: *"Check my battery."*  
  * Jarvis: Runs `upower -i $(upower -e | grep BAT)` in Tier 1 auto-approval, vocally responds: *"Battery is at 87% and currently pending-charge."*
* **Step 2B: Application Launch (`CMD-02`)**:  
  * You say: *"Open file manager."*  
  * Jarvis: Spawns GNOME Nautilus file explorer on screen immediately.
* **Step 2C: Safe Window Close (`CMD-04`)**:  
  * You say: *"Close this window."*  
  * Jarvis: Issues `alt+f4` via whitelisted auto-approval, closing Nautilus cleanly.
* **Step 2D: Audio Setting (`CMD-06` / `CMD-07`)**:  
  * You say: *"Set volume to fifty percent."*  
  * Jarvis: Executes `wpctl set-volume @DEFAULT_SINK@ 0.50` and confirms vocally.

---

### Act 3: Live Interruption & Full-Duplex Barge-In (Proving RQ2)
* **What you say**:  
  > *"Tell me about the weather in Pori."*
* **Jarvis starts speaking**:  
  > *"Currently in Pori, it is overcast with a temperature of..."*
* **What you do (Mid-Sentence Interruption)**:  
  Speak loudly and clearly:  
  > *"Jarvis, stop!"*
* **What Jarvis does**:  
  Audio playback immediately cuts off within **100 ms**. No audio bleed, no endless echo feedback, and the system resets to listen state.
* **What you explain to supervisor**:  
  > *"This proves full-duplex acoustic echo cancellation. Despite audio playing over open speakers, the PipeWire WebRTC AEC filter and our turn-boundary VAD buffer flush prevent self-triggering and process the interruption instantly."*

---

### Act 4: Autonomous Security Containment & Voice Teardown
* **Step 4A: Safe Rejection of Arbitrary Command**:  
  * You say: *"Create a new folder called project."*  
  * Jarvis: Blocks `mkdir project` and vocally responds: *"I cannot execute that command; it is outside my authorized capabilities."*  
  * You explain: *"This demonstrates our Two-Tier Action Containment (`ADR-005`): the assistant refuses unauthorized host system mutations."*
* **Step 4B: Clean Teardown**:  
  * You say: *"Shut down."*  
  * Jarvis: Spoken farewell (*"Shutting down. Goodbye."*), shuts down HUD, frees PortAudio streams, and cleanly returns to terminal bash prompt.

---

## 🔬 Section 2: Definitive Answers to the 3 Research Questions

### 📌 RQ1: Concurrency & Streaming Pipelining
> **Question**: *How can an asynchronous multi-threaded pipeline (`Listen`, `Converse`, `Speak`, `Action`) minimize Time-to-First-Audio (TTFA) while separating real-time dialogue from structured tool calls?*

* **The Academic Answer**:  
  Conventional conversational systems use a sequential "waterfall" architecture (Wait for user silence $\to$ Transcribe full audio with STT $\to$ Wait for full LLM response completion $\to$ Synthesize audio with TTS $\to$ Play audio). This produces unergonomic latencies of 3.0–5.0 seconds.  
  In this thesis, we implemented a decoupled 4-stage pipeline with **Token-Level Streaming TTS Chunking** (`ADR-004`). The LLM streams tokens immediately; an algorithmic sentence-boundary heuristic detects clause delimiters (commas, periods, conjunctions) after only 3–5 tokens (~15–20 phonemes). This first phonemic packet is dispatched to Coqui VITS synthesizer while the SLM continues generating remaining tokens concurrently.
* **Empirical Proof (`BENCH-002`)**:  
  - **Mean Time-to-First-Token (TTFT)**: **37.0 ms** ($\pm 10.7\text{ ms}$).  
  - **Mean Time-to-First-Audio (TTFA)**: **390.5 ms** ($\pm 128.5\text{ ms}$) (Well below the 1,500 ms target).  
  - **Throughput**: **62.1 tokens/sec** on local edge hardware.

---

### 📌 RQ2: Acoustic Echo Cancellation & Mid-Sentence Barge-In
> **Question**: *What combination of system-level acoustic echo cancellation (PipeWire WebRTC AEC) and soft audio state management is required to support reliable mid-sentence barge-in without self-triggering?*

* **The Academic Answer**:  
  Software-only mic muting ("half-duplex") eliminates feedback but makes mid-speech interruption impossible. True full-duplex requires continuous microphone listening during speaker playback.  
  We solved this through a dual-layer approach:  
  1. **DSP Layer**: Linux system-level PipeWire WebRTC AEC (`libpipewire-module-echo-cancel`) subtracts the sink reference signal from the capture stream in hardware/kernel space.  
  2. **Orchestrator Layer**: To solve residual transient acoustic energy (`PRB-001`, `PRB-014`), the microphone stream buffer is explicitly flushed upon TTS termination, and the WebRTC VAD state machine executes a hard reset (`vad.reset()`) across turn boundaries with an 800ms silence hang-over debouncer (`EXP-001`).
* **Empirical Proof (`BENCH-002`)**:  
  - Mid-sentence barge-in stops TTS playback in $< 100\text{ ms}$.  
  - Zero runaway self-triggering loops during open-speaker playback.

---

### 📌 RQ3: Asymmetric Edge-Cloud Viability & 4GB VRAM Budget
> **Question**: *How effectively can an asymmetric architecture, coupling a local 4GB VRAM edge device with free-tier cloud APIs, replicate the responsiveness of commercial voice assistants while maintaining hands-free desktop control?*

* **The Academic Answer**:  
  Running standard 7B or 8B parameter models locally on a 4GB workstation is mathematically impossible due to memory limits (a 4-bit 7B model requires 4.3 GB alone, causing instant CUDA Out-Of-Memory or operating system thrashing; `PRB-003`).  
  We established an asymmetric allocation strategy (`ADR-001`):  
  - Local Edge SLM (`Qwen2.5-3B-Instruct` Q4_K_M): ~1.9 GB VRAM  
  - Local STT (`Whisper base.en`): ~250 MB VRAM  
  - Local TTS (`Coqui VITS LJSpeech`): ~300 MB VRAM  
  - Total active VRAM footprint: **2,423 MB** to **2,790 MB**, leaving **1.3–1.6 GB of dedicated VRAM headroom** for the Fedora GNOME display server and Wayland compositor.  
  - For complex reasoning or code generation, tasks are routed asynchronously to cloud models while the edge model handles immediate vocal backchanneling.
* **Empirical Proof (`BENCH-002`)**:  
  - Intent classification accuracy: **100.0%** across all 11 frozen evaluation categories.  
  - Local edge latency is completely immune to network packet drops or cloud jitter.

---

## 🛡️ Section 3: The Supervisor Q&A Master Bank (Top 10 Questions)

### Q1: *"Why did you freeze only 10 commands instead of letting an LLM execute arbitrary bash?"*
- **Defense Answer**:  
  *"Arbitrary command generation by edge SLMs introduces severe safety hazards, prompt injection vulnerabilities, and latency unpredictability. Freezing the action catalog to 10 strictly audited system commands (`SPEC-003`) guarantees deterministic execution, zero privilege escalation, and enables rigorous statistical evaluation across benchmark trials."*  
  *(Citations: [[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]], [[SPEC-003]])*

### Q2: *"Why did you choose a 3B parameter model instead of 7B or 8B?"*
- **Defense Answer**:  
  *"The entire thesis is bounded by a realistic 4GB VRAM workstation budget. In our initial experiments, a 7B 4-bit model required 4.3 GB of VRAM alone, instantly triggering CUDA Out-Of-Memory when loaded alongside Whisper and Coqui TTS. Qwen2.5-3B-Instruct requires only 1.9 GB, allowing the complete speech-to-speech pipeline to operate stably at 2.4 GB peak VRAM, leaving 1.5 GB of headroom for the display server."*  
  *(Citations: [[ADR-001_VRAM_Budget_Allocation]], [[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]])*

### Q3: *"How do you achieve a sub-400ms Time-to-First-Audio (TTFA) when TTS synthesis takes time?"*
- **Defense Answer**:  
  *"We avoid the conventional waterfall architecture where the system waits for the complete LLM response before beginning TTS. Instead, we implemented Token-Level Streaming Chunking (`ADR-004`). The orchestrator detects natural clause boundaries (commas, conjunctions, periods) after just 3–5 tokens, streaming the first phonetic chunk directly to the VITS synthesizer while the LLM continues generating subsequent tokens in parallel."*  
  *(Citations: [[ADR-004_Token_Level_Streaming_TTS_Chunking]], [[BENCH-002_Empirical_Results]])*

### Q4: *"Why did you reject Coqui XTTS v2 in favor of Coqui VITS?"*
- **Defense Answer**:  
  *"Two critical reasons: First, memory contention: XTTS v2 requires ~1.6 GB of VRAM, pushing total usage to 3.75 GB and risking instant OOM when opening a browser window (`PRB-003`). VITS requires only ~300 MB. Second, licensing compliance: XTTS v2 is governed by the Coqui Public Model License (CPML), which strictly forbids commercial use and imposes legal constraints, whereas VITS is under the permissive MIT license."*  
  *(Citations: [[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]], [[Pinned_Models_and_Licenses]])*

### Q5: *"How do you prevent the microphone from picking up the assistant's own voice (Acoustic Echo)?"*
- **Defense Answer**:  
  *"We use a multi-tiered acoustic isolation pipeline: system-level PipeWire WebRTC Acoustic Echo Cancellation (`ADR-002`), combined with post-playback input stream buffer flushing and turn-boundary VAD state resets (`PRB-001`, `PRB-014`). This eliminates stale acoustic energy before the microphone re-arms."*  
  *(Citations: [[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]], [[PRB-014_Stdin_Deadlock_on_Window_Close_and_PortAudio_Shutdown_Freeze]])*

### Q6: *"What happens if an out-of-scope or dangerous command is spoken?"*
- **Defense Answer**:  
  *"Our Two-Tier Action Containment architecture (`ADR-005`) validates all action requests against an audited whitelist. If an unapproved command is requested (e.g. `mkdir` or `rm`), the security policy denies execution, emits a safety telemetry warning, and informs the user vocally without destabilizing the system."*  
  *(Citations: [[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]])*

### Q7: *"What was the hardest bug you encountered and how did you resolve it?"*
- **Defense Answer**:  
  *"Acoustic feedback loop and thread deadlocks (`PRB-001` and `PRB-014`). During initial testing, speaker output bled into the microphone, triggering false speech detections where the assistant replied to itself indefinitely. In addition, C-level PortAudio streams spawned by `sounddevice` bypassed Python's thread manager, causing process hangs on shutdown. We solved this by implementing turn-boundary VAD resets, input buffer flushes, and explicit PortAudio C-stream termination handlers."*  
  *(Citations: [[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]], [[PRB-014_Stdin_Deadlock_on_Window_Close_and_PortAudio_Shutdown_Freeze]])*

### Q8: *"Why did you have to adjust terminal execution for Fedora 40/41?"*
- **Defense Answer**:  
  *"Modern Fedora 40 and 41 replaced `gnome-terminal` with `ptyxis` as the default container-native terminal. We implemented dynamic terminal binary discovery in `system_actions.py` (`ptyxis` $\to$ `gnome-terminal` $\to$ `kgx`), ensuring complete cross-version portability on Fedora Linux."*  
  *(Citations: [[Frozen_Fedora_Commands]])*

### Q9: *"What is the licensing status of every component in this system?"*
- **Defense Answer**:  
  *"Every software module and model weight was audited: Whisper (OpenAI - MIT), Qwen 2.5 3B (Alibaba - Apache 2.0), Coqui VITS (Coqui Community - MIT), PipeWire (LGPL 2.1+), and our custom orchestrator code (Devyansh Bhateja - MIT). The entire production stack is 100% permissively licensed for both academic research and commercial deployment."*  
  *(Citations: [[Pinned_Models_and_Licenses]])*

### Q10: *"What are the limitations of this work, and what should be done in future research?"*
- **Defense Answer**:  
  *"The primary limitation is the frozen 10-command catalog. While this was necessary to establish rigorous empirical baselines, future work can implement dynamic tool-calling within sandboxed Linux containers (such as Bubblewrap or Flatpak portals) and integrate multi-speaker diarization for multi-user environments."*  
  *(Citations: [[Draft_System_Architecture]])*
