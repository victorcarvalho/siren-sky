import base64

from backend import classifiers


def test_encode_image_returns_base64(image_file):
    image_path = image_file("encoded.png")

    encoded = classifiers.encode_image(image_path)

    assert encoded == base64.b64encode(image_path.read_bytes()).decode("utf-8")


def test_get_image_mime_type_uses_extension(image_file):
    image_path = image_file("photo.png")

    assert classifiers.get_image_mime_type(image_path) == "image/png"


def test_classify_image_openai_uses_client_and_strips_output(image_file):
    calls = {}

    class FakeResponse:
        output_text = "  Yes  "

    class FakeResponses:
        def create(self, **kwargs):
            calls["kwargs"] = kwargs
            return FakeResponse()

    class FakeClient:
        responses = FakeResponses()

    result = classifiers.classify_image_openai(
        client=FakeClient(),
        image_path=image_file("sample.jpg"),
        model="test-model",
        prompt="Is there garbage here?",
        detail="high",
    )

    assert result == "Yes"
    assert calls["kwargs"]["model"] == "test-model"
    content = calls["kwargs"]["input"][0]["content"]
    assert content[0]["text"] == "Is there garbage here?"
    assert content[1]["detail"] == "high"
    assert content[1]["image_url"].startswith("data:image/jpeg;base64,")


def test_classify_image_simulated_is_deterministic(image_file):
    image_path = image_file("sample.jpg")

    first = classifiers.classify_image_simulated(image_path)
    second = classifiers.classify_image_simulated(image_path)

    assert first == second
    assert first in {"Yes", "No"}
