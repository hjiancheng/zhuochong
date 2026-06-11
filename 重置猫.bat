@echo off
chcp 65001 >nul
echo ===============================
echo   🧪 月薪猫 - 开发者重置工具
echo ===============================
echo.
echo   即将清除桌宠的所有数据！
echo   包括：档案、记忆、状态...
echo.
echo   ⚠️  此操作不可恢复！
echo.
set /p confirm="确认重置？(输入 YES 继续): "
if "%confirm%"=="YES" (
    python reset.py
    echo.
    echo 🐱 猫已回归初始状态。下次启动将重新创猫。
) else (
    echo ❌ 已取消。
)
pause
