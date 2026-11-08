---
id: PRB-006
title: Ambient Noise VAD Cascading Hallucination & Multilingual Autoregressive Drift
research_question: "[[Research_Questions|RQ2]]"
status: Solved
tags: [problem, failed-attempt, solution, rq2, vad, whisper, hallucination, qwen]
related: ["[[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]]", "[[PRB-002_Whisper_Short_Utterance_Hallucination]]", "[[Pinned_Models_and_Licenses]]"]
---

# ⚠️ PRB-006: Ambient Noise VAD Cascading Hallucination & Multilingual Autoregressive Drift

## 1. Problem Description & Symptoms
When running `python main.py` live in a quiet room, the assistant entered an infinite, autonomous speaking loop without the user talking:
1. **Unprovoked VAD Triggers**: The voice activity collector triggered repeatedly on silence and faint fan hiss (`[LISTEN] Speech ended (185280 bytes)`).
2. **Multilingual ASR Hallucinations**: Whisper (`base`) transcribed ambient background noise into random foreign phrases:
   - Japanese: `ご視聴ありがとうございました` (*"Thank you for watching"*, a known YouTube training subtitle artifact)
   - Arabic: `حلو حوال يدومي`
   - Korean: `빨라`
   - Japanese: `はむき`
3. **LLM Language Mirroring**: The SLM (Qwen 2.5 3B) received foreign input tokens, mirrored the input language, and emitted Chinese/Japanese responses:
   - Prompt: `ご視聴ありがとうございました` $\rightarrow$ LLM: `ACTION: speak("谢谢观看")`
   - Prompt: `حلو حوال يدومي` $\rightarrow$ LLM: `شكراً، على الرحب و السعة! كيف يمكنني مساعدتك اليوم؟`
4. **Action Crash**: `parse_action_from_llm` returned an `ActionRequest` whose `slots=True` lacked `utterance_id`, crashing with:
   `AttributeError: 'ActionRequest' object has no attribute 'utterance_id'`.
5. **Self-Triggering Feedback Loop**: Synthetic TTS playback bled into the microphone, triggering false barge-in interrupts, which cut off playback with `SIGKILL` (-9) and fed audio tails back into Whisper.

---

## 2. Failed Attempts & Negative Results (Thesis Goldmine)

### Failed Attempt 1: Standalone WebRTC VAD Mode 1
- **What was tried**: Relied on default WebRTC VAD mode 1 without energy thresholding.
- **Negative Result**: Mode 1 ("low bitrate") evaluates spectral features but lacks energy amplitude constraints. In quiet rooms, microphone thermal noise, breathing, and PC fan whine repeatedly triggered false `SPEECH_START` and `SPEECH_END` events.
- **Why it failed**: WebRTC VAD is trained on telephonic frequencies; low-level stationary noise with spectral variation easily fools low-aggression models when not gated by absolute RMS amplitude.

### Failed Attempt 2: Audio Peak-Only Normalization (`audio = audio / peak`)
- **What was tried**: Normalized all audio frames to maximum peak amplitude (1.0) prior to Whisper inference.
- **Negative Result**: When audio contained only faint room noise (e.g., peak amplitude = 0.008, or -42 dBFS), dividing by `peak` multiplied ambient static by **125x**, transforming inaudible room hum into deafening digital white noise.
- **Why it failed**: Peak normalization without an energy floor eradicates the signal-to-noise ratio distinction, forcing the neural acoustic encoder to hallucinate phonetic content from amplified static.

### Failed Attempt 3: Unconstrained Language Decoding (`language=None`)
- **What was tried**: Allowed Whisper to automatically infer spoken language dynamically.
- **Negative Result**: Lacking explicit English constraints, Whisper's language identifier assigned high posterior probabilities to Asian and Middle-Eastern language tokens containing high-frequency YouTube subtitle tokens.
- **Why it failed**: Autoregressive decoders fall back on training dataset priors when acoustic probability distributions are uniform (pure noise).

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Dual-Gate VAD Architecture (`vad.py`)**:
   - Upgraded WebRTC VAD to **Mode 2 (Aggressive)**.
   - Enforced a strict **dual-gate**: a frame is speech if and only if WebRTC VAD classifies it as speech **AND** frame RMS energy exceeds `0.02` ($RMS \ge 0.02$).
   - Enforced an utterance-level gate on `SPEECH_END`: collected buffer must have $Peak \ge 0.035$ and $RMS \ge 0.008$.
2. **Anti-Hallucination ASR Pipeline (`transcription.py`)**:
   - Pinned `language="en"` explicitly.
   - Enforced pre-inference silence rejection: if $Peak < 0.035$ or $RMS < 0.008$, return empty string immediately without invoking Whisper.
   - Clamped gain normalization to $3.0\times$ (`gain = min(1.0 / peak, 3.0)`), completely preventing the amplification of background noise floors.
   - Configured Whisper decoding hyperparameters: `temperature=0.0`, `no_speech_threshold=0.6`, `logprob_threshold=-1.0`, `compression_ratio_threshold=2.4`, `condition_on_previous_text=False`.
   - Added `_HALLUCINATION_BLACKLIST` to strip residual YouTube subtitle artifacts.
3. **Action Protocol Slots & Directive Defusing (`action_protocol.py` & `interaction_orchestrator.py`)**:
   - Added `utterance_id: str = ""` to `ActionRequest(slots=True)`.
   - Unified imports so orchestrator and protocol share the identical dataclass.
   - Added automatic rerouting for hallucinated `ACTION: speak(...)` commands directly to spoken text queues.
4. **Prompt Language Pinning (`llm_stream.py`)**:
   - Added explicit system prompt directive: *"You are an English-only desktop voice assistant. You MUST ALWAYS respond exclusively in clear English. Never output non-English text."*

---

## 4. Academic Thesis Contribution
- **Empirical HCI Finding**: Demonstrates that full-duplex conversational loops on edge hardware suffer from *Autoregressive Cascading Hallucination (ARCH)*: a minor upstream VAD false positive amplifies across unconstrained ASR and SLM decoders into a self-perpetuating feedback cycle.
- **Architectural Solution**: Solved via a **Dual-Gate Energy-Spectral VAD** and **Bounded Pre-ASR Normalization**, proving that edge full-duplex systems require multi-stage signal-energy gating before neural inference.
- **Thesis Reference**: Chapter 4 (Engineering Challenges & Acoustic Echo Mitigation), Section 4.3 (VAD Self-Triggering and Neural Hallucination Cascades).
