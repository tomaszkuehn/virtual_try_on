# Virtual Try-On Application

This application processes person and clothing photographs to generate try-on images using Alibaba Cloud Qwen.

## Features

- Person and clothing image processing
- Image preprocessing and resizing
- Integration with Alibaba Cloud Qwen (when configured)
- Demo mode for testing without Alibaba Cloud credentials
- Batch processing capabilities
- Command-line interface

## Installation

1. Clone or download this repository
2. Navigate to the virtual_try_on directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Usage

### Basic Usage

```bash
python -m src.tryon_app --person person.jpg --clothing shirt.jpg --output result.jpg
```

### With Alibaba Cloud Qwen

To use the actual Alibaba Cloud Qwen models, you need to:

1. Set up an Alibaba Cloud account
2. Enable the DashScope service
3. Get your API key from the Alibaba Cloud console
4. Provide your API key:

```bash
python -m src.tryon_app --person person.jpg --clothing shirt.jpg --output result.jpg --api-key YOUR_DASHSCOPE_API_KEY
```

### Command Line Arguments

- `--person`: Path to person photograph (required)
- `--clothing`: Path to clothing photograph (required)
- `--output`: Path to save the result (optional)
- `--api-key`: Alibaba Cloud DashScope API key (for Qwen-Image-2.0)
- `--demo`: Force demo mode (useful for testing)

## How It Works

1. **Input Validation**: Loads and validates both person and clothing images
2. **Preprocessing**: Resizes and pads images to appropriate dimensions for the AI model
3. **Processing**: 
   - With Alibaba Cloud: Sends images to DashScope Qwen endpoint for try-on generation
   - Demo Mode: Creates a composite image for demonstration purposes
4. **Output**: Returns or saves the generated try-on image

## Requirements

- Python 3.8+
- Alibaba Cloud account (for actual AI model usage)
- Dependencies listed in requirements.txt

## Notes

- This application currently runs in demo mode by default, creating a composite image
- To use actual AI try-on capabilities, you need to:
  1. Have access to Alibaba Cloud DashScope service
  2. Replace the `_call_dashscope_qwen` method with actual API calls to your Qwen model (if needed)
  3. Provide valid Alibaba Cloud API credentials

## Project Structure

```
virtual_try_on/
├── src/
│   └── tryon_app.py          # Main application logic
├── tests/                    # Unit tests (to be added)
├── docs/                     # Documentation (to be added)
├── scripts/                  # Helper scripts (to be added)
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
└README.md                    # This file
```

## Future Enhancements

- Actual integration with Alibaba Cloud's Qwen models for virtual try-on
- Improved image preprocessing for better try-on results
- Web interface using Flask or FastAPI
- Support for various clothing types (tops, bottoms, full outfits)
- Advanced pose detection and garment warping
- Batch processing optimizations