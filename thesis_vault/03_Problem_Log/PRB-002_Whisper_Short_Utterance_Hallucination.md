---
id: PRB-002
title: Whisper Short Utterance Hallucination & Confirmation Loss
research_question: "[[Research_Questions|RQ1]]"
status: Solved
tags: [problem, failed-attempt, solution, rq1, whisper, stt, hallucination]
related: ["[[Pinned_Models_and_Licenses]]", "[[Frozen_Fedora_Commands]]"]
---

# ⚠️ PRB-002: Whisper Short Utterance Hallucination & Confirmation Loss

## 1. Problem Description & Symptoms
When the assistant asked for confirmation to execute a desktop command (*"Approve action? (yes/no)"*), the user's short one-word responses (*"yes"*, *"yeah"*, *"no"*) were either:
1. Completely dropped by Whisper (returning an empty transcript `""`), or
2. Hallucinated into generic phrases like *"Thank you for watching"*, *"Subtitles by..."*, or *"You"*.

This caused command execution to time out or fail.

---

## 2. Failed Attempts & Negative Results (Thesis Goldmine)

### Failed Attempt 1: Lowering VAD Prefix Padding to 50ms
- **What was tried**: Reduced `prefix_padding_ms` from 300ms to 50ms in [[vad.py]] to minimize latency.
- **Negative Result**: Cut off the initial plosive consonants of short words (e.g., the *"y"* sound in *"yes"* was clipped, leaving only a short hiss *"-es"*). Whisper could not transcribe clipped phonemes and outputted empty strings.
- **Why it failed**: Neural ASR decoders depend heavily on leading consonant acoustic energy.

### Failed Attempt 2: Conditioning on Previous Text (`condition_on_previous_text=True`)
- **What was tried**: Enabled Whisper's built-in autoregressive context conditioning.
- **Negative Result**: Compounded the hallucination problem. If a prior turn ended with a conversational phrase, Whisper repeated fragments of the previous turn when fed short 300ms audio bursts.
- **Why it failed**: Short audio clips lack sufficient acoustic evidence to override strong autoregressive language model priors.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Disabled Text Conditioning**: Set `condition_on_previous_text=False` explicitly in [[transcription.py]]:
   ```python
   result = model.transcribe(
       audio,
       fp16=False,
       language="en",
       condition_on_previous_text=False,
   )
   ```
2. **Audio Peak Normalization**: Normalized low-energy short utterance frames to prevent signal loss:
   ```python
   peak = float(np.max(np.abs(audio)))
   if peak > 0:
       audio = audio / peak
   ```
3. **Prefix Padding Extended**: Preserved 300ms of pre-speech audio frames (`prefix_padding_ms=300`) to guarantee full consonant capture.

---

## 4. Academic Thesis Contribution
- Highlights an important HCI vulnerability in edge voice agents: standard Whisper models trained on 30-second audio windows fail on sub-second voice confirmations unless pre-padding, peak normalization, and autoregressive conditioning suppression are enforced.
