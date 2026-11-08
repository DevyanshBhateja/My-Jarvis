---
id: SPEC-005
title: Thesis Research Questions & Hypotheses
tags: [specification, research_questions, methodology, thesis]
related: ["[[Supervisor_Guidelines]]", "[[00_Map_of_Content]]", "[[ADR-003_Double_AI_Asymmetric_Duplex]]"]
---

# 🔬 Thesis Research Questions & Hypotheses

The thesis investigates three core research questions (RQs) situated at the intersection of real-time audio systems and edge AI orchestration.

---

## RQ1: Concurrency & Streaming Pipelining
> **Question**: *How can an asynchronous multi-threaded pipeline (`Listen`, `Converse`, `Speak`, `Action`) minimize Time-to-First-Audio (TTFA) while separating real-time dialogue from structured tool calls?*

- **Hypothesis**: By coupling token-level LLM streaming directly with sentence-bounded TTS chunking (10–15 tokens per chunk), Time-to-First-Audio can be compressed under 1.5 seconds, even on local edge GPUs.
- **Experimental Target**: Measure TTFA across 100 conversational turns; prove that pipelined chunk synthesis starts before full LLM response generation completes.
- **Linked Notes**: [[ADR-004_Token_Level_Streaming_TTS_Chunking]], [[EXP-002_Local_vs_Cloud_Routing_Latency]].

---

## RQ2: Acoustic Echo Cancellation & Mid-Sentence Barge-In
> **Question**: *What combination of system-level acoustic echo cancellation (PipeWire WebRTC AEC) and soft audio state management is required to support reliable mid-sentence barge-in without self-triggering?*

- **Hypothesis**: Software-only microphone pausing suppresses echo but destroys full-duplex responsiveness. A system-level PipeWire WebRTC AEC virtual sink/source filter chain is necessary and sufficient to permit simultaneous listening during playback with barge-in reaction latency under 200ms.
- **Experimental Target**: Test false-interruption rate (when assistant self-triggers) and true-interruption latency across 50 simulated speaker bleed trials.
- **Linked Notes**: [[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]], [[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]].

---

## RQ3: Asymmetric Edge-Cloud ("Double-AI") Viability
> **Question**: *How effectively can an asymmetric architecture, coupling a local 4GB VRAM edge device with free-tier cloud APIs, replicate the responsiveness of commercial, high-end voice assistants while maintaining hands-free desktop control?*

- **Hypothesis**: An asymmetric "Double-AI" model—where a fast local SLM (Qwen 2.5 3B) provides instant conversational backchanneling while a cloud worker (Llama 3.3 70B via NVIDIA NIM) asynchronously plans and verifies OS actions—satisfies sub-second conversational ergonomics without exceeding a 4GB VRAM ceiling.
- **Experimental Target**: Measure end-to-end task completion times and VRAM usage on the [[Frozen_Fedora_Commands]].
- **Linked Notes**: [[ADR-001_VRAM_Budget_Allocation]], [[ADR-003_Double_AI_Asymmetric_Duplex]], [[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]].
