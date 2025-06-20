@echo off
echo Building MeshagePR executable...
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
echo Building with PyInstaller...
pyinstaller MeshagePR.spec

echo.
echo Build complete! Check the 'dist' folder for your executable.
echo.
pause 