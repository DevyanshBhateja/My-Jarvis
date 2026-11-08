---
id: DRAFT-001
title: Thesis Chapter Draft: System Architecture & Concurrency
tags: [thesis-draft, architecture, chapter3, concurrency]
related: ["[[00_Map_of_Content]]", "[[ADR-003_Double_AI_Asymmetric_Duplex]]", "[[ADR-004_Token_Level_Streaming_TTS_Chunking]]"]
---

# 📝 Thesis Draft: Chapter 3 — System Architecture & Implementation

*(Ready for inclusion into Bachelor's Thesis report)*

## 3.1 Pipelined Multi-Threaded Concurrency
To transcend the latency bottlenecks of conventional half-duplex voice assistants, `MY_JARVIS` implements a concurrent, asynchronous four-thread pipeline coordinated by an [[interaction_orchestrator.py|Interaction Orchestrator]]:

1. **The Listen Thread**: Interfaces directly with the Linux audio subsystem via `sounddevice`. Collects raw 16 kHz 16-bit mono PCM frames (30ms chunks), streams frames into WebRTC VAD, and monitors for speech-boundary transitions. It runs continuously, remaining active even while the assistant is speaking to enable mid-sentence barge-in.
2. **The Converse Thread**: Consumes transcribed user text from the audio queue. Directs the prompt to the language model router, streaming tokens in real time. Rather than buffering complete responses, it evaluates a dual-trigger heuristic (sentence-ending punctuation or 12-token window), immediately dispatching ready text chunks to the synthesis queue.
3. **The Speak Thread**: Manages the neural TTS engine. It consumes text chunks, synthesizes audio waveforms, and streams playback through native PipeWire utilities (`pw-play`). Crucially, this thread continuously checks a thread-safe `user_interrupt_requested` atomic event flag; if asserted, it executes an immediate SIGKILL on the player subprocess within 100ms.
4. **The Action Thread**: Decoupled from acoustic generation, this worker consumes structured `ACTION:` directives emitted by the language models. It handles user confirmation prompts and executes deterministic OS commands, returning execution status back to the dialogue state machine without blocking speech.

---

## 3.2 Asymmetric Edge-Cloud ("Double-AI") Duplex
The system bridges resource-constrained edge computing with cloud intelligence through an asymmetric dual-tier architecture:
- **Tier 1 (Edge Loop)**: Pinned to local hardware (NVIDIA RTX 3050, 4GB VRAM). Combines Whisper `base.en` (~250MB VRAM), an Ollama-quantized `Qwen 2.5 3B` SLM (~1.90GB VRAM), and Coqui VITS (~300MB VRAM). Total VRAM allocation is constrained to 2.45 GB, leaving 1.55 GB of headroom for OS display buffers. This loop provides sub-second conversational backchanneling and immediate user feedback.
- **Tier 2 (Cloud Reasoning Worker)**: Interfaced via NVIDIA NIM developer endpoints hosting `Meta Llama 3.3 70B Instruct`. Cloud invocation is reserved for complex multi-step reasoning, code generation, and complex desktop diagnostic planning.
