"""A drop-in TTS backend that calls your deployed Runpod Flash endpoint.

Same interface as `ElevenClient`, so the pipeline doesn't change — you just swap
which client it constructs. In `pipeline.py`:

    # from .eleven_client import ElevenClient
    from .runpod_backend import RunpodFlashClient as ElevenClient   # <- one line

Then set the environment:
    RUNPOD_FLASH_URL   the invoke URL of your deployed Flash endpoint
    RUNPOD_API_KEY     if your endpoint requires auth (optional)

That one-line swap — same app, self-hosted model on Runpod instead of a hosted
API — is the heart of the demo. Time the first vs. second call; the difference
is your cold-start story.
"""
from __future__ import annotations

import base64
import os

import httpx


class RunpodFlashClient:
    def __init__(self) -> None:
        self._url = os.getenv("RUNPOD_FLASH_URL", "")
        if not self._url:
            raise RuntimeError("RUNPOD_FLASH_URL is not set (your deployed Flash endpoint).")
        key = os.getenv("RUNPOD_API_KEY", "")
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        self._http = httpx.Client(base_url=self._url, headers=headers, timeout=300.0)

    def design_voice(self, name: str, prompt: str) -> str:
        """Return a 'voice handle' for an NPC.

        Flash TTS voices aren't pre-created like a hosted API's — you choose a
        speaker at synth time (a preset name, or a path to a short reference wav
        for cloning). Simplest for the demo: map each NPC to a preset speaker,
        or ship a few reference clips in the repo and return the right one here.
        """
        # TODO: map `prompt` -> a real speaker preset or reference-wav path.
        return name

    def text_to_speech(
        self, voice_id: str, text: str, out_path: str, direction: str | None = None
    ) -> str:
        resp = self._http.post("", json={"input": {"text": text, "speaker": voice_id}})
        resp.raise_for_status()
        data = resp.json()
        if "audio_base64" not in data:
            raise RuntimeError(f"endpoint returned no audio: {data}")
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(data["audio_base64"]))
        return out_path

    def sound_effect(self, prompt: str, out_path: str) -> str:
        raise NotImplementedError("Not needed for the Flash demo.")
