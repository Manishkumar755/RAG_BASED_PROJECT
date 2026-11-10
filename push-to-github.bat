@echo off
setlocal

echo ========================================================
echo Push Innefu Labs RAG Platform to GitHub
echo ========================================================
echo.

set /p REPO_URL="Enter your GitHub repository URL (e.g., https://github.com/Manishkumar755/rag-platform.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No repository URL entered. Exiting.
    pause
    exit /b 1
)

echo.
echo [1/3] Setting remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [2/3] Setting main branch...
git branch -M main

echo [3/3] Pushing code to GitHub...
git push -u origin main

echo.
echo ========================================================
echo Pushed to GitHub successfully!
echo Next steps:
echo 1. Deploy backend on Render (https://render.com)
echo 2. Deploy frontend on Vercel (https://vercel.com)
echo See DEPLOYMENT.md for step-by-step instructions.
echo ========================================================
pause
