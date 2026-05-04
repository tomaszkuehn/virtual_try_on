@echo off
REM Startup script for Virtual Try-On Web Application

echo Starting Virtual Try-On Web Application...
echo Installing dependencies...
pip install -r requirements.txt

echo Starting web server...
echo Access the application at: http://localhost:5000
echo To access from Android device on same network: http://[YOUR_IP]:5000
echo.
web_app.py