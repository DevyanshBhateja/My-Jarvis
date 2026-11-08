---
id: MOC-000
title: Thesis Research Map of Content (MOC)
tags: [moc, dashboard, thesis, index]
---

# 🎓 Thesis Research Map of Content (MOC)

> **Thesis Title**: Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations  
> **Author**: Devyansh Bhateja  
> **Degree**: Bachelor's in AI and Data Engineering (2026)  
> **Hardware Target**: NVIDIA GeForce RTX 3050 (4GB VRAM) on Fedora Linux  

Welcome to the central research and engineering graph for the thesis. This vault tracks all architecture decisions, experiments, failed attempts, solutions, and benchmarks to directly feed into the thesis writing.

---

## 🧭 Core Navigation

```
                       [[Research_Questions]]
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
[[Pinned_Models_and_Licenses]] [[Frozen_Fedora_Commands]] [[Abbreviations_Glossary]]
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                 [[Architecture Decisions (ADRs)]]
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
[[Problem Log & Failures]]                    [[Experiments & Benchmarks]]
        │                                               │
        └───────────────────────┬───────────────────────┘
                                ▼
                    [[Thesis Chapter Drafts]]
```

---

## 1. Thesis Foundation & Specifications
- [[Supervisor_Guidelines]] — Feedback checklist from the supervisor and compliance tracking.
- [[Thesis_Proposal_Revised]] — The complete revised thesis proposal approved for submission.
- [[Research_Questions]] — Detailed breakdown of RQ1 (Concurrency), RQ2 (Barge-In), and RQ3 (Edge-Cloud).
- [[Pinned_Models_and_Licenses]] — Pinned model versions, licenses (MIT, Apache 2.0, CPML), and VRAM budgets.
- [[Frozen_Fedora_Commands]] — The strictly scoped 10-command benchmark catalog.
- [[Abbreviations_Glossary]] — Formal nomenclature for all abbreviations used in the thesis.

---

## 2. Architectural Decision Records (ADRs)
- [[ADR-001_VRAM_Budget_Allocation]] — Allocating 4GB VRAM between Whisper, Ollama, and Coqui TTS.
- [[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]] — Trade-offs between soft mic muting vs system-level PipeWire WebRTC AEC.
- [[ADR-003_Double_AI_Asymmetric_Duplex]] — Decoupling real-time conversational edge loop from async cloud reasoning worker.
- [[ADR-004_Token_Level_Streaming_TTS_Chunking]] — Sentence boundary and token count heuristics for sub-second TTFA.
- [[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]] — Two-tier command containment, dedicated terminal isolation, and vocal telemetry.
- [[ADR-006_Hardware_Bounded_Audio_Limits_and_State_Inspection]] — Hardware ceiling limits (-l 1.0), overamplification guardrails, and volume state inspection.
- [[ADR-007_Hierarchical_Edge_Cloud_Relay_and_Silent_Execution]] — Hierarchical Edge-Cloud Relay, silent cloud task execution, and unified edge speech synthesis.
- [[ADR-008_Extended_Workstation_Suite_and_Media_Routing]] — Extended Workstation Suite, browser-anchored YouTube music routing, and D-Bus MPRIS media control.
- [[ADR-009_Decoupled_Zero_VRAM_Holographic_HUD]] — Decoupled zero-VRAM holographic desktop HUD architecture and multiprocess isolation.
- [[ADR-010_Concurrent_SLM_VRAM_Preload_and_Live_Information_Augmentation]] — Concurrent SLM VRAM preload, residency persistence, and dual-modal weather vocal telemetry.

---

## 3. The Problem & Failure Log (Crucial Thesis Material)
> *"Mention the problems: what failed, what was attempted, what solution worked."*

