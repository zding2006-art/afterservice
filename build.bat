@echo off
chcp 65001 >nul
title 构建售后分析系统 - PyInstaller 打包

echo ========================================
echo   售后分析系统 - PyInstaller 打包构建
echo ========================================
echo.

:: 检测 Python 和 PyInstaller
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/4] 安装 PyInstaller...
    pip install pyinstaller --quiet
)

:: 确保依赖
echo [1/4] 确认依赖...
pip install flask flask-cors pandas openpyxl numpy --quiet

echo [2/4] 清理旧构建...
if exist "dist\shouhou_analyzer" rmdir /S /Q "dist\shouhou_analyzer"
if exist "build" rmdir /S /Q "build"
if exist "shouhou_analyzer.spec" del /Q "shouhou_analyzer.spec"

echo [3/4] PyInstaller 打包（onedir 模式，约需 1-2 分钟）...
python -m PyInstaller ^
    --onedir ^
    --name "shouhou_analyzer" ^
    --noconsole ^
    --hidden-import flask ^
    --hidden-import flask_cors ^
    --hidden-import openpyxl ^
    --hidden-import pandas ^
    --hidden-import numpy ^
    --hidden-import json ^
    --hidden-import sqlite3 ^
    --hidden-import unicodedata ^
    --exclude-module matplotlib ^
    --exclude-module scipy ^
    --collect-all openpyxl ^
    backend\app.py

if %errorlevel% neq 0 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo [4/4] 组装发布目录...
:: 创建必要子目录
if not exist "dist\shouhou_analyzer\frontend" mkdir "dist\shouhou_analyzer\frontend"
if not exist "dist\shouhou_analyzer\backend" mkdir "dist\shouhou_analyzer\backend"
if not exist "dist\shouhou_analyzer\uploads" mkdir "dist\shouhou_analyzer\uploads"

:: 复制前端文件
copy /Y "frontend\index.html" "dist\shouhou_analyzer\frontend\" >nul
copy /Y "frontend\logo.png" "dist\shouhou_analyzer\frontend\" >nul 2>nul

:: 复制使用指南
copy /Y "使用指南.md" "dist\shouhou_analyzer\" >nul

:: 创建启动脚本
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo title 售后数据分析后台
    echo.
    echo echo ============================================
    echo echo   售后数据分析后台 v1.0
    echo echo   株式会社 Water X Technologies
    echo echo ============================================
    echo echo.
    echo echo 正在启动服务...
    echo echo.
    echo cd /d "%%~dp0"
    echo if not exist "backend" mkdir "backend"
    echo if not exist "uploads" mkdir "uploads"
    echo start http://localhost:5859
    echo shouhou_analyzer.exe
    echo pause
) > "dist\shouhou_analyzer\启动.bat"

:: 清理构建中间文件
rmdir /S /Q "build" 2>nul
del /Q "shouhou_analyzer.spec" 2>nul

echo.
echo ========================================
echo   构建完成！
echo.
echo   发布目录：dist\shouhou_analyzer\
echo.
echo   使用方法：
echo     1. 将 shouhou_analyzer 文件夹复制到任意电脑
echo     2. 双击 "启动.bat"
echo     3. 浏览器自动打开 http://localhost:5859
echo.
echo   无需安装 Python 或其他依赖！
echo ========================================
echo.
pause
