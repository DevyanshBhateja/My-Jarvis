---
id: ADR-008
title: Extended Workstation Suite, Browser-Anchored Media Routing, and MPRIS Integration
tags: [adr, architecture, workstation, media, actions, thesis, rq1]
status: Accepted
related: ["[[Frozen_Fedora_Commands]]", "[[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]]", "[[ADR-006_Hardware_Bounded_Audio_Limits_and_State_Inspection]]", "[[ADR-007_Hierarchical_Edge_Cloud_Relay_and_Silent_Execution]]"]
---

# 🏛️ ADR-008: Extended Workstation Suite, Browser-Anchored Media Routing, and MPRIS Integration

## Context & Problem Statement
In human-agent desktop interaction, users expect voice assistants to control daily PC workflows beyond narrow academic diagnostic benchmarks. 

However, expanding system capabilities on Linux presents two design tensions:
1. **Thesis Benchmark Integrity**: The supervisor's mandate (*"make a list of what it can do, test that, nothing more"*) requires a frozen, deterministic test catalog (`SPEC-003`) to ensure repeatable statistical evaluation (50 trials per command). Uncontrolled command addition risks breaking benchmark reproducibility.
2. **Proprietary Media App Fragmentation**: The user does not run native desktop Spotify or dedicated YouTube client binaries. Requesting music playback or video streaming often results in failed application launches, missing authentication tokens, or unresponsive desktop daemons.

## Decision Drivers
- **Bifurcated Profile Architecture**: Maintain strict separation between the **Frozen Fedora Benchmark Suite** (10 commands for Chapter 5 empirical tests) and the **Extended Daily Workstation Suite** (for practical hands-free operation).
- **Universal Browser Anchoring**: Route music, songs, and video queries into query-encoded YouTube URLs rendered in the native browser (Firefox).
- **Universal Linux Media Control**: Utilize standard Linux D-Bus MPRIS (`org.mpris.MediaPlayer2`) via `busctl` to control active media streams (play/pause, next, previous) across any web browser or native media player without needing third-party libraries or proprietary APIs.
- **Closed-Loop Vocal Telemetry**: Ensure newly added diagnostics (`free -h`, `df -h /`, `date`) parse structured metrics into natural spoken English rather than reading raw terminal tables.

## Considered Options
1. **Option A (Dedicated Desktop App Integration)**:
   - Install and control native Spotify / YouTube desktop clients.
   - *Rejected*: User explicitly relies on customized web and browser workflows; native clients introduce extraneous background memory overhead (~400MB RAM each) conflicting with the 4GB VRAM workstation envelope.
2. **Option B (Unrestricted Shell Execution)**:
   - Allow the LLM to emit arbitrary bash commands.
   - *Rejected*: Violates thesis safety guarantees; risk of shell injection or system instability.
3. **Option C (Controlled Extensible Whitelist + Browser-Anchored Media - Accepted)**:
   - **Extended Whitelist**: Adds `code`, `gnome-calculator`, `gnome-control-center`, `free -h` (RAM), `df -h /` (Disk storage), `date`, `loginctl lock-session`, and GNOME interactive screenshot overlay.
   - **Browser Media Routing**: Maps all musical and video requests to `open_url("https://www.youtube.com/results?search_query=...")` in Firefox.
   - **Universal MPRIS Control**: Controls media playback across all active desktop players via `media_control("play-pause"|"next"|"previous")`.

## Architecture & Whitelist Specification

```
User Voice Request ──► SLM Intent Recognition
                              │
    ┌─────────────────────────┼─────────────────────────┐
    ▼ (System App)            ▼ (Music / Video Query)   ▼ (Media Playback)
open_app("code")      open_url("https://youtube...")  media_control("play-pause")
open_app("calculator")        │ (xdg-open)                     │ (D-Bus MPRIS)
                              ▼                                ▼
                        Firefox Web                   Brave / Firefox / VLC
```

### Approved Extended Capabilities:
1. **Productivity Apps**: Visual Studio Code (`code`), GNOME Calculator (`gnome-calculator`), GNOME Settings (`gnome-control-center`).
2. **Media Playback**: `open_url(youtube_search)`, `media_control(play-pause|next|previous)`.
3. **Workstation Control**: `take_screenshot()` (GNOME Shell Interactive Screenshot), `lock_screen()` (`loginctl lock-session`).
4. **Hardware Telemetry**: `free -h` (available vs total RAM), `df -h /` (available vs total disk storage), `date` (current date & time).

## Consequences & Academic Contribution
- **Positive**:
  - Delivers a comprehensive, hands-free personal assistant experience on Fedora Linux.
  - Keeps memory usage pristine by leveraging Firefox web playback rather than heavy desktop electron apps.
  - Zero disruption to the 10 Frozen Benchmark Commands (`SPEC-003`).
- **Thesis Impact**: Contributes to Chapter 3 (System Architecture & Action Containment) and Chapter 5 (Evaluation of Human-Agent Interaction on Edge Linux Workstations).
