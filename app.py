import os
import sys
import numpy as np
import torch
import cv2
from PIL import Image
from io import BytesIO
import modal
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, Response

# Create a Modal image with all required dependencies
image = (
    modal.Image.debian_slim()
    .apt_install(["libgl1-mesa-glx", "libglib2.0-0"])  # Install system dependencies for OpenCV
    .pip_install([
        "torch>=1.7.0", 
        "numpy>=1.19.0", 
        "Pillow>=8.0.0", 
        "opencv-python>=4.4.0", 
        "scikit-image>=0.17.2", 
        "fastapi>=0.68.0", 
        "python-multipart>=0.0.5",
        "gdown>=4.6.0"  # Add gdown for Google Drive downloads
    ])
)

# Create a Modal app
app = modal.App("u2net-bg-remover")

# Only add essential directories for the model
image = (
    image
    # Add only the model implementation and weights file
    .add_local_dir("U-2-Net/model", "/root/model")
    .add_local_dir("U-2-Net/saved_models/u2net", "/root/saved_models/u2net")
    .add_local_dir("templates", "/root/templates")
)

# Define a class for background removal
class BackgroundRemover:
    def __init__(self):
        self.model = None
        
    def download_model_weights(self, model_path):
        """Download the model weights file if it doesn't exist"""
        print(f"Model weights not found at {model_path}, attempting to download...")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        try:
            # Try HuggingFace first (reliable direct download)
            import urllib.request
            print("Downloading from HuggingFace...")
            url = "https://huggingface.co/akhaliq/u2net/resolve/main/u2net.pth"
            urllib.request.urlretrieve(url, model_path)
            
            # Verify file was downloaded correctly
            if os.path.exists(model_path) and os.path.getsize(model_path) > 1000000:  # >1MB
                print("Successfully downloaded model weights!")
                return True
            else:
                print("Download from HuggingFace failed, trying Google Drive...")
                os.remove(model_path)  # Remove the potentially corrupted file
        except Exception as e:
            print(f"Error downloading from HuggingFace: {str(e)}")
            
        try:
            # Try using gdown for Google Drive
            import gdown
            print("Downloading from Google Drive...")
            url = "https://drive.google.com/uc?id=1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ"
            gdown.download(url, model_path, quiet=False)
            
            # Verify file was downloaded correctly
            if os.path.exists(model_path) and os.path.getsize(model_path) > 1000000:  # >1MB
                print("Successfully downloaded model weights!")
                return True
            else:
                print("Download from Google Drive failed")
                if os.path.exists(model_path):
                    os.remove(model_path)  # Remove the potentially corrupted file
        except Exception as e:
            print(f"Error downloading from Google Drive: {str(e)}")
            
        return False
        
    def load_model(self):
        """Load the U-2-Net model"""
        # Import U-2-Net model dynamically
        sys.path.append("/root")
        from model.u2net import U2NET
        
        # Set up model path
        model_path = "/root/saved_models/u2net/u2net.pth"
        
        # Check if model file exists and is valid, try to download if not
        if not os.path.exists(model_path) or os.path.getsize(model_path) < 1000000:  # <1MB is too small
            if not self.download_model_weights(model_path):
                error_msg = (
                    f"Could not download model weights to {model_path}.\n"
                    "Please download the model weights file (u2net.pth) manually and place it in the U-2-Net/saved_models/u2net/ directory.\n"
                    "You can download it from: https://drive.google.com/file/d/1ao1ovG1Qtx4b7EoskHXmi2E9rp5CHLcZ/view?usp=sharing\n"
                    "See the README.md file for detailed instructions."
                )
                print(error_msg)
                raise FileNotFoundError(error_msg)
        
        # Load model
        print("Loading U-2-Net model...")
        net = U2NET(3, 1)
        net.load_state_dict(torch.load(model_path, map_location="cpu"))
        net.eval()
        self.model = net
        print("Model loaded successfully!")
        
    def preprocess(self, image):
        """Preprocess input image before feeding to the model"""
        # Resize and normalize
        image = image.resize((320, 320), Image.LANCZOS)
        image = np.array(image).astype(np.float32)
        
        # Normalize to [0, 1]
        image = image / 255.0
        
        # Convert to PyTorch tensor and add batch dimension
        image = torch.from_numpy(image.transpose((2, 0, 1))).float()
        image = image.unsqueeze(0)
        return image
    
    def norm_pred(self, d):
        """Normalize the predicted saliency map"""
        ma = torch.max(d)
        mi = torch.min(d)
        return (d - mi) / (ma - mi)
    
    def predict(self, image_tensor):
        """Run model inference on the preprocessed image"""
        with torch.no_grad():
            d1, d2, d3, d4, d5, d6, d7 = self.model(image_tensor)
        
        # Use d1 as the final prediction
        pred = d1[:, 0, :, :]
        pred = self.norm_pred(pred)
        return pred
    
    def postprocess(self, original_image, mask_tensor):
        """Create transparent image using the predicted mask"""
        # Convert mask to numpy
        mask = mask_tensor.squeeze().cpu().numpy()
        
        # Resize mask to original image size
        mask = cv2.resize(mask, (original_image.width, original_image.height))
        
        # Apply threshold to create binary mask
        mask = (mask > 0.5).astype(np.uint8) * 255
        
        # Convert original image to numpy
        image_np = np.array(original_image)
        
        # Create RGBA image (with transparency)
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            # RGB image - PIL already uses RGB order, so we don't need to reorder the channels
            # Just create an RGBA image directly
            rgba = np.zeros((image_np.shape[0], image_np.shape[1], 4), dtype=np.uint8)
            rgba[:, :, 0:3] = image_np  # Copy the RGB channels
            rgba[:, :, 3] = mask  # Set the alpha channel
        else:
            # Already has alpha channel or is grayscale
            rgba = cv2.merge([image_np, mask])
            
        return Image.fromarray(rgba)
    
    def remove_background(self, image_data):
        """Remove background from an image"""
        try:
            # Convert binary data to PIL image
            image = Image.open(BytesIO(image_data)).convert("RGB")
            
            # Preprocess
            image_tensor = self.preprocess(image)
            
            # Predict
            pred = self.predict(image_tensor)
            
            # Postprocess
            result = self.postprocess(image, pred)
            
            # Return the image as bytes
            buffer = BytesIO()
            result.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error removing background: {str(e)}")
            raise

