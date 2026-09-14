@echo off
chcp 65001 >nul
title 永恒之道 · 正在启动...
set ROOT=%~dp0
cd /d "%ROOT%"

if exist "%ROOT%\.venv\Scripts\pythonw.exe" (
    start "" "%ROOT%\.venv\Scripts\pythonw.exe" "%ROOT%\start_desktop.pyw"
    exit /b 0
)

if exist "%ROOT%\.venv\Scripts\python.exe" (
    "%ROOT%\.venv\Scripts\python.exe" "%ROOT%\main.py" --desktop
    exit /b 0
)

echo [错误] 未能在当前目录找到 .venv 运行环境。
echo 请确保项目依赖已就绪。
pause
