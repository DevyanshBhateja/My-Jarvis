---
id: PRB-008
title: Out-of-Scope Command Hallucination & Blocking Stdin Deadlock
research_question: "[[Research_Questions|RQ1]]"
status: Solved
tags: [problem, failed-attempt, solution, rq1, security, frozen_commands, stdin, deadlock]
related: ["[[Frozen_Fedora_Commands]]", "[[PRB-007_Non_Daemon_Thread_Deadlock_SIGINT]]"]
---

# ⚠️ PRB-008: Out-of-Scope Command Hallucination & Blocking Stdin Deadlock

## 1. Problem Description & Symptoms
When the user said *"Shut down."* into the microphone:
1. **Out-of-Scope Execution Hallucination**: Because the voice exit parser checked `"shutdown"` without spaces, the phrase `"Shut down."` was passed to the SLM (Qwen 2.5 3B). The LLM interpreted the input as a workstation power command and emitted:
   ```text
   ACTION: run_command("shutdown now")
   ```
   This violated Golden Rule 1 (*"Never introduce unbounded features, random tools, or arbitrary desktop commands"*).
2. **Blocking Stdin Confirmation Lockup**: The safety mechanism triggered:
   ```text
   [ACTION REQUEST] Run command 'shutdown now'
   > Approve action? (yes/no): Run command 'shutdown now'
   ```
   and called standard `input()`. This performed a blocking `read()` on `sys.stdin`.
3. **Shutdown Deadlock**: When the user subsequently said *"exit."*, the orchestrator closed the microphone and initiated teardown, but the background `action` worker thread was permanently blocked on C-level `stdin` I/O, freezing the process indefinitely.

---

## 2. Failed Attempts & Negative Results (Thesis Discussion)

### Failed Attempt 1: Raw String In-Set Matching (`{"shutdown"}`)
- **What was tried**: Checked `clean_prompt in {"exit", "quit", "shutdown"}`.
- **Negative Result**: Natural ASR often inserts spaces, trailing periods, or capitalization (e.g. `"Shut down."` vs `"shutdown"`). Any unhandled variation bypassed the assistant exit hook and reached the LLM.

### Failed Attempt 2: Synchronous Console Confirmation via `input()`
- **What was tried**: Relied on standard Python `input()` to prompt for human approval before dangerous actions.
- **Negative Result**: In hands-free voice interfaces, the user is talking via microphone, not typing into the console. Blocking `stdin` starves background event loops and deadlocks thread join routines during teardown.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Frozen Fedora Whitelist Enforcement (`action_executor.py`)**:
   - Implemented `is_action_whitelisted(request)` strictly enforcing [[Frozen_Fedora_Commands]] (`CMD-01` to `CMD-10`).
   - If an action outside the approved 10 is received (e.g., `shutdown now`, `rm`, arbitrary scripts), it is immediately blocked at the gate with zero execution and zero confirmation prompts:
     ```text
     [ACTION SAFETY DENIED] Blocked: shell command 'shutdown now' is outside the 10 Frozen Fedora Commands.
     ```
2. **Non-Blocking Timed Confirmation (`action_executor.py`)**:
   - Replaced blocking `input()` with asynchronous multiplexing via `select.select([sys.stdin], [], [], timeout=10.0)`:
     ```python
     if sys.stdin.isatty():
         rlist, _, _ = select.select([sys.stdin], [], [], timeout)
         if rlist:
             response = sys.stdin.readline().strip()
         else:
             print("\n[TIMEOUT] No input received within timeout. Defaulting to deny.")
     ```
   - Automatically aborts and denies unapproved actions after 10 seconds without stalling the assistant.
3. **Broadened Voice Exit Normalization (`interaction_orchestrator.py`)**:
   - Expanded exit phrase recognition to include multi-word triggers: `"shut down"`, `"turn off"`, `"power off"`, `"close assistant"`, `"goodbye"`, and suffix matches (`"jarvis shut down"`).

---

## 4. Academic Thesis Contribution
- **Deterministic Action Containment**: Demonstrates that generative SLMs cannot be granted direct shell dispatch on edge workstations; every action directive must pass through a strict deterministic whitelist gate prior to safety dialogs.
- **Asynchronous Human-in-the-Loop Ergonomics**: Proves that interactive confirmation in voice-first systems requires non-blocking timeout fallbacks to prevent zombie threads and threadpool teardown deadlocks.
- **Thesis Reference**: Chapter 3 (System Architecture), Section 3.5 (Security & Frozen Fedora Command Sandbox).