# FastAPI app
web_app = FastAPI()

@web_app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the index page"""
    with open("/root/templates/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@web_app.post("/remove-background")
async def remove_background(image: UploadFile = File(...)):
    """API endpoint for background removal"""
    try:
        # Read image data
        contents = await image.read()
        
        # Remove background using Modal function
        result = bg_remover_instance.remote(contents)
        
        # Return result
        return Response(content=result, media_type="image/png")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# Modal container that keeps the model loaded
@app.function(
    image=image,
    keep_warm=1,  # Keep one instance warm for faster responses
    timeout=600,  # 10 minute timeout
)
def bg_remover_instance(image_data: bytes):
    """Modal function that loads, processes with the model, and returns the result"""
    remover = BackgroundRemover()
    remover.load_model()
    return remover.remove_background(image_data)

# Modal web endpoint that serves the FastAPI app
@app.function(
    image=image,
    cpu=1,
    memory=4096,  # 4GB memory
    timeout=60,  # 1 minute timeout
)
@modal.asgi_app()
def fastapi_app():
    """ASGI app for serving the web interface"""
    return web_app

# Simplified local testing for just one image
@app.local_entrypoint()
def main(input_path: str, output_path: str):
    """Local testing entrypoint"""
    print(f"Removing background from {input_path}...")
    try:
        # Read input image
        with open(input_path, "rb") as f:
            image_data = f.read()
        
        # Process the image (directly, without calling remover.get())
        remover = BackgroundRemover()
        remover.load_model()
        result = remover.remove_background(image_data)
        
        # Save the output
        with open(output_path, "wb") as f:
            f.write(result)
        
        print(f"Saved result to {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
