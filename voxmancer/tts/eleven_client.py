"""Wrapper around the ElevenLabs API using the official SDK."""
from __future__ import annotations

import httpx
from pathlib import Path

from elevenlabs.client import ElevenLabs

from ..config import get_settings


class ElevenClient:
    def __init__(self) -> None:
        s = get_settings()
        if not s.elevenlabs_api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set (see .env.example).")
        self._client = ElevenLabs(api_key=s.elevenlabs_api_key)
        self._api_key = s.elevenlabs_api_key
        self._base_url = s.eleven_base_url

    def design_voice(self, name: str, prompt: str) -> str:
        """Return a voice_id for a voice generated from `prompt` via Voice Design.

        Uses ElevenLabs Voice Design API to create a unique voice from text
        description. This works on free and paid plans.
        """
        with httpx.Client() as http:
            response = http.post(
                f"{self._base_url}/voice-design/create",
                headers={"xi-api-key": self._api_key},
                json={
                    "name": name,
                    "voice_description": prompt,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("voice_id") or data.get("generated_voice_id")

    def text_to_speech(
        self, voice_id: str, text: str, out_path: str, direction: str | None = None
    ) -> str:
        """Render `text` in `voice_id` to an audio file at `out_path`; return it.

        Synthesizes speech using the specified voice. The `direction` parameter
        is prepended to the text as an acting note.
        """
        if direction:
            text = f"({direction}) {text}"

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)

        with httpx.Client() as http:
            response = http.post(
                f"{self._base_url}/text-to-speech/{voice_id}",
                headers={"xi-api-key": self._api_key},
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    },
                },
                timeout=60.0,
            )
            if response.status_code != 200:
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text
                raise RuntimeError(
                    f"ElevenLabs TTS failed ({response.status_code}): {error_detail}"
                )

        with open(out_path, "wb") as f:
            f.write(response.content)

        return out_path

    def sound_effect(self, prompt: str, out_path: str) -> str:
        """Generate a short SFX/ambiance clip from a text prompt; return the path."""
        audio = self._client.sound_generation.generate(
            text=prompt,
            duration_seconds=10,
        )

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        return out_path

    def voice_exists(self, voice_id: str) -> bool:
        """Check if a voice_id exists in your ElevenLabs account.

        Useful for validating cached voice_ids before trying to use them.
        Returns True if the voice exists and is accessible, False otherwise.
        """
        try:
            with httpx.Client() as http:
                response = http.get(
                    f"{self._base_url}/voices/{voice_id}",
                    headers={"xi-api-key": self._api_key},
                    timeout=10.0,
                )
                return response.status_code == 200
        except Exception:
            return False
