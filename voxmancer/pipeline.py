"""Orchestration — campaign file (+ optional scene) -> voiced interlude mp3.

    load campaign ─► [write scene | load scene] ─► design voices ─► render ─► mp3

Pass `scene_path` to skip the LLM entirely and voice a hand-written scene.
Supports multiple TTS backends via TTS_BACKEND environment variable.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

from .models import Campaign, RenderResult, Scene
from .core.renderer import render_scene
from .core.scene_writer import write_scene
from .core.voice_designer import build_voice_library


def _get_tts_client():
    """Return the configured TTS client based on TTS_BACKEND env var."""
    backend = os.getenv("TTS_BACKEND", "elevenlabs").lower()

    if backend == "kokoro":
        from .tts.kokoro_tts_backend import KokoroTTSClient

        return KokoroTTSClient()
    elif backend == "kokoro_http":
        from .tts.kokoro_http_client import KokoroHTTPClient

        return KokoroHTTPClient()
    elif backend == "elevenlabs":
        from .tts.eleven_client import ElevenClient

        return ElevenClient()
    else:
        raise ValueError(
            f"Unknown TTS_BACKEND: {backend}. Supported: elevenlabs, kokoro, kokoro_http"
        )


def load_campaign(path: Path) -> Campaign:
    return Campaign(**yaml.safe_load(Path(path).read_text()))


def load_scene(path: Path) -> Scene:
    return Scene(**yaml.safe_load(Path(path).read_text()))


def run(
    campaign_path: Path,
    out_path: Path,
    scene_path: Path | None = None,
    work_dir: Path = Path(".voxmancer"),
) -> RenderResult:
    campaign = load_campaign(campaign_path)
    client = _get_tts_client()

    scene = load_scene(scene_path) if scene_path else write_scene(campaign)
    library = build_voice_library(campaign, client)  # Uses ~/.voxmancer/voices.json by default
    audio = render_scene(scene, campaign, client, out_path, work_dir / "clips")

    return RenderResult(audio_path=str(audio), scene=scene, voice_library=library)
