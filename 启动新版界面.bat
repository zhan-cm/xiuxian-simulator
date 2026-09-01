@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

set "XIU_PYTHON=.venv\Scripts\python.exe"
set "XIU_CHECK_LOG=data\logs\最近一次环境检查.txt"
if exist "%XIU_PYTHON%" (
  "%XIU_PYTHON%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
  if errorlevel 1 goto incompatible_environment
)
if not exist "%XIU_PYTHON%" (
  echo 正在创建新版所需的 Python 环境……
  set "XIU_BOOTSTRAP="
  set "XIU_BOOTSTRAP_ARGS="
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 (
      set "XIU_BOOTSTRAP=py"
      set "XIU_BOOTSTRAP_ARGS=-3"
    )
  )
  if not defined XIU_BOOTSTRAP (
    where python >nul 2>nul
    if not errorlevel 1 (
      python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
      if not errorlevel 1 set "XIU_BOOTSTRAP=python"
    )
  )
  if not defined XIU_BOOTSTRAP goto missing_python
  "!XIU_BOOTSTRAP!" !XIU_BOOTSTRAP_ARGS! -m venv .venv
  if errorlevel 1 goto failed
)

"%XIU_PYTHON%" -c "import fastapi, uvicorn" >nul 2>nul
if errorlevel 1 (
  echo 正在安装新版本地接口组件……
  "%XIU_PYTHON%" -m pip install -e .
  if errorlevel 1 goto failed
)

if not exist "frontend\dist\index.html" (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo 未找到预构建界面或 Node.js。开发构建需要 Node.js 20.19 或更高版本。
    goto failed
  )
  if not exist "frontend\node_modules\vite\package.json" (
    echo 正在安装新版界面组件，首次运行需要一点时间……
    pushd frontend
    call npm install
    if errorlevel 1 (
      popd
      goto failed
    )
    popd
  )
  echo 正在构建《问道长生》V0.61 游戏界面……
  pushd frontend
  call npm run build
  if errorlevel 1 (
    popd
    goto failed
  )
  popd
)

if not exist "data\logs" mkdir "data\logs"
"%XIU_PYTHON%" main.py --check > "%XIU_CHECK_LOG%" 2>&1
if errorlevel 1 (
  type "%XIU_CHECK_LOG%"
  goto failed
)
echo 启动自检通过，报告已保存到“%XIU_CHECK_LOG%”。
echo 正在打开《问道长生》V0.61 游戏界面……
"%XIU_PYTHON%" main.py --modern-web
set "XIU_EXIT=%errorlevel%"
if not "%XIU_EXIT%"=="0" goto failed
exit /b 0

:incompatible_environment
if not exist "data\logs" mkdir "data\logs"
> "%XIU_CHECK_LOG%" echo [失败] 现有 .venv 已损坏或 Python 版本低于 3.11。
>> "%XIU_CHECK_LOG%" echo 请关闭游戏，将项目中的 .venv 文件夹重命名后再次双击启动器。
type "%XIU_CHECK_LOG%"
echo.
echo 环境检查报告位于“%XIU_CHECK_LOG%”。
pause
exit /b 1

:missing_python
echo.
echo 未找到 Python 3.11 或更高版本。
echo 请先安装 Python，然后重新双击本文件。
pause
exit /b 1

:failed
echo.
echo 新版界面未能启动，请保留此窗口中的错误信息。
if exist "%XIU_CHECK_LOG%" echo 环境检查报告位于“%XIU_CHECK_LOG%”。
echo 请先双击“检查环境.bat”，根据报告修复后再试。
pause
exit /b 1
