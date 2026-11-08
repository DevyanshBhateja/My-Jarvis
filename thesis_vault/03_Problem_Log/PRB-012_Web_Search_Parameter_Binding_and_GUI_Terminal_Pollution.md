---
id: PRB-012
title: Web Search Parameter Binding Failure & GUI Subprocess Terminal Pollution
research_question: "[[Research_Questions|RQ1]]"
status: Solved
tags: [problem, failed-attempt, solution, rq1, desktop_automation, prompt_engineering, subprocess_isolation]
related: ["[[ADR-008_Extended_Workstation_Suite_and_Media_Routing]]", "[[PRB-009_Silent_Action_Completion_and_Terminal_Pollution]]"]
---

# ⚠️ PRB-012: Web Search Parameter Binding Failure & GUI Subprocess Terminal Pollution

## 1. Problem Description & Symptoms
During live spoken interaction testing:
1. **Query-Action Disconnection (Empty App Launch)**:
   - When the user requested: *"Can you look for the weather in Ireland?"*, the assistant responded:
     ```text
     [LLM][local][token] 'ACTION: open_app("firefox")'
     [ACTION RESULT] Opened app: firefox
     [ACTION→VOICE] Enqueuing spoken telemetry: Opening Firefox.
     ```
   - **Symptom**: Firefox launched successfully on the desktop, but navigated to a blank new tab without initiating a search for the requested information (weather in Ireland).
2. **GUI Stdio Terminal Pollution**:
   - Spawning Firefox directly via `subprocess.Popen([app_name])` caused the browser's GTK and SafeBrowsing internal diagnostics to bleed directly into the runner terminal:
     ```text
     (org.mozilla.firefox:16351): Gtk-WARNING **: Theme parsing error: gtk.css:2:21: Junk at end of value for box-shadow
     Safe Browsing server returned a 400 during update: ...
     ```
   - **Symptom**: These external GUI error traces polluted the terminal log, burying the assistant's speech and telemetry indicators.

---

## 2. Failed Attempts & Negative Results (Crucial for Thesis Discussion)

### Failed Attempt 1: Expecting Multi-Step GUI Automation via Small Language Model (SLM)
- **What was tried**: Expecting the edge SLM (`qwen2.5:3b`) to first open the browser (`open_app("firefox")`), then synthesize subsequent GUI automation steps (e.g., typing into the address bar or navigating to Google).
- **Negative Result**: Edge SLMs lack sufficient context window and planning depth to coordinate multi-turn GUI automation states over audio channels without a dedicated vision/accessibility agent (e.g. AT-SPI). The model simply considered the command fulfilled once `open_app("firefox")` was returned.

### Failed Attempt 2: Standard Subprocess Execution without stdio Redirection
- **What was tried**: Launching desktop applications using default `subprocess.Popen([app_name])`.
- **Negative Result**: Modern desktop GUI applications (e.g., Firefox, Nautilus) write numerous GTK CSS warnings, GLib deprecation notices, and network update diagnostics directly to inherited stdout and stderr streams, causing severe terminal pollution.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Direct Parameterized URL Search Action (`llm_stream.py`)**:
   - Augmented the system prompt to explicitly bind web search, lookups, and topical queries directly to parameterized search URLs rather than a bare application launch:
     ```python
     # System Prompt rule:
     "When the user asks to look up, search for, or check something online (e.g. weather, news, facts, topics, 'look for the weather in Ireland'):"
     "ACTION: open_url(\"https://www.google.com/search?q=<encoded_query>\")"
     ```
   - Live testing confirmed that when prompted *"Can you look for the weather in Ireland?"*, the local SLM now emits:
     ```text
     ACTION: open_url("https://www.google.com/search?q=weather+in+Ireland")
     ```
