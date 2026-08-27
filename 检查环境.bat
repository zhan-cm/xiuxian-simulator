@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  set "XIU_PYTHON=.venv\Scripts\python.exe"
  set "XIU_PYTHON_ARGS="
  goto run_checks
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info[:2] in [(3, n) for n in range(11, 100)] else 1)" >nul 2>nul
  if not errorlevel 1 (
    set "XIU_PYTHON=py"
    set "XIU_PYTHON_ARGS=-3"
    goto run_checks
  )
)
where python >nul 2>nul
if not errorlevel 1 (
  python -c "import sys; raise SystemExit(0 if sys.version_info[:2] in [(3, n) for n in range(11, 100)] else 1)" >nul 2>nul
  if not errorlevel 1 (
    set "XIU_PYTHON=python"
    set "XIU_PYTHON_ARGS="
    goto run_checks
  )
)

echo 未找到 Python 3.11 或更高版本。
echo 请先安装 Python，然后重新双击本文件。
pause
exit /b 1

:run_checks
"%XIU_PYTHON%" %XIU_PYTHON_ARGS% main.py --check
set "XIU_EXIT=%errorlevel%"
echo.
if "%XIU_EXIT%"=="0" (
  echo 检查完成。按任意键关闭此窗口。
) else (
  echo 检查未通过。请保留此窗口中的错误信息。
)
pause
exit /b %XIU_EXIT%
