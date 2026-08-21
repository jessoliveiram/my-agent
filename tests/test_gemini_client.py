from unittest.mock import Mock

import pytest
import requests

from src import gemini_client


def test_extract_text_handles_nested_candidates():
    payload = {"candidates": [{"content": {"parts": [{"text": "hello"}]}}]}

    assert gemini_client._extract_text(payload) == "hello"


def test_generate_text_rejects_empty_prompt():
    with pytest.raises(ValueError):
        gemini_client.generate_text(" ")


def test_generate_text_requires_api_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr(gemini_client.dotenv, "load_dotenv", lambda: None)

    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY"):
        gemini_client.generate_text("summarize")


def test_rest_fallback_returns_generated_text(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "summary"}]}}]
    }
    monkeypatch.setattr(gemini_client.requests, "post", Mock(return_value=response))

    result = gemini_client._rest_fallback("api-key", "model", "prompt")

    assert result == "summary"
    response.raise_for_status.assert_called_once()


def test_rest_fallback_retries_and_sanitizes_error(monkeypatch):
    post = Mock(side_effect=requests.Timeout("api-key=secret"))
    sleep = Mock()
    monkeypatch.setattr(gemini_client.requests, "post", post)
    monkeypatch.setattr(gemini_client.time, "sleep", sleep)

    with pytest.raises(RuntimeError, match="Generative API REST request failed") as error:
        gemini_client._rest_fallback("api-key", "model", "prompt")

    assert post.call_count == 3
    assert sleep.call_count == 2
    assert "secret" not in str(error.value)


def test_generate_text_uses_sdk_and_returns_text(monkeypatch):
    class FakeModel:
        name = "gemini-test"
        supported_actions = ["generateContent"]

    models = Mock()
    models.list.return_value = [FakeModel()]
    models.generate_content.return_value = Mock(text="generated")
    client = Mock(models=models)
    genai = Mock()
    genai.Client.return_value = client

    monkeypatch.setenv("GOOGLE_API_KEY", "api-key")
    monkeypatch.setattr(gemini_client, "genai", genai)

    assert gemini_client.generate_text("summarize") == "generated"
    genai.Client.assert_called_once_with(api_key="api-key")
    models.generate_content.assert_called_once_with(
        model="gemini-2.0-flash", contents="summarize"
    )
