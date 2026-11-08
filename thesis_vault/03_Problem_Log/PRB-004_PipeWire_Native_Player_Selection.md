---
id: PRB-004
title: Audio Player Process Hanging & Stdin Blocking with FFplay
research_question: "[[Research_Questions|RQ2]]"
status: Solved
tags: [problem, failed-attempt, solution, rq2, audio, pipewire, ffplay]
related: ["[[ADR-002_PipeWire_WebRTC_AEC_vs_Soft_Pause]]", "[[EXP-001_VAD_Speech_End_Debouncing]]"]
---

# ⚠️ PRB-004: Audio Player Process Hanging & Stdin Blocking with FFplay

## 1. Problem Description & Symptoms
When streaming audio chunks via `ffplay` subprocesses in [[coqui_tts.py]], playback would periodically stall or hang indefinitely. The assistant became unresponsive, and the listen loop was blocked waiting for the player process to exit.

---

## 2. Failed Attempts & Negative Results (Thesis Goldmine)

### Failed Attempt 1: Using `mpg123` with Raw Audio Pipes
- **What was tried**: Piped synthesized raw PCM samples via stdout to `mpg123 -` subprocess.
- **Negative Result**: `mpg123` intermittently suffered buffer underruns, producing metallic clicking and popping artifacts at sentence chunk boundaries.
- **Why it failed**: Fixed PipeWire quantum clock synchronization mismatches between Python's buffer write rate and `mpg123` consumption.

### Failed Attempt 2: Unconstrained `ffplay` Subprocess
- **What was tried**: Executed `ffplay -nodisp -autoexit chunk.wav`.
- **Negative Result**: `ffplay` by default attaches to standard input (`stdin`) to listen for keyboard shortcuts (space to pause, q to quit). In a multithreaded terminal application, it stole stdin from the main process, resulting in hung zombie processes when stdin was closed or contested.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Prioritize Native PipeWire Utilities**: In `_pick_player()`, prioritized native PipeWire (`pw-play`) and PulseAudio (`paplay`) before falling back to `ffplay`:
   ```python
   def _pick_player():
       for command in (
           ("pw-play",),
           ("paplay",),
           ("ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-nostdin"),
           ("mpg123", "-q")
       ):
           if which(command[0]) is not None:
               return list(command)
   ```
2. **Passed `-nostdin` Flag to FFplay**: When `ffplay` is used as a fallback, explicitly passing `-nostdin` prevents it from waiting on interactive keyboard input.
3. **Subprocess Timeouts**: Wrapped player execution in hard timeouts (`timeout=5.0`) with `SIGKILL` cleanup upon cancellation.

---

## 4. Academic Thesis Contribution
- Documents the importance of low-level Linux audio subsystem integration: Native audio server tools (`pw-play`) bypass intermediate format conversions, achieve zero buffer underruns, and respect PipeWire's echo-cancellation routing natively.
