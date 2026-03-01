@echo off
echo ======================================
echo  Shree Ganesha SilkManagement System Builder
echo  Building executable with PyInstaller
echo ======================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

echo.
echo Building executable...
echo.

REM Build with PyInstaller
python -m PyInstaller ^
    --name="BoutiqueManagement" ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --add-data="config.py;." ^
    --hidden-import=PIL._tkinter_finder ^
    --collect-all customtkinter ^
    --collect-all matplotlib ^
    main.py

echo.
echo ======================================
echo Build complete!
echo Executable location: dist\BoutiqueManagement.exe
echo ======================================
echo.
echo Note: The executable will be approximately 150-200MB due to matplotlib.
echo.
pause
