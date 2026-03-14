@echo off
echo ========================================
echo Shree Ganesha Silk System Compiler
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo PyInstaller ready!
echo.

REM Check if all dependencies are installed
echo Checking dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo All dependencies installed!
echo.

echo ========================================
echo Starting compilation...
echo This may take 2-5 minutes...
echo ========================================
echo.

REM Compile the application
REM Compile the application
pyinstaller --onefile --windowed --name "BoutiqueManagerPro" --collect-all customtkinter main.py

if errorlevel 1 (
    echo.
    echo ERROR: Compilation failed!
    echo Please check the errors above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Compilation Successful!
echo ========================================
echo.
echo Your executable is located at:
echo %CD%\dist\BoutiqueManagement.exe
echo.
echo File size: 
dir dist\BoutiqueManagement.exe | find "BoutiqueManagement.exe"
echo.
echo You can now distribute this .exe file!
echo.
echo IMPORTANT NOTES:
echo 1. Copy the .exe to a new folder before running
echo 2. The database will be created in the same folder as the .exe
echo 3. Invoices will be saved in an 'invoices' subfolder
echo.
pause
