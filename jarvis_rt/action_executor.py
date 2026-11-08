"""Confirm and execute ACTION requests safely."""

from __future__ import annotations

import re
import select
import sys
from typing import Callable, Optional

from .action_protocol import ActionRequest
from . import system_actions


_CONFIRM_YES = {"yes", "yeah", "approve", "go ahead", "ok", "okay"}
_CONFIRM_NO = {"no", "stop", "cancel", "nope", "deny"}

# Approved Frozen Fedora & Extended Workstation Suite (SPEC-003 / ADR-008)
APPROVED_OPEN_APPS = {
    "firefox",
    "brave",
    "brave-browser",
    "com.brave.Browser",
    "nautilus",
    "gnome-terminal",
    "ptyxis",
    "terminal",
    "code",
    "gnome-calculator",
    "gnome-control-center",
}

APPROVED_COMMANDS = {
    "wpctl set-mute @DEFAULT_SINK@ toggle",
    "wpctl set-mute @DEFAULT_SINK@ 1",
    "wpctl set-mute @DEFAULT_SINK@ 0",
    "wpctl set-volume @DEFAULT_SINK@ 5%+",
    "wpctl set-volume -l 1.0 @DEFAULT_SINK@ 5%+",
    "wpctl set-volume @DEFAULT_SINK@ 5%-",
    "wpctl set-volume -l 1.0 @DEFAULT_SINK@ 1.0",
    "wpctl set-volume -l 1.0 @DEFAULT_SINK@ 100%",
    "wpctl set-volume @DEFAULT_SINK@ 1.0",
    "wpctl set-volume @DEFAULT_SINK@ 100%",
    "wpctl set-volume @DEFAULT_SINK@ 0",
    "wpctl set-volume @DEFAULT_SINK@ 0%",
    "wpctl get-volume @DEFAULT_SINK@",
    "top -b -n1 | head -5",
    "hostname -I",
    "free -h",
    "free -m",
    "df -h /",
    'date +"%A, %B %d, %Y, %I:%M %p"',
    "date",
    "loginctl lock-session",
}


def is_action_whitelisted(request: ActionRequest) -> tuple[bool, str]:
    """Check if action strictly complies with authorized capabilities (SPEC-003 / ADR-008)."""
    name = request.name
    args = [str(a) for a in request.args]

    if name == "open_app":
        if args and args[0] in APPROVED_OPEN_APPS:
            return True, f"open_app({args[0]})"
        return False, f"Blocked: app '{args[0] if args else ''}' is not in approved apps {APPROVED_OPEN_APPS}"

    if name == "close_app":
        app = args[0].lower().strip() if args else ""
        if any(term in app for term in ("ptyxis", "terminal", "gnome-terminal", "kgx", "xterm", "bash", "python", "ide", "code")):
            return False, "Blocked: closing terminal or development environment is strictly prohibited."
        return True, f"close_app({app})"

    if name == "open_url":
        if args and (args[0].startswith("http://") or args[0].startswith("https://")):
            return True, f"open_url({args[0][:50]}...)"
        return False, f"Blocked: invalid or non-web URL '{args[0] if args else ''}'"

    if name == "media_control":
        act = (args[0] if args else "play-pause").lower()
        if act in ("play-pause", "toggle", "next", "skip", "prev", "previous", "back"):
            return True, f"media_control({act})"
        return False, f"Blocked: unknown media action '{act}'"

    if name == "take_screenshot":
        return True, "take_screenshot()"

    if name == "lock_screen":
        return True, "lock_screen()"

    if name == "get_weather":
        return True, f"get_weather('{args[0] if args else ''}')"

    if name == "hotkey":
        if len(args) == 2 and args[0].lower() == "alt" and args[1].lower() == "f4":
            return True, "hotkey('alt', 'f4')"
        return False, f"Blocked: hotkey {args} is not authorized"

    if name == "run_command":
        if not args:
            return False, "Blocked: empty run_command"
        cmd = args[0].strip()
        # If the SLM omits the trailing volume value after @DEFAULT_SINK@ when intending 100%:
        if cmd.strip() in ("wpctl set-volume -l 1.0 @DEFAULT_SINK@", "wpctl set-volume @DEFAULT_SINK@"):
            cmd = "wpctl set-volume -l 1.0 @DEFAULT_SINK@ 100%"
            request.args[0] = cmd

        # Automatically enforce hardware limit -l 1.0 on volume upward adjustments
        if "wpctl set-volume" in cmd and "-l 1.0" not in cmd:
            cmd = cmd.replace("wpctl set-volume", "wpctl set-volume -l 1.0")
            request.args[0] = cmd

        # Whitelist any safe wpctl set-volume command (e.g., 50%, 50%+, 0.5, 5%-, 5%+, 100%)
        if re.match(r"^wpctl\s+set-volume\s+(-l\s+1\.0\s+)?@DEFAULT_SINK@\s+\d+(\.\d+)?%?[+-]?$", cmd):
            return True, f"run_command('{cmd}')"

        if cmd in APPROVED_COMMANDS or cmd.startswith("upower -i") or cmd.startswith("date"):
            return True, f"run_command('{cmd}')"
        return False, f"Blocked: shell command '{cmd}' is outside authorized capabilities."

    return False, f"Blocked: action '{name}' is not in authorized capabilities."


