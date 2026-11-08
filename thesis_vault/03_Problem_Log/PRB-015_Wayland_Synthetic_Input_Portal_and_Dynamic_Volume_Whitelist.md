---
id: PRB-015
title: Wayland Synthetic Keystroke Security Modal and Rigid Volume Whitelist Rejection
research_question: [[RQ1_Concurrency_Pipelining]]
status: Solved
tags: [problem, failed-attempt, solution, wayland, security, audio, rq1]
---

# PRB-015: Wayland Synthetic Keystroke Security Modal and Rigid Volume Whitelist Rejection

## 1. Problem Description & Symptoms
- **Symptom 1 (Window Close)**: When executing `hotkey("alt", "f4")` to close an active window under Fedora GNOME, GNOME intercepted the call and presented a system security modal titled:  
  `Remote Desktop: Allow Remote Interaction`.
- **Symptom 2 (Volume Control)**: When asking *"Can you set the volume to 50%?"*, the local SLM emitted:  
  `ACTION: run_command("wpctl set-volume -l 1.0 @DEFAULT_SINK@ 50%+")`.  
  The system rejected the action with:  
  `[ACTION SAFETY DENIED] Blocked: shell command 'wpctl set-volume -l 1.0 @DEFAULT_SINK@ 50%+' is outside authorized capabilities.`

---

## 2. Root Cause Analysis

### A. Wayland Security Model vs. Synthetic Input
Unlike legacy X11, Wayland strictly isolates input events between display clients to prevent keylogging and unauthorized input injection. When `pyautogui` attempts to simulate `Alt + F4` through Xwayland or the `xdg-desktop-portal`, GNOME's Mutter compositor classifies the virtual input stream as a "Remote Desktop" interaction and demands manual user consent via a modal dialog.

### B. Overly Rigid String Matching for Audio Commands
`action_executor.py` initially used exact string membership (`if cmd in APPROVED_COMMANDS`). The catalog contained fixed increments (`5%+`, `5%-`, `100%`, `0%`), but omitted arbitrary percentages (e.g., `50%`, `50%+`, `75%`), triggering the safety containment barrier even though the request was safe.

---

## 3. Working Solution

### Solution 1: Wayland-Safe Native Process Lifecycle Management
Instead of injecting brittle synthetic keystrokes via `pyautogui`, `system_actions.py` now maintains a tracking stack of spawned processes (`RECENT_PROCESSES`). When `hotkey("alt", "f4")` is called:
1. It pops the most recently launched process (e.g., Nautilus file manager, Calculator, Terminal) and cleanly terminates it via `proc.terminate()`.
2. As a fallback, it executes audited process termination (`pkill -f <app>`) for approved utilities.
3. This completely eliminates the GNOME "Remote Desktop" dialog, guarantees zero Wayland permission popups, and closes foreground windows instantly.

### Solution 2: Regex-Validated Volume Adjustments with Hardware Ceiling
Updated `action_executor.py` with safe regex matching:
```python
# Enforce hardware safety limit -l 1.0
if "wpctl set-volume" in cmd and "-l 1.0" not in cmd:
    cmd = cmd.replace("wpctl set-volume", "wpctl set-volume -l 1.0")
    request.args[0] = cmd

# Whitelist any safe volume adjustment pattern
if re.match(r"^wpctl\s+set-volume\s+(-l\s+1\.0\s+)?@DEFAULT_SINK@\s+\d+(\.\d+)?%?[+-]?$", cmd):
    return True, f"run_command('{cmd}')"
```
Spoken telemetry dynamically reports the exact target volume (e.g. *"Volume set to 50%."*).

---

## 4. Academic Thesis Contribution
- **Wayland Security Boundaries in Desktop Automation**: Highlights why edge AI agents on modern Linux workstations cannot rely on X11-era GUI automation tools like `pyautogui`. Process lifecycle management provides a deterministic, zero-permission alternative.
- **Reference in Thesis**: Chapter 3 (System Architecture, Section 3.4: Action Containment) and Chapter 5 (Engineering Challenges).
