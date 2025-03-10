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

## API Usage

The application provides a REST API endpoint that can be used from any programming language to remove backgrounds from images. Here's how to integrate with the API:

### Endpoint

```
POST https://pollinations--u2net-bg-remover-fastapi-app.modal.run/remove-background
```

The endpoint accepts image uploads via multipart/form-data with a field named `image`. It returns a transparent PNG with the background removed.

### Python Example

```python
import requests

# Upload a local image file
def remove_background_from_file(image_path):
    # URL of the deployed Modal app
    api_url = "https://pollinations--u2net-bg-remover-fastapi-app.modal.run/remove-background"
    
    # Send the request
    with open(image_path, "rb") as img_file:
        files = {"image": (image_path, img_file, "image/jpeg")}
        response = requests.post(api_url, files=files)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Save the processed image (transparent PNG)
        with open("result.png", "wb") as f:
            f.write(response.content)
        print("Background removed successfully!")
        return "result.png"
    else:
        print(f"Error: {response.text}")
        return None

# Process an image from a URL
def remove_background_from_url(image_url):
    # URL of the deployed Modal app
    api_url = "https://pollinations--u2net-bg-remover-fastapi-app.modal.run/remove-background"
    
    # Download the image
    response = requests.get(image_url)
    image_data = BytesIO(response.content)
    
    # Send the image to your background removal service
    files = {"image": ("image.jpg", image_data, "image/jpeg")}
    response = requests.post(api_url, files=files)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Save the processed image (transparent PNG)
        with open("result.png", "wb") as f:
            f.write(response.content)
        print("Background removed successfully!")
        return "result.png"
    else:
        print(f"Error: {response.text}")
        return None

# Example usage
if __name__ == "__main__":
    # Method 1: Local file
    remove_background_from_file("path/to/your/image.jpg")
    
    # Method 2: Image URL
    remove_background_from_url("https://example.com/path/to/image.jpg")
```

### JavaScript Example

```javascript
// Function to remove background from a file input
async function removeBackgroundFromFile(fileInput) {
  const file = fileInput.files[0];
  if (!file) {
    console.error("No file selected");
    return null;
  }

  // URL of the deployed Modal app
  const apiUrl = "https://pollinations--u2net-bg-remover-fastapi-app.modal.run/remove-background";
  
  // Create a FormData object and append the file
  const formData = new FormData();
  formData.append("image", file);

  try {
    // Send the request
    const response = await fetch(apiUrl, {
      method: "POST",
      body: formData,
    });

    // Check if request was successful
    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    // Get the response as a blob
    const resultBlob = await response.blob();
    
    // Create a URL for the blob
    const imageUrl = URL.createObjectURL(resultBlob);
    return imageUrl;
  } catch (error) {
    console.error("Error removing background:", error);
    return null;
  }
}

// Function to remove background from an image URL
async function removeBackgroundFromUrl(imageUrl) {
  // URL of the deployed Modal app
  const apiUrl = "https://pollinations--u2net-bg-remover-fastapi-app.modal.run/remove-background";

  try {
    // First, fetch the image from the URL
    const imageResponse = await fetch(imageUrl);
    if (!imageResponse.ok) {
      throw new Error('Failed to fetch image from URL');
    }
    
    // Get the image data as a blob
    const imageBlob = await imageResponse.blob();
    
    // Create a FormData object and append the image blob
    const formData = new FormData();
    formData.append("image", imageBlob, "image.jpg");
    
    // Send the request to the background removal service
    const response = await fetch(apiUrl, {
      method: "POST",
      body: formData,
    });
    
    // Check if request was successful
    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }
    
    // Get the response as a blob
    const resultBlob = await response.blob();
    
    // Create a URL for the blob
    const resultImageUrl = URL.createObjectURL(resultBlob);
    
    return resultImageUrl;
  } catch (error) {
    console.error("Error removing background:", error);
    return null;
  }
}

// Example usage with a file input
document.getElementById("imageInput").addEventListener("change", async (event) => {
  const resultUrl = await removeBackgroundFromFile(event.target);
  if (resultUrl) {
    // Display the result
    const img = document.createElement("img");
    img.src = resultUrl;
    document.getElementById("result").appendChild(img);
    
    // Create download link
    const downloadLink = document.createElement("a");
    downloadLink.href = resultUrl;
    downloadLink.download = "removed_background.png";
    downloadLink.textContent = "Download Image";
    document.getElementById("result").appendChild(downloadLink);
  }
});

// Example usage with an image URL
document.getElementById("processUrlBtn").addEventListener("click", async () => {
  const imageUrl = document.getElementById("urlInput").value;
  const resultUrl = await removeBackgroundFromUrl(imageUrl);
  if (resultUrl) {
    // Display the result
    const img = document.createElement("img");
    img.src = resultUrl;
    document.getElementById("result").appendChild(img);
  }
});
```

### Complete HTML Example

