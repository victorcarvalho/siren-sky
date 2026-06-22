import pytest

import config


def test_require_openai_api_key_raises_when_missing(monkeypatch):
    monkeypatch.setattr(config, "OPENAI_API_KEY", None)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not set"):
        config.require_openai_api_key()


def test_require_openai_api_key_returns_value(monkeypatch):
    monkeypatch.setattr(config, "OPENAI_API_KEY", "sk-test")

    assert config.require_openai_api_key() == "sk-test"