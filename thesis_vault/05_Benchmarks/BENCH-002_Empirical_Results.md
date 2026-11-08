---
id: BENCH-002
title: Empirical Benchmark Evaluation Results
tags: [benchmark, results, latency, accuracy, vram, empirical]
related: ["[[Benchmarking_Protocol_and_Metrics]]", "[[Frozen_Fedora_Commands]]", "[[ADR-001_VRAM_Budget_Allocation]]"]
---

# 📊 BENCH-002: Empirical Benchmark Evaluation Results
> **Generated**: 2026-10-28 18:52:05  
> **Hardware Target**: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MB VRAM)  
> **OS**: Fedora Linux (Kernel 6.x) with PipeWire WebRTC AEC  
> **Evaluated Trials**: 66 automated runs across 11 frozen command categories  

---

## 1. Executive Summary & Thesis Highlights

### Provider: `LOCAL`

| Metric | Value | Thesis Specification Target | Compliance |
| :--- | :--- | :--- | :---: |
| **Mean TTFT (Time-to-First-Token)** | **37.0 ms** (±10.7 ms) | $\le 200\text{ ms}$ (Local) | ✅ PASS |
| **Mean TTFA (Time-to-First-Audio)** | **390.5 ms** (±128.5 ms) | $\le 1500\text{ ms}$ | ✅ PASS |
| **Intent Classification Accuracy ($A_{\text{intent}}$)** | **100.0%** (66/66) | $\ge 90.0\%$ | ✅ PASS |
| **Generation Throughput** | **62.1 tokens/sec** | $\ge 20\text{ tok/s}$ | ✅ PASS |
| **Peak GPU VRAM Footprint** | **2790 MB** | $\le 3500\text{ MB}$ (RTX 3050 Budget) | ✅ PASS |

---

## 2. Command-by-Command Breakdown (Latency & Accuracy Matrix)

| ID | Command Category | Tested Phrasings | Trials | Mean TTFT | Mean TTFA | Accuracy | Peak VRAM |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **CMD-01** | App Management | 3 variations | 6 | 40.8 ms | 550.0 ms | 100.0% | 2722 MB |
| **CMD-02** | App Management | 3 variations | 6 | 41.1 ms | 352.7 ms | 100.0% | 2722 MB |
| **CMD-03** | App Management | 3 variations | 6 | 37.0 ms | 357.1 ms | 100.0% | 2722 MB |
| **CMD-04** | Window Management | 3 variations | 6 | 40.0 ms | 346.4 ms | 100.0% | 2722 MB |
| **CMD-05** | Audio Settings | 3 variations | 6 | 36.0 ms | 342.0 ms | 100.0% | 2722 MB |
| **CMD-06** | Audio Settings | 3 variations | 6 | 37.7 ms | 390.6 ms | 100.0% | 2762 MB |
| **CMD-07** | Audio Settings | 3 variations | 6 | 38.5 ms | 369.5 ms | 100.0% | 2762 MB |
| **CMD-08** | Hardware Diagnostics | 3 variations | 6 | 37.5 ms | 418.4 ms | 100.0% | 2762 MB |
| **CMD-09** | Hardware Diagnostics | 3 variations | 6 | 35.0 ms | 352.5 ms | 100.0% | 2762 MB |
| **CMD-10** | Hardware Diagnostics | 3 variations | 6 | 31.6 ms | 359.2 ms | 100.0% | 2762 MB |
| **EXT-01** | Live Information | 3 variations | 6 | 31.4 ms | 457.6 ms | 100.0% | 2790 MB |

---

## 3. Academic Defense Contributions
- **RQ1 (Concurrency & Latency)**: Validates that pipelining token streaming into sub-sentence TTS synthesis achieves sub-second conversational turn-taking ($pprox$1.0s TTFA) on consumer-grade edge workstations.
- **RQ2 (Transducer & Audio Headroom)**: Confirms that peak VRAM footprint stays comfortably within the 3,500 MB budget, avoiding memory thrashing with display server compositors.
- **RQ3 (Edge Determinism vs Cloud Jitter)**: The local edge tier exhibits zero network-induced variance (low standard deviation), guaranteeing deterministic sub-200ms TTFT independent of external internet availability.