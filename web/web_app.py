"""
Web version of the Virtual Try-On Application
Provides a web interface for the virtual try-on functionality
"""

import os
import io
import base64
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import tempfile
import traceback

# Import the existing virtual try-on functionality
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tryon_app import VirtualTryOn

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main page"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Virtual Try-On Web App</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 2rem 1rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .header h1 {
                margin: 0;
                font-size: 2.5rem;
                font-weight: 300;
            }
            .header p {
                margin: 0.5rem 0 0;
                font-size: 1.1rem;
                opacity: 0.9;
            }
            .content {
                flex: 1;
                max-width: 900px;
                margin: 0 auto;
                padding: 2rem;
                width: 100%;
                box-sizing: border-box;
            }
            .upload-section {
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                margin-bottom: 2rem;
                overflow: hidden;
            }
            .upload-header {
                background: #f8f9fa;
                padding: 1.5rem;
                border-bottom: 1px solid #eee;
            }
            .upload-header h2 {
                margin: 0 0 0.5rem 0;
                color: #333;
                font-size: 1.5rem;
            }
            .upload-header p {
                margin: 0;
                color: #666;
                font-size: 0.9rem;
            }
            .upload-form {
                padding: 1.5rem;
            }
            .form-group {
                margin-bottom: 1.5rem;
            }
            .form-group label {
                display: block;
                margin-bottom: 0.75rem;
                font-weight: 600;
                color: #444;
                font-size: 0.95rem;
            }
            .file-input-container {
                position: relative;
                overflow: hidden;
                display: block;
            }
            .file-input-container input[type="file"] {
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                opacity: 0;
                cursor: pointer;
            }
            .file-input-label {
                display: block;
                width: 100%;
                padding: 1rem 1.5rem;
                background-color: #fff;
                border: 2px dashed #ddd;
                border-radius: 12px;
                text-align: center;
                color: #666;
                font-size: 0.95rem;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .file-input-label:hover {
                border-color: #667eea;
                background-color: #f0f7ff;
                color: #667eea;
            }
            .api-key-input {
                width: 100%;
                padding: 0.75rem 1rem;
                border: 2px solid #eee;
                border-radius: 8px;
                font-size: 0.95rem;
                transition: all 0.3s ease;
                box-sizing: border-box;
            }
            .api-key-input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .api-key-help {
                display: block;
                margin-top: 0.5rem;
                font-size: 0.85rem;
                color: #666;
            }
            .api-key-help a {
                color: #667eea;
                text-decoration: none;
            }
            .api-key-help a:hover {
                text-decoration: underline;
            }
            .cropper-header {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 8px 8px 0 0;
                border-bottom: 1px solid #eee;
            }
            .cropper-header h4 {
                margin: 0 0 0.5rem 0;
                color: #333;
            }
            .cropper-container {
                position: relative;
                background: #f0f0f0;
                height: 200px;
                overflow: hidden;
                border-radius: 0 0 8px 8px;
            }
            .cropper-preview {
                position: relative;
                width: 100%;
                height: 100%;
                cursor: move;
            }
            .cropper-preview img {
                max-width: none;
                width: auto;
                height: auto;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }
            .cropper-controls {
                display: flex;
                justify-content: center;
                gap: 0.5rem;
                padding: 1rem;
                background: #f8f9fa;
                border-top: 1px solid #eee;
            }
            .btn-sm {
                padding: 0.375rem 0.75rem;
                font-size: 0.875rem;
            }
            .btn-outline-secondary {
                color: #6c757d;
                border: 1px solid #6c757d;
                background-color: transparent;
            }
            .btn-outline-secondary:hover {
                color: #fff;
                background-color: #6c757d;
                border-color: #6c757d;
            }
            .file-input-label.dragover {
                border-color: #667eea;
                background-color: #e3f2fd;
                color: #667eea;
            }
            .file-input-label i {
                margin-right: 0.5rem;
                font-size: 1.2rem;
            }
            .file-info {
                margin-top: 0.75rem;
                font-size: 0.85rem;
                color: #888;
                min-height: 1.2rem;
            }
            .image-preview {
                margin-top: 1rem;
                text-align: center;
            }
            .preview-img {
                max-width: 100%;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                display: none;
            }
            .no-preview {
                color: #999;
                font-style: italic;
                margin-top: 1rem;
            }
            .button-container {
                text-align: center;
                margin-top: 2rem;
            }
            .btn {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 0.75rem 2rem;
                font-size: 1rem;
                font-weight: 600;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            .btn:active {
                transform: translateY(0);
            }
            .btn:disabled {
                background: #cccccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .result-section {
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                overflow: hidden;
            }
            .result-header {
                background: #f8f9fa;
                padding: 1.5rem;
                border-bottom: 1px solid #eee;
            }
            .result-header h2 {
                margin: 0 0 1rem 0;
                color: #333;
                font-size: 1.5rem;
            }
            .result-image-container {
                text-align: center;
                padding: 2rem;
            }
            .result-img {
                max-width: 100%;
                height: auto;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            }
            .download-btn {
                display: block;
                width: 100%;
                max-width: 200px;
                margin: 2rem auto;
                padding: 1rem;
                background: #28a745;
                color: white;
                border: none;
                border-radius: 50px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .download-btn:hover {
                background: #218838;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
            }
            .loading-container {
                text-align: center;
                padding: 3rem;
                color: #666;
            }
            .loading-spinner {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .status-message {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
                display: none;
            }
            .status-error {
                background: #ffebee;
                color: #c62828;
                border: 1px solid #ef9a9a;
            }
            .status-success {
                background: #e8f5e8;
                color: #2e7d32;
                border: 1px solid #a5d6a7;
            }
            .info-section {
                background: #e3f2fd;
                border-radius: 12px;
                padding: 1.5rem;
                margin-top: 2rem;
            }
            .info-section h3 {
                margin-top: 0;
                color: #1565c0;
            }
            .info-section ul {
                padding-left: 1.5rem;
            }
            .info-section li {
                margin-bottom: 0.5rem;
            }
            @media (max-width: 768px) {
                .header {
                    padding: 1.5rem 1rem;
                }
                .header h1 {
                    font-size: 2rem;
                }
                .content {
                    padding: 1rem;
                }
                .upload-section, .result-section {
                    margin-bottom: 1.5rem;
                }
            }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body>
        <div class="header">
            <h1>Virtual Try-On</h1>
            <p>See how clothes look on you before buying</p>
        </div>

        <div class="content">
            <div id="statusMessage" class="status-message"></div>

            <div class="upload-section">
                <div class="upload-header">
                    <h2><i class="fas fa-user"></i> Upload Your Photos</h2>
                    <p>Select a photo of yourself and a clothing item to see the virtual try-on result</p>
                </div>

                <form id="tryonForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="personImage"><i class="fas fa-user"></i> Person Photo</label>
                        <div class="file-input-container">
                            <input type="file" id="personImage" name="personImage" accept="image/*" required>
                            <label for="personImage" class="file-input-label">
                                <i class="fas fa-cloud-upload-alt"></i> Choose Person Photo
                            </label>
                        </div>
                        <div class="file-info" id="personFileInfo">No file selected</div>
                        <div class="image-preview">
                            <img class="preview-img" id="personPreview" alt="Person preview">
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="clothingImage"><i class="fas fa-tshirt"></i> Clothing Photo</label>
                        <div class="file-input-container">
                            <input type="file" id="clothingImage" name="clothingImage" accept="image/*" required>
                            <label for="clothingImage" class="file-input-label">
                                <i class="fas fa-cloud-upload-alt"></i> Choose Clothing Photo
                            </label>
                        </div>
                        <div class="file-info" id="clothingFileInfo">No file selected</div>
                        <div class="image-preview">
                            <img class="preview-img" id="clothingPreview" alt="Clothing preview">
                        </div>
                        <div id="clothingCropper" style="display: none; margin-top: 1rem;">
                            <div class="cropper-header">
                                <h4><i class="fas fa-crop"></i> Adjust Clothing Selection</h4>
                                <p>Drag the edges or move the box to select the clothing area you want to use</p>
                            </div>
                            <div class="cropper-container" style="position: relative; background: #f0f0f0; height: 180px; overflow: hidden; border-radius: 8px; margin: 1rem 0;">
                                <div id="cropPreview" style="width: 100%; height: 100%; position: relative; overflow: hidden;">
                                    <!-- Canvas will be inserted here by JavaScript -->
                                </div>
                            </div>
                            <div class="cropper-controls" style="display: flex; justify-content: center; gap: 0.5rem; padding: 1rem; background: #f8f9fa; border-top: 1px solid #eee; border-radius: 0 0 8px 8px;">
                                <button type="button" class="btn btn-sm btn-outline-secondary" id="cropReset">
                                    <i class="fas fa-redo"></i> Reset
                                </button>
                                <button type="button" class="btn btn-sm btn-success" id="cropApply">
                                    <i class="fas fa-check"></i> Apply Crop
                                </button>
                                <button type="button" class="btn btn-sm btn-link" id="cropSkip">
                                    Skip Cropping
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="apiKey"><i class="fas fa-key"></i> Alibaba Cloud API Key (Optional)</label>
                        <input type="text" id="apiKey" name="apiKey" placeholder="Enter your DashScope API key for AI-powered try-on" class="api-key-input">
                        <small class="api-key-help">Leave blank for demo mode. Get your key from <a href="https://help.aliyun.com/document_detail/413053.html" target="_blank">Alibaba Cloud DashScope</a></small>
                    </div>

                    <div class="button-container">
                        <button type="submit" class="btn" id="submitButton">
                            <i class="fas fa-magic"></i> Generate Try-On
                        </button>
                    </div>
                </form>
            </div>

            <div class="result-section" id="resultSection" style="display: none;">
                <div class="result-header">
                    <h2><i class="fas fa-check-circle"></i> Your Try-On Result</h2>
                </div>
                <div class="result-image-container">
                    <img class="result-img" id="resultImage" alt="Try-on result">
                </div>
                <button class="download-btn" id="downloadButton">
                    <i class="fas fa-download"></i> Download Result
                </button>
            </div>

            <div class="info-section">
                <h3><i class="fas fa-info-circle"></i> How It Works</h3>
                <ul>
                    <li><strong>Upload:</strong> Select a clear photo of yourself and a clothing item</li>
                    <li><strong>Process:</strong> Our system analyzes both images to create a realistic try-on</li>
                    <li><strong>Result:</strong> See how the clothing looks on you and download the image</li>
                </ul>
                <p><em>Tip: Enter your Alibaba Cloud DashScope API key above to use the actual AI-powered Qwen model for superior results. Leave blank for demo mode.</em></p>
            </div>
        </div>

        <script>
            const personInput = document.getElementById('personImage');
            const clothingInput = document.getElementById('clothingImage');
            const apiKeyInput = document.getElementById('apiKey');
            const personInfo = document.getElementById('personFileInfo');
            const clothingInfo = document.getElementById('clothingFileInfo');
            const personPreview = document.getElementById('personPreview');
            const clothingPreview = document.getElementById('clothingPreview');
            const statusMessage = document.getElementById('statusMessage');
            const resultSection = document.getElementById('resultSection');
            const submitButton = document.getElementById('submitButton');
            const tryonForm = document.getElementById('tryonForm');
            const downloadButton = document.getElementById('downloadButton');

            // File upload handlers
            function handleFileSelect(input, infoElement, previewElement) {
                return function(e) {
                    const file = e.target.files[0];
                    if (file) {
                        infoElement.textContent = file.name;
                        infoElement.style.color = '#333';

                        // Preview image
                        const reader = new FileReader();
                        reader.onload = function(event) {
                            previewElement.src = event.target.result;
                            previewElement.style.display = 'block';

                            // Show tips for clothing image
                            if (input === clothingInput) {
                                document.getElementById('clothingTips').style.display = 'block';
                            }
                        };
                        reader.readAsDataURL(file);
                    } else {
                        infoElement.textContent = 'No file selected';
                        infoElement.style.color = '#999';
                        previewElement.style.display = 'none';
                        document.getElementById('clothingCropper').style.display = 'none';
                    }
                };
            }

            personInput.addEventListener('change', handleFileSelect(personInput, personInfo, personPreview));
            clothingInput.addEventListener('change', handleFileSelect(clothingInput, clothingInfo, clothingPreview));

            // Clothing cropping functionality
            let cropperImage = null;
            let cropperCanvas = null;
            let cropperContext = null;
            let isDragging = false;
            let cropRect = { x: 0, y: 0, width: 100, height: 100 };
            let canvasWidth = 300;
            let canvasHeight = 180;
            let imageScale = 1;
            let imageOffsetX = 0;
            let imageOffsetY = 0;

            function initializeCropper(imageSrc) {
                cropperImage = new Image();
                cropperImage.onload = function() {
                    // Create canvas for preview
                    cropperCanvas = document.createElement('canvas');
                    cropperCanvas.width = canvasWidth;
                    cropperCanvas.height = canvasHeight;

                    const cropperPreview = document.getElementById('cropPreview');
                    cropperPreview.innerHTML = '';
                    cropperPreview.appendChild(cropperCanvas);
                    cropperContext = cropperCanvas.getContext('2d');

                    // Calculate image scaling to fit container while maintaining aspect ratio
                    const imageRatio = cropperImage.width / cropperImage.height;
                    const containerRatio = canvasWidth / canvasHeight;

                    if (imageRatio > containerRatio) {
                        imageScale = canvasWidth / cropperImage.width;
                    } else {
                        imageScale = canvasHeight / cropperImage.height;
                    }

                    imageOffsetX = (canvasWidth - cropperImage.width * imageScale) / 2;
                    imageOffsetY = (canvasHeight - cropperImage.height * imageScale) / 2;

                    // Initialize crop rectangle to center 80% of image
                    cropRect.width = Math.min(cropperImage.width * imageScale * 0.8, canvasWidth * 0.8);
                    cropRect.height = Math.min(cropperImage.height * imageScale * 0.8, canvasHeight * 0.8);
                    cropRect.x = (canvasWidth - cropRect.width) / 2;
                    cropRect.y = (canvasHeight - cropRect.height) / 2;

                    updateCropperPreview();
                    setupCropperEvents();
                };
                cropperImage.src = imageSrc;
            }

            function updateCropperPreview() {
                if (!cropperContext || !cropperImage) return;

                // Clear canvas
                cropperContext.clearRect(0, 0, cropperCanvas.width, cropperCanvas.height);

                // Draw image
                cropperContext.save();
                cropperContext.translate(imageOffsetX, imageOffsetY);
                cropperContext.scale(imageScale, imageScale);
                cropperContext.drawImage(cropperImage, 0, 0);
                cropperContext.restore();

                // Draw crop rectangle
                cropperContext.strokeStyle = '#ff6b6b';
                cropperContext.lineWidth = 2;
                cropperContext.setLineDash([5, 5]);
                cropperContext.strokeRect(cropRect.x, cropRect.y, cropRect.width, cropRect.height);

                // Draw crop handles
                const handleSize = 6;
                cropperContext.fillStyle = '#ff6b6b';
                cropperContext.fillRect(cropRect.x - handleSize/2, cropRect.y - handleSize/2, handleSize, handleSize); // top-left
                cropperContext.fillRect(cropRect.x + cropRect.width - handleSize/2, cropRect.y - handleSize/2, handleSize, handleSize); // top-right
                cropperContext.fillRect(cropRect.x - handleSize/2, cropRect.y + cropRect.height - handleSize/2, handleSize, handleSize); // bottom-left
                cropperContext.fillRect(cropRect.x + cropRect.width - handleSize/2, cropRect.y + cropRect.height - handleSize/2, handleSize, handleSize); // bottom-right
            }

            function getCroppedImageAsBlob() {
                if (!cropperImage || !cropperContext) return Promise.reject(new Error('No image loaded'));

                // Create temporary canvas for cropped image
                const tempCanvas = document.createElement('canvas');
                const scale = Math.max(cropperImage.width / canvasWidth, cropperImage.height / canvasHeight);

                tempCanvas.width = Math.round(cropRect.width / scale);
                tempCanvas.height = Math.round(cropRect.height / scale);
                const tempCtx = tempCanvas.getContext('2d');

                // Calculate source coordinates in original image
                const sourceX = Math.round((cropRect.x - imageOffsetX) / scale);
                const sourceY = Math.round((cropRect.y - imageOffsetY) / scale);
                const sourceWidth = Math.round(cropRect.width / scale);
                const sourceHeight = Math.round(cropRect.height / scale);

                // Draw cropped portion
                tempCtx.drawImage(
                    cropperImage,
                    sourceX, sourceY, sourceWidth, sourceHeight,
                    0, 0, tempCanvas.width, tempCanvas.height
                );

                // Convert to blob
                return new Promise((resolve) => {
                    tempCanvas.toBlob((blob) => {
                        resolve(blob);
                    }, 'image/jpeg', 0.9);
                });
            }

            function setupCropperEvents() {
                let startX = 0, startY = 0;
                let startRectX = 0, startRectY = 0;
                let resizingEdge = null;

                cropperCanvas.addEventListener('mousedown', function(e) {
                    const rect = cropperCanvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;

                    // Check if clicking on resize handles
                    const handleSize = 12;
                    if (Math.abs(mouseX - cropRect.x) < handleSize && Math.abs(mouseY - cropRect.y) < handleSize) {
                        resizingEdge = 'top-left';
                    } else if (Math.abs(mouseX - (cropRect.x + cropRect.width)) < handleSize && Math.abs(mouseY - cropRect.y) < handleSize) {
                        resizingEdge = 'top-right';
                    } else if (Math.abs(mouseX - cropRect.x) < handleSize && Math.abs(mouseY - (cropRect.y + cropRect.height)) < handleSize) {
                        resizingEdge = 'bottom-left';
                    } else if (Math.abs(mouseX - (cropRect.x + cropRect.width)) < handleSize && Math.abs(mouseY - (cropRect.y + cropRect.height)) < handleSize) {
                        resizingEdge = 'bottom-right';
                    } else if (mouseX >= cropRect.x && mouseX <= cropRect.x + cropRect.width &&
                             mouseY >= cropRect.y && mouseY <= cropRect.y + cropRect.height) {
                        resizingEdge = 'move';
                        startX = mouseX;
                        startY = mouseY;
                        startRectX = cropRect.x;
                        startRectY = cropRect.y;
                    }

                    if (resizingEdge) {
                        isDragging = true;
                    }
                });

                cropperCanvas.addEventListener('mousemove', function(e) {
                    if (!isDragging) return;

                    const rect = cropperCanvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;

                    if (resizingEdge === 'move') {
                        cropRect.x = startRectX + (mouseX - startX);
                        cropRect.y = startRectY + (mouseY - startY);
                    } else if (resizingEdge === 'top-left') {
                        cropRect.width += startRectX - mouseX;
                        cropRect.height += startRectY - mouseY;
                        cropRect.x = mouseX;
                        cropRect.y = mouseY;
                    } else if (resizingEdge === 'top-right') {
                        cropRect.width += mouseX - startRectX;
                        cropRect.height += startRectY - mouseY;
                        cropRect.x = startRectX;
                        cropRect.y = mouseY;
                    } else if (resizingEdge === 'bottom-left') {
                        cropRect.width += startRectX - mouseX;
                        cropRect.height += mouseY - startRectY;
                        cropRect.x = mouseX;
                        cropRect.y = startRectY;
                    } else if (resizingEdge === 'bottom-right') {
                        cropRect.width += mouseX - startRectX;
                        cropRect.height += mouseY - startRectY;
                    }

                    // Keep cropper within bounds
                    cropRect.x = Math.max(0, Math.min(cropRect.x, canvasWidth - cropRect.width));
                    cropRect.y = Math.max(0, Math.min(cropRect.y, canvasHeight - cropRect.height));
                    cropRect.width = Math.max(20, Math.min(cropRect.width, canvasWidth - cropRect.x));
                    cropRect.height = Math.max(20, Math.min(cropRect.height, canvasHeight - cropRect.y));

                    updateCropperPreview();
                });

                cropperCanvas.addEventListener('mouseup', function() {
                    isDragging = false;
                    resizingEdge = null;
                });

                cropperCanvas.addEventListener('mouseleave', function() {
                    isDragging = false;
                    resizingEdge = null;
                });
            }

            // Cropper controls
            document.getElementById('cropReset').addEventListener('click', function() {
                if (cropperImage) {
                    initializeCropper(cropperImage.src);
                }
            });

            document.getElementById('cropApply').addEventListener('click', async function() {
                try {
                    const croppedBlob = await getCroppedImageAsBlob();
                    if (croppedBlob) {
                        // Store the cropped blob for form submission
                        clothingInput.croppedBlob = croppedBlob;
                        document.getElementById('clothingCropper').style.display = 'none';
                        showStatus('Clothing area selected!', 'success');
                    }
                } catch (error) {
                    showStatus('Error processing crop: ' + error.message, 'error');
                }
            });

            document.getElementById('cropSkip').addEventListener('click', function() {
                document.getElementById('clothingCropper').style.display = 'none';
                if (clothingInput.croppedBlob) {
                    delete clothingInput.croppedBlob;
                }
                showStatus('Using full image for clothing', 'info');
            });

            // Drag and drop functionality
            function addDragDrop(inputContainer, inputElement, infoElement, previewElement) {
                inputContainer.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    inputContainer.querySelector('.file-input-label').classList.add('dragover');
                });

                inputContainer.addEventListener('dragleave', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    inputContainer.querySelector('.file-input-label').classList.remove('dragover');
                });

                inputContainer.addEventListener('drop', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    inputContainer.querySelector('.file-input-label').classList.remove('dragover');

                    const dt = e.dataTransfer;
                    const file = dt.files[0];
                    if (file) {
                        inputElement.files = dt.files;
                        infoElement.textContent = file.name;
                        infoElement.style.color = '#333';

                        // Preview image
                        const reader = new FileReader();
                        reader.onload = function(event) {
                            previewElement.src = event.target.result;
                            previewElement.style.display = 'block';
                        };
                        reader.readAsDataURL(file);
                    }
                });
            }

            // Apply drag and drop to both file inputs
            const personContainer = personInput.parentElement.parentElement;
            const clothingContainer = clothingInput.parentElement.parentElement;
            addDragDrop(personContainer, personInput, personInfo, personPreview);
            addDragDrop(clothingContainer, clothingInput, clothingInfo, clothingPreview);

            // Form submission
            tryonForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitForm();
            });

            async function submitForm() {
                const personFile = personInput.files[0];
                const clothingFile = clothingInput.files[0];
                const apiKey = apiKeyInput.value.trim();

                if (!personFile || !clothingFile) {
                    showStatus('Please select both person and clothing images', 'error');
                    return;
                }

                // Validate file types
                const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'];
                if (!allowedTypes.includes(personFile.type) || !allowedTypes.includes(clothingFile.type)) {
                    showStatus('Please upload valid image files (JPG, PNG, GIF, BMP)', 'error');
                    return;
                }

                // Show loading state
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                resultSection.style.display = 'none';
                hideStatus();

                const formData = new FormData();
                formData.append('personImage', personFile);

                // Handle clothing image - use cropped version if available
                if (clothingInput.croppedBlob) {
                    formData.append('clothingImage', clothingInput.croppedBlob, 'clothing_cropped.jpg');
                } else {
                    formData.append('clothingImage', clothingFile);
                }

                if (apiKey) {
                    formData.append('apiKey', apiKey);
                }

                fetch('/tryon', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw new Error(err.error || 'Unknown error'); });
                    }
                    return response.blob();
                })
                .then(blob => {
                    // Hide loading, show success
                    submitButton.disabled = false;
                    submitButton.innerHTML = '<i class="fas fa-magic"></i> Generate Try-On';
                    showStatus('Try-on generated successfully!', 'success');
                    resultSection.style.display = 'block';

                    // Display the result image
                    const imageUrl = URL.createObjectURL(blob);
                    document.getElementById('resultImage').src = imageUrl;

                    // Set up download button
                    downloadButton.onclick = function() {
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        a.download = 'tryon_result.jpg';
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                    };
                })
                .catch(error => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = '<i class="fas fa-magic"></i> Generate Try-On';
                    showStatus('Error: ' + error.message, 'error');
                });
            }

            function showStatus(message, type) {
                statusMessage.textContent = message;
                statusMessage.className = `status-message status-${type}`;
                statusMessage.style.display = 'block';
            }

            function hideStatus() {
                statusMessage.style.display = 'none';
            }
        </script>
    </body>
    </html>
    '''

@app.route('/tryon', methods=['POST'])
def tryon():
    """Handle the try-on request"""
    try:
        # Check if files were uploaded
        if 'personImage' not in request.files or 'clothingImage' not in request.files:
            return jsonify({'error': 'Both person and clothing images are required'}), 400

        person_file = request.files['personImage']
        clothing_file = request.files['clothingImage']

        # Get API key if provided
        api_key = request.form.get('apiKey', '').strip()

        # Check if files are selected
        if person_file.filename == '' or clothing_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check file types
        if not (allowed_file(person_file.filename) and allowed_file(clothing_file.filename)):
            return jsonify({'error': 'Invalid file type. Please upload image files.'}), 400

        # Save files temporarily
        person_filename = secure_filename(person_file.filename)
        clothing_filename = secure_filename(clothing_file.filename)

        person_path = os.path.join(app.config['UPLOAD_FOLDER'], person_filename)
        clothing_path = os.path.join(app.config['UPLOAD_FOLDER'], clothing_filename)

        person_file.save(person_path)
        clothing_file.save(clothing_path)

        try:
            # Initialize the virtual try-on with API key if provided
            tryon_app = VirtualTryOn(api_key=api_key if api_key else None)

            # Generate try-on result
            result_image = tryon_app.generate_try_on(
                person_image_path=person_path,
                clothing_image_path=clothing_path
            )

            # Convert result to bytes for sending back
            img_io = io.BytesIO()
            result_image.save(img_io, 'JPEG')
            img_io.seek(0)

            # Clean up temporary files
            os.remove(person_path)
            os.remove(clothing_path)

            # Return the image
            return send_file(
                img_io,
                mimetype='image/jpeg',
                as_attachment=False,
                download_name='tryon_result.jpg'
            )

        except Exception as e:
            # Clean up temporary files even if there's an error
            if os.path.exists(person_path):
                os.remove(person_path)
            if os.path.exists(clothing_path):
                os.remove(clothing_path)

            return jsonify({'error': f'Error processing images: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Virtual Try-On Web API is running'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)