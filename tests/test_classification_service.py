import pytest

from backend import classification_service
from backend import classifiers
from backend.classifiers import ClassificationSettings


SIMULATED_SETTINGS = ClassificationSettings(
    model="debug",
    prompt="test prompt",
    detail="low",
)


LIVE_SETTINGS = ClassificationSettings(
    model="test-model",
    prompt="test prompt",
    detail="low",
)


def test_classify_image_path_uses_simulated_classifier(monkeypatch, image_file):
    image_path = image_file("sample.jpg")
    monkeypatch.setattr(
        classifiers,
        "classify_image_simulated",
        lambda path: "No" if path == image_path else "unexpected",
    )

    assert classification_service.classify_image_path(
        image_path,
        settings=SIMULATED_SETTINGS,
    ) == "No"


def test_classify_image_path_requires_api_key_for_live_predictions(monkeypatch, image_file):
    image_path = image_file("sample.jpg")

    from backend import config
    monkeypatch.setattr(config, "OPENAI_API_KEY", None)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not set"):
        classification_service.classify_image_path(
            image_path,
            settings=LIVE_SETTINGS,
        )


def test_classify_image_bytes_validates_image(monkeypatch, image_file):
    image_path = image_file("sample.png")
    monkeypatch.setattr(
        classification_service,
        "classify_image_path",
        lambda path, settings=None: "Yes",
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


LOCAL_SETTINGS = ClassificationSettings(
    model="localmodel",
    prompt="test prompt",
    detail="low",
)


def test_classify_image_path_uses_local_classifier_for_local_models(monkeypatch, image_file):
    image_path = image_file("sample.jpg")
    calls = {}
    
    def mock_classify_local(image_path, model, prompt, detail):
        calls["img_path"] = image_path
        calls["model"] = model
        calls["prompt"] = prompt
        calls["detail"] = detail
        return "Yes"

    # Patch the function imported in strategies/classifiers
    monkeypatch.setattr(
        classifiers,
        "classify_image_local",
        mock_classify_local
    )

    result = classification_service.classify_image_path(
        image_path,
        settings=LOCAL_SETTINGS,
    )

    assert result == "Yes"
    assert calls["img_path"] == image_path
    assert calls["model"] == "localmodel"
    assert calls["prompt"] == "test prompt"
    assert calls["detail"] == "low"
