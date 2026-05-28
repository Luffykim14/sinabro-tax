@echo off
chcp 65001 >nul
cd /d C:\Users\luffy\tax_auto

echo === .gitignore 생성 ===
(
echo __pycache__/
echo *.pyc
echo *.pyo
echo .env
echo .venv/
echo venv/
echo outputs/
echo uploads/
echo *.log
echo .DS_Store
echo {templates,static,uploads,outputs}/
) > .gitignore

echo === Procfile 생성 ===
echo web: gunicorn app:app > Procfile

echo === runtime.txt 생성 ===
echo python-3.11.9 > runtime.txt

echo === Git 초기화 및 푸시 ===
git init
git branch -M main
git add .
git commit -m "Initial commit for Render deployment"
git remote remove origin 2>nul
git remote add origin https://github.com/Luffykim14/sinabro-tax.git
git push -u origin main

echo.
echo === 완료 ===
pause
