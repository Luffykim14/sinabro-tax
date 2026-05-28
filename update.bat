@echo off
chcp 65001 >nul
cd /d C:\Users\luffy\tax_auto
echo === 변경사항 확인 ===
git status
echo.
echo === 커밋 및 푸시 ===
git add .
git commit -m "Add login authentication and login.html"
git push origin main
echo.
echo === 완료! Render 자동 재배포 시작됨 ===
pause
