---
id: ADR-005
title: Two-Tier Action Containment, Dedicated Terminal Isolation, and Closed-Loop Vocal Telemetry
tags: [adr, architecture, safety, frozen_commands, telemetry, voice]
status: Accepted
related: ["[[Frozen_Fedora_Commands]]", "[[ADR-003_Double_AI_Asymmetric_Duplex]]", "[[PRB-008_Out_of_Scope_Command_Hallucination_Stdin_Deadlock]]", "[[PRB-009_Silent_Action_Completion_and_Terminal_Pollution]]"]
---

# 🏛️ ADR-005: Two-Tier Action Containment, Dedicated Terminal Isolation, and Closed-Loop Vocal Telemetry

## Context & Problem Statement
In voice-driven desktop automation, invoking system utilities creates three distinct HCI dilemmas:
1. **Approval Friction**: Forcing users to manually confirm safe, read-only diagnostic checks (e.g. *"What is my IP address?"*) destroys conversational ergonomics.
2. **Terminal Pollution & Stdin Starvation**: Spawning user terminal sessions inside the host assistant runner pollutes diagnostic logs and deadlocks process teardown if commands block on standard input.
3. **Silent Action Completion**: Executing OS commands in background worker threads without routing standard output back into the speech engine leaves the user in complete silence.

## Decision Drivers
- **Thesis Safety Scope**: Compliance with the [[Frozen_Fedora_Commands]] specification (`SPEC-003`).
- **Hands-Free Conversational Flow**: Zero keyboard or terminal typing required for daily voice interactions.
- **Process Isolation**: The background assistant daemon must run undisturbed regardless of user terminal workflows.
- **Audible Multimodal Feedback**: Real-time voice answers for all queried system metrics.

## Considered Options
1. **Option A (Indiscriminate Manual Approval)**: Prompt for keyboard confirmation on every action (`yes/no`).
   - *Rejected*: Inoperable for hands-free voice agents; blocks threads when console input is unattended.
2. **Option B (Unrestricted Execution)**: Auto-execute all tool calls without gating.
   - *Rejected*: Dangerous; allows LLMs to close windows or run destructive commands if prompted maliciously or hallucinated.
3. **Option C (Two-Tier Containment + Vocal Telemetry - Accepted)**:
   - **Tier 1 (Auto-Approved / Zero-Prompt)**: Read-only diagnostics (`hostname -I`, `top`, `upower`), audio controls (`wpctl`), and safe app launches (`firefox`, `nautilus`, `gnome-terminal`).
   - **Tier 2 (Confirmed)**: Destructive desktop operations (`hotkey("alt", "f4")`).
   - **Dedicated GUI Terminal**: Spawns an isolated `gnome-terminal` window for interactive user shell sessions.
   - **Vocal Telemetry Feedback**: Parses command outputs and speaks answers directly via TTS.

## Decision & Rationale
We implement **Option C**:
1. **Strict Whitelist Gate (`action_executor.py`)**: Actions are strictly checked against `CMD-01` to `CMD-10`. Any call outside the specification (e.g. `shutdown now`) is immediately blocked.
2. **Zero-Friction Read-Only Telemetry**: Querying IP, CPU, or battery executes silently via internal subprocesses, parses raw metrics, and synthesizes natural English answers (e.g., *"Your local IP address is 192.168.1.131"*).
3. **Dedicated Terminal Isolation**: Invoking terminal tools launches a clean `gnome-terminal` GUI instance, maintaining pristine separation between the assistant daemon and user interactive workspaces.
4. **Bounded Agent Prompting (`llm_stream.py`)**: Grounded system prompt explicitly informs the SLM of its 10 authorized abilities, preventing out-of-distribution tool hallucinations.

## Consequences & Academic Contribution
- **Positive**: Sub-second end-to-end latency for diagnostic queries; complete hands-free interaction; zero host terminal contamination.
- **Negative**: Adds light parsing logic for regex extraction of IP, CPU, and battery percentages.
- **Thesis Impact**: Contributes to Chapter 3 (System Architecture & Action Execution Engine) and Chapter 5 (Evaluation of Human-Agent Safety Paradigms on Linux Workstations).