def is_action_auto_approved(request: ActionRequest) -> bool:
    """Tier 1 actions (read-only diagnostics, audio, apps, media, web, weather, window close) require zero approval.
    Tier 2 actions require user confirmation."""
    if request.name in ("open_app", "close_app", "open_url", "media_control", "take_screenshot", "lock_screen", "run_command", "get_weather", "hotkey"):
        return True
    return False


def format_action_result_speech(request: ActionRequest, raw_output: str) -> str:
    """Format raw action execution output into a natural spoken English response."""
    # Check for safety denials or execution errors first
    if "Safety policy error:" in raw_output or "Blocked:" in raw_output:
        return "I cannot execute that command; it is outside my authorized capabilities."
    if "Action cancelled by user" in raw_output or "timed out" in raw_output:
        return "Action was cancelled."
    if "Unknown action:" in raw_output or "Failed to execute" in raw_output:
        return "The action failed to execute."

    name = request.name
    args = [str(a) for a in request.args]

    if name == "close_app":
        app = args[0].lower() if args else "application"
        if "brave" in app or "browser" in app:
            return "Closed Brave browser window."
        if "firefox" in app:
            return "Closed Firefox."
        if "nautilus" in app or "file" in app:
            return "Closed file manager."
        if "calculator" in app:
            return "Closed calculator."
        return f"Closed {args[0] if args else 'application'}."

    if name == "open_app":
        app = args[0] if args else "application"
        if app == "code":
            return "Opening Visual Studio Code."
        elif app == "gnome-calculator":
            return "Opening calculator."
        elif app == "gnome-control-center":
            return "Opening system settings."
        elif app == "gnome-terminal":
            return "Opening a separate terminal window."
        elif app == "nautilus":
            return "Opening file manager."
        elif app in ("brave", "brave-browser", "com.brave.browser"):
            return "Opening Brave."
        elif app == "firefox":
            return "Opening Firefox."
        return f"Opening {app}."

    if name == "get_weather":
        if raw_output and not raw_output.startswith("Failed"):
            return raw_output
        loc = args[0] if args else "your area"
        return f"Unable to fetch weather for {loc}."

    if name == "open_url":
        url = args[0] if args else ""
        browser = system_actions.get_default_browser_name()
        if "youtube.com" in url or "youtu.be" in url:
            if "search_query=" in url:
                import urllib.parse
                raw_q = url.split("search_query=")[-1].split("&")[0]
                q = urllib.parse.unquote_plus(raw_q)
                return f"Searching for {q} on YouTube in {browser}."
            return f"Opening YouTube in {browser}."
        if "google.com/search" in url or "duckduckgo.com" in url:
            import urllib.parse
            q_param = "q=" if "q=" in url else "query="
            raw_q = url.split(q_param)[-1].split("&")[0]
            q = urllib.parse.unquote_plus(raw_q)
            summary = system_actions.get_web_summary(q)
            if summary:
                return f"Searching for {q} in {browser}. {summary}"
            return f"Searching for {q} in {browser}."
        return f"Opening the link in {browser}."

    if name == "media_control":
        act = (args[0] if args else "play-pause").lower()
        if "next" in act or "skip" in act:
            return "Skipped to next track."
        if "prev" in act or "back" in act:
            return "Returned to previous track."
        return "Media playback toggled."

    if name == "take_screenshot":
        return "Opening screenshot tool."

    if name == "lock_screen":
        return "Workstation screen locked."

    if name == "hotkey":
        return "Window closed."

    if name == "run_command" and args:
        cmd = args[0].strip()
        # 1. IP Address
        if cmd == "hostname -I":
            text = raw_output.replace("Command output:", "").strip()
            ips = text.split()
            first_ip = ips[0] if ips else "unknown"
            return f"Your local IP address is {first_ip}."

        # 2. Volume & Mute
        if "wpctl get-volume" in cmd:
            match = re.search(r"Volume:\s*(\d+[\.,]?\d*)", raw_output)
            is_muted = "[MUTED]" in raw_output
            if match:
                val = float(match.group(1).replace(",", "."))
                pct = int(round(val * 100))
                if is_muted:
                    return f"Current volume is {pct} percent, and audio is currently muted."
                return f"Current volume is {pct} percent."
            return "Volume status checked."

        if "wpctl set-mute" in cmd:
            if cmd.endswith(" 1"):
                return "Audio muted."
            if cmd.endswith(" 0"):
                return "Audio unmuted."
            return "Audio mute toggled."

        if "wpctl set-volume" in cmd:
            vol_match = re.search(r"@DEFAULT_SINK@\s+(\d+(\.\d+)?%?[+-]?)", cmd)
            if vol_match:
                level_str = vol_match.group(1).strip()
                if level_str in ("1.0", "100%", "100%+"):
                    return "Volume set to maximum, 100 percent."
                if level_str in ("0", "0%", "0.0"):
                    return "Volume set to minimum, 0 percent."
                if level_str == "5%+":
                    return "Volume increased by 5 percent."
                if level_str == "5%-":
                    return "Volume decreased by 5 percent."
                if "%" in level_str:
                    clean_pct = level_str.rstrip("+-")
                    return f"Volume set to {clean_pct}."
                try:
                    pct_val = int(round(float(level_str) * 100))
                    return f"Volume set to {pct_val} percent."
                except Exception:
                    pass
            return "Volume updated."

        # 3. CPU Usage
        if "top" in cmd:
            match = re.search(r"(\d+[\.,]?\d*)\s*id", raw_output)
            if match:
                idle = match.group(1).replace(",", ".")
                try:
                    idle_val = float(idle)
                    used_val = round(100.0 - idle_val, 1)
                    return f"CPU usage is currently {used_val} percent, with {idle} percent idle."
                except ValueError:
                    pass
            return "CPU check complete. System load is normal."

        # 4. Battery Check
        if "upower" in cmd:
            pct_match = re.search(r"percentage:\s*(\d+%)", raw_output)
            state_match = re.search(r"state:\s*([a-zA-Z-]+)", raw_output)
            pct = pct_match.group(1) if pct_match else ""
            state = state_match.group(1) if state_match else ""
            if pct and state:
                return f"Battery is at {pct} and currently {state}."
            elif pct:
                return f"Battery is at {pct}."
            return "Battery status checked."

        # 5. RAM / Memory Check
        if "free" in cmd:
            m_free = re.search(r"Mem:\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+(\S+)", raw_output)
            if m_free:
                total, used, avail = m_free.groups()
                return f"You have {avail} of RAM available out of {total} total."
            return "Memory check complete."

        # 6. Disk Storage Check
        if "df" in cmd:
            for line in raw_output.splitlines():
                if line.strip().endswith("/"):
                    parts = line.split()
                    if len(parts) >= 5:
                        size, avail, pct = parts[1], parts[3], parts[4]
                        return f"You have {avail} of disk storage available on the root drive, {pct} used."
            return "Disk storage check complete."

        # 7. Date & Time
        if cmd.startswith("date"):
            clean = raw_output.replace("Command output:", "").strip()
            return f"It is {clean}."

        # 8. Lock Session
        if "loginctl lock-session" in cmd:
            return "Workstation screen locked."

    return "Action completed."


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _interpret_confirmation(text: str) -> Optional[bool]:
    normalized = _normalize(text)
    if not normalized:
        return None
    if normalized in _CONFIRM_YES:
        return True
    if normalized in _CONFIRM_NO:
        return False
    return None


