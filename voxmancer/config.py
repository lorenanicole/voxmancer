"""Runtime settings, read once from the environment (.env supported)."""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    # API Keys
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Backend selection
    tts_backend: str = os.getenv("TTS_BACKEND", "piper")
    llm_backend: str = os.getenv("LLM_BACKEND", "ollama")

    # Model configuration
    llm_model: str = os.getenv("LLM_MODEL", "mistral")
    voxmancer_llm_model: str = os.getenv("VOXMANCER_LLM_MODEL", "claude-3-5-sonnet-latest")

    # API endpoints
    eleven_base_url: str = os.getenv("ELEVEN_BASE_URL", "https://api.elevenlabs.io/v1")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")


@lru_cache
def get_settings() -> Settings:
    return Settings()
