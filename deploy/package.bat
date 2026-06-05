@echo off
REM ====================================================
REM 售后数据分析系统 — 部署包打包脚本
REM 打包 deploy/ 文件夹，方便发给日本朋友
REM ====================================================
echo ============================================
echo   Water X Technologies
echo   售后数据分析系统 — 部署包打包
echo ============================================
echo.

set "VERSION=V1.1"

if exist deploy.zip del deploy.zip

echo → 正在打包 deploy/ 文件夹...
powershell Compress-Archive -Path deploy\* -DestinationPath shouhou_analyzer_%VERSION%.zip -Force

if %ERRORLEVEL% EQU 0 (
    echo ✅ 打包成功！
    echo    文件: shouhou_analyzer_%VERSION%.zip
    echo    大小: 
    powershell (Get-Item shouhou_analyzer_%VERSION%.zip).Length / 1MB | ForEach-Object { $_.ToString("F2") + " MB" }
    echo.
    echo 📤 你可以将这个 ZIP 文件发给日本朋友了！
    echo 📖 解压后请阅读 README_JP.md
) else (
    echo ❌ 打包失败，请重试
)

pause
