---
id: PRB-001
title: VAD Self-Triggering Due to Speaker Acoustic Feedback Bleed
research_question: "[[Research_Questions|RQ2]]"
status: Solved
tags: [problem, failed-attempt, solution, rq2, audio, vad, feedback]
related: ["[[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]]", "[[EXP-001_VAD_Speech_End_Debouncing]]"]
---

# ⚠️ PRB-001: VAD Self-Triggering Due to Speaker Acoustic Feedback Bleed

## 1. Problem Description & Symptoms
When Jarvis spoke through external desktop speakers, the microphone picked up the assistant's own synthesized voice. WebRTC VAD interpreted this as user speech, emitting a `speech_start` event. This triggered the barge-in cancellation mechanism, causing Jarvis to abruptly interrupt itself after speaking only 2–3 words and re-transcribe its own audio output.

---

## 2. Failed Attempts & Negative Results (Thesis Goldmine)

### Failed Attempt 1: Increasing Energy Threshold & WebRTC Aggressiveness
- **What was tried**: Increased WebRTC VAD aggressiveness from Mode 1 to Mode 3, and raised RMS energy threshold from `0.025` to `0.080` in [[vad.py]].
- **Negative Result**: While quiet speaker output was ignored, normal user speech from 1–2 meters away was frequently missed entirely (false-negative speech rejection). When speaker volume was high, the audio still broke through the aggressive filter.
- **Why it failed**: Fixed amplitude thresholds cannot differentiate between the assistant's voice at 75 dB SPL and user voice at 75 dB SPL.

### Failed Attempt 2: Soft Microphone Muting (`mic.pause()`)
- **What was tried**: In [[mic_stream.py]], added `self._paused.set()` on TTS playback start and `self._paused.clear()` on playback completion.
- **Negative Result**: The self-triggering stopped completely, but this converted the system into a **half-duplex walkie-talkie**. If the user attempted to interrupt mid-speech to say *"stop"*, the microphone was dead, making barge-in impossible.
- **Why it failed**: Solved the symptom by sacrificing the core thesis requirement of full-duplex operation.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **PipeWire WebRTC AEC Virtual Filter**: Loaded `libpipewire-module-echo-cancel` at the system level. PipeWire routes speaker playback into the WebRTC AEC reference channel and subtracts it in real-time from the microphone input before passing frames to Python [[sounddevice]].
2. **Speech End Debounce**: Added `speech_end_debounce_ms = 800ms` and `silence_duration_ms = 2000ms` in [[vad.py]] so residual acoustic transients do not trigger false conversational turns.

### Why It Works
The adaptive digital filter continuously models room acoustics and subtracts the exact synthesized waveform from the microphone signal, leaving only ambient room noise and genuine external human speech.

---

## 4. Academic Thesis Contribution
- Directly answers **RQ2**: Demonstrates that acoustic echo cancellation cannot be solved purely in application-level Python logic through volume gating without sacrificing full-duplex functionality. A system-level hardware/DSP filter (such as PipeWire WebRTC AEC) is mandatory on edge workstations with open speakers.
