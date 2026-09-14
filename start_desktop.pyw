"""Single-click desktop launcher for The Eternal Dao (《永恒之道》)."""
from __future__ import annotations

import io
import os
from pathlib import Path
import subprocess
import sys
import traceback

# In pythonw.exe, sys.stdout and sys.stderr are None, which causes uvicorn to fail with:
# AttributeError: 'NoneType' object has no attribute 'isatty'
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

root = Path(__file__).resolve().parent

# 1. Environment auto-detection and re-execution
venv_pythonw = root / ".venv" / "Scripts" / "pythonw.exe"
venv_python = root / ".venv" / "Scripts" / "python.exe"

# If we are NOT already running under the project's .venv python
current_exe = Path(sys.executable).resolve()
in_venv = False
try:
    if venv_python.is_file() and current_exe.samefile(venv_python):
        in_venv = True
    elif venv_pythonw.is_file() and current_exe.samefile(venv_pythonw):
        in_venv = True
except Exception:
    pass

if not in_venv:
    target_py = venv_pythonw if venv_pythonw.is_file() else venv_python
    if target_py.is_file():
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
        subprocess.Popen(
            [str(target_py), str(Path(__file__).resolve())] + sys.argv[1:],
            cwd=str(root),
            creationflags=creationflags,
        )
        sys.exit(0)

# 2. Main launch with GUI error fallback
src_dir = root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


def show_gui_error(title: str, message: str) -> None:
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)  # MB_ICONERROR
    except Exception:
        print(f"[{title}] {message}", file=sys.stderr)


if __name__ == "__main__":
    try:
        from xiuxian_simulator.cli import build_engine
        from xiuxian_simulator.desktop import run_desktop_app

        engine = build_engine(root)
        run_desktop_app(engine, root)
    except Exception as exc:
        err_log = root / "data" / "launcher_error.log"
        try:
            err_log.parent.mkdir(parents=True, exist_ok=True)
            with open(err_log, "a", encoding="utf-8") as f:
                f.write(f"\n--- 启动异常: {exc} ---\n")
                traceback.print_exc(file=f)
        except Exception:
            pass
        show_gui_error(
            "永恒之道 · 启动异常",
            f"游戏启动时发生错误：\n{exc}\n\n详细错误日志已记录于：\ndata/launcher_error.log\n\n您可以尝试双击运行根目录下的【启动游戏.bat】。"
        )
        sys.exit(1)
