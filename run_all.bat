@echo off
chcp 65001 > nul
echo ================================================
echo   날씨알림봇 - 봇 + 대시보드 동시 시작
echo ================================================
echo.
echo 대시보드: http://127.0.0.1:8500
echo 봇과 서버가 각각 별도 창에서 실행됩니다.
echo.
cd /d "%~dp0"
start "텔레그램 봇" cmd /k "chcp 65001 & python bot.py"
timeout /t 2 > nul
start "대시보드 서버" cmd /k "chcp 65001 & python dashboard_server.py"
timeout /t 3 > nul
start "" "http://127.0.0.1:8500"
echo 실행 완료! 브라우저가 자동으로 열립니다.
pause
