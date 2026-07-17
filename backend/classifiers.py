import base64
import mimetypes

import openai
from openai import OpenAI
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def create_openai_client(api_key, timeout=15.0):
    return OpenAI(api_key=api_key, timeout=timeout)


def encode_image(image_path):
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def get_image_mime_type(image_path):
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
def classify_image_openai(client, image_path, model, prompt, detail="auto"):
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

def create_gemini_client(api_key):
    return genai.Client(api_key=api_key)


def classify_image_local(image_path, model, prompt, detail="auto"):
    pass

def classify_image_simulated(image_path):
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
def classify_image_gemini(client, image_path, model, prompt):
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
