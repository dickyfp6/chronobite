@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo PUSH YOUR CHANGES TO BOTH REPOS (ORIGIN ^& UPSTREAM)
echo ========================================================
echo.

:: Get current branch name dynamically
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
if "!BRANCH!"=="" (
    echo [ERROR] Could not detect current git branch. Make sure git is initialized.
    pause
    exit /b 1
)
echo Active branch: !BRANCH!
echo.

:: Prompt for commit message
set /p commit_msg="Enter description of your changes: "
if "!commit_msg!"=="" (
    set commit_msg=Update code
)

echo.
echo 1. Saving changes locally (Git commit)...
git add .
git commit -m "!commit_msg!"
echo.

echo 2. Pushing to your personal repo (origin - updates Vercel/Render)...
git push origin !BRANCH!
if %errorlevel% neq 0 (
    echo [ERROR] Failed to push to origin.
    pause
    exit /b 1
)

echo.
echo 3. Pushing to your friend's repo (upstream - shares code with friend)...
git push upstream !BRANCH!
if %errorlevel% neq 0 (
    echo [ERROR] Failed to push to upstream.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo SUCCESS: Changes saved and pushed to both repositories!
echo ========================================================
pause
