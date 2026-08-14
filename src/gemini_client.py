"""Wrapper for calling Gemini (Generative AI) using the official google-genai SDK.

Small robustness improvements: safer model listing, clearer REST fallback helper,
and improved error messages to aid unit testing and failure diagnosis.
"""
import os
import dotenv
import time
from typing import List

try:
    from google import genai
except Exception:  # pragma: no cover - environment-specific
    genai = None

import requests


def _rest_fallback(api_key: str, model: str, prompt: str) -> str:
    """Call the Generative Language REST endpoint as a final fallback."""
    endpoint = f"https://generativelanguage.googleapis.com/v1beta2/models/{model}:generateText"
    params = {"key": api_key}
    body = {"prompt": {"text": prompt}}
    backoff = 1
    for attempt in range(3):
        try:
            resp = requests.post(endpoint, params=params, json=body, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if "candidates" in data and data["candidates"]:
                return data["candidates"][0].get("output", data["candidates"][0].get("content", ""))
            if "output" in data:
                return data["output"]
            return str(data)
        except requests.RequestException as e:
            if attempt < 2:
                time.sleep(backoff)
                backoff *= 2
                continue
            raise RuntimeError(f"Generative API REST failed: {e}") from e


def generate_text(prompt: str, model: str = "gemini-3.5-flash") -> str:
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
        # Prefer raising a clear error to help tests/devs install the SDK.
        raise RuntimeError("google.genai is not available in this environment. Install the Google GenAI SDK or set up REST fallback.")

    client = genai.Client(api_key=api_key)

    # Build a dynamic fallback list from the GenAI service: prefer models that
    # advertise generation capabilities. If listing fails, fall back to a
    # conservative static list.
    candidates: List[str] = [model]
    try:
        available = client.models.list()
        for m in available:
            name = getattr(m, 'name', None)
            if not name or name in candidates:
                continue
            actions = getattr(m, 'supported_actions', None) or getattr(m, 'supportedActions', None) or []
            try:
                if any('generate' in str(a).lower() for a in actions):
                    candidates.append(name)
            except Exception:
                # ignore malformed metadata
                continue
    except Exception:
        # if model listing fails (network, permissions), use a safe static fallback
        candidates.extend(["gemini-1.0"])

    last_exc = None
    for m in candidates:
        backoff = 1
        for attempt in range(4):
            try:
                response = client.models.generate_content(model=m, contents=prompt)
                # genai response may expose text or candidates
                if hasattr(response, "text") and response.text:
                    return response.text
                if hasattr(response, "candidates") and response.candidates:
                    first = response.candidates[0]
                    return getattr(first, "content", getattr(first, "output", str(first)))
                return str(response)
            except Exception as e:
                last_exc = e
                msg = str(e)
                # if server busy (503), retry with backoff
                if "503" in msg or "UNAVAILABLE" in msg or "high demand" in msg.lower():
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                # other errors -> break and try next model
                break

    # REST fallback using Generative Language API
    return _rest_fallback(api_key, candidates[-1], prompt)
