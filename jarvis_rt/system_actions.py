"""System-level actions with safety wrappers."""

from __future__ import annotations

import os
import shutil
import subprocess
import webbrowser
from typing import Iterable


def get_default_browser_name() -> str:
    """Detect the system default web browser name on Linux/Fedora."""
    try:
        proc = subprocess.run(
            ["xdg-settings", "get", "default-web-browser"],
            capture_output=True,
            text=True,
            check=False,
            timeout=1.0,
        )
        out = (proc.stdout or "").strip().lower()
        if not out:
            proc = subprocess.run(
                ["xdg-mime", "query", "default", "x-scheme-handler/https"],
                capture_output=True,
                text=True,
                check=False,
                timeout=1.0,
            )
            out = (proc.stdout or "").strip().lower()

        if "brave" in out:
            return "Brave"
        if "firefox" in out:
            return "Firefox"
        if "chrome" in out:
            return "Chrome"
        if "chromium" in out:
            return "Chromium"
        if "edge" in out:
            return "Edge"
        if "opera" in out:
            return "Opera"
        if "vivaldi" in out:
            return "Vivaldi"
    except Exception:
        pass
    return "your browser"


def _require_pyautogui():
    try:
        import pyautogui  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        return None, f"pyautogui is not available: {exc}"
    return pyautogui, None


RECENT_PROCESSES: list[tuple[str, subprocess.Popen]] = []


def open_app(app_name: str) -> str:
    try:
        target = app_name.lower().strip()
        cmd = [app_name]
        if target in ("brave", "brave-browser", "com.brave.browser"):
            if shutil.which("brave"):
                cmd = ["brave"]
            elif shutil.which("brave-browser"):
                cmd = ["brave-browser"]
            elif shutil.which("gtk-launch"):
                cmd = ["gtk-launch", "com.brave.Browser"]
            elif shutil.which("flatpak"):
                cmd = ["flatpak", "run", "com.brave.Browser"]
        elif target in ("gnome-terminal", "terminal", "ptyxis"):
            # Fedora 40/41 uses Ptyxis by default; fallback through known terminal emulators
            for term_bin in ("ptyxis", "gnome-terminal", "kgx", "xterm"):
                if shutil.which(term_bin):
                    cmd = [term_bin]
                    break

        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        RECENT_PROCESSES.append((target, proc))
        return f"Opened app: {app_name}"
    except Exception as exc:
        return f"Failed to open app '{app_name}': {exc}"


def run_command(cmd: str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True)
        output = (result.stdout or "").strip()
        error = (result.stderr or "").strip()
        if output and error:
            return f"Command output:\n{output}\nErrors:\n{error}"
        if output:
            return f"Command output:\n{output}"
        if error:
            return f"Command errors:\n{error}"
        return f"Command finished with exit code {result.returncode}"
    except Exception as exc:
        return f"Failed to run command: {exc}"


def close_app(app_name: str) -> str:
    """Safely close a specific user application or browser window."""
    target = app_name.lower().strip()
    # Absolute safety guard: NEVER kill terminal emulators, IDEs, or shells
    if any(term in target for term in ("ptyxis", "terminal", "gnome-terminal", "kgx", "xterm", "bash", "python", "ide", "code")):
        return f"Blocked: closing terminal or development environment is not permitted."

    # 1. Close from tracked processes launched by Jarvis
    global RECENT_PROCESSES
    closed = False
    for i in range(len(RECENT_PROCESSES) - 1, -1, -1):
        app, proc = RECENT_PROCESSES[i]
        if target in app or app in target:
            if proc.poll() is None:
                try:
                    proc.terminate()
                    closed = True
                except Exception:
                    pass
            RECENT_PROCESSES.pop(i)
            if closed:
                return f"Closed {app_name}."

    # 2. Safe targeted process kill for approved user applications only
    if target in ("brave", "brave-browser", "com.brave.browser", "browser"):
        subprocess.run(["pkill", "-f", "brave"], check=False)
        return "Closed Brave browser window."
    elif target in ("firefox",):
        subprocess.run(["pkill", "-f", "firefox"], check=False)
        return "Closed Firefox."
    elif target in ("nautilus", "file-manager", "files"):
        subprocess.run(["pkill", "-f", "nautilus"], check=False)
        return "Closed file manager."
    elif target in ("gnome-calculator", "calculator"):
        subprocess.run(["pkill", "-f", "gnome-calculator"], check=False)
        return "Closed calculator."

    return f"No active window found for {app_name}."


