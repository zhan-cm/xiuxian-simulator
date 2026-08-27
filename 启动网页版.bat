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
echo 正在检查运行环境……
"%XIU_PYTHON%" %XIU_PYTHON_ARGS% main.py --check
if errorlevel 1 (
  echo.
  echo 环境检查未通过，游戏尚未启动。
  pause
  exit /b 1
)

echo.
echo 正在打开《问道长生》网页版……
"%XIU_PYTHON%" %XIU_PYTHON_ARGS% main.py --web
set "XIU_EXIT=%errorlevel%"
if not "%XIU_EXIT%"=="0" (
  echo.
  echo 游戏服务异常退出，错误代码：%XIU_EXIT%
  pause
)
exit /b %XIU_EXIT%
