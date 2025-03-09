# U-2-Net Background Remover for Modal

This project wraps the U-2-Net background removal model to deploy it on [Modal](https://modal.com). U-2-Net is a highly effective model for removing backgrounds from images.

## Project Structure

```
├── U-2-Net/                 # Original U-2-Net repository
│   ├── model/               # Model architecture
│   ├── saved_models/        # Directory for pre-trained weights (need to be downloaded separately)
│   └── test_data/           # Sample images for testing
├── app.py                   # Main Modal application
├── templates/               # Web frontend
│   └── index.html           # HTML UI for uploading images
└── requirements.txt         # Project dependencies
```

## Setup and Deployment

### Prerequisites

- Python 3.8+
- Modal account and CLI setup
- U-2-Net pre-trained model weights (must be downloaded separately, see below)

### Model Weights Download

⚠️ **Important:** Before using this application, you must download the U-2-Net model weights:

1. Create the directory structure for model weights:

```bash
mkdir -p U-2-Net/saved_models/u2net
```

2. Download the model weights:

```bash
# Main U-2-Net model (for general object segmentation)
wget https://github.com/xuebinqin/U-2-Net/releases/download/1.0/u2net.pth -O U-2-Net/saved_models/u2net/u2net.pth

# Optional: Human portrait model (for better results on human subjects)
# mkdir -p U-2-Net/saved_models/u2net_portrait
# wget https://github.com/xuebinqin/U-2-Net/releases/download/1.0/u2net_portrait.pth -O U-2-Net/saved_models/u2net_portrait/u2net_portrait.pth

# Optional: Smaller model (faster but less accurate)
# mkdir -p U-2-Net/saved_models/u2netp
# wget https://github.com/xuebinqin/U-2-Net/releases/download/1.0/u2netp.pth -O U-2-Net/saved_models/u2netp/u2netp.pth
```

> Note: Model weights files are approximately 176MB each.

### Local Development

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
# source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Test the application locally:

```bash
# Replace with actual file paths
modal run app.py --input_path "U-2-Net/test_data/test_images/bike.jpg" --output_path "output.png"
```

### Deploying to Modal

1. Ensure you're logged in to Modal with your account:

```bash
modal login
```

2. Deploy the application:

```bash
modal deploy app.py
```

3. Once deployed, your application will be available at the URL provided by Modal. You can also access it through the Modal dashboard.

### Deploying to Another Modal Account

This wrapper can be used for multiple Modal accounts. To deploy to a different account:

1. The new user should clone this repository:

```bash
git clone https://github.com/your-username/u2_bg_remover_modal_wrap.git
cd u2_bg_remover_modal_wrap
```

2. Download the model weights following the instructions in the [Model Weights Download](#model-weights-download) section.

3. The new user should install the Modal CLI and log in with their account:

```bash
pip install modal
modal login
```

4. (Optional) If desired, they can modify the app name in `app.py` to reflect their ownership:

```python
# Create a Modal app
app = modal.App("custom-name-u2net-bg-remover")
```

5. Deploy to their Modal account:

```bash
modal deploy app.py
```

6. The application will be deployed to their Modal account with a unique URL following this pattern:
   `https://username--app-name-function-name.modal.run`

## Usage

### Web Interface

After deployment, navigate to the root URL of your Modal application to access the web interface:

1. Click the upload area or drag and drop an image
2. Click "Remove Background" to process the image
3. The result will be displayed with a transparent background (PNG format)

### API Usage

You can also use the background removal endpoint programmatically:

```python
import requests

response = requests.post(
    "https://your-modal-endpoint.modal.run/remove-background",
    files={"image": open("path/to/your/image.jpg", "rb")}
)

# Save the result
with open("result.png", "wb") as f:
    f.write(response.content)
```

## How It Works

1. **Image Upload**: User uploads an image via the web interface or API
2. **Preprocessing**: Image is resized to 320x320 and normalized
3. **Model Inference**: U-2-Net processes the image to create a saliency map
4. **Postprocessing**: The saliency map is used to create an alpha channel
5. **Result**: The original image with a transparent background is returned

## Implementing Additional Features

### Mask Threshold Adjustment

To implement a mask threshold adjustment feature, you would need to modify the code before deployment:

1. Update the `index.html` file to include a slider or input field for the threshold value
2. Modify the FastAPI endpoint to accept this threshold parameter
3. Update the `postprocess` method in the `BackgroundRemover` class to use the provided threshold value instead of the fixed 0.5 value:

```python
# Current implementation
mask = (mask > 0.5).astype(np.uint8) * 255

# Modified implementation with threshold parameter
mask = (mask > threshold).astype(np.uint8) * 255
```

4. Redeploy the application with `modal deploy app.py`

Other potential features like different model options or image resizing would follow the same pattern: modify the code before deployment, and then redeploy the application.

## Credits

- [U-2-Net](https://github.com/xuebinqin/U-2-Net) - Original implementation by Xuebin Qin
- [Modal](https://modal.com) - Cloud platform for deployment
