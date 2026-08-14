"""Wrapper for calling Gemini (Generative AI) using the official google-genai SDK.

Small robustness improvements: safer model listing, clearer REST fallback helper,
and improved error messages to aid unit testing and failure diagnosis.
"""
import os
import time
from typing import Any, List

import dotenv
import requests

try:
    from google import genai
except Exception:  # pragma: no cover - environment-specific
    genai = None


def _extract_text(payload: Any) -> str:
    """Normalize Gemini response payloads to plain text."""
    if payload is None:
        return ""

    if isinstance(payload, str):
        return payload

    if isinstance(payload, dict):
        if "text" in payload and isinstance(payload["text"], str):
            return payload["text"]
        if "output" in payload and isinstance(payload["output"], str):
            return payload["output"]

        parts = payload.get("parts")
        if parts:
            texts = []
            for part in parts:
                if isinstance(part, dict):
                    text = part.get("text")
                    if text:
                        texts.append(str(text))
                elif hasattr(part, "text") and part.text:
                    texts.append(str(part.text))
            if texts:
                return "".join(texts)

        content = payload.get("content")
        if content:
            extracted = _extract_text(content)
            if extracted:
                return extracted

        candidates = payload.get("candidates")
        if candidates:
            return _extract_text(candidates[0])

    if hasattr(payload, "text") and payload.text:
        return str(payload.text)

    if hasattr(payload, "candidates") and payload.candidates:
        return _extract_text(payload.candidates[0])

    if hasattr(payload, "content"):
        return _extract_text(payload.content)

    return str(payload)


def _rest_fallback(api_key: str, model: str, prompt: str) -> str:
    """Call the Generative Language REST endpoint as a final fallback."""
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    params = {"key": api_key}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    backoff = 1

    for attempt in range(3):
        try:
            resp = requests.post(endpoint, params=params, json=body, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            candidates = data.get("candidates")
            if candidates:
                return _extract_text(candidates[0])

            if "output" in data:
                return str(data["output"])

            return str(data)
        except requests.RequestException as e:
            if attempt < 2:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise RuntimeError(f"Generative API REST failed: {e}") from e


def generate_text(prompt: str, model: str = "gemini-2.0-flash") -> str:
    """Generate text from Gemini with retries and fallbacks.

    Tries the preferred `model`, retries on transient server errors (503), and
    falls back to alternative models and finally to the REST endpoint if
    necessary.
    """
    dotenv.load_dotenv()

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set GOOGLE_API_KEY in your environment (eg .env or $env:GOOGLE_API_KEY)"
        )

    if genai is None:
        return _rest_fallback(api_key, model, prompt)

    client = genai.Client(api_key=api_key)

    # Build a dynamic fallback list from the GenAI service: prefer models that
    # advertise generation capabilities. If listing fails, fall back to a
    # conservative static list.
    candidates: List[str] = [model]
    try:
        available = client.models.list()
        for m in available:
            name = getattr(m, "name", None)
            if not name or name in candidates:
                continue
            actions = getattr(m, "supported_actions", None) or getattr(m, "supportedActions", None) or []
            try:
                if any("generate" in str(a).lower() for a in actions):
                    candidates.append(name)
            except Exception:
                continue
    except Exception:
        candidates.extend(["gemini-1.5-flash", "gemini-1.5-pro"])

    for candidate in candidates:
        backoff = 1
        for attempt in range(4):
            try:
                response = client.models.generate_content(model=candidate, contents=prompt)
                text = _extract_text(response)
                if text:
                    return text
                return str(response)
            except Exception as e:
                msg = str(e)
                if "503" in msg or "UNAVAILABLE" in msg or "high demand" in msg.lower():
                    if attempt < 3:
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                break

    return _rest_fallback(api_key, candidates[-1], prompt)
