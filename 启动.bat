@echo off
chcp 65001 >nul
title 月薪猫桌宠
cd /d "%~dp0"

echo.
echo   🐱 月薪猫 - 启动中...
echo.

REM ═══ 步骤1: 查找可用Python ═══
set "PYTHON="
for %%p in (python3.exe python.exe "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
            "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
            "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
            "%ProgramFiles%\Python313\python.exe"
            D:\python3.11\python.exe D:\Python3.14\python.exe) do (
    if not defined PYTHON (
        "%%~p" --version >nul 2>&1
        if not errorlevel 1 set "PYTHON=%%~p"
    )
)

if not defined PYTHON (
    echo   ❌ 未检测到 Python！
    echo.
    echo   请先安装 Python 3.10 或更高版本：
    echo   👉 https://www.python.org/downloads/
    echo.
    echo   ⚠️ 安装时务必勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo   找到 Python: %PYTHON%

REM ═══ 步骤2: 检查/创建虚拟环境 ═══
set "VENV_PYTHON=venv\Scripts\python.exe"
set "VENV_PYTHONW=venv\Scripts\pythonw.exe"

if exist "%VENV_PYTHONW%" goto run

echo   首次运行，正在创建虚拟环境...
"%PYTHON%" -m venv venv
if errorlevel 1 (
    echo   ❌ 创建虚拟环境失败
    echo   请检查 Python 安装是否完整
    pause
    exit /b 1
)

echo   正在安装依赖...
"%VENV_PYTHON%" -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet 2>nul
"%VENV_PYTHON%" -m pip install apscheduler -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet
if errorlevel 1 (
    echo   ⚠️ 清华镜像失败，尝试官方源...
    "%VENV_PYTHON%" -m pip install apscheduler --quiet
    if errorlevel 1 (
        echo   ❌ 依赖安装失败
        echo   请检查网络连接后重试
        pause
        exit /b 1
    )
)
echo   ✅ 环境准备完成！

REM ═══ 步骤3: 启动 ═══
:run
echo   正在启动月薪猫...
start "" "%VENV_PYTHONW%" "main_tk.py"
if errorlevel 1 (
    REM pythonw 启动失败，尝试用 python
    start "" "%VENV_PYTHON%" "main_tk.py"
)

echo   🐱 猫已启动！查看桌面吧~
timeout /t 2 >nul
exit
