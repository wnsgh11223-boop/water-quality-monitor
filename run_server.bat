@echo off
chcp 65001 > nul
echo ================================================
echo   날씨알림봇 - 대시보드 서버 시작
echo ================================================
echo.
echo 브라우저에서 http://127.0.0.1:8500 으로 접속하세요.
echo 종료하려면 이 창을 닫거나 Ctrl+C 를 누르세요.
echo.
cd /d "%~dp0"
python dashboard_server.py
pause
