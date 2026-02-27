@echo off
echo ======================================
echo   Teamily AI Core 启动
echo ======================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装
    pause
    exit /b 1
)

REM 检查配置文件
if not exist config.json (
    echo 📝 创建配置文件...
    copy config.json.example config.json
    echo ⚠️ 请编辑 config.json 填入 API Key
    pause
    exit /b 1
)

echo 🤖 启动 Teamily AI Core 服务...
echo.
python service.py

pause
