---
id: GUIDE-001
title: Live Demonstration Protocol and Supervisor Defense Guide
tags: [demo, protocol, presentation, defense, thesis, guide]
related: ["[[Supervisor_Guidelines]]", "[[Frozen_Fedora_Commands]]", "[[BENCH-002_Empirical_Results]]", "[[ADR-001_VRAM_Budget_Allocation]]", "[[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]]"]
---

# 🎬 Live Demonstration Protocol and Supervisor Defense Guide

> **Target Audience**: Thesis Supervisor & Academic Evaluation Committee  
> **Duration**: 4–5 minutes  
> **Key Objective**: Empirically prove real-time full-duplex edge performance (sub-second TTFA, barge-in) and deterministic desktop automation on an NVIDIA RTX 3050 (4GB VRAM) laptop under Fedora Linux.

---

## 1. Pre-Flight Health Check (60 Seconds Before Demo)

Run these quick checks in a terminal before welcoming the supervisor:

### Check 1: VRAM Baseline & Zombie Processes
Ensure no rogue processes are consuming GPU memory:
```bash
nvidia-smi
```
- **Expected Baseline**: Free VRAM $\ge 3.4\text{ GB}$ (Display server using $\approx 300\text{--}500\text{ MB}$).
- *If VRAM is occupied*: Kill any lingering python or browser instances (`killall -9 python; killall -9 brave`).

### Check 2: Ollama Daemon Status
Verify Ollama is active with the pinned edge model:
```bash
ollama list
```
- **Expected**: `qwen2.5:3b-instruct-q4_K_M` (or `qwen2.5:3b`) present.

### Check 3: Audio Input & PipeWire Levels
- Open GNOME Sound Settings or run `wpctl status`.
- Ensure microphone input volume is set between **70% and 80%** (prevents clipping and ambient room noise triggers).

---

## 2. Optimal Screen Layout (Split-Screen Display)

Arrange the laptop screen or external projector into a two-column layout:

```
┌────────────────────────────────────────┬────────────────────────────────────────┐
│ LEFT COLUMN: Academic & Telemetry      │ RIGHT COLUMN: Visual HUD Experience    │
│                                        │                                        │
│  [Top: Main Terminal]                  │  [Jarvis Holographic HUD]              │
│  $ source .venv/bin/activate           │  - Arc Reactor Core                    │
│  $ python main.py                      │  - Real-Time Audio Reactive Waveforms  │
│  (Shows live VAD, TTFT, TTFA, actions) │  - Token-by-token text stream          │
│                                        │                                        │
│  [Bottom: Live GPU Monitor]            │                                        │
│  $ watch -n 1 nvidia-smi               │                                        │
│  (Proves <2.5GB active VRAM live!)     │                                        │
└────────────────────────────────────────┴────────────────────────────────────────┘
```

> **Why this layout impresses evaluators**: The supervisor sees scientific proof (live GPU memory consumption, millisecond latency logs) alongside the clean user-facing HUD.

---

## 3. The 4-Act Master Demonstration Script

### 🎬 Act 1: Instant Conversational Edge Latency (RQ1)
*Goal: Prove sub-second Time-to-First-Audio (TTFA) on 4GB edge hardware without cloud dependency.*

1. **You Say**:  
   > *"Hello Jarvis, can you hear me?"*
2. **Jarvis Responds** (within $\approx 300\text{ ms}$):  
   > *"Yes, I can hear you clearly. How can I assist you today?"*
3. **Supervisor Commentary to Say**:  
   > *"Notice the voice response started in approximately 300 milliseconds. Whisper STT, Qwen-2.5-3B SLM, and Coqui VITS TTS are all running concurrently on this 4GB laptop GPU, utilizing token-level streaming chunking."*

---

### 🎬 Act 2: Deterministic Desktop Automation (SPEC-003)
*Goal: Demonstrate safe, human-in-the-loop desktop control strictly within the 10 Frozen Fedora commands.*

#### Step 2A: Hardware Diagnostics (`CMD-08`)
1. **You Say**:  
   > *"Check CPU usage"*
2. **Jarvis Responds**:  
   > Executes `top -b -n1`, summarizes current load, and speaks: *"CPU usage is currently at X percent."*

#### Step 2B: Application Management (`CMD-01` / `CMD-02`)
1. **You Say**:  
   > *"Open file manager"*
2. **Jarvis Responds**:  
   > GNOME Nautilus file manager opens immediately on screen.

#### Step 2C: Safe Window Termination (`CMD-04`)
1. **You Say**:  
   > *"Close this window"*
2. **Jarvis Responds**:  
   > Sends `alt+f4` via whitelisted auto-approval, closing the Nautilus window smoothly.

#### Step 2D: Audio Routing (`CMD-06` / `CMD-07`)
1. **You Say**:  
   > *"Set volume to fifty percent"*
2. **Jarvis Responds**:  
   > Adjusts PipeWire sink volume via `wpctl set-volume @DEFAULT_SINK@ 0.50` and confirms.

---

### 🎬 Act 3: Full-Duplex Interruption / Barge-In (RQ2)
*Goal: Prove acoustic echo cancellation and natural conversational interruption mid-speech.*

