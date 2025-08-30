@echo off

start "Climate Poll Bot" cmd /k "start_bot.bat"
timeout /t 2 /nobreak >nul

start "Climate Poll Web" cmd /k "start_web.bat"
timeout /t 2 /nobreak >nul
