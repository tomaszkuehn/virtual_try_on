# Virtual Try-On Web Application

This is a web-based version of the Virtual Try-On application that provides a user-friendly interface accessible from any web browser, including Android devices.

## Features

- Upload person and clothing photos through a web interface
- View the generated try-on result in real-time
- Download the result image
- Responsive design that works on mobile devices
- Reuses the existing Python virtual try-on logic

## How It Works

1. User visits the web application in their browser
2. Uploads a person photo and a clothing photo
3. The Flask backend processes the images using the existing `tryon_app.py` logic
4. Returns the generated try-on image for display and download

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. Navigate to the web directory:
   ```bash
   cd /d/kody/AI/przymiarki/virtual_try_on/web
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python web_app.py
   ```

4. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

### Accessing from Android Devices

To access the application from an Android device on the same network:

1. Make sure your computer and Android device are connected to the same Wi-Fi network
2. Find your computer's IP address (run `ipconfig` on Windows or `ifconfig` on Mac/Linux)
3. On your Android device, open a browser and go to:
   ```
   http://[YOUR_COMPUTER_IP]:5000
   ```
   For example: `http://192.168.1.100:5000`

## How to Use

1. Click "Choose File" under "Person Photo" and select a photo of a person
2. Click "Choose File" under "Clothing Photo" and select a photo of clothing
3. Click the "Generate Try-On" button
4. Wait for the processing to complete (usually a few seconds)
5. View the result and click "Download Result" to save the image

## Notes

- This version runs in **demo mode** by default, which creates a composite image for demonstration purposes
- For actual AI-powered try-on using Alibaba Cloud's Qwen models, you would need to:
  1. Set up an Alibaba Cloud account
  2. Enable the DashScope service
  3. Obtain an API key
  4. Modify the web app to accept and use the API key
- The maximum file size for uploads is 16MB
- Supported image formats: PNG, JPG, JPEG, GIF, BMP

## Customization

To customize the application:

- Modify `web_app.py` to change the Flask endpoints or add features
- Update the HTML/CSS/JavaScript in the `index()` function to change the interface
- Adjust image processing parameters in the existing `tryon_app.py` if needed

## Troubleshooting

If you encounter issues:

1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Check that port 5000 is not already in use by another application
3. Verify that you have write permissions to the temporary directory
4. Check the console output for any error messages when running `python web_app.py`