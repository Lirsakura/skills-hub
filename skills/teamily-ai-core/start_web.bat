@echo off
echo ======================================
echo   Teamily AI Core Web 控制台
echo ======================================
echo.

cd /d "%~dp0"

REM 检查并安装依赖
pip install flask >nul 2>&1

echo 🌐 启动 Web 控制台...
echo 📍 访问地址: http://localhost:5000
echo.
echo 按 Ctrl+C 停止服务
echo.

python web_dashboard.py

pause