def describe_action(request: ActionRequest) -> str:
    if request.name == "open_app":
        return f"Open app '{request.args[0]}'"
    if request.name == "close_app":
        return f"Close app '{request.args[0] if request.args else 'window'}'"
    if request.name == "run_command":
        return f"Run command '{request.args[0]}'"
    if request.name == "open_url":
        return f"Open URL '{request.args[0]}'"
    if request.name == "type_text":
        return f"Type text ({len(request.args[0])} chars)"
    if request.name == "press_key":
        return f"Press key '{request.args[0]}'"
    if request.name == "hotkey":
        return "Press hotkey: " + " + ".join(request.args)
    if request.name == "click":
        x = request.kwargs.get("x", request.args[0] if request.args else "?")
        y = request.kwargs.get("y", request.args[1] if len(request.args) > 1 else "?")
        button = request.kwargs.get("button", "left")
        return f"Click at ({x}, {y}) with {button} button"
    if request.name == "scroll":
        amount = request.args[0] if request.args else 0
        return f"Scroll by {amount}"
    if request.name == "read_file":
        return f"Read file '{request.args[0]}'"
    if request.name == "write_file":
        return f"Write file '{request.args[0]}'"
    if request.name == "list_dir":
        return f"List directory '{request.args[0]}'"
    return f"Execute action '{request.name}'"