1. **You Say**:  
   > *"Tell me about the weather in Pori"*
2. **Jarvis Starts Speaking**:  
   > *"Currently in Pori, it is overcast with a temperature of 17 degrees Celsius. Wind speeds are..."*
3. **You Interrupt (Mid-Sentence)**:  
   > *"Jarvis, stop"* (or *"Hold on Jarvis"*)
4. **Jarvis Behavior**:  
   > Immediately cuts off audio playback within $100\text{ ms}$. No audio bleed, no VAD cascade, no system freeze.
5. **Supervisor Commentary to Say**:  
   > *"This demonstrates full-duplex barge-in. Despite the assistant's voice playing through the laptop speakers, the WebRTC VAD and PipeWire buffer flush detect my voice, cancel the speaker echo, and instantly halt the TTS thread without deadlocking."*

---

### 🎬 Act 4: Clean Voice Shutdown Protocol
*Goal: Demonstrate robust software engineering and graceful transducer lifecycle management.*

1. **You Say**:  
   > *"Shut down"*
2. **Jarvis Responds**:  
   > *"Shutting down. Goodbye!"*
3. **System Behavior**:  
   > Closes the PortAudio microphone stream, terminates the HUD process, releases all GPU buffers, and returns cleanly to the bash prompt.

---

## 4. Supervisor Defense Q&A Cheatsheet

Be prepared for these 5 probable supervisor questions. Use the exact academic rationale provided below:

### Q1: *"Why did you freeze only 10 commands instead of letting an LLM execute arbitrary bash?"*
- **Answer**:  
  > *"Arbitrary command generation by edge SLMs introduces severe safety hazards, prompt injection vulnerabilities, and latency unpredictability. Freezing the action catalog to 10 strictly audited system commands (`SPEC-003`) guarantees deterministic execution, zero privilege escalation, and enables rigorous statistical evaluation across benchmark trials."*  
  > *(Reference: [[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]] and [[SPEC-003]])*

### Q2: *"Why did you choose a 3B parameter model instead of a standard 7B or 8B model?"*
- **Answer**:  
  > *"The entire thesis is bounded by a realistic 4GB VRAM workstation budget. In our initial experiments, a 7B 4-bit model required 4.3 GB of VRAM alone, instantly triggering CUDA Out-Of-Memory when loaded alongside Whisper and Coqui TTS. Qwen2.5-3B-Instruct requires only 1.9 GB, allowing the complete speech-to-speech pipeline to operate stably at 2.4 GB peak VRAM, leaving 1.5 GB of headroom for the display server."*  
  > *(Reference: [[ADR-001_VRAM_Budget_Allocation]] and [[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]])*

### Q3: *"How do you achieve a sub-300ms Time-to-First-Audio (TTFA) when TTS synthesis is inherently slow?"*
- **Answer**:  
  > *"We avoid the conventional waterfall architecture where the system waits for the complete LLM response before beginning TTS. Instead, we implemented Token-Level Streaming Chunking (`ADR-004`). The orchestrator detects natural clause boundaries (commas, conjunctions, periods) after just 3–5 tokens, streaming the first phonetic chunk directly to the VITS synthesizer while the LLM continues generating subsequent tokens in parallel."*  
  > *(Reference: [[ADR-004_Token_Level_Streaming_TTS_Chunking]] and [[BENCH-002_Empirical_Results]])*

### Q4: *"How do you prevent the microphone from picking up the assistant's own voice and triggering a loop?"*
- **Answer**:  
  > *"We use a multi-tiered acoustic isolation pipeline: system-level PipeWire WebRTC Acoustic Echo Cancellation (`ADR-002`), combined with post-playback input stream buffer flushing and turn-boundary VAD state resets (`PRB-001`, `PRB-014`). This eliminates stale acoustic energy before the microphone re-arms."*  
  > *(Reference: [[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]] and [[PRB-014_Stdin_Deadlock_on_Window_Close_and_PortAudio_Shutdown_Freeze]])*

### Q5: *"What quantitative empirical evidence do you have that this system meets real-time constraints?"*
- **Answer**:  
  > *"We built an automated benchmark suite (`BENCH-002`) testing across all 10 frozen commands. The empirical results show a mean Time-to-First-Token (TTFT) of 44.7 ms, a mean Time-to-First-Audio (TTFA) of 294.7 ms (well below our 1500 ms target), an intent classification accuracy of 97.0%, and a peak VRAM footprint of 2,423 MB."*  
  > *(Reference: [[BENCH-002_Empirical_Results]] and [[Benchmarking_Protocol_and_Metrics]])*

---

## 5. Emergency Troubleshooting Playbook

| Symptom | Cause | 10-Second Emergency Fix |
| :--- | :--- | :--- |
| **No response to voice** | Mic level too low or muted | Check GNOME sound settings; ensure mic slider is at 80%. |
| **Assistant self-triggers** | Speaker volume too loud for room acoustics | Lower volume: `wpctl set-volume @DEFAULT_SINK@ 40%` or use a headset. |
| **Ollama connection refused** | Ollama daemon not running | In a second terminal: `ollama serve &` |
| **HUD doesn't open** | Brave window was already open | It will fall back to voice; or open `http://127.0.0.1:5055` in browser manually. |
