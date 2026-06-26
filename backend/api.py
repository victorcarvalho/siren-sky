"""FastAPI service for image classification."""

import base64
import binascii

from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn

from backend.classification_service import DEFAULT_SETTINGS, classify_image_bytes
from backend.classifiers import create_openai_client
from backend.config import require_openai_api_key
from backend.schemas import Base64ClassificationRequest, ClassificationResponse, HealthResponse

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
    if not DEFAULT_SETTINGS.use_simulated_predictions:
        try:
            client = create_openai_client(require_openai_api_key())
        except RuntimeError as e:
            print(f"Warning: {e}")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="ok", service="siren-sky-classifier")


@app.post("/classify", response_model=ClassificationResponse)
async def classify(file: UploadFile = File(...)):
    """
    Classify an uploaded image.
    
    Returns classification result from the configured model.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        classification = classify_image_bytes(
            image_bytes=contents,
            filename=file.filename,
            client=client,
            settings=DEFAULT_SETTINGS,
        )

        return ClassificationResponse(
            filename=file.filename,
            classification=classification,
            model=DEFAULT_SETTINGS.model,
            simulated=DEFAULT_SETTINGS.use_simulated_predictions,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@app.post("/classify-base64", response_model=ClassificationResponse)
async def classify_base64(image_data: Base64ClassificationRequest):
    """
    Classify an image provided as base64-encoded data.
    
    Expected JSON body:
    {
        "image": "base64_encoded_image_string",
        "filename": "optional_filename.jpg"
    }
    """
    try:
        image_bytes = base64.b64decode(image_data.image, validate=True)
        classification = classify_image_bytes(
            image_bytes=image_bytes,
            filename=image_data.filename,
            client=client,
            settings=DEFAULT_SETTINGS,
        )

        return ClassificationResponse(
            filename=image_data.filename,
            classification=classification,
            model=DEFAULT_SETTINGS.model,
            simulated=DEFAULT_SETTINGS.use_simulated_predictions,
        )
    except binascii.Error as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
