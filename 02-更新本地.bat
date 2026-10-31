@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 从云端更新到本地

git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
    echo [错误] 当前文件夹不是 Git 仓库
    pause
    exit /b 1
)

git pull
if errorlevel 1 (
    echo.
    echo [失败] 更新失败，请看上面的报错
) else (
    echo.
    echo [完成] 本地已是最新
)
pause