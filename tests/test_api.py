import pytest
import openai
from fastapi.testclient import TestClient
from backend import api
from backend.api import app

client = TestClient(app)


def test_api_maps_timeout_error(monkeypatch):
    def mock_classify(*args, **kwargs):
        raise openai.APITimeoutError(request=None)

    monkeypatch.setattr(api, "classify_image_bytes", mock_classify)

    response = client.post(
        "/classify",
        files={"file": ("test.png", b"fake-bytes", "image/png")}
    )

    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]


def test_api_maps_connection_error(monkeypatch):
    def mock_classify(*args, **kwargs):
        raise openai.APIConnectionError(request=None)

    monkeypatch.setattr(api, "classify_image_bytes", mock_classify)

    response = client.post(
        "/classify",
        files={"file": ("test.png", b"fake-bytes", "image/png")}
    )

    assert response.status_code == 503
    assert "connection failed" in response.json()["detail"]


def test_api_maps_rate_limit_error(monkeypatch):
    class FakeRequest:
        pass

    class FakeResponse:
        request = FakeRequest()
        status_code = 429
        headers = {}

    def mock_classify(*args, **kwargs):
        raise openai.RateLimitError(
            message="Rate limit exceeded",
            response=FakeResponse(),
            body=None
        )

    monkeypatch.setattr(api, "classify_image_bytes", mock_classify)

    response = client.post(
        "/classify",
        files={"file": ("test.png", b"fake-bytes", "image/png")}
    )

    assert response.status_code == 429
    assert "rate limit exceeded" in response.json()["detail"]
