import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from backend.classifiers import classify_image_openai, classify_image_simulated
from backend.config import CLASSIFICATION_PROMPT, IMAGE_DETAIL, MODEL, USE_SIMULATED_PREDICTIONS


@dataclass(frozen=True)
class ClassificationSettings:
    model: str
    prompt: str
    detail: str
    use_simulated_predictions: bool


DEFAULT_SETTINGS = ClassificationSettings(
    model=MODEL,
    prompt=CLASSIFICATION_PROMPT,
    detail=IMAGE_DETAIL,
    use_simulated_predictions=USE_SIMULATED_PREDICTIONS,
)


def validate_image_bytes(image_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(image_bytes)
            temp_file.flush()
            with Image.open(temp_file.name) as image:
                image.verify()
    except UnidentifiedImageError as exc:
        raise ValueError("File must be a valid image") from exc


def write_temp_image(filename, image_bytes):
    suffix = Path(filename).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(image_bytes)
        return Path(temp_file.name)


def classify_image_path(image_path, client=None, settings=DEFAULT_SETTINGS):
    if settings.use_simulated_predictions:
        return classify_image_simulated(image_path)

    if client is None:
        raise RuntimeError("OpenAI client is not initialized. Check OPENAI_API_KEY.")

    return classify_image_openai(
        client=client,
        image_path=image_path,
        model=settings.model,
        prompt=settings.prompt,
        detail=settings.detail,
    )


def classify_image_bytes(image_bytes, filename, client=None, settings=DEFAULT_SETTINGS):
    validate_image_bytes(image_bytes)
    image_path = write_temp_image(filename, image_bytes)

    try:
        return classify_image_path(image_path, client=client, settings=settings)
    finally:
        image_path.unlink(missing_ok=True)
