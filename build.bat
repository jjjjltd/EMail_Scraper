@echo off
echo ========================================
echo Email Scraper - Building Executable
echo ========================================
echo.

REM Kill any running instances
echo Checking for running Email Scraper processes...
taskkill /F /IM EmailScraper.exe 2>nul
timeout /t 2 >nul

REM Clean previous build
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist EmailScraper.spec del EmailScraper.spec

echo.
echo Building standalone executable...
echo This may take a few minutes...
echo.

REM Build with PyInstaller
pyinstaller --name=EmailScraper ^
    --onefile ^
    --windowed ^
    --add-data="templates;templates" ^
    --icon=NONE ^
    --clean ^
    app.py

echo.
if exist dist\EmailScraper.exe (
    echo ========================================
    echo SUCCESS! Executable built successfully
    echo ========================================
    echo.
    echo Location: dist\EmailScraper.exe
    echo Size: 
    dir dist\EmailScraper.exe | find "EmailScraper.exe"
    echo.
    echo You can now distribute dist\EmailScraper.exe
    echo.
) else (
    echo ========================================
    echo ERROR: Build failed
    echo ========================================
    echo.
    echo Please check the output above for errors
    echo.
)

echo.
echo Cleaning up build artifacts...
if exist build rmdir /s /q build
if exist EmailScraper.spec del EmailScraper.spec

pause
