@echo off
chcp 65001 > nul
title 시나브로마케팅 세금계산서 자동입력

set ANTHROPIC_API_KEY=여기에키입력

cd /d C:\Users\luffy\tax_auto

echo ================================================
echo   시나브로마케팅 세금계산서 자동 입력 프로그램
echo ================================================
echo.
echo  브라우저에서 http://localhost:5000 을 여세요!
echo  종료하려면 이 창에서 Ctrl+C 를 누르세요.
echo.

python app.py
pause