def _execute_action(request: ActionRequest) -> str:
    handler = getattr(system_actions, request.name, None)
    if handler is None:
        return f"Unknown action: {request.name}"
    return handler(*request.args, **request.kwargs)


def confirm_and_execute(
    request: ActionRequest,
    voice_confirm_fn: Callable[[], Optional[bool]] | None = None,
    timeout: float = 10.0,
) -> str:
    # 1. Thesis Scope Enforcement: Check Frozen Fedora Whitelist
    allowed, reason = is_action_whitelisted(request)
    if not allowed:
        print(f"[ACTION SAFETY DENIED] {reason}")
        return f"Safety policy error: {reason}"

    description = describe_action(request)
    print(f"[ACTION REQUEST] {description} ({reason})")

    # 2. Check Tier: Auto-Approved vs Confirmed
    if is_action_auto_approved(request):
        print(f"[ACTION AUTO-APPROVED] Executing Tier 1 action: {description}")
        result = _execute_action(request)
        print(f"[ACTION RESULT] {result}")
        return result

    # 3. Tier 2: Voice or Timed Stdin Confirmation
    approved: Optional[bool] = None
    if voice_confirm_fn is not None:
        print("[ACTION CONFIRMATION] Asking for voice approval")
        approved = voice_confirm_fn()

    if approved is None:
        try:
            from jarvis_ui.state_bridge import ui_bridge
            ui_bridge.post_action("Confirmation Needed", description)
        except Exception:
            pass
        print(f"> Approve action? (yes/no) [Auto-deny in {timeout}s]: {description} -> ", end="", flush=True)
        response = ""
        try:
            if sys.stdin.isatty():
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if rlist:
                    response = sys.stdin.readline().strip()
                else:
                    print("\n[TIMEOUT] No input received within timeout. Defaulting to deny.")
            else:
                response = ""
        except Exception as e:
            print(f"\n[ERROR] Stdin read error: {e}")
            response = ""

        approved = _interpret_confirmation(response)

    if approved:
        result = _execute_action(request)
        print(f"[ACTION RESULT] {result}")
        return result

    print("[ACTION CANCELLED] Action cancelled by user or timed out.")
    return "Action cancelled by user or timed out"
