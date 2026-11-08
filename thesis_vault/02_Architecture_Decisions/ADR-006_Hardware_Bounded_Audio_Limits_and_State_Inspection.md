---
id: ADR-006
title: Hardware-Bounded Audio Limits, Overamplification Guardrails, and State Inspection
tags: [adr, architecture, safety, audio, wireplumber, pipewire, telemetry]
status: Accepted
related: ["[[Frozen_Fedora_Commands]]", "[[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]]", "[[PRB-010_Uncoordinated_Audio_Stream_Collision_and_False_Success_Reporting]]"]
---

# 🏛️ ADR-006: Hardware-Bounded Audio Limits, Overamplification Guardrails, and State Inspection

## Context & Problem Statement
In WirePlumber (`wpctl`), volume adjustments behave differently from standard desktop graphical user interfaces (GNOME Settings):
1. **Unbounded Overamplification**: Executing `wpctl set-volume @DEFAULT_SINK@ 5%+` without a limit flag permits volume values to continuously scale past $1.0$ ($100\%$) up to $1.5+$ ($150\%$). While GNOME's UI enforces a strict $100\%$ ceiling unless "Over-amplification" is explicitly toggled in settings, headless CLI invocations will over-drive software digital gain, introducing severe acoustic distortion, clipping, and physical speaker damage risks.
2. **Audio State Opacity**: The conversational assistant lacked awareness of the machine's actual volume level, minimum ($0\%$), and maximum ($100\%$) bounds, leaving users unable to ask *"What is the current volume?"* or deterministically set bounds (*"Set volume to maximum"*, *"Mute"*).

## Decision Drivers
- **Acoustic Safety & Hardware Protection**: Enforce strict hardware ceiling limits at $100\%$ ($1.0$) to prevent digital audio clipping and speaker blowouts.
- **Desktop UI Alignment**: Match standard Fedora/GNOME slider constraints where nominal maximum is $100\%$.
- **Closed-Loop Multimodal Awareness**: Allow bidirectional inspection where the agent can both set and verbally report volume metrics.
- **Thesis Scope Compliance**: Restrict audio interactions to deterministic WirePlumber commands without introducing unbounded tools.

## Decision & Implementation
We extend Category 2 of the [[Frozen_Fedora_Commands]] specification with bounded WirePlumber directives:
1. **Mandatory Hardware Upper Bound (`-l 1.0`)**:
   All upward volume adjustments enforce the `--limit 1.0` parameter:
   `wpctl set-volume -l 1.0 @DEFAULT_SINK@ 5%+` and `wpctl set-volume -l 1.0 @DEFAULT_SINK@ 1.0`.
   Even if an incoming LLM tool call omits `-l 1.0`, the execution engine automatically injects the limit parameter prior to subprocess execution.
2. **Explicit Bound and Mute Commands**:
   - Maximum volume ($100\%$): `wpctl set-volume -l 1.0 @DEFAULT_SINK@ 1.0`
   - Minimum volume ($0\%$): `wpctl set-volume @DEFAULT_SINK@ 0`
   - Discrete mute controls: `wpctl set-mute @DEFAULT_SINK@ 1` (mute), `wpctl set-mute @DEFAULT_SINK@ 0` (unmute), and `toggle`.
3. **Volume State Querying & Vocal Telemetry**:
   - Volume query command: `wpctl get-volume @DEFAULT_SINK@`.
   - Output parsing regex: extracts floating-point volume (e.g. `Volume: 0.95` $\rightarrow$ $95\%$) and mute flag (`[MUTED]`).
   - Closed-loop speech feedback: *"Current volume is 95 percent"* or *"Current volume is 95 percent, and audio is currently muted."*
4. **Agent Self-Awareness Grounding**:
   The system prompt in `ChatHistory` explicitly informs the SLM that minimum volume is $0\%$ (silent) and maximum volume is $100\%$, establishing crisp situational awareness.

## Consequences & Academic Contribution
- **Positive**: Eliminates over-amplification distortion; provides natural closed-loop vocal queries for system volume; guarantees safe desktop audio bounds.
- **Negative**: Adds light parsing logic for WirePlumber output in `action_executor.py`.
- **Thesis Impact**: Contributes to Chapter 3 (*System Architecture: Safe Desktop Actuation*) and Chapter 4 (*Edge Workstation Hardware Integration and Acoustic Safety*).
