@echo off
chcp 65001 >nul
title Climate Poll Bot - Telegram Bot

cd /d "%~dp0bot"

echo.
echo Запуск бота...
echo Для остановки нажмите Ctrl+C
echo ========================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo Произошла ошибка при запуске бота!
    pause
)