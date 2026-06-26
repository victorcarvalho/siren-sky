import base64
import mimetypes

from openai import OpenAI


def create_openai_client(api_key):
    return OpenAI(api_key=api_key)


def encode_image(image_path):
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def get_image_mime_type(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    return mime_type or "image/jpeg"


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

def classify_image_local(image_path, model, prompt, detail="auto"):
    pass

def classify_image_simulated(image_path):
    """Simulate garbage classification based on image path hash for reproducibility."""
    import hashlib
    hash_val = int(hashlib.md5(str(image_path).encode()).hexdigest(), 16)
    return "Yes" if hash_val % 3 == 0 else "No"
