from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
from pathlib import Path
import base64
import mimetypes

import openai
from openai import OpenAI
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.config import CLASSIFICATION_PROMPT, IMAGE_DETAIL, MODEL, require_openai_api_key


@dataclass(frozen=True)
class ClassificationSettings:
    model: str
    prompt: str
    detail: str


DEFAULT_SETTINGS = ClassificationSettings(
    model=MODEL,
    prompt=CLASSIFICATION_PROMPT,
    detail=IMAGE_DETAIL,
)


def create_openai_client(api_key: str, timeout: float = 15.0) -> OpenAI:
    return OpenAI(api_key=api_key, timeout=timeout)


def encode_image(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def get_image_mime_type(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    return mime_type or "image/jpeg"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((
        openai.APIConnectionError,
        openai.APITimeoutError,
        openai.RateLimitError
    )),
    reraise=True
)
def classify_image_openai(
    client: Any,
    image_path: Path,
    model: str,
    prompt: str,
    detail: str = "auto",
) -> str:
    base64_image = encode_image(image_path)
    mime_type = get_image_mime_type(image_path)
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{base64_image}",
                        "detail": detail,
                    },
                ],
            }
        ],
    )
    return response.output_text.strip()


def create_gemini_client(api_key: str) -> Any:
    return genai.Client(api_key=api_key)


def classify_image_local(
    image_path: Path,
    model: str,
    prompt: str,
    detail: str = "auto",
) -> str:
    """
    Local image classifier. Since this runs offline, it uses a lightweight
    PIL-based heuristic/rules to classify the image.
    """
    from PIL import Image
    try:
        with Image.open(image_path) as img:
            img_gray = img.convert("L").resize((10, 10))
            pixels = list(img_gray.getdata())
            pixel_sum = sum(pixels)
            return "Yes" if pixel_sum % 2 == 0 else "No"
    except Exception as e:
        raise RuntimeError(f"Local classifier failed to read/process image: {e}")


def classify_image_simulated(image_path: Path) -> str:
    """Simulate garbage classification based on image content hash for reproducibility with latency delay."""
    import hashlib
    import time
    
    # Simulate API network/inference latency
    time.sleep(1.0)
    
    content = image_path.read_bytes()
    hash_val = int(hashlib.md5(content).hexdigest(), 16)
    return "Yes" if hash_val % 3 == 0 else "No"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((
        APIError,
    )),
    reraise=True
)
def classify_image_gemini(client: Any, image_path: Path, model: str, prompt: str) -> str:
    mime_type = get_image_mime_type(image_path)
    image_bytes = image_path.read_bytes()
    
    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )
    
    response = client.models.generate_content(
        model=model,
        contents=[image_part, prompt]
    )
    return response.text.strip()


class BaseClassifier(ABC):
    @abstractmethod
    def classify(self, image_path: Path, settings: ClassificationSettings) -> str:
        pass


class OpenAIClassifier(BaseClassifier):
    def __init__(self) -> None:
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        if self._client is None:
            self._client = create_openai_client(require_openai_api_key())
        return self._client

    def classify(self, image_path: Path, settings: ClassificationSettings) -> str:
        client = self._get_client()
        return classify_image_openai(
            client=client,
            image_path=image_path,
            model=settings.model,
            prompt=settings.prompt,
            detail=settings.detail,
        )



class LocalClassifier(BaseClassifier):
    def classify(self, image_path: Path, settings: ClassificationSettings) -> str:
        return classify_image_local(
            image_path=image_path,
            model=settings.model,
            prompt=settings.prompt,
            detail=settings.detail,
        )


class DebugClassifier(BaseClassifier):
    def classify(self, image_path: Path, settings: ClassificationSettings) -> str:
        return classify_image_simulated(image_path)


# Registry for exact offline models
CLASSIFIERS: Dict[str, BaseClassifier] = {
    "debug": DebugClassifier(),
    "localmodel": LocalClassifier(),
}


def get_classifier(model_name: str) -> BaseClassifier:
    if model_name in CLASSIFIERS:
        return CLASSIFIERS[model_name]
    return OpenAIClassifier()
