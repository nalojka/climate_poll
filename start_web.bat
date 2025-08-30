@echo off
chcp 65001 >nul
title Climate Poll Bot - Web Server

echo ========================================
echo    Запуск веб-сервера статистики
echo ========================================
echo.

cd /d "%~dp0web"


echo.
echo Запуск веб-сервера...
echo Сервер будет доступен по адресу: http://localhost:5000
echo Для остановки нажмите Ctrl+C
echo ========================================
echo.

python app.py

if errorlevel 1 (
    echo.
    echo Произошла ошибка при запуске веб-сервера!
    pause
)