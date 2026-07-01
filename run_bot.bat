@echo off
chcp 65001 > nul
echo ================================================
echo   날씨알림봇 - 텔레그램 봇 시작
echo ================================================
echo.
echo 종료하려면 이 창을 닫거나 Ctrl+C 를 누르세요.
echo.
cd /d "%~dp0"
python bot.py
pause
