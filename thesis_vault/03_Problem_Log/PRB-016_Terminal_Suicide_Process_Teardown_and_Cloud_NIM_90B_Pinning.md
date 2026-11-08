---
id: PRB-016
title: Terminal and IDE Parent Process Termination and Cloud NIM 90B Model Pinning
research_question: [[RQ1_Concurrency_Pipelining]], [[RQ3_Edge_Cloud_Viability]]
status: Solved
tags: [problem, failed-attempt, solution, safety, process-management, cloud, rq1, rq3]
---

# PRB-016: Terminal and IDE Parent Process Termination and Cloud NIM 90B Model Pinning

## 1. Problem Description & Symptoms
During a live demonstration:
1. **Host Environment Teardown (Terminal Suicide)**: When a web search tab opened in the browser and the user commanded *"Close the opened brave window"*, the assistant's window-closing fallback executed `pkill -f ptyxis`. Because the assistant and the IDE server were running inside the Ptyxis terminal, it terminated its own host terminal, crashing the active session and web IDE.
2. **Cloud NIM 404 Failure**: Dispatching reasoning queries to the cloud failed with HTTP 404 (`Function not found for account`), falling back to local edge execution.

---

## 2. Root Cause Analysis

### A. Indiscriminate Process Fallback in Window Teardown
In `system_actions.py`, `hotkey("alt", "f4")` contained a fallback loop:
```python
for app in ("nautilus", "gnome-calculator", "ptyxis", "gnome-terminal"):
    subprocess.run(["pkill", "-f", app], check=False)
```
Because browser URLs opened via `xdg-open` were not previously tracked in `RECENT_PROCESSES`, the queue was empty. The fallback loop iterated through the list, reached `ptyxis` (the host terminal emulator on Fedora), and terminated the parent process of the running assistant.

### B. NVIDIA NIM Preview Endpoint Retirement
The configured model `nvidia/nemotron-3-super-120b-a12b` was a preview container function that reached end-of-life or was not activated on developer accounts, resulting in 404 errors during cloud API calls.

---

## 3. Working Solution

### Solution 1: Terminal Immune System & Targeted `close_app` Action
1. **Explicit Terminal Immunization**: Hardcoded safety barriers in [system_actions.py](file:///home/dave/Documents/Projects/MY_JARVIS/jarvis_rt/system_actions.py) and [action_executor.py](file:///home/dave/Documents/Projects/MY_JARVIS/jarvis_rt/action_executor.py) strictly block terminating `ptyxis`, `gnome-terminal`, `kgx`, `xterm`, `bash`, `python`, or `code`.
2. **Targeted `close_app` Primitive**: Added `close_app(app_name: str)` (e.g. `close_app("brave")`, `close_app("nautilus")`). When the user commands *"Close the opened brave window"*, the SLM generates `ACTION: close_app("brave")`, isolating the target window.
3. **Browser Lifecycle Tracking**: `open_url()` now registers the launched browser process into `RECENT_PROCESSES`, enabling deterministic window termination.

### Solution 2: Verified NVIDIA NIM 90B Model Pinning
Benchmarked all 84 active endpoints on the user's NVIDIA NIM account. Pinned `meta/llama-3.2-90b-vision-instruct`, which was verified live:
- Response latency: ~3.5–4.5s.
- Token-by-token streaming: Verified (47 tokens streamed with zero errors).
- Configured in `.env`: `JARVIS_NVIDIA_MODEL="meta/llama-3.2-90b-vision-instruct"`.

---

## 4. Academic Thesis Contribution
- **Process Privilege & Host Containment**: In desktop automation research, an assistant must maintain a strict "self-preservation" invariant where operating system actions can never target the assistant's own host process hierarchy or terminal emulator.
- **Reference in Thesis**: Chapter 3 (System Architecture, Section 3.4: Action Containment) and Chapter 5 (Engineering Challenges & Failure Analysis).