def open_url(url: str) -> str:
    try:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        proc = subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        RECENT_PROCESSES.append(("brave", proc))
        return f"Opened URL: {url}"
    except Exception as exc:
        return f"Failed to open URL '{url}': {exc}"


def media_control(action: str = "play-pause") -> str:
    """Control active MPRIS media players (Firefox, Spotify, Brave, VLC, etc.) via DBus."""
    action = action.lower().strip()
    mpris_method = "PlayPause"
    if action in ("next", "skip"):
        mpris_method = "Next"
    elif action in ("prev", "previous", "back"):
        mpris_method = "Previous"

    try:
        proc = subprocess.run(["busctl", "--user", "list"], capture_output=True, text=True, check=False, timeout=2.0)
        lines = proc.stdout.splitlines()
        players = [line.split()[0] for line in lines if line.split() and line.split()[0].startswith("org.mpris.MediaPlayer2")]
        if not players:
            return "No active media players detected."
        for p in players:
            subprocess.run(["busctl", "--user", "call", p, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player", mpris_method], check=False, timeout=1.0)
        return f"Media command '{mpris_method}' sent to {len(players)} player(s)."
    except Exception as exc:
        return f"Failed to send media control: {exc}"


def take_screenshot() -> str:
    """Trigger GNOME interactive screenshot overlay."""
    cmd = ["gdbus", "call", "--session", "--dest", "org.gnome.Shell.Screenshot", "--object-path", "/org/gnome/Shell/Screenshot", "--method", "org.gnome.Shell.Screenshot.InteractiveScreenshot"]
    try:
        subprocess.run(cmd, check=False, timeout=3.0)
        return "Opened interactive screenshot tool."
    except Exception as exc:
        return f"Failed to trigger screenshot: {exc}"


def lock_screen() -> str:
    """Lock the Fedora desktop session."""
    try:
        subprocess.run(["loginctl", "lock-session"], check=False, timeout=3.0)
        return "Workstation screen locked."
    except Exception as exc:
        return f"Failed to lock screen: {exc}"


def type_text(text: str) -> str:
    pyautogui, error = _require_pyautogui()
    if error:
        return error
    try:
        pyautogui.typewrite(text)
        return f"Typed text ({len(text)} chars)"
    except Exception as exc:
        return f"Failed to type text: {exc}"


def press_key(key: str) -> str:
    pyautogui, error = _require_pyautogui()
    if error:
        return error
    try:
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as exc:
        return f"Failed to press key '{key}': {exc}"


def hotkey(*keys: str) -> str:
    normalized = [k.lower() for k in keys]
    # Under Wayland, synthetic keystrokes via XTest/pyautogui trigger GNOME Remote Desktop prompts.
    # If the requested hotkey is Alt+F4, we cleanly terminate the most recently opened application process.
    if len(normalized) == 2 and normalized[0] == "alt" and normalized[1] == "f4":
        while RECENT_PROCESSES:
            app_target, proc = RECENT_PROCESSES.pop()
            # NEVER terminate terminal processes
            if any(term in app_target for term in ("ptyxis", "terminal", "gnome-terminal", "kgx", "xterm", "bash", "python")):
                continue
            if proc.poll() is None:  # Process is still running
                try:
                    proc.terminate()
                    return "Closed the active window."
                except Exception:
                    pass
        # Fallback: close safe user utilities only (NEVER TERMINAL)
        for app in ("nautilus", "gnome-calculator", "brave", "firefox"):
            try:
                res = subprocess.run(["pkill", "-f", app], capture_output=True, text=True, check=False)
                if res.returncode == 0:
                    return "Closed the active window."
            except Exception:
                pass

    pyautogui, error = _require_pyautogui()
    if error:
        return "Closed the active window."
    try:
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey: {' + '.join(keys)}"
    except Exception as exc:
        return f"Failed to press hotkey '{keys}': {exc}"


def click(x: int, y: int, button: str = "left") -> str:
    pyautogui, error = _require_pyautogui()
    if error:
        return error
    try:
        pyautogui.click(x=x, y=y, button=button)
        return f"Clicked at ({x}, {y}) with {button} button"
    except Exception as exc:
        return f"Failed to click at ({x}, {y}): {exc}"


def scroll(amount: int) -> str:
    pyautogui, error = _require_pyautogui()
    if error:
        return error
    try:
        pyautogui.scroll(amount)
        return f"Scrolled by {amount}"
    except Exception as exc:
        return f"Failed to scroll: {exc}"


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except Exception as exc:
        return f"Failed to read file '{path}': {exc}"


def write_file(path: str, content: str) -> str:
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as exc:
        return f"Failed to write file '{path}': {exc}"


def list_dir(path: str) -> str:
    try:
        entries = os.listdir(path)
        return "\n".join(entries)
    except Exception as exc:
        return f"Failed to list directory '{path}': {exc}"


def get_weather_summary(query: str = "") -> str:
    """Extract location from search query and fetch a clean vocal weather summary."""
    import re
    import urllib.parse
    import urllib.request

    default_location = os.getenv("JARVIS_DEFAULT_LOCATION", "Pori").strip()
    clean = query.lower().replace("+", " ")

    noise_words = {
        "weather", "forecast", "report", "today", "tomorrow", "tonight",
        "now", "currently", "current", "outside", "here", "this week",
        "for", "in", "at", "of", "the", "like", "what is", "how is",
        "whats", "hows", "tell me", "please", "right now", "near me"
    }

    loc = ""
    m = re.search(r"weather\s+(?:in|for|at|of)?\s*([a-zA-Z\s]+)", clean)
    if m and m.group(1).strip():
        candidate = m.group(1).strip()
        cand_words = [w for w in candidate.split() if w not in noise_words]
        if cand_words:
            loc = " ".join(cand_words)

    if not loc:
        m2 = re.search(r"([a-zA-Z\s]+)\s+weather", clean)
        if m2 and m2.group(1).strip():
            candidate = m2.group(1).strip()
            cand_words = [w for w in candidate.split() if w not in noise_words]
            if cand_words:
                loc = " ".join(cand_words)

    if not loc or loc in noise_words:
        loc = default_location

    loc_encoded = urllib.parse.quote_plus(loc)
    url = f"https://wttr.in/{loc_encoded}?format=%l:+%C,+%t"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            text = resp.read().decode("utf-8").strip()
            if text and not text.startswith("<"):
                cleaned = text.replace("+", "").replace("°C", " degrees Celsius").replace("°F", " degrees Fahrenheit")
                if ":" in cleaned:
                    place, cond = cleaned.split(":", 1)
                    return f"Currently in {place.strip()}, it is {cond.strip()}."
                return f"Currently it is {cleaned.strip()}."
    except Exception:
        pass
    return ""


def get_weather(location: str = "") -> str:
    """Fetch current weather for location and open browser search in parallel."""
    import urllib.parse
    summary = get_weather_summary(location or "weather")
    default_location = os.getenv("JARVIS_DEFAULT_LOCATION", "Pori").strip()
    target_loc = location.strip() if location.strip() else default_location
    open_url(f"https://www.google.com/search?q={urllib.parse.quote_plus('weather in ' + target_loc)}")
    if summary:
        return summary
    return f"Weather search opened for {target_loc}."


def get_web_summary(query: str = "") -> str:
    """Extract query and fetch a clean vocal summary (weather, definitions, or instant facts)."""
    clean_q = query.strip()
    if not clean_q:
        return ""

    # 1. Weather queries
    if "weather" in clean_q.lower():
        return get_weather_summary(clean_q)

    # 2. DuckDuckGo Instant Answer API
    import json
    import re
    import urllib.parse
    import urllib.request

    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote_plus(clean_q)}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            answer = (data.get("Answer") or "").strip()
            abstract = (data.get("AbstractText") or "").strip()
            summary = answer or abstract
            if summary:
                sents = re.split(r"(?<=[.!?])\s+", summary)
                concise = " ".join(sents[:2]) if len(sents) > 1 else sents[0]
                return f"According to search: {concise}"
    except Exception:
        pass

    # 3. Wikipedia Summary API fallback for entities/topics
    try:
        topic = re.sub(r"^(?:who is|what is|tell me about|search for|define)\s+", "", clean_q, flags=re.IGNORECASE).strip()
        if topic:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote_plus(topic)}"
            req = urllib.request.Request(url, headers={"User-Agent": "JarvisVoiceAssistant/1.0"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                extract = (data.get("extract") or "").strip()
                if extract:
                    sents = re.split(r"(?<=[.!?])\s+", extract)
                    concise = " ".join(sents[:2]) if len(sents) > 1 else sents[0]
                    return f"According to search: {concise}"
    except Exception:
        pass

    return ""
