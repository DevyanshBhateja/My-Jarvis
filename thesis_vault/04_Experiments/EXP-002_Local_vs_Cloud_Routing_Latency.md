---
id: EXP-002
title: Local Edge SLM vs. Cloud NIM Routing Latency
research_question: "[[Research_Questions|RQ1]]"
tags: [experiment, latency, ttft, ttfa, edge-cloud, routing]
status: Completed
related: ["[[ADR-003_Double_AI_Asymmetric_Duplex]]", "[[Benchmarking_Protocol_and_Metrics]]"]
---

# 🧪 EXP-002: Local Edge SLM vs. Cloud NIM Routing Latency

## Objective
Measure empirical Time-to-First-Token (TTFT) and Time-to-First-Audio (TTFA) across the local edge provider (Ollama Qwen 2.5 3B) versus the cloud provider (NVIDIA NIM Llama 3.3 70B) under identical user prompts.

---

## Experimental Setup
- **Hardware**: RTX 3050 (4GB VRAM), Fedora Linux 40, Wi-Fi 6 connection (~20ms ping to cloud endpoint).
- **Prompt Set**: 30 standardized queries (10 short conversational, 10 desktop actions from [[Frozen_Fedora_Commands]], 10 complex multi-step reasoning).
- **Measurement Tool**: Timestamp telemetry logging in [[interaction_orchestrator.py]].

---

## Empirical Benchmark Findings (Summary)

| Provider | Model Size | Avg. TTFT (ms) | Avg. TTFA (ms) | Std Dev (ms) | Network Overhead |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Local Ollama** | Qwen 2.5 3B (Q4_K_M) | **145 ms** | **1,020 ms** | $\pm 45\text{ ms}$ | 0 ms (Deterministic) |
| **Cloud NVIDIA NIM** | Llama 3.3 70B (FP8) | **480 ms** | **1,650 ms** | $\pm 310\text{ ms}$| Dependent on WAN jitter |

---

## Conclusion & Action
The local SLM yields a **$3.3\times$ faster TTFT** with virtually zero jitter. This validates the "Double-AI" hypothesis in [[ADR-003_Double_AI_Asymmetric_Duplex]]: the local edge tier should always handle immediate voice output, while the cloud tier handles background tool reasoning.
