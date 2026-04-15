# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview
This repository contains a Virtual Try-On application that processes person and clothing photographs to generate try-on images using Alibaba Cloud Qwen.

## Project Structure
```
virtual_try_on/
├── src/
│   └── tryon_app.py          # Main application logic
├── tests/                    # Unit tests
├── docs/                     # Documentation
├── scripts/                  # Helper scripts
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
└── README.md                 # Detailed documentation
```

## Getting Started

### Prerequisites
- Python 3.8+
- Alibaba Cloud account (for actual AI model usage)

### Installation
1. Navigate to the virtual_try_on directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install in development mode:
   ```bash
   pip install -e .
   ```

### Usage Examples

#### Basic Usage (Demo Mode)
```bash
python -m src.tryon_app --person person.jpg --clothing shirt.jpg --output result.jpg
```

#### With Alibaba Cloud Qwen-Image-2.0
```bash
python -m src.tryon_app --person person.jpg --clothing shirt.jpg --output result.jpg --api-key YOUR_DASHSCOPE_API_KEY
```

#### Force Demo Mode
```bash
python -m src.tryon_app --person person.jpg --clothing shirt.jpg --output result.jpg --demo
```

## Key Features

1. **Image Processing**: Loads and validates person and clothing photographs
2. **Preprocessing**: Resizes and pads images for optimal AI model input
3. **AI Integration**: Connects to Alibaba Cloud Qwen-Image-2.0 for try-on generation (when configured)
4. **Demo Mode**: Runs in simulation mode for testing without Alibaba Cloud credentials
5. **Batch Processing**: Supports processing multiple person-clothing pairs
6. **Command Line Interface**: Easy-to-use CLI with helpful arguments

## Development Guidelines

### Making Changes
- Modify `src/tryon_app.py` for core functionality changes
- Add tests in the `tests/` directory
- Update documentation in `README.md` and `docs/` as needed
- Follow existing code style and patterns

### Running Tests
```bash
python -m pytest tests/ -v
```

### Creating Sample Images
```bash
python example_usage.py
```

## Alibaba Cloud Integration

To use actual AI try-on capabilities:

1. **Set up Alibaba Cloud Account**:
   - Create an account on Alibaba Cloud
   - Enable the DashScope service in the console
   - Obtain your API key from the DashScope dashboard

2. **Install DashScope Dependencies**:
   ```bash
   pip install dashscope
   ```

3. **Provide API Key**:
   - Use `--api-key YOUR_DASHSCOPE_API_KEY` when running the application
   - Or set the `DASHSCOPE_API_KEY` environment variable

4. **Model Usage**:
   - Uses exclusively the `qwen-image-2.0` model for image generation
   - No model selection parameter is available (fixed to qwen-image-2.0)
   - Utilizes the MultiModalConversation API for image understanding and generation tasks

## Troubleshooting

### Common Issues
- **"DashScope not available"**: Install `dashscope` package
- **Authentication errors**: Ensure proper Alibaba Cloud API key setup
- **Image loading errors**: Verify image file paths and formats are correct
- **Output directory errors**: Ensure output directory exists or use absolute paths
- **API quota exceeded**: Check your DashScope usage and billing

### Getting Help
- Check the README.md for detailed usage instructions
- Review the example_usage.py file for demonstration code
- Examine unit tests in the tests/ directory for usage patterns