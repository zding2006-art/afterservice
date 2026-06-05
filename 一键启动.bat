@echo off
chcp 65001 >nul
title 售后数据分析系统 — 一键启动
color 0A
cd /d "%~dp0"

echo.
echo   ╔════════════════════════════════════════╗
echo   ║   售后数据分析后台 v1.0                ║
echo   ║   株式会社 Water X Technologies        ║
echo   ╚════════════════════════════════════════╝
echo.

:: ── 检查 Python ──
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [✓] Python %%v 已就绪

:: ── 检查依赖 ──
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 首次运行，正在安装依赖包...
    pip install flask flask-cors pandas openpyxl numpy -i https://pypi.tuna.tsinghua.edu.cn/simple --quiet
    if %errorlevel% neq 0 (
        echo [!] 清华源失败，尝试默认源...
        pip install flask flask-cors pandas openpyxl numpy --quiet
    )
)
echo [✓] 依赖已就绪

:: ── 确保子目录 ──
if not exist "backend"  mkdir "backend"
if not exist "uploads"  mkdir "uploads"

:: ── 关闭旧进程 ──
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5859.*LISTENING"') do (
    echo [✓] 关闭旧进程 PID=%%a
    taskkill /F /PID %%a >nul 2>&1
)

:: ── 清理代理环境变量（防止影响本地访问）──
set ALL_PROXY=
set HTTP_PROXY=
set HTTPS_PROXY=

:: ── 启动后端（最小化窗口）──
echo.
echo 正在启动服务...
start "售后数据分析后台" /min python backend\app.py

:: ── 等待端口就绪 ──
echo 等待服务就绪...
set RETRY=0
:wait
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":5859.*LISTENING" >nul
if %errorlevel% equ 0 goto ready
set /a RETRY+=1
if %RETRY% lss 15 goto wait
echo [警告] 服务启动超时，请检查 backend\app.py 是否正常
pause
exit /b 1

:ready
echo [✓] 服务就绪

:: ── 打开浏览器 ──
start "" http://localhost:5859

echo.
echo ════════════════════════════════════════════
echo   服务已启动！浏览器已打开：
echo   http://localhost:5859
echo.
echo   提示：
echo   · 最小化的 Python 窗口是后台服务
echo   · 关闭 Python 窗口 = 停止服务
echo   · 本窗口可安全关闭，不影响服务
echo ════════════════════════════════════════════
echo.

:: 3 秒后自动关闭本窗口
timeout /t 3 /nobreak >nul
exit
