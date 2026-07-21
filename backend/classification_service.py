from typing import Any, Optional
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from backend.classifiers import classify_image_openai, classify_image_simulated, classify_image_local
from backend.config import CLASSIFICATION_PROMPT, IMAGE_DETAIL, MODEL


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


def validate_image_bytes(image_bytes: bytes) -> None:
    try:
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(image_bytes)
            temp_file.flush()
            with Image.open(temp_file.name) as image:
                image.verify()
    except UnidentifiedImageError as exc:
        raise ValueError("File must be a valid image") from exc


def write_temp_image(filename: str, image_bytes: bytes) -> Path:
    suffix = Path(filename).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(image_bytes)
        return Path(temp_file.name)


def classify_image_path(
    image_path: Path,
    client: Optional[Any] = None,
    settings: ClassificationSettings = DEFAULT_SETTINGS,
) -> str:
    if settings.model == "debug":
        return classify_image_simulated(image_path)

    if settings.model == "localmodel":
        return classify_image_local(
            image_path=image_path,
            model=settings.model,
            prompt=settings.prompt,
            detail=settings.detail,
        )

    if client is None:
        raise RuntimeError("OpenAI client is not initialized. Check API keys.")

    return classify_image_openai(
        client=client,
        image_path=image_path,
        model=settings.model,
        prompt=settings.prompt,
        detail=settings.detail,
    )


def classify_image_bytes(
    image_bytes: bytes,
    filename: str,
    client: Optional[Any] = None,
    settings: ClassificationSettings = DEFAULT_SETTINGS,
) -> str:
    validate_image_bytes(image_bytes)
    image_path = write_temp_image(filename, image_bytes)

    try:
        return classify_image_path(image_path, client=client, settings=settings)
    finally:
        image_path.unlink(missing_ok=True)

