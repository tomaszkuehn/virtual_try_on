@echo off
REM Setup script for Virtual Try-On Application (Windows)

echo Setting up Virtual Try-On Application...

REM Check if Python is available
where python3 >nul 2>&1
if errorlevel 1 (
    where python >nul 2>&1
    if errorlevel 1 (
        echo Error: Python is not installed or not in PATH
        exit /b 1
    )
)

echo Python version:
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install in development mode
echo Installing package in development mode...
pip install -e .

echo.
echo Setup complete!
echo.
echo To use the application:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run the application: python -m src.tryon_app --help
echo.
echo For Google Cloud integration:
echo - Set up a Google Cloud project
echo - Enable Vertex AI API
echo - Authenticate with Google Cloud
echo - Provide your project ID when running the application