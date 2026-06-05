@echo off
chcp 65001 >nul
title 售后数据分析后台

echo ========================================
echo   售后数据分析后台管理系统
echo ========================================
echo.

:: 检测 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [2/3] 正在安装依赖包...
    pip install -r backend\requirements.txt --quiet
) else (
    echo [2/3] 依赖已就绪，跳过安装
)

echo [3/3] 启动服务...
echo.
echo 服务地址：http://localhost:5859
echo 按 Ctrl+C 停止服务
echo.

cd backend
python app.py

pause
