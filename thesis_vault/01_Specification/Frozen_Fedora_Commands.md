---
id: SPEC-003
title: Frozen Fedora Benchmark Commands
tags: [specification, commands, fedora, benchmark, testing]
related: ["[[Supervisor_Guidelines]]", "[[Benchmarking_Protocol_and_Metrics]]", "[[ADR-003_Double_AI_Asymmetric_Duplex]]"]
---

# 🛡️ Frozen Fedora Benchmark Commands

Following the supervisor's directive (*"make a list what i can do, test that nothing more"*), the scope of OS automation is strictly restricted to **exactly 10 deterministic commands** across 3 functional categories.

---

## The 10 Approved Commands

### Category 1: Application & Window Management
| ID | Voice Prompt Example | Internal Action Mapping | Target System Utility | Expected Result |
| :--- | :--- | :--- | :--- | :--- |
| **CMD-01** | *"Open browser"* / *"Launch Firefox"* | `open_app("firefox")` | `subprocess.Popen(["firefox"])` | Firefox window renders |
| **CMD-02** | *"Open file manager"* | `open_app("nautilus")` | `subprocess.Popen(["nautilus"])` | Nautilus file explorer opens |
| **CMD-03** | *"Open terminal"* | `open_app("gnome-terminal")`| `subprocess.Popen(["gnome-terminal"])` | GNOME Terminal launches |
| **CMD-04** | *"Close this window"* | `hotkey("alt", "f4")` | `pyautogui.hotkey('alt', 'f4')` | Foreground window terminates |

### Category 2: Workspace & Audio Settings (PipeWire/WirePlumber)
| ID | Voice Prompt Example | Internal Action Mapping | Target System Utility | Expected Result |
| :--- | :--- | :--- | :--- | :--- |
| **CMD-05** | *"Mute sound"* / *"Unmute audio"* | `run_command("wpctl set-mute @DEFAULT_SINK@ toggle")` | `wpctl` (WirePlumber) | Sink audio mute toggles (or sets 1/0) |
| **CMD-06** | *"Turn up volume"* / *"Max volume"* | `run_command("wpctl set-volume -l 1.0 @DEFAULT_SINK@ 5%+")` | `wpctl` | Sink volume increases by 5% (capped at 100%) or sets to 1.0 |
| **CMD-07** | *"Turn down volume"* / *"What is my volume?"* | `run_command("wpctl set-volume @DEFAULT_SINK@ 5%-")` / `get-volume` | `wpctl` | Sink volume decreases by 5% (or 0) / returns current % |

### Category 3: System State & Hardware Diagnostics
| ID | Voice Prompt Example | Internal Action Mapping | Target System Utility | Expected Result |
| :--- | :--- | :--- | :--- | :--- |
| **CMD-08** | *"Check CPU usage"* | `run_command("top -b -n1 | head -5")` | Linux `top` via subprocess | Returns CPU idle / usage % |
| **CMD-09** | *"Check battery"* | `run_command("upower -i $(upower -e | grep BAT)")` | `upower` daemon | Returns battery percentage & state |
| **CMD-10** | *"What is my IP address?"*| `run_command("hostname -I")` | Linux `hostname` | Returns local IPv4 address |

---

## Evaluation Constraints
- **Zero Extraneous Actions**: No browser DOM scraping, arbitrary code execution, or mouse movement tasks will be evaluated.
- **Safety Protocol**: All commands trigger an explicit confirmation dialogue in the assistant (`"Approved?"`) before execution to satisfy human-in-the-loop safety requirements.
- **Trial Repetitions**: In the final thesis evaluation, each of these 10 commands will be tested across **50 trials** under varying ambient noise levels to compute statistically significant accuracy percentages.