2. **Subprocess stdio Nullification (`system_actions.py`)**:
   - Redirected `stdout` and `stderr` to `subprocess.DEVNULL` for both `open_app()` and `open_url()`:
     ```python
     subprocess.Popen(
         [app_name],
         stdout=subprocess.DEVNULL,
         stderr=subprocess.DEVNULL,
         start_new_session=True,
     )
     ```
   - This cleanly silences all GTK, GLib, and SafeBrowsing terminal logs.
3. **Spoken Telemetry & Browser Identity Mismatch**:
   - `open_url` relies on Linux `xdg-open`, which delegates to the user's desktop default browser (`com.brave.Browser` / Brave), but `format_action_result_speech()` originally hardcoded *"in Firefox"*.
   - **Symptom**: Jarvis announced it was searching in Firefox while Brave opened on the workstation screen.

---

## 2. Failed Attempts & Negative Results (Crucial for Thesis Discussion)

### Failed Attempt 1: Expecting Multi-Step GUI Automation via Small Language Model (SLM)
- **What was tried**: Expecting the edge SLM (`qwen2.5:3b`) to first open the browser (`open_app("firefox")`), then synthesize subsequent GUI automation steps (e.g., typing into the address bar or navigating to Google).
- **Negative Result**: Edge SLMs lack sufficient context window and planning depth to coordinate multi-turn GUI automation states over audio channels without a dedicated vision/accessibility agent (e.g. AT-SPI). The model simply considered the command fulfilled once `open_app("firefox")` was returned.

### Failed Attempt 2: Standard Subprocess Execution without stdio Redirection
- **What was tried**: Launching desktop applications using default `subprocess.Popen([app_name])`.
- **Negative Result**: Modern desktop GUI applications (e.g., Firefox, Nautilus) write numerous GTK CSS warnings, GLib deprecation notices, and network update diagnostics directly to inherited stdout and stderr streams, causing severe terminal pollution.

### Failed Attempt 3: Static Browser Identity Assumptions in Speech Synthesis
- **What was tried**: Hardcoding "Firefox" into spoken telemetry templates assuming a fixed browser distribution.
- **Negative Result**: On modern desktop Linux, users frequently use alternative or containerized browsers (e.g., Brave via Flatpak). Hardcoded strings broke agent grounded truth.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Direct Parameterized URL Search Action (`llm_stream.py`)**:
   - Augmented the system prompt to explicitly bind web search, lookups, and topical queries directly to parameterized search URLs rather than a bare application launch:
     ```python
     "ACTION: open_url(\"https://www.google.com/search?q=<encoded_query>\")"
     ```
2. **Subprocess stdio Nullification (`system_actions.py`)**:
   - Redirected `stdout` and `stderr` to `subprocess.DEVNULL` for both `open_app()` and `open_url()`.
3. **Dynamic Desktop Browser Detection (`system_actions.py` & `action_executor.py`)**:
   - Implemented `get_default_browser_name()` querying `xdg-settings get default-web-browser` and `xdg-mime query default x-scheme-handler/https`.
   - Resolves system defaults dynamically (`Brave`, `Firefox`, `Chrome`, etc.).
   - Added support for Flatpak/desktop launchers via `gtk-launch com.brave.Browser` / `flatpak run com.brave.Browser` when `open_app("brave")` is invoked.
   - Dynamic vocal telemetry: *"Searching for '{query}' in Brave."*

---

## 4. Academic Thesis Contribution
- **Action Granularity & Parameter Binding in Edge Voice Systems**: Demonstrates that for constrained edge SLMs (3B parameters), abstract user intents ("look up X") must be mapped directly to atomic, parameterized desktop directives (`open_url`) rather than decomposed into sequential application-launch and GUI-interaction workflows.
- **Grounded Telemetry in Multi-Browser Desktop Environments**: Validates that agent vocal feedback must reflect the true operating system state (resolved via standard desktop integration protocols like XDG) rather than hardcoded prompt heuristics.
- **Reference in Thesis**: Chapter 3 (System Implementation), Section 3.6 (Desktop Action Execution & Grounded Telemetry).
