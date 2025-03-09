# U-2-Net Background Remover (Modal Implementation)

A web application that uses the U-2-Net model to automatically remove backgrounds from images, deployed with Modal.com.

## Project Structure

```
.
├── U-2-Net/                  # U-2-Net model directory
│   ├── model/                # Model architecture code
│   └── saved_models/u2net/   # Directory for model weights (auto-downloaded at runtime)
├── templates/                # Web interface templates
├── app.py                    # Main application file for Modal deployment
├── local_test.py             # Script for local testing
└── requirements.txt          # Project dependencies
```

## Overview

This application wraps the U-2-Net deep learning model developed by Xuebin Qin et al. to automatically remove backgrounds from images. The model is deployed as a web service on Modal, allowing users to upload images and receive versions with transparent backgrounds.

## Features

- **Automatic Background Removal**: Upload any image to get a transparent PNG with the background removed
- **Web Interface**: Simple web UI for uploading images and downloading results
- **Automated Model Loading**: The application automatically downloads the model weights at runtime (~176MB)
- **Optimized Deployment**: Efficient deployment on Modal.com with minimal container size
- **Fixed Color Handling**: Properly handles RGB/BGR color channel conversion for accurate colors
- **OpenCV Dependency Management**: Pre-configured with necessary system dependencies for OpenCV

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/rafabez/u2_bg_remover_modal_wrap.git
cd u2_bg_remover_modal_wrap
```

### 2. Deploy to Modal

The application is designed to be deployed directly to Modal with minimal setup:

1. Install the Modal CLI:
```bash
pip install modal
```

2. Log in to Modal:
```bash
modal token new
```

3. Deploy the application:
```bash
modal deploy app.py
```

That's it! The application will automatically download the U-2-Net model weights file (~176MB) the first time it runs. You don't need to manually download or place any model files.

### Local Development

If you want to test or develop locally:

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Test the application locally:

```bash
# Replace with actual file paths
python local_test.py input_image.jpg output_image.png
```

## Model Details

The U-2-Net model is a two-level nested U-structure architecture designed for salient object detection. This implementation uses it for background removal by generating a binary mask that separates the foreground (object) from the background.

For more information about the model, see the [original U-2-Net repository](https://github.com/xuebinqin/U-2-Net).

## Deployment

The application is deployed at: https://rafabez--u2net-bg-remover-fastapi-app.modal.run

### How It Works

1. The Modal deployment creates a container with all necessary dependencies (including OpenCV requirements)
2. The first time the application runs, it automatically downloads the model weights from multiple backup sources
3. FastAPI serves the web interface and API endpoints
4. When an image is uploaded, the background removal function processes it with proper color channel handling
5. The transparent PNG result is returned to the user

## For Others Deploying This Project

If someone else wants to deploy this project to their own Modal account:

1. Clone the repository:
```bash
git clone https://github.com/rafabez/u2_bg_remover_modal_wrap.git
cd u2_bg_remover_modal_wrap
```

2. Install the Modal CLI and log in with their account:
```bash
pip install modal
modal token new
```

3. (Optional) Modify the app name in `app.py` to reflect their ownership:
```python
# Create a Modal app
app = modal.App("your-username-u2net-bg-remover")
```

4. Deploy to their Modal account:
```bash
modal deploy app.py
```

The application will be deployed with a unique URL following this pattern:
`https://username--app-name-fastapi-app.modal.run`

## Acknowledgments

- Original U-2-Net implementation by [Xuebin Qin et al.](https://github.com/xuebinqin/U-2-Net)
- Image processing using OpenCV and PIL
- Web service built with FastAPI
- Deployment on Modal.com

## License

This project is released under the same license as the original U-2-Net implementation (Apache 2.0).
