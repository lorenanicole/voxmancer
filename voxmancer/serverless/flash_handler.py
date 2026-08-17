"""Voxmancer TTS — a Runpod Flash serverless app.

Flash runs a GPU workload on Runpod Serverless as a plain Python app — no Docker.
This handler loads Kokoro (open-source lightweight TTS) once per worker (cold start),
then synthesizes audio for each request.

The model is loaded once and reused across requests, making subsequent calls fast.

For the full campaign-to-audio-drama workflow, see ../voxmancer/runpod_handler.py
"""
from __future__ import annotations

import base64
import io
import time

import numpy as np
import scipy.io.wavfile

# Model is loaded once per worker and reused across requests
_MODEL = None


def _load_model():
    """Load Kokoro TTS model once per worker."""
    global _MODEL
    if _MODEL is None:
        try:
            import kokoro

            _MODEL = kokoro
        except ImportError:
            raise RuntimeError("Kokoro not installed. Ensure pyproject.toml has --extras kokoro")
    return _MODEL


def synthesize(text: str, voice: str = "af") -> bytes:
    """Synthesize audio using Kokoro TTS.

    Args:
        text: Text to synthesize
        voice: Kokoro voice preset (af=American female, am=American male,
               bf=British female, bm=British male)

    Returns:
        WAV audio bytes
    """
    kokoro = _load_model()

    # Generate audio (returns numpy array at 24kHz)
    generator = kokoro.generate(text, voice=voice, speed=1.0)
    audio_array = generator.audio if hasattr(generator, "audio") else generator

    if not isinstance(audio_array, np.ndarray):
        raise ValueError(f"Expected numpy array, got {type(audio_array)}")

    # Convert to WAV bytes (24-bit, 24kHz)
    wav_buffer = io.BytesIO()
    scipy.io.wavfile.write(wav_buffer, 24000, audio_array.astype(np.float32))
    wav_buffer.seek(0)
    return wav_buffer.read()


def handler(event: dict) -> dict:
    """RunPod Flash handler for TTS synthesis.

    Request format:
    {
      "input": {
        "text": "The text to synthesize",
        "voice": "af"  # or am, bf, bm (optional, default: af)
      }
    }

    Response format:
    {
      "success": true,
      "audio_base64": "...",
      "format": "wav",
      "sample_rate": 24000,
      "generation_time_ms": 1234
    }
    """
    start_time = time.time()

    try:
        payload = event.get("input", event) or {}
        text = (payload.get("text") or "").strip()
        voice = payload.get("voice", "af").lower()

        if not text:
            return {"success": False, "error": "no text provided"}

        if voice not in ["af", "am", "bf", "bm"]:
            return {
                "success": False,
                "error": f"invalid voice '{voice}' (must be: af, am, bf, bm)",
            }

        # Synthesize
        audio_bytes = synthesize(text, voice)

        generation_time_ms = round((time.time() - start_time) * 1000)

        return {
            "success": True,
            "audio_base64": base64.b64encode(audio_bytes).decode(),
            "format": "wav",
            "sample_rate": 24000,
            "generation_time_ms": generation_time_ms,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generation_time_ms": round((time.time() - start_time) * 1000),
        }


# For local testing
if __name__ == "__main__":
    test_event = {
        "input": {
            "text": "Hello, this is Kokoro text-to-speech on RunPod Flash.",
            "voice": "am",
        }
    }

    result = handler(test_event)
    print(f"Success: {result['success']}")
    if result["success"]:
        print(f"Audio size: {len(result['audio_base64'])} chars")
        print(f"Generation time: {result['generation_time_ms']}ms")
        print(f"Sample rate: {result['sample_rate']}Hz")
    else:
        print(f"Error: {result['error']}")
