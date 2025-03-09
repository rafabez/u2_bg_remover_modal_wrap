import os
import sys
import numpy as np
import torch
import cv2
from PIL import Image
from io import BytesIO

# Add U-2-Net to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "U-2-Net"))
from model.u2net import U2NET

def load_model(model_path):
    """Load the U-2-Net model"""
    print(f"Loading model from {model_path}")
    net = U2NET(3, 1)
    
    if torch.cuda.is_available():
        net.load_state_dict(torch.load(model_path))
        net.cuda()
        print("Model loaded on GPU")
    else:
        net.load_state_dict(torch.load(model_path, map_location='cpu'))
        print("Model loaded on CPU")
    
    net.eval()
    return net

def preprocess(image):
    """Preprocess input image before feeding to the model"""
    # Resize and normalize
    image = image.resize((320, 320), Image.LANCZOS)
    image = np.array(image).astype(np.float32)
    
    # Normalize to [0, 1]
    image = image / 255.0
    
    # Convert to PyTorch tensor and add batch dimension
    image = torch.from_numpy(image.transpose((2, 0, 1))).float()
    image = image.unsqueeze(0)
    
    # Move to GPU if available
    if torch.cuda.is_available():
        image = image.cuda()
        
    return image

def norm_pred(d):
    """Normalize the predicted saliency map"""
    ma = torch.max(d)
    mi = torch.min(d)
    return (d - mi) / (ma - mi)

def postprocess(original_image, mask_tensor):
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
        # RGB image
        r, g, b = cv2.split(image_np)
        rgba = cv2.merge([b, g, r, mask])
    else:
        # Already has alpha channel or is grayscale
        rgba = cv2.merge([image_np, mask])
        
    return Image.fromarray(rgba)

def remove_background(input_path, output_path, model):
    """Remove background from an image"""
    try:
        print(f"Processing image: {input_path}")
        # Load image
        image = Image.open(input_path).convert("RGB")
        
        # Preprocess
        image_tensor = preprocess(image)
        
        # Predict
        with torch.no_grad():
            d1, d2, d3, d4, d5, d6, d7 = model(image_tensor)
        
        # Use d1 as the final prediction
        pred = d1[:, 0, :, :]
        pred = norm_pred(pred)
        
        # Postprocess
        result = postprocess(image, pred)
        
        # Save the result
        result.save(output_path)
        print(f"Result saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Error removing background: {str(e)}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python local_test.py <input_image_path> <output_image_path>")
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Set up model path
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            "U-2-Net", "saved_models", "u2net", "u2net.pth")
    
    # Load model
    model = load_model(model_path)
    
    # Process image
    success = remove_background(input_path, output_path, model)
    
    if success:
        print("Background removal completed successfully!")
    else:
        print("Background removal failed.")

if __name__ == "__main__":
    main()
