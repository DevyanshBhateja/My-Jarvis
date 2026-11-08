---
id: PRB-009
title: Silent Action Completion & Lack of Agent Capability Self-Awareness
research_question: "[[Research_Questions|RQ1]]"
status: Solved
tags: [problem, failed-attempt, solution, rq1, voice_feedback, telemetry, prompt_engineering]
related: ["[[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]]", "[[Frozen_Fedora_Commands]]"]
---

# ⚠️ PRB-009: Silent Action Completion & Lack of Agent Capability Self-Awareness

## 1. Problem Description & Symptoms
During live spoken interaction:
1. **Silent Action Execution**: When the user asked *"Now what is my IP address?"*, the SLM emitted `ACTION: run_command("hostname -I")` without any natural language tokens. The action executor ran the command and printed the IP address to the host runner terminal, but **did not pass the output to the TTS voice engine**. The user was left in complete silence.
2. **Generic Disclaimer Evasiveness**: When the user asked *"What are the capabilities I have allowed you to run commands on this PC?"*, the SLM answered:
   ```text
   "I'm sorry, but as a voice assistant, I don't have direct access to system capabilities or permissions. I can run certain system commands... but I don't have access to detailed information about what commands or actions have been allowed on the system."
   ```
   The model had no grounded awareness of its 10 authorized commands.
3. **Execution Context Confusion**: Spawning commands in the host runner terminal blurred the boundary between assistant daemon diagnostics and user desktop workflows.

---

## 2. Failed Attempts & Negative Results (Thesis Discussion)

### Failed Attempt 1: Relying on Model Co-Generation of Spoken Answers
- **What was tried**: Expecting the SLM to simultaneously generate conversational speech and tool call directives in a single turn.
- **Negative Result**: Small Language Models (3B parameters) frequently emit *only* the tool directive (e.g. `ACTION: run_command("hostname -I")`) when fine-tuned on code/tool datasets, suppressing conversational tokens entirely. This creates a silent user experience.

### Failed Attempt 2: Unspecified System Prompt Tool Examples
- **What was tried**: Providing syntax examples (`ACTION: open_app(...)`) in the system prompt without declaring the agent's explicit operational boundary.
- **Negative Result**: Led to evasive hallucinations (*"I don't know my permissions"*) and risky attempts to invoke unauthorized commands (`shutdown now`).

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Closed-Loop Vocal Telemetry (`action_executor.py` & `interaction_orchestrator.py`)**:
   - Implemented `format_action_result_speech(request, raw_output)` to parse command outputs into clean, spoken English sentences:
     - `hostname -I` $\rightarrow$ *"Your local IP address is 192.168.1.131."*
     - `top` $\rightarrow$ *"CPU usage is currently 4.2 percent, with 95.8 percent idle."*
     - `upower` $\rightarrow$ *"Battery is at 85 percent and currently charging."*
   - In `_action_loop`, after action completion, the result is immediately piped into the TTS synthesis queue, ensuring the user audibly hears the answer without lag.
2. **Dedicated Terminal Isolation (`system_actions.py`)**:
   - Terminal app requests strictly launch an independent `gnome-terminal` GUI window via `subprocess.Popen(["gnome-terminal"])`, cleanly isolating user terminal activities from the assistant runner.
3. **Bounded Agent Prompting (`llm_stream.py`)**:
   - Injected the explicit 10-command specification into the SLM system prompt:
     *"You have exactly 10 authorized capabilities on this Fedora workstation: 1. Open Applications... 2. Window Management... 3. Audio Control... 4. System Diagnostics... If the user asks what capabilities, tools, or powers you have on this PC, explain these 10 exact abilities concisely."*

---

## 4. Academic Thesis Contribution
- **Audio-Action Convergence in Edge Voice Agents**: Demonstrates that tool-calling in pure voice assistants cannot treat action execution as an asynchronous side effect; tool output must close the conversational loop by generating audible telemetry.
- **Thesis Reference**: Chapter 3 (System Architecture), Section 3.6 (Closed-Loop Vocal Telemetry & Terminal Isolation).
