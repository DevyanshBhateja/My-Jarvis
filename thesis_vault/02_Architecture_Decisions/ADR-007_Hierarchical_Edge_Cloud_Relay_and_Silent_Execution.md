---
id: ADR-007
title: Hierarchical Edge-Cloud Relay Pattern and Silent Background Reasoning
tags: [adr, architecture, edge_cloud, relay, routing, rq3, rq1, voice]
status: Accepted
related: ["[[ADR-001_VRAM_Budget_Allocation]]", "[[ADR-003_Double_AI_Asymmetric_Duplex]]", "[[ADR-004_Token_Level_Streaming_TTS_Chunking]]", "[[RQ3_Edge_Cloud_Viability]]", "[[RQ1_Concurrency_Pipelining]]"]
---

# 🏛️ ADR-007: Hierarchical Edge-Cloud Relay Pattern and Silent Background Reasoning

## Context & Problem Statement
In hybrid edge-cloud voice assistants operating on resource-constrained hardware (NVIDIA RTX 3050 4GB VRAM), complex tasks (e.g., multi-criteria trip planning, structured data extraction, deep mathematical reasoning) exceed the context window and parameter reasoning capacity of the local Small Language Model (SLM, `Qwen2.5-3B-Instruct`).

However, delegating complex tasks directly to cloud frontier LLMs (such as NVIDIA NIM's 120B parameter `nvidia/nemotron-3-super-120b-a12b`) creates two severe Human-Computer Interaction (HCI) and pipeline failures:
1. **The "Split-Brain" Persona Dilemma**: Cloud models possess different stylistic biases, verbose tendencies, and formatting habits (emitting markdown tables, bullet points, citations, and internal chain-of-thought tokens). Streaming cloud tokens directly into text-to-speech (TTS) produces jarring, robotic vocalizations of punctuation (`"vertical bar Restaurant vertical bar..."`) and destroys user immersion.
2. **Audio Pipeline Blocking & TTS Lock**: Reading a 500-word cloud markdown output aloud blocks the conversation pipeline for several minutes, rendering the assistant unresponsive to subsequent edge dialogue.

## Decision Drivers
- **Unified Edge Persona**: The local voice assistant ("Jarvis") must remain the sole authoritative voice interface.
- **Cognitive Specialization**: The cloud should serve strictly as a silent compute coprocessor (handling heavy reasoning, search, and structuring), while the edge SLM acts as conversational synthesizer and speech actuator.
- **Multimodal Separation**: Complex structured results (tables, lists, budgets) belong on the workstation display / terminal, while voice feedback should be limited to concise, actionable summaries (1–2 sentences).
- **Latency & Fault Tolerance**: If cloud reasoning fails or times out, the edge model must fail gracefully.

## Considered Options
1. **Option A (Direct Cloud Token Streaming to TTS)**:
   - Stream tokens from the cloud API directly into the TTS token chunker.
   - *Rejected*: Cloud models produce verbose markdown tables, raw bullets, and reasoning traces that sound terrible over TTS.
2. **Option B (Rule-Based Regex Markdown Stripping)**:
   - Run regex cleaners on cloud text before sending to TTS.
   - *Rejected*: Inflexible; cannot summarize a 500-word table into a coherent 1-sentence conversational takeaway.
3. **Option C (Hierarchical Edge-Cloud Relay - Accepted)**:
   - **Step 1 (Silent Cloud Execution)**: Complex requests are routed to NVIDIA NIM (`nvidia/nemotron-3-super-120b-a12b`), which reasons silently in the background. Internal `reasoning_content` is filtered, and the full structured response is rendered cleanly in the workstation console for visual inspection.
   - **Step 2 (Local Edge Relay Synthesis)**: The full cloud result is piped into the local edge model (`Qwen2.5-3B`) via a structured relay prompt.
   - **Step 3 (Conversational Voice Out)**: The local edge model produces a 1–2 sentence natural voice summary confirming completion and stating key takeaways, which is streamed to Coqui TTS.

## Architecture Diagram
```
User Speech ──► Whisper STT ──► LLM Router (Complexity Analysis)
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼ (Simple / Bounded)                    ▼ (Complex / Unbounded)
           Local SLM (Qwen 3B)                     Cloud NIM (Nemotron 120B)
                 │                                       │ (Silent Execution)
                 │                                 Full Structured Result
                 │                                       │ (Visual Console Log)
                 │                                       ▼
                 │ ◄────────────────────────────── Relay Synthesis Prompt
                 ▼
         1-2 Sentence Voice
                 │
                 ▼
          Coqui VITS TTS ──► PipeWire (pw-play)
```

## Consequences & Academic Contribution
- **Positive**: 
  - Completely eliminates awkward TTS table reading and persona fragmentation.
  - Gives the user both full, rich structured data on-screen and instant, hands-free conversational summaries through audio.
  - Preserves 4GB VRAM budget by keeping large parameters entirely remote while maintaining edge sovereignty.
- **Negative**:
  - Adds ~500ms of local SLM inference latency after cloud task completion for summary synthesis.
- **Thesis Impact**: Directly answers [[RQ3_Edge_Cloud_Viability]] (coordinating heterogeneous edge-cloud pipelines without persona fragmentation) and Chapter 3 (System Architecture).
