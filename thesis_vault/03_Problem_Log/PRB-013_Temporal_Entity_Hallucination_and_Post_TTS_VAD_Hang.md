---
id: PRB-013
title: Temporal Entity Hallucination in Weather Routing and Post-TTS VAD Acoustic Hang
research_question: "[[Research_Questions|RQ2]]"
status: Solved
tags: [problem, failed-attempt, solution, rq2, vad, weather, aec, pipewire, acoustic-feedback]
related: ["[[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]]", "[[PRB-006_VAD_Cascade_Multilingual_Hallucination]]", "[[ADR-010_Concurrent_SLM_Warmup_and_Live_Information_Augmentation]]"]
---

# ⚠️ PRB-013: Temporal Entity Hallucination in Weather Routing and Post-TTS VAD Acoustic Hang

## 1. Problem Description & Symptoms
During live full-duplex conversational sessions on the Fedora edge workstation:
1. **Weather Location Hallucination**: When the user asked *"what is the weather today"* or *"weather today"*, Jarvis extracted `"today"` as the target geographical entity, querying `wttr.in/today`. This returned weather data for a remote municipality named *Today* (`Currently in Today, it is Overcast, 17 degrees Celsius`), rather than the user's actual location (**Pori, Finland**, where conditions were ~11°C Cloudy).
2. **Post-TTS Conversational Lockup ("Stuck at Converse")**: Immediately following TTS playback completion (`[SPEAK] Playback ended ... [CONVERSE] Completed utterance`), the system ceased listening for subsequent speech turns. The user spoke to the assistant, but no voice activity was detected, no transcription was emitted, and the terminal appeared frozen at `[CONVERSE] Completed utterance`.

---

## 2. Failed Attempts & Negative Results (Thesis Goldmine)

### Failed Attempt 1: Greedy Regex Matching Without Temporal Entity Sanitization
- **What was tried**: Used regex `re.search(r"weather\s+(?:in|for|at|of)?\s*([a-zA-Z\s]+)", clean)` to capture everything following prepositional keywords.
- **Negative Result**: Captured conversational stop words and temporal adverbs (`"today"`, `"now"`, `"currently"`, `"outside"`, `"tonight"`), causing the external HTTP weather service to resolve false geolocations.
- **Why it failed**: Natural voice queries conflate temporal qualifiers with spatial entities. Without a semantic token stop-list and a workstation location anchor, greedy parsers overfit to temporal adverbs.

### Failed Attempt 2: Relying Solely on Silence Timeout Without Hardware Buffer Flush
- **What was tried**: In [[vad.py]], relied on high silence durations (1500ms) and debounce frames (600ms, total 2.1s) to let residual room echoes settle naturally after TTS playback.
- **Negative Result**: When TTS audio finished playing through speakers, residual echo frames buffered in `MicrophoneStream._frames` (queue size 128) left `VoiceActivityCollector._triggered = True`. When the user spoke immediately after TTS, no new `SPEECH_START` event could be emitted because the VAD was already triggered. Furthermore, ambient room noise reset the 2.1-second silence counter repeatedly, causing the VAD to collect audio indefinitely without ever emitting `SPEECH_END`.
- **Why it failed**: Asynchronous physical transducer queues retain acoustic tail energy. Software silence counters cannot differentiate between human speech and decaying room reverberations unless the audio pipeline is actively purged at the turn boundary.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Dual-Stage Location Extraction & Workstation Default Anchor (`system_actions.py`)**:
   - Filtered out conversational noise and temporal tokens (`{"today", "now", "tonight", "tomorrow", "currently", "outside", "forecast", "here", "this week"}`).
   - If the extracted location is empty or in the noise set, fall back to `JARVIS_DEFAULT_LOCATION` from `.env` (configured to **Pori**).
   - Formatted speech output and Google Search query synchronously so spoken results and browser cards match identically (`Pori: Cloudy, +11°C`).

2. **Acoustic Queue Purge & VAD Turn Reset (`mic_stream.py` & `interaction_orchestrator.py`)**:
   - Added `MicrophoneStream.flush()` to drain stale hardware frames immediately upon TTS completion.
   - Called `self.vad.reset()` in both `on_tts_end` and the `_handle_user_utterance` `finally` block to clear residual speaker reverberations.

3. **Responsive Conversational VAD Tuning & Safeguards (`vad.py`)**:
   - Reduced silence duration from 1500ms to **800ms** and debounce from 600ms to **250ms** (total ~1.05s silence to end turn).
   - Added `max_utterance_ms = 15000` (15s ceiling) to prevent runaway collection hangs.
   - Added explicit console logging `[LISTEN] User speech detected, listening...` when speech starts in normal conversational mode, eliminating perceived UI freezes.

---

## 4. Academic Thesis Contribution
- **RQ2 (Full-Duplex Acoustic Boundaries)**: Proves that in edge conversational systems, full-duplex speaker playback leaves a residual acoustic trail in both hardware buffers and software state collectors. Clean turn-taking requires explicit hardware queue flushing and VAD reset at the conclusion of speech output to avoid transducer deadlock.
- **Reference in Thesis**: Chapter 4 (Engineering Full-Duplex Edge Pipelines), Section 4.4 (Turn Boundary Flushing and Acoustic Re-Priming).
