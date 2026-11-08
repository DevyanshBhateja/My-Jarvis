---
id: ADR-002
title: PipeWire WebRTC AEC vs. Software Microphone Muting
tags: [adr, architecture, audio, pipewire, aec, barge-in, decision]
status: Accepted
related: ["[[Research_Questions]]", "[[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]]", "[[EXP-001_VAD_Speech_End_Debouncing]]"]
---

# 🏛️ ADR-002: PipeWire WebRTC AEC vs. Software Microphone Muting

## Context & Problem Statement
In voice assistants with external speakers, the assistant's synthesized voice loops back into its own microphone. This causes acoustic feedback and self-triggering: the VAD detects speech, transcribes the assistant's own voice, and interrupts playback.

The initial fix applied in the repository was a **software microphone pause**:
```python
def pause(self):
    self._paused.set()  # Mute microphone during TTS playback
```
However, while software muting completely eliminates echo, it **destroys true full-duplex functionality**: if the microphone is muted, the user cannot interrupt (barge-in) mid-sentence!

## Decision Drivers
1. **Full-Duplex Requirement**: Assistant must continuously listen *while* actively speaking.
2. **Barge-In Latency**: Delay between user speech onset and assistant silence must be $\le 200\text{ ms}$.
3. **False Interruption Rate**: Assistant's own voice must never register as user speech ($< 2\%$ error rate).
4. **Linux OS Integration**: Must leverage Fedora's default audio server (**PipeWire**).

## Decision & Rationale
We transition from software microphone pausing to **system-level Acoustic Echo Cancellation (AEC)** via the Linux PipeWire WebRTC echo-cancel filter chain:

```
┌────────────────────────────────────────────────────────┐
│             PIPEWIRE WEBRTC AEC FILTER CHAIN           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  [TTS Playback Stream] ──► [Virtual Sink (Echo-Cancel)]│
│                                    │ (Reference Audio) │
│                                    ▼                   │
│  [Physical Mic Capture] ──► [WebRTC AEC DSP Algorithm] │
│                                    │ (Subtracted Audio)│
│                                    ▼                   │
│                            [Clean Mic Source]          │
│                                    │                   │
│                                    ▼                   │
│                          [Jarvis VAD + Whisper]        │
└────────────────────────────────────────────────────────┘
```

The system filter is enabled in PipeWire via:
```bash
pw-cli load-module libpipewire-module-echo-cancel
```

## Consequences & Thesis Contribution
- **Positive**: True full-duplex is enabled. The microphone remains open 100% of the time, allowing immediate barge-in without self-triggering.
- **Negative**: Adds ~10–20ms algorithmic DSP latency and slight CPU overhead for the WebRTC AEC filter.
- **Comparison for Thesis (RQ2)**: Provides empirical comparison data between:
  1. *Baseline*: No AEC (high false-trigger rate).
  2. *Soft Muting*: 0% false triggers, but 0% barge-in capability (half-duplex).
  3. *PipeWire WebRTC AEC*: True full-duplex with verified barge-in under 200ms.