Here's a complete HTML example that you can use as a starting point for integrating with the API:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Background Removal Example</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    .container {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .section {
      border: 1px solid #ccc;
      padding: 20px;
      border-radius: 8px;
    }
    .result-container {
      margin-top: 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    img {
      max-width: 100%;
      border: 1px dashed #ccc;
      margin: 10px 0;
    }
    .btn {
      padding: 8px 16px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    .btn:hover {
      background-color: #45a049;
    }
    #urlInput {
      width: 100%;
      padding: 8px;
      margin-bottom: 10px;
    }
  </style>
</head>
<body>
  <h1>U-2-Net Background Removal</h1>
  
  <div class="container">
    <div class="section">
      <h2>Upload Local Image</h2>
      <input type="file" id="imageInput" accept="image/*">
      <div id="localResult" class="result-container"></div>
    </div>
    
    <div class="section">
      <h2>Process Image from URL</h2>
      <input type="text" id="urlInput" placeholder="Enter image URL...">
      <button id="processUrlBtn" class="btn">Process URL</button>
      <div id="urlResult" class="result-container"></div>
    </div>
  </div>

  <script>
    const apiUrl = "https://pollinations--u2net-bg-remover-fastapi-app.modal.run/remove-background";
    
    // Function to process local file upload
    async function processLocalImage(fileInput) {
      const file = fileInput.files[0];
      if (!file) return;
      
      const localResult = document.getElementById("localResult");
      localResult.innerHTML = "<p>Processing...</p>";
      
      const formData = new FormData();
      formData.append("image", file);
      
      try {
        const response = await fetch(apiUrl, {
          method: "POST",
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }
        
        const resultBlob = await response.blob();
        const imageUrl = URL.createObjectURL(resultBlob);
        
        localResult.innerHTML = `
          <h3>Result:</h3>
          <img src="${imageUrl}" alt="Processed Image">
          <a href="${imageUrl}" download="background_removed.png" class="btn">Download</a>
        `;
      } catch (error) {
        localResult.innerHTML = `<p>Error: ${error.message}</p>`;
        console.error("Error removing background:", error);
      }
    }
    
    // Function to process image from URL
    async function processImageFromUrl() {
      const imageUrl = document.getElementById("urlInput").value.trim();
      if (!imageUrl) {
        alert("Please enter a valid URL");
        return;
      }
      
      const urlResult = document.getElementById("urlResult");
      urlResult.innerHTML = "<p>Processing...</p>";
      
      try {
        // First, fetch the image from the URL
        const imageResponse = await fetch(imageUrl);
        if (!imageResponse.ok) {
          throw new Error('Failed to fetch image from URL');
        }
        
        // Get the image data as a blob
        const imageBlob = await imageResponse.blob();
        
        // Create a FormData object and append the image blob
        const formData = new FormData();
        formData.append("image", imageBlob, "image.jpg");
        
        // Send to background removal service
        const response = await fetch(apiUrl, {
          method: "POST",
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }
        
        const resultBlob = await response.blob();
        const resultImageUrl = URL.createObjectURL(resultBlob);
        
        urlResult.innerHTML = `
          <h3>Result:</h3>
          <img src="${resultImageUrl}" alt="Processed Image">
          <a href="${resultImageUrl}" download="background_removed.png" class="btn">Download</a>
        `;
      } catch (error) {
        urlResult.innerHTML = `<p>Error: ${error.message}</p>`;
        console.error("Error removing background:", error);
      }
    }
    
    // Event listeners
    document.getElementById("imageInput").addEventListener("change", (event) => {
      processLocalImage(event.target);
    });
    
    document.getElementById("processUrlBtn").addEventListener("click", processImageFromUrl);
  </script>
</body>
</html>
```

### cURL Example

Here's how to use the API with cURL from the command line:

```bash
# Upload a local image file
curl -X POST \
  -F "image=@path/to/your/image.jpg" \
  https://pollinations--u2net-bg-remover-fastapi-app.modal.run/remove-background \
  --output result.png
```

### Node.js Example

```javascript
const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');

// URL of the deployed Modal app
const apiUrl = "https://pollinations--u2net-bg-remover-fastapi-app.modal.run/remove-background";

async function removeBackground(imagePath) {
  try {
    // Create form data
    const formData = new FormData();
    formData.append('image', fs.createReadStream(imagePath));
    
    // Make the request
    const response = await axios.post(apiUrl, formData, {
      headers: formData.getHeaders(),
      responseType: 'arraybuffer'
    });
    
    // Save the result
    const outputPath = 'result.png';
    fs.writeFileSync(outputPath, response.data);
    console.log(`Background removed successfully! Result saved to ${outputPath}`);
    return outputPath;
  } catch (error) {
    console.error('Error removing background:', error.message);
    return null;
  }
}

// Example usage
removeBackground('path/to/your/image.jpg');
```

### Integration Considerations

1. **CORS Limitations**: If you're calling the API from a web browser on a different domain, you might encounter CORS issues. In this case, you may need to:
   - Call the API from your backend server
   - Set up a proxy server
   - Contact the Modal team owner to add CORS headers to the deployment

2. **Error Handling**: Always implement proper error handling to account for:
   - Network failures
   - Invalid images
   - Server errors
   - Timeout issues (for large images)

3. **File Size Limits**: The API may have limits on file size. Consider compressing large images before sending them.

4. **Image Formats**: While the API can handle most common image formats (JPEG, PNG, etc.), for best results, provide clear images with distinct foreground and background.

## Acknowledgments

- Original U-2-Net implementation by [Xuebin Qin et al.](https://github.com/xuebinqin/U-2-Net)
- Image processing using OpenCV and PIL
- Web service built with FastAPI
- Deployment on Modal.com

## License

This project is released under the same license as the original U-2-Net implementation (Apache 2.0).
