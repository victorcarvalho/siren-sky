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


GEMINI_SETTINGS = ClassificationSettings(
    model="gemini-2.0-flash",
    prompt="test prompt",
    detail="low",
    use_simulated_predictions=False,
)


def test_classify_image_path_uses_gemini_classifier_for_gemini_models(monkeypatch, image_file):
    image_path = image_file("sample.jpg")
    calls = {}
    
    def mock_classify_gemini(client, image_path, model, prompt):
        calls["client"] = client
        calls["img_path"] = image_path
        calls["model"] = model
        calls["prompt"] = prompt
        return "Yes"

    monkeypatch.setattr(
        classification_service,
        "classify_image_gemini",
        mock_classify_gemini
    )

    result = classification_service.classify_image_path(
        image_path,
        client="fake-gemini-client",
        settings=GEMINI_SETTINGS,
    )

    assert result == "Yes"
    assert calls["client"] == "fake-gemini-client"
    assert calls["img_path"] == image_path
    assert calls["model"] == "gemini-2.0-flash"
    assert calls["prompt"] == "test prompt"


def test_classify_image_path_requires_gemini_client_for_live_predictions(image_file):
    image_path = image_file("sample.jpg")

    with pytest.raises(RuntimeError, match="Gemini client is not initialized"):
        classification_service.classify_image_path(
            image_path,
            client=None,
            settings=GEMINI_SETTINGS,
        )

