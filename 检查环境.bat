@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "XIU_PYTHON="
if exist ".venv\Scripts\python.exe" set "XIU_PYTHON=.venv\Scripts\python.exe"
if not defined XIU_PYTHON where py >nul 2>nul && set "XIU_PYTHON=py -3"
if not defined XIU_PYTHON where python >nul 2>nul && set "XIU_PYTHON=python"
if not defined XIU_PYTHON (
  echo 未找到 Python 3.11 或更高版本。
  pause
  exit /b 1
)
%XIU_PYTHON% main.py --check
pause
