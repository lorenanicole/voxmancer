"""HTTP client for Kokoro TTS running on a remote RunPod pod."""
from __future__ import annotations

import base64
import os
from typing import Optional

import requests


class KokoroHTTPClient:
    """Call Kokoro TTS on a remote RunPod pod via HTTP proxy.

    Expects a Kokoro Pod deployed on RunPod with an HTTP endpoint.
    Set RUNPOD_KOKORO_URL environment variable to the pod's invoke URL.

    Example:
        export RUNPOD_KOKORO_URL=https://xxxxx-kokoro-xxxxx.proxy.runpod.net/
        client = KokoroHTTPClient()
        audio = client.text_to_speech("Hello", voice_id="af")
    """

    def __init__(self, kokoro_url: Optional[str] = None):
        """Initialize HTTP client for remote Kokoro pod.

        Args:
            kokoro_url: Base URL of Kokoro pod (https://...-kokoro-....proxy.runpod.net).
                       If None, reads from RUNPOD_KOKORO_URL environment variable.
        """
        self.kokoro_url = (kokoro_url or os.getenv("RUNPOD_KOKORO_URL", "")).rstrip("/")
        if not self.kokoro_url:
            raise ValueError(
                "RUNPOD_KOKORO_URL not set. Deploy Kokoro pod and set environment variable."
            )

    def text_to_speech(self, text: str, voice_id: str = "af") -> bytes:
        """Generate speech from text via remote Kokoro pod.

        Args:
            text: Text to synthesize
            voice_id: Kokoro voice preset (af, am, bf, bm)

        Returns:
            WAV audio bytes (24kHz, mono)

        Raises:
            RuntimeError: If pod request fails or returns error
            requests.RequestException: If HTTP request fails
        """
        payload = {"input": {"text": text, "voice": voice_id}}

        response = requests.post(f"{self.kokoro_url}/run", json=payload, timeout=300)
        response.raise_for_status()

        result = response.json()
        if result.get("status") != "COMPLETED":
            raise RuntimeError(
                f"Kokoro pod request failed: {result.get('status')} — {result.get('error')}"
            )

        # RunPod returns base64-encoded WAV audio in output
        audio_b64 = result.get("output", {}).get("audio")
        if not audio_b64:
            raise RuntimeError("Kokoro pod returned no audio data")

        return base64.b64decode(audio_b64)

    def voice_exists(self, voice_id: str) -> bool:
        """Check if voice preset is available.

        Kokoro has 4 fixed presets: af, am, bf, bm.
        """
        return voice_id.lower() in ["af", "am", "bf", "bm"]

    def design_voice(self, prompt: str) -> str:
        """Kokoro doesn't support voice design via prompts.

        Return a fixed preset based on description length/content heuristic.
        In practice, this should be overridden by voice_mapper to choose
        from existing presets rather than "designing" new voices.
        """
        # Simple heuristic: use different presets based on prompt characteristics
        if any(word in prompt.lower() for word in ["female", "woman", "girl", "soprano"]):
            return "af"
        elif any(word in prompt.lower() for word in ["male", "man", "boy", "bass"]):
            return "am"
        else:
            return "af"  # Default to female
