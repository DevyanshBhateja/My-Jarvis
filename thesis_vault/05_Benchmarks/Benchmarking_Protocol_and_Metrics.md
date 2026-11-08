---
id: BENCH-001
title: Benchmarking Protocol, Formulas & Metric Definitions
tags: [benchmark, metrics, formulas, methodology]
related: ["[[Supervisor_Guidelines]]", "[[Frozen_Fedora_Commands]]", "[[Research_Questions]]"]
---

# 📊 Benchmarking Protocol, Formulas & Metric Definitions

To satisfy the supervisor's requirement (*"minimal testing: test time and accuracy, mention the problems"*), this document formally defines the metrics and evaluation protocol.

---

## 1. Latency & Timing Metrics

### A. Time-to-First-Token (TTFT)
The duration between the end of user speech transcription and the emission of the first text token by the language model:
$$\text{TTFT} = t_{\text{first\_token}} - t_{\text{prompt\_dispatched}}$$
*Target*: $\le 200\text{ ms}$ (Local Edge) | $\le 600\text{ ms}$ (Cloud).

### B. Time-to-First-Audio (TTFA)
The end-to-end user-perceived conversational latency—from the precise moment human speech stops until the first sound emerges from the speaker:
$$\text{TTFA} = t_{\text{audio\_playback\_start}} - t_{\text{user\_speech\_end}}$$
*Components*: $\text{TTFA} = \Delta t_{\text{VAD\_debounce}} + \Delta t_{\text{Whisper\_ASR}} + \Delta t_{\text{TTFT}} + \Delta t_{\text{TTS\_chunk\_synthesis}} + \Delta t_{\text{player\_buffer}}$.  
*Target*: $\le 1500\text{ ms}$.

### C. Barge-In Interruption Latency ($L_{\text{barge}}$)
The time required to detect human interruption and terminate speaker audio:
$$L_{\text{barge}} = t_{\text{audio\_killed}} - t_{\text{user\_barge\_onset}}$$
*Target*: $\le 200\text{ ms}$.

---

## 2. Accuracy & Reliability Metrics

### A. Intent Classification Accuracy ($A_{\text{intent}}$)
Percentage of voice prompts correctly mapped to the intended action among the [[Frozen_Fedora_Commands]]:
$$A_{\text{intent}} = \frac{N_{\text{correct\_intent}}}{N_{\text{total\_trials}}} \times 100\%$$
*Evaluation sample*: $N = 500$ (50 repetitions across all 10 frozen commands).

### B. Command Execution Success Rate ($S_{\text{exec}}$)
Percentage of approved actions successfully completed by the Linux operating system without throwing an exception or non-zero exit code:
$$S_{\text{exec}} = \frac{N_{\text{successful\_executions}}}{N_{\text{approved\_commands}}} \times 100\%$$

### C. False Barge-In Rate ($R_{\text{false\_barge}}$)
Rate at which the assistant falsely self-interrupts due to acoustic echo bleed or ambient non-speech room noise:
$$R_{\text{false\_barge}} = \frac{N_{\text{false\_interruptions}}}{N_{\text{assistant\_turns}}} \times 100\%$$
*Target*: $\le 2.0\%$.

---

## 3. Resource Utilization Profiling
Monitored via `pynvml` / `nvidia-smi` and Python `psutil`:
1. **Peak GPU VRAM Usage (MB)** — Must stay $\le 3500\text{ MB}$ at all times on the RTX 3050.
2. **Average Host CPU Utilization (%)** — Monitored across all 4 pipeline worker threads.
3. **Bandwidth Overhead (KB/s)** — Edge-to-cloud payload traffic when cloud worker is active.
