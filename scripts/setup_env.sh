#!/bin/bash
# Setup script for Virtual Try-On Application

echo "Setting up Virtual Try-On Application..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

echo "Python version: $(python3 --version)"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install in development mode
echo "Installing package in development mode..."
pip install -e .

echo ""
echo "Setup complete!"
echo ""
echo "To use the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python -m src.tryon_app --help"
echo ""
echo "For Google Cloud integration:"
echo "- Set up a Google Cloud project"
echo "- Enable Vertex AI API"
echo "- Authenticate with Google Cloud"
echo "- Provide your project ID when running the application"