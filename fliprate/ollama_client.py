"""Minimal Ollama HTTP chat client (stdlib only). Localhost only."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Optional


DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
if not DEFAULT_HOST.startswith("http"):
    DEFAULT_HOST = "http://" + DEFAULT_HOST


class OllamaError(RuntimeError):
    pass


def chat(
    model: str,
    messages: list[dict],
    *,
    temperature: float = 0.0,
    seed: int = 0,
    num_predict: int = 96,
    num_ctx: int = 4096,
    host: Optional[str] = None,
    timeout: int = 180,
) -> dict:
    """One non-streaming /api/chat call. Returns {content, raw_response}."""
    url = (host or DEFAULT_HOST).rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "seed": seed,
            "num_predict": num_predict,
            "num_ctx": num_ctx,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise OllamaError(
            f"Ollama request failed ({url}): {e}. "
            "Start the local server with: "
            "OLLAMA_MODELS=/workspace/tools/ollama/models "
            "/workspace/tools/ollama/bin/ollama serve"
        ) from e
    content = (body.get("message") or {}).get("content") or ""
    return {"content": content, "raw_response": body}


def list_models(host: Optional[str] = None, timeout: int = 10) -> list[str]:
    url = (host or DEFAULT_HOST).rstrip("/") + "/api/tags"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return [m.get("name") for m in body.get("models", []) if m.get("name")]
