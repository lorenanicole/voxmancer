"""A drop-in LLM backend that calls your deployed Runpod Flash endpoint.

Same interface as the Anthropic client, so scene_writer.py doesn't change.
Set the environment:
    LLM_BACKEND=runpod_flash
    RUNPOD_LLM_URL      the invoke URL of your deployed Flash LLM endpoint
    RUNPOD_LLM_API_KEY  if your endpoint requires auth (optional)

This lets you run an open-source LLM (Mistral, Llama, etc.) on Runpod instead
of Claude, while keeping the same voxmancer pipeline.
"""
from __future__ import annotations

import os

import httpx


class RunpodLLMClient:
    """Minimal client for calling an LLM on Runpod Flash.

    Mimics the anthropic.Anthropic.messages.create() interface.
    """

    def __init__(self) -> None:
        self._url = os.getenv("RUNPOD_LLM_URL", "")
        if not self._url:
            raise RuntimeError("RUNPOD_LLM_URL is not set (your deployed Flash LLM endpoint).")
        key = os.getenv("RUNPOD_LLM_API_KEY", "")
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        self._http = httpx.Client(base_url=self._url, headers=headers, timeout=300.0)
        self.messages = _MessagesProxy(self)

    def messages_create(
        self,
        model: str,
        system: str,
        max_tokens: int,
        messages: list[dict],
    ) -> RunpodLLMResponse:
        """Call the LLM endpoint and return a response matching anthropic.Message."""
        # Pack system + user message into a single prompt for the LLM
        user_message = messages[0]["content"] if messages else ""
        prompt = f"{system}\n\n{user_message}"

        # Try Ollama API format first
        resp = self._http.post(
            "/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
        )

        if resp.status_code == 404:
            # Fall back to RunPod Flash format
            resp = self._http.post(
                "",
                json={
                    "input": {
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                    }
                },
            )

        resp.raise_for_status()
        data = resp.json()

        # Handle both Ollama and RunPod response formats
        text = data.get("response") or data.get("text")
        if not text:
            raise RuntimeError(f"endpoint returned no text: {data}")

        return RunpodLLMResponse(text=text)


class RunpodLLMResponse:
    """Mock anthropic.Message response."""

    def __init__(self, text: str) -> None:
        self.text = text

    @property
    def content(self) -> list:
        """Return content in the shape scene_writer.py expects."""
        return [type("obj", (), {"text": self.text})()]


class _MessagesProxy:
    """Proxy object to mimic anthropic.messages.create() interface."""

    def __init__(self, client: RunpodLLMClient) -> None:
        self._client = client

    def create(
        self,
        model: str,
        system: str,
        max_tokens: int,
        messages: list[dict],
    ) -> RunpodLLMResponse:
        """Forward to the client's messages_create method."""
        return self._client.messages_create(
            model=model,
            system=system,
            max_tokens=max_tokens,
            messages=messages,
        )
