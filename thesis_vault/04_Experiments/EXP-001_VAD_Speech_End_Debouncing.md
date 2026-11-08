---
id: EXP-001
title: VAD Speech-End Debounce Threshold Tuning
research_question: "[[Research_Questions|RQ2]]"
tags: [experiment, vad, debounce, tuning, latency]
status: Completed
related: ["[[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]]", "[[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]]"]
---

# 🧪 EXP-001: VAD Speech-End Debounce Threshold Tuning

## Objective
Determine the optimal `silence_duration_ms` and `speech_end_debounce_ms` parameters in [[vad.py]] that balance natural conversational pauses (preventing mid-sentence cutoffs) against conversational responsiveness (minimizing dead air before ASR triggers).

---

## Experimental Setup
- **Audio Sample**: 20 spoken test sentences containing mid-sentence thinking pauses (e.g., *"Open the browser... [pause]... and navigate to the student portal"*).
- **VAD Engine**: WebRTC VAD (Mode 1) at 16 kHz sample rate.
- **Tested Parameters**:
  - Config A: `silence_duration = 500ms`, `debounce = 200ms` (Aggressive)
  - Config B: `silence_duration = 1200ms`, `debounce = 400ms` (Balanced)
  - Config C: `silence_duration = 2000ms`, `debounce = 800ms` (Tolerant - Current Repo)

---

## Results & Empirical Observations

| Parameter Set | Premature Cutoff Rate (%) | Post-Speech Dead Air (ms) | User Experience Assessment |
| :--- | :--- | :--- | :--- |
| **Config A (500ms / 200ms)** | 65% (13/20 cuts) | ~520 ms | Unusable. Assistant interrupts user mid-thought. |
| **Config B (1200ms / 400ms)**| 15% (3/20 cuts) | ~1240 ms | Good for fast speakers; occasionally cuts slow speakers. |
| **Config C (2000ms / 800ms)**| **0% (0/20 cuts)** | **~2080 ms** | Zero premature interruptions; slight perceptible delay. |

---

## Conclusion & Action
**Config C** was selected as the default stability profile in [[vad.py]]. For the thesis evaluation, we demonstrate the mathematical trade-off curve between premature turn truncation and turn-taking latency.
