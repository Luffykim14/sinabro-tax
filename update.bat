@echo off
chcp 65001 >nul
cd /d C:\Users\luffy\tax_auto

REM 국세청 양식 자동 등록 (다운로드 폴더에서 복사)
if exist "C:\Users\luffy\Downloads\세금계산서등록양식(일반).xlsx" (
    echo === 양식 파일 복사 ===
    copy /Y "C:\Users\luffy\Downloads\세금계산서등록양식(일반).xlsx" "template.xlsx"
)

echo === 변경사항 확인 ===
git status
echo.
echo === 커밋 및 푸시 ===
git add .
git commit -m "Fix httpx compat and embed default tax template"
git push origin main
echo.
echo === 완료! Render 자동 재배포 시작됨 ===
pause