- [[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]] — Assistant interrupting itself due to speaker acoustic bleed.
- [[PRB-002_Whisper_Short_Utterance_Hallucination]] — Single-word confirmations ("yes", "stop") lost or hallucinated.
- [[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]] — Coqui XTTS v2 causing CUDA OOM when combined with Ollama.
- [[PRB-004_PipeWire_Native_Player_Selection]] — Player hangs with `ffplay` vs native PipeWire `pw-play` / `paplay`.
- [[PRB-005_PipeWire_Virtual_Source_Zero_Volume]] — Virtual echo cancellation source defaulting to 0% volume (-inf dB).
- [[PRB-006_VAD_Cascade_Multilingual_Hallucination]] — Ambient noise VAD cascading into multilingual Whisper hallucinations & runaway loop.
- [[PRB-007_Non_Daemon_Thread_Deadlock_SIGINT]] — Non-daemon worker threads causing deadlock on Ctrl+C (SIGINT) shutdown.
- [[PRB-008_Out_of_Scope_Command_Hallucination_Stdin_Deadlock]] — Out-of-scope command hallucination (e.g. "shutdown now") & blocking stdin teardown freeze.
- [[PRB-009_Silent_Action_Completion_and_Terminal_Pollution]] — Silent action completion on diagnostics and model capability unawareness.
- [[PRB-010_Uncoordinated_Audio_Stream_Collision_and_False_Success_Reporting]] — Dual audio stream playback collision and false-positive action success reporting.
- [[PRB-011_NVIDIA_NIM_Reasoning_Token_Exhaustion_and_Split_Brain_Voice]] — Token limit exhaustion on NIM reasoning models and split-brain direct TTS vocalization.
- [[PRB-012_Web_Search_Parameter_Binding_and_GUI_Terminal_Pollution]] — Web search parameter binding failure and GUI subprocess terminal pollution.
- [[PRB-013_Temporal_Entity_Hallucination_and_Post_TTS_VAD_Hang]] — Temporal entity hallucination in weather regex and post-TTS VAD acoustic hang.
- [[PRB-014_Stdin_Deadlock_on_Window_Close_and_PortAudio_Shutdown_Freeze]] — Stdin confirmation deadlock on window close and PortAudio thread hang on voice shutdown.
- [[PRB-015_Wayland_Synthetic_Input_Portal_and_Dynamic_Volume_Whitelist]] — Wayland synthetic keystroke security modal and rigid volume whitelist rejection.
- [[PRB-016_Terminal_Suicide_Process_Teardown_and_Cloud_NIM_90B_Pinning]] — Terminal and IDE parent process termination and Cloud NIM 90B model pinning.

---

## 4. Empirical Experiments & Benchmarks
- [[EXP-001_VAD_Speech_End_Debouncing]] — Testing silence duration thresholds (500ms vs 1200ms vs 2000ms).
- [[EXP-002_Local_vs_Cloud_Routing_Latency]] — Comparative TTFT and TTFA measurements for Ollama vs NVIDIA NIM.
- [[Benchmarking_Protocol_and_Metrics]] — Methodology for calculating TTFT, TTFA, and command execution accuracy.
- [[BENCH-002_Empirical_Results]] — Comprehensive empirical latency, accuracy, and VRAM evaluation across the 10 Frozen Fedora commands.

---

## 5. Thesis Writing Drafts & Presentation
- **[[Thesis_Part1_Chapters_1_and_2]]** — Formal Part 1: Chapters 1 & 2 (Introduction, Problem Formulation, Theoretical Foundations & State-of-the-Art).
- **[[Thesis_Part2_Chapters_3_and_4]]** — Formal Part 2: Chapters 3 & 4 (System Architecture, Concurrency Pipeline & The 16 Engineering Challenges).
- **[[Thesis_Part3_Chapters_5_and_6]]** — Formal Part 3: Chapters 5 & 6 (Quantitative Benchmarks, Answers to RQ1–RQ3 & Final Conclusions).
- [[Draft_System_Architecture]] — Content ready for Chapter 3: System Design & Implementation.
- [[Draft_Problems_and_Failure_Modes]] — Content ready for Chapter 4/5: Engineering Challenges & Discussion.
- [[Live_Demo_Protocol_and_Defense_Guide]] — The master 4-act live demonstration script and supervisor defense Q&A guide.
- [[Master_Thesis_Defense_and_RQ_Answers]] — Complete oral defense script, rigorous answers to RQ1–RQ3, and supervisor Q&A bank.
