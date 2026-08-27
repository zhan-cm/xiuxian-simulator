@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo 未找到项目虚拟环境，请先按 README 完成 Python 环境准备。
  pause
  exit /b 1
)
".venv\Scripts\python.exe" main.py --web
if errorlevel 1 pause
