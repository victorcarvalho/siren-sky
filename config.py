import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).parent
DATASET_PATH = PROJECT_ROOT / os.environ.get("DATASET_PATH", "dataset")
IMAGE_EXTENSIONS = {".jpg", ".jpeg"}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("MODEL", "gpt-4.1-nano")
TRACKING_URI = os.environ.get("TRACKING_URI", "http://127.0.0.1:5000")
EXPERIMENT_NAME = os.environ.get("EXPERIMENT_NAME", "siren-sky-benchmark")
CLASSIFICATION_PROMPT = os.environ.get(
    "CLASSIFICATION_PROMPT",
    "Is there garbage in this image? Answer with yes or no.",
)
IMAGE_DETAIL = os.environ.get("IMAGE_DETAIL", "auto")
USE_SIMULATED_PREDICTIONS = os.environ.get("USE_SIMULATED_PREDICTIONS", "false").lower() == "true"

# Image preprocessing settings (to reduce token usage and API costs)
PREPROCESS_IMAGES = os.environ.get("PREPROCESS_IMAGES", "true").lower() == "true"
MAX_IMAGE_WIDTH = int(os.environ.get("MAX_IMAGE_WIDTH", "1024"))  # Resize width (pixels)
MAX_IMAGE_HEIGHT = int(os.environ.get("MAX_IMAGE_HEIGHT", "1024"))  # Resize height (pixels)
JPEG_QUALITY = int(os.environ.get("JPEG_QUALITY", "85"))  # JPEG compression quality (1-95)


def require_openai_api_key():
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Create a .env file with OPENAI_API_KEY=your_api_key_here "
            "or set the environment variable before running."
        )

    return OPENAI_API_KEY
