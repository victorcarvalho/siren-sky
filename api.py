"""FastAPI service for image classification."""

import io
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn

from classifiers import classify_image_openai, classify_image_simulated, create_openai_client
from config import (
    CLASSIFICATION_PROMPT,
    IMAGE_DETAIL,
    MODEL,
    USE_SIMULATED_PREDICTIONS,
    require_openai_api_key,
)

app = FastAPI(
    title="Siren Sky Classifier API",
    description="API for classifying images using OpenAI vision models",
    version="1.0.0",
)

# Initialize client at startup if not using simulated predictions
client = None


@app.on_event("startup")
async def startup_event():
    global client
    if not USE_SIMULATED_PREDICTIONS:
        try:
            client = create_openai_client(require_openai_api_key())
        except RuntimeError as e:
            print(f"Warning: {e}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "siren-sky-classifier"}


@app.post("/classify")
async def classify(file: UploadFile = File(...)):
    """
    Classify an uploaded image.
    
    Returns classification result from the configured model.
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Save to temporary file for processing
        temp_path = Path(f"/tmp/{file.filename}")
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Classify based on mode
        if USE_SIMULATED_PREDICTIONS:
            classification = classify_image_simulated(temp_path)
        else:
            if client is None:
                raise HTTPException(
                    status_code=503,
                    detail="OpenAI client not initialized. Check OPENAI_API_KEY."
                )
            classification = classify_image_openai(
                client=client,
                image_path=temp_path,
                model=MODEL,
                prompt=CLASSIFICATION_PROMPT,
                detail=IMAGE_DETAIL,
            )
        
        return {
            "filename": file.filename,
            "classification": classification,
            "model": MODEL,
            "simulated": USE_SIMULATED_PREDICTIONS,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.post("/classify-base64")
async def classify_base64(image_data: dict):
    """
    Classify an image provided as base64-encoded data.
    
    Expected JSON body:
    {
        "image": "base64_encoded_image_string",
        "filename": "optional_filename.jpg"
    }
    """
    import base64
    
    try:
        image_b64 = image_data.get("image")
        filename = image_data.get("filename", "image.jpg")
        
        if not image_b64:
            raise HTTPException(status_code=400, detail="Missing 'image' field")
        
        # Decode base64
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save to temporary file
        temp_path = Path(f"/tmp/{filename}")
        with open(temp_path, "wb") as f:
            f.write(image_bytes)
        
        # Classify
        if USE_SIMULATED_PREDICTIONS:
            classification = classify_image_simulated(temp_path)
        else:
            if client is None:
                raise HTTPException(
                    status_code=503,
                    detail="OpenAI client not initialized. Check OPENAI_API_KEY."
                )
            classification = classify_image_openai(
                client=client,
                image_path=temp_path,
                model=MODEL,
                prompt=CLASSIFICATION_PROMPT,
                detail=IMAGE_DETAIL,
            )
        
        return {
            "filename": filename,
            "classification": classification,
            "model": MODEL,
            "simulated": USE_SIMULATED_PREDICTIONS,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
