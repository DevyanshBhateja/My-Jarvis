---
id: ADR-003
title: Double-AI Asymmetric Duplex Architecture
tags: [adr, architecture, double-ai, routing, async, decision]
status: Accepted
related: ["[[Research_Questions]]", "[[EXP-002_Local_vs_Cloud_Routing_Latency]]", "[[Frozen_Fedora_Commands]]"]
---

# 🏛️ ADR-003: Double-AI Asymmetric Duplex Architecture

## Context & Problem Statement
When a user issues a complex command (e.g., *"Check CPU usage, summarize what's eating memory, and open Firefox if memory is under 80%"*), two conflicting constraints emerge:
1. **Conversational Latency**: Spoken conversational interfaces demand an immediate response within 1.0–1.5s to feel natural. Waiting 4–6s for a cloud reasoning model or complex tool planner makes the system feel broken.
2. **Edge Hardware Limitation**: A 3B local SLM lacks the multi-step planning capability of a 70B+ model, but a 70B+ model cannot fit in 4GB VRAM.

## Decision Drivers
1. **Low Time-to-First-Audio (TTFA)**: Instant conversational acknowledgment.
2. **Accurate Tool Execution**: Accurate parameter mapping for [[Frozen_Fedora_Commands]].
3. **Zero Marginal Cost**: Local Ollama execution + free developer API tiers (NVIDIA NIM).

## Decision & Rationale
We implement an **Asymmetric "Double-AI" Hybrid Duplex**:
- **Tier 1 (Edge Dialogue Loop - Local SLM)**:
  - Model: `qwen2.5:3b` via Ollama.
  - Role: Handles immediate conversational acknowledgment, casual chit-chat, and low-latency backchanneling (*"Checking system statistics for you now..."*).
- **Tier 2 (Cloud Worker Loop - Asynchronous Reasoning)**:
  - Model: `meta/llama-3.3-70b-instruct` via NVIDIA NIM free tier.
  - Role: Dispatched in the background on complex intent. Executes deep reasoning, parses multi-step shell directives, and pipes completion results back into Tier 1.

```
 User Voice Input
        │
        ▼
  [Whisper STT]
        │
   ┌────┴────────────────────────┐
   ▼                             ▼
[Local Edge SLM (Qwen 3B)]   [Cloud Reasoning Worker (70B)]
 (Instant Spoken Reply)       (Async Tool Call & Planning)
   │                             │
   ▼                             ▼
[Coqui VITS Playback]        [Action Executor / OS Task]
 ("Looking into that...")        │ (Result State)
   ▲                             │
   └─────────────────────────────┘
```

## Consequences & Thesis Contribution
- Solves the trade-off between edge model reasoning weakness and cloud latency delay.
- Directly addresses **RQ3**: Demonstrates that consumer edge workstations can match commercial smart-speaker responsiveness without paid enterprise infrastructure.
