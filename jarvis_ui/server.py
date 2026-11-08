"""Lightweight local web server serving the Jarvis Holographic HUD via SSE."""

from __future__ import annotations

import json
import logging
import os
import queue
import threading
from pathlib import Path
from flask import Flask, Response, jsonify, send_from_directory

from .state_bridge import ui_bridge

# Disable Flask / Werkzeug access request spam in terminal
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")


@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


@app.route("/api/status")
def status():
    return jsonify({
        "status": "online",
        "state": ui_bridge._current_state,
        "engine": ui_bridge._current_engine,
        "action": ui_bridge._current_action,
        "user_text": ui_bridge._user_text,
        "jarvis_text": ui_bridge._jarvis_text,
    })


@app.route("/api/stream")
def stream():
    """Server-Sent Events endpoint streaming real-time state changes to HUD."""
    def event_generator():
        q = ui_bridge.subscribe()
        try:
            while True:
                try:
                    event = q.get(timeout=20.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except queue.Empty:
                    # Keep-alive heartbeat ping
                    yield ": ping\n\n"
        except GeneratorExit:
            pass
        finally:
            ui_bridge.unsubscribe(q)

    return Response(
        event_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


class HUDServer:
    """Manages the background Flask server thread."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5055):
        self.host = host
        self.port = port
        self.server_thread: threading.Thread | None = None
        self._server = None

    def start(self) -> str:
        """Start the server on a daemon thread and return URL."""
        from werkzeug.serving import make_server

        self._server = make_server(self.host, self.port, app, threaded=True)
        self.server_thread = threading.Thread(
            target=self._server.serve_forever,
            name="JarvisHUDServerThread",
            daemon=True,
        )
        self.server_thread.start()
        ui_bridge.activate()
        url = f"http://{self.host}:{self.port}"
        print(f"[HUD] Holographic Interface Server running at: {url}")
        return url

    def stop(self) -> None:
        if self._server:
            try:
                self._server.shutdown()
            except Exception:
                pass
            self._server = None
