---
id: PRB-005
title: PipeWire WebRTC AEC Virtual Source Initialized at Zero Volume
research_question: "[[Research_Questions|RQ2]]"
status: Solved
tags: [problem, solution, rq2, pipewire, audio, aec]
related: ["[[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]]", "[[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]]"]
---

# ⚠️ PRB-005: PipeWire WebRTC AEC Virtual Source Initialized at Zero Volume

## 1. Problem Description & Symptoms
When deploying the `libpipewire-module-echo-cancel` virtual filter chain on Fedora Linux, the physical microphone (ASUS C-Media USB Audio) showed active capture levels ($90\%$, $-2.75\text{ dB}$), but applications capturing from `@DEFAULT_SOURCE@` (the virtual `Echo Cancellation Source`) received pure silence ($\text{RMS} = 0.00000$, $-120\text{ dBFS}$).

---

## 2. Failed Attempts & Negative Results (Thesis Goldmine)
- **Attempt 1: ALSA direct device capture bypass**: Attempted opening `hw:0,0` directly in Python `sounddevice`.
  - *Result*: Bypassed PipeWire, but also bypassed the acoustic echo cancellation filter entirely, causing acoustic feedback when speakers were active.
- **Attempt 2: Checking physical source mute state**:
  - *Result*: Verified physical source was unmuted, yet virtual source stream remained suspended at zero signal.

---

## 3. Working Solution & Root Cause Analysis
- **The Fix**: Inspected virtual source gain levels using `pactl get-source-volume @DEFAULT_SOURCE@`. Discovered PipeWire created the virtual sink/source node with an initial volume of $0\%$ ($- \infty\text{ dB}$).
- **Command Executed**:
  ```bash
  pactl set-source-volume @DEFAULT_SOURCE@ 100%
  ```
- **Verification**: Immediate ambient room noise capture resumed at $\text{RMS} = 0.000168$, properly routed through the WebRTC AEC filter.

---

## 4. Academic Thesis Contribution
- Demonstrates an OS integration vulnerability in Linux-based full-duplex systems: Virtual DSP filter chains (AEC) do not automatically inherit hardware gain profiles upon instantiation. Automated startup scripts must explicitly assert virtual node volume parity with physical capture devices.
