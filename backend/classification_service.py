import tempfile
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from backend.classifiers import ClassificationSettings, DEFAULT_SETTINGS, get_classifier


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
    settings: ClassificationSettings = DEFAULT_SETTINGS,
) -> str:
    classifier = get_classifier(settings.model)
    return classifier.classify(image_path, settings)


def classify_image_bytes(
    image_bytes: bytes,
    filename: str,
    settings: ClassificationSettings = DEFAULT_SETTINGS,
) -> str:
    validate_image_bytes(image_bytes)
    image_path = write_temp_image(filename, image_bytes)

    try:
        return classify_image_path(image_path, settings=settings)
    finally:
        image_path.unlink(missing_ok=True)
