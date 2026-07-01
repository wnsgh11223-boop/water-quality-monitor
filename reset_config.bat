@echo off
chcp 65001 > nul
echo 설정을 초기화합니다...
cd /d "%~dp0"
if exist .env del .env
echo 완료! run_all.bat 를 실행하면 설정을 다시 입력할 수 있습니다.
pause
