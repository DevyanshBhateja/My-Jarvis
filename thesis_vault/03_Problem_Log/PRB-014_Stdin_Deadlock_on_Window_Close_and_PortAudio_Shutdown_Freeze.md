---
id: PRB-014
title: Stdin Confirmation Deadlock on Window Close and PortAudio Thread Hang on Voice Shutdown
research_question: "[[Research_Questions|RQ1_Concurrency_Pipelining]]"
status: Solved
tags: [problem, failed-attempt, solution, rq1, threading, pyautogui, portaudio, shutdown, telemetry]
related: ["[[Frozen_Fedora_Commands]]", "[[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]]", "[[PRB-007_Non_Daemon_Thread_Deadlock_SIGINT]]", "[[PRB-013_Temporal_Entity_Hallucination_and_Post_TTS_VAD_Hang]]"]
---

# ⚠️ PRB-014: Stdin Confirmation Deadlock on Window Close and PortAudio Thread Hang on Voice Shutdown

## 1. Problem Description & Symptoms
During full-duplex conversational sessions with the Holographic HUD interface active:
1. **Window Close Deadlock**: When the user commanded *"Can you close the current open brave window?"*, the assistant parsed `ACTION: hotkey("alt", "f4")` but stalled for 10 seconds and cancelled with *"Action was cancelled"*. The console showed a blocking prompt: `> Approve action? (yes/no) [Auto-deny in 10.0s]`. The user, viewing the HUD GUI, received no voice prompt and no UI alert, resulting in a silent timeout.
2. **Process Teardown Freeze on Voice Exit**: When the user spoke *"Shut down"*, the assistant logged `Exit voice command received: 'Shut down.'. Shutting down.` but the process never returned to the bash prompt. The user had to press `Ctrl+C` to terminate the process.
3. **Monolithic Weather Telemetry Bias**: The assistant synthesized spoken information solely for weather queries; all general knowledge searches only voiced *"Searching for X in Brave"* without reading answers.

---

## 2. Failed Attempts & Negative Results (Thesis Discussion)

### Failed Attempt 1: Treating `hotkey("alt", "f4")` as an Unverified Tier 2 Action
- **What was tried**: Classified `hotkey` under Tier 2 in [[action_executor.py]] requiring keyboard standard input confirmation.
- **Negative Result**: In a hands-free conversational voice assistant (and especially with an active GUI window), blocking on `sys.stdin` starves user input, causing 100% false-positive timeouts.
- **Why it failed**: Under [[Frozen_Fedora_Commands]] (`CMD-04`), closing the active window via `alt+f4` is an explicit user-commanded action. When strict whitelisting already blocks every other hotkey except `("alt", "f4")`, an extra stdin prompt is redundant and antithetical to voice ergonomics.

### Failed Attempt 2: Setting `stop_event` Without Explicit Transducer Teardown
- **What was tried**: Calling `self.stop_event.set()` upon receiving an exit voice phrase, expecting Python runtime garbage collection to terminate threads.
- **Negative Result**: `InteractionOrchestrator.shutdown()` had an early-return guard `if self.stop_event.is_set(): return`, which aborted cleanup before closing the microphone. The underlying PortAudio C stream thread spawned by `sounddevice` kept the POSIX process alive indefinitely.
- **Why it failed**: C-extension threads do not observe Python GIL state changes or daemon flags; physical audio devices must be explicitly closed via `sd.InputStream.close()`.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Auto-Approval of Whitelisted Window Closure (`action_executor.py`)**:
   - Added `"hotkey"` to `is_action_auto_approved()`. Because `is_action_whitelisted()` strictly blocks any hotkey combination other than `("alt", "f4")`, window closing executes immediately upon voice request with spoken confirmation (*"Window closed."*).
   - Added HUD UI broadcast (`ui_bridge.post_action("Confirmation Needed", description)`) for any future actions requiring user approval.

2. **Clean Two-Stage Graceful Shutdown Pipeline (`interaction_orchestrator.py`, `controller.py`, `main.py`)**:
   - Voice exit triggers spoken acknowledgement: `ui_bridge.post_jarvis_speech("Shutting down. Goodbye.")` followed by `self.tts_client.speak("Shutting down. Goodbye.")`.
   - Fixed `InteractionOrchestrator.shutdown()` state flag (`self._shutdown_done`) so cleanup always executes: PortAudio stream closed, queues drained, and worker threads joined.
   - `main.py` terminates the HUD browser process (`hud_launcher.close()`), halts Flask server, and calls `os._exit(0)` to prevent C-library stream hangs.

3. **Generalized Vocal Web Search Telemetry (`system_actions.py` & `action_executor.py`)**:
   - Implemented `get_web_summary(query: str)` using DuckDuckGo Instant Answer API and Wikipedia REST summary.
   - For all web searches, Jarvis opens the browser tab AND vocalizes the exact answer (e.g. *"Searching for Albert Einstein in Brave. According to search: Albert Einstein was a German-born theoretical physicist..."*).
   - Updated system prompt in [[llm_stream.py]] so the SLM answers general knowledge questions directly from weights without opening unnecessary search tabs.

---

## 4. Academic Thesis Contribution
- **RQ1 (Pipelining & Teardown)**: Proves that in dual-modal edge AI architectures, asynchronous native C streams (PortAudio) decouple from the Python thread manager. Complete process lifecycle termination requires deterministic physical transducer unbinding rather than event-flag polling.
- **Thesis Reference**: Chapter 3 (System Architecture & Action Execution Engine), Section 3.5; Chapter 4 (Process Lifecycle and Acoustic Gating).
