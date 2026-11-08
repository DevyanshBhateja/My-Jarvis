---
id: SPEC-006
title: Bachelor’s Thesis Proposal (Revised)
tags: [proposal, specification, supervisor, thesis]
related: ["[[Supervisor_Guidelines]]", "[[Pinned_Models_and_Licenses]]", "[[Frozen_Fedora_Commands]]", "[[Abbreviations_Glossary]]", "[[Research_Questions]]"]
---

# Bachelor’s Thesis Proposal (Revised)

## Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations

**Author:** Devyansh Bhateja  
**Degree Programme:** AI and Data Engineering  
**Academic Year:** 2026  
**Target Hardware:** NVIDIA GeForce RTX 3050 (4GB VRAM)  
**Operating System:** Fedora Linux 40/41  
**Generated Word Document:** `file:///home/dave/Documents/Projects/MY_JARVIS/Thesis_Proposal_Revised.docx`

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

---

## 4. Research Questions & Formal Hypotheses
See detailed analysis in [[Research_Questions]]:
- **RQ1 (Concurrency & Pipelining)**: Minimizing TTFA via token streaming and sentence-bounded chunking.
- **RQ2 (Acoustic Echo & Mid-Sentence Barge-In)**: Eliminating feedback loops via PipeWire WebRTC AEC.
- **RQ3 (Asymmetric Edge-Cloud Viability)**: Replicating commercial responsiveness with a 4GB edge GPU + free-tier cloud.

---

## 5. Scope Containment: The Frozen Fedora Benchmark Suite
Strictly restricted to the 10 approved commands defined in [[Frozen_Fedora_Commands]]:
- **CMD 01-04**: App Launch & Windowing (Firefox, Nautilus, Terminal, Alt+F4)
- **CMD 05-07**: Workspace Audio Settings (Mute, Volume Up, Volume Down)
- **CMD 08-10**: System Diagnostics (CPU Load, Battery Level, Local IP)

---

## 6. Pinned Model Specifications & VRAM Budget
Defined in [[Pinned_Models_and_Licenses]] and [[ADR-001_VRAM_Budget_Allocation]]:
- Whisper `base.en` (250MB) + Ollama `qwen2.5:3b` (1900MB) + Coqui VITS (300MB) = **2.45 GB VRAM** (1.55 GB buffer for desktop).

---

## 7. Minimal Testing Protocol & Known Problems
Defined in [[Benchmarking_Protocol_and_Metrics]] and [[Draft_Problems_and_Failure_Modes]]:
- **Latency**: TTFT, TTFA, Barge-in Reaction Latency ($L_{\text{barge}} \le 200\text{ms}$).
- **Accuracy**: Intent classification ($N=500$), Execution rate, False barge-in rate ($\le 2\%$).
- **Problems**: AEC bleed, Whisper short-utterance hallucination, VRAM contention, WAN jitter.

---

## 8. Licensing Audit
Audited in [[Pinned_Models_and_Licenses]]:
- MIT (Whisper, VITS, MY_JARVIS), Apache 2.0 (Qwen 2.5), CPML (XTTS v2 research-only restriction), NVIDIA Dev Terms (NIM).

---

## 9. Prerequisites for Reproduction
Documented in [[Pinned_Models_and_Licenses]]:
- RTX 3050 (4GB), Fedora 40/41, PipeWire WebRTC AEC, Ollama, Python 3.11 virtual environment.

---

## 10. Abbreviations & Nomenclature
Defined in [[Abbreviations_Glossary]]: Full expansion for AEC, ASR, CPML, D-Bus, FP16, HCI, LLM, NIM, OOM, PCM, RMS, SLM, STT, TTFA, TTFT, TTS, VAD, VITS, VRAM, XTTS.
