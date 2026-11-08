"""Launcher for the standalone Jarvis HUD desktop window with single-instance enforcement."""

from __future__ import annotations

import atexit
import os
import shutil
import subprocess
import sys
import time
from typing import Optional


def _has_pywebview_backend() -> bool:
    """Check if Python GTK or Qt bindings exist for native pywebview rendering."""
    try:
        import gi  # noqa: F401
        return True
    except Exception:
        pass
    try:
        import PyQt6  # noqa: F401
        return True
    except Exception:
        pass
    try:
        import PySide6  # noqa: F401
        return True
    except Exception:
        pass
    return False


def kill_existing_hud(url: str = "http://127.0.0.1:5055") -> None:
    """Ensure only one instance of the HUD is alive by terminating lingering instances."""
    try:
        # Bracket expression avoids matching grep/pkill command itself
        clean_url = url.replace("http://", "").replace("https://", "")
        pattern = f"[{clean_url[0]}]{clean_url[1:]}"
        subprocess.run(
            ["pkill", "-f", pattern],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


class HUDLauncher:
    """Manages the lifecycle of the standalone HUD window."""

    def __init__(self, url: str = "http://127.0.0.1:5055"):
        self.url = url
        self._proc: Optional[subprocess.Popen] = None
        atexit.register(self.close)

    def launch(self) -> None:
        """Launch the HUD window, ensuring exactly one instance is active."""
        # 1. Enforce strict single-instance: kill any lingering previous window
        kill_existing_hud(self.url)
        time.sleep(0.15)

        # 2. Check if native pywebview backend is available (without triggering error traces)
        if _has_pywebview_backend():
            try:
                import webview  # type: ignore
                import multiprocessing

                def _webview_worker(u: str):
                    try:
                        webview.create_window(
                            title="J.A.R.V.I.S. Core Interface",
                            url=u,
                            width=960,
                            height=720,
                            resizable=True,
                            background_color="#060a14",
                        )
                        webview.start(debug=False)
                    except Exception:
                        pass

                p = multiprocessing.Process(target=_webview_worker, args=(self.url,), daemon=True)
                p.start()
                print("[HUD] Launched native WebKit HUD window.")
                return
            except Exception:
                pass

        # 3. Dedicated standalone desktop app window (Brave / Chrome / system browser)
        # Check if Brave Flatpak exists
        if shutil.which("flatpak"):
            try:
                check = subprocess.run(
                    ["flatpak", "info", "com.brave.Browser"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if check.returncode == 0:
                    self._proc = subprocess.Popen(
                        ["flatpak", "run", "com.brave.Browser", f"--app={self.url}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    print(f"[HUD] Launched standalone Brave app window: {self.url}")
                    return
            except Exception:
                pass

        # Direct desktop binaries with --app support
        for binary in ("brave", "brave-browser", "google-chrome", "chromium"):
            if shutil.which(binary):
                try:
                    self._proc = subprocess.Popen(
                        [binary, f"--app={self.url}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    print(f"[HUD] Launched {binary} app window: {self.url}")
                    return
                except Exception:
                    pass

        # Fallback: standard desktop handler
        try:
            self._proc = subprocess.Popen(
                ["xdg-open", self.url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"[HUD] Opened interface via xdg-open: {self.url}")
        except Exception as exc:
            print(f"[HUD] Failed to launch window: {exc}")

    def close(self) -> None:
        """Cleanly terminate the active HUD window upon shutdown."""
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=1.0)
            except Exception:
                pass
            self._proc = None
        kill_existing_hud(self.url)
