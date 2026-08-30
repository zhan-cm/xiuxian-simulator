@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "XIU_PYTHON=.venv\Scripts\python.exe"
if not exist "%XIU_PYTHON%" (
  echo 正在创建新版所需的 Python 环境……
  py -3 -m venv .venv
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
  echo 正在构建《问道长生》V0.42 新版界面……
  pushd frontend
  call npm run build
  if errorlevel 1 (
    popd
    goto failed
  )
  popd
)

echo 正在打开《问道长生》V0.42 新版界面……
"%XIU_PYTHON%" main.py --modern-web
set "XIU_EXIT=%errorlevel%"
if not "%XIU_EXIT%"=="0" goto failed
exit /b 0

:failed
echo.
echo 新版界面未能启动，请保留此窗口中的错误信息。
echo 旧版仍可通过“启动网页版.bat”正常使用。
pause
exit /b 1
