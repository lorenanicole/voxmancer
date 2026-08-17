"""Local LLM backend using Ollama.

Ollama runs LLMs locally (CPU or GPU). Perfect for development and testing
before deploying to Runpod or a hosted API.

Setup:
  1. Install Ollama: https://ollama.ai
  2. Start a model: ollama run mistral
  3. Set: LLM_BACKEND=ollama

That's it. No API keys, no network calls outside localhost.
"""
from __future__ import annotations

import os

import httpx


class OllamaLLMClient:
    """Local LLM client via Ollama.

    Mimics the anthropic.Anthropic.messages.create() interface.
    """

    def __init__(self) -> None:
        self._url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self._http = httpx.Client(base_url=self._url, timeout=600.0)

    def messages_create(
        self,
        model: str,
        system: str,
        max_tokens: int,
        messages: list[dict],
    ) -> OllamaLLMResponse:
        """Call Ollama's generate endpoint and return a response."""
        user_message = messages[0]["content"] if messages else ""
        prompt = f"{system}\n\n{user_message}"

        resp = self._http.post(
            "/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "num_predict": max_tokens,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        if "response" not in data:
            raise RuntimeError(f"Ollama returned no response: {data}")

        return OllamaLLMResponse(text=data["response"])


class OllamaLLMResponse:
    """Mock anthropic.Message response."""

    def __init__(self, text: str) -> None:
        self.text = text

    @property
    def content(self) -> list:
        """Return content in the shape scene_writer.py expects."""
        return [type("obj", (), {"text": self.text})()]
