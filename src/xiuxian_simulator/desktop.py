"""Desktop native application shell for The Eternal Dao (《永恒之道》)."""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import io
import uvicorn

# In pythonw.exe, sys.stdout and sys.stderr are None, which causes uvicorn to fail with:
# AttributeError: 'NoneType' object has no attribute 'isatty'
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

from .engine import GameEngine
from .modern_web import create_modern_app


def find_edge_binary() -> str | None:
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


import socket
import urllib.request


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def find_available_port(start_port: int = 8765, host: str = "127.0.0.1") -> int:
    port = start_port
    while is_port_in_use(port, host):
        port += 1
    return port


def wait_for_server(url: str, timeout: float = 6.0) -> bool:
    deadline = time.time() + timeout
    health_url = url.rstrip("/") + "/api/v1/health"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=0.5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.15)
    return False


def run_desktop_app(
    engine: GameEngine,
    root: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    width: int = 1280,
    height: int = 820,
) -> None:
    """Launch the game as a dedicated, borderless desktop application window."""
    actual_port = find_available_port(port, host)
    app = create_modern_app(engine, root)
    config = uvicorn.Config(
        app,
        host=host,
        port=actual_port,
        log_level="warning",
        log_config=None,
    )
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    url = f"http://{host}:{actual_port}/"
    wait_for_server(url)

    # 1. Try pywebview first if available
    try:
        import webview

        window = webview.create_window(
            title="永恒之道 · 仙家修仙文字模拟器",
            url=url,
            width=width,
            height=height,
            min_size=(960, 600),
            background_color="#faf7f0",
        )
        webview.start()
        return
    except ImportError:
        pass

    # 2. Native Windows Edge App Mode (zero dependencies, standalone window)
    edge_exe = find_edge_binary()
    if edge_exe:
        app_arg = f"--app={url}"
        size_arg = f"--window-size={width},{height}"
        user_data = root / "data" / ".app_profile"
        user_data.mkdir(parents=True, exist_ok=True)
        data_arg = f"--user-data-dir={user_data}"

        proc = subprocess.Popen([edge_exe, app_arg, size_arg, data_arg])
        proc.wait()
    else:
        import webbrowser

        webbrowser.open(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
