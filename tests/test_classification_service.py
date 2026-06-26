import pytest

from backend import classification_service
from backend.classification_service import ClassificationSettings


SIMULATED_SETTINGS = ClassificationSettings(
    model="test-model",
    prompt="test prompt",
    detail="low",
    use_simulated_predictions=True,
)


LIVE_SETTINGS = ClassificationSettings(
    model="test-model",
    prompt="test prompt",
    detail="low",
    use_simulated_predictions=False,
)


def test_classify_image_path_uses_simulated_classifier(monkeypatch, image_file):
    image_path = image_file("sample.jpg")
    monkeypatch.setattr(
        classification_service,
        "classify_image_simulated",
        lambda path: "No" if path == image_path else "unexpected",
    )

    assert classification_service.classify_image_path(
        image_path,
        settings=SIMULATED_SETTINGS,
    ) == "No"


def test_classify_image_path_requires_client_for_live_predictions(image_file):
    image_path = image_file("sample.jpg")

    with pytest.raises(RuntimeError, match="OpenAI client is not initialized"):
        classification_service.classify_image_path(
            image_path,
            client=None,
            settings=LIVE_SETTINGS,
        )


def test_classify_image_bytes_validates_image(monkeypatch, image_file):
    image_path = image_file("sample.png")
    monkeypatch.setattr(
        classification_service,
        "classify_image_path",
        lambda path, client=None, settings=None: "Yes",
    )

    result = classification_service.classify_image_bytes(
        image_path.read_bytes(),
        "sample.png",
        settings=SIMULATED_SETTINGS,
    )

    assert result == "Yes"


def test_classify_image_bytes_rejects_invalid_image():
    with pytest.raises(ValueError, match="valid image"):
        classification_service.classify_image_bytes(
            b"not an image",
            "sample.jpg",
            settings=SIMULATED_SETTINGS,
        )
