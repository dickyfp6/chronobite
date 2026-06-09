@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo SYNC UPDATES FROM FRIEND (UPSTREAM -^> ORIGIN)
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

echo 1. Fetching updates from friend's repo (upstream)...
git fetch upstream
if %errorlevel% neq 0 (
    echo [ERROR] Failed to fetch from upstream.
    pause
    exit /b 1
)

echo.
echo 2. Merging updates into your local branch (!BRANCH!)...
git merge upstream/!BRANCH! -m "Merge updates from upstream/!BRANCH!"
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Merge conflict detected or merge failed.
    echo Please resolve conflicts manually (e.g. in VS Code),
    echo commit the resolved files, and then push using git_push_changes.bat.
    pause
    exit /b 1
)

echo.
echo 3. Pushing merged updates to your personal repo (origin)...
git push origin !BRANCH!
if %errorlevel% neq 0 (
    echo [ERROR] Failed to push to origin.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo SUCCESS: Code is fully synced and deployed to your server!
echo ========================================================
pause
