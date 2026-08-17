"""Tests for configuration."""
import pytest
from voxmancer.config import get_settings, Settings


@pytest.mark.unit
def test_settings_creation():
    """Test creating settings object."""
    settings = Settings(
        tts_backend="piper",
        llm_backend="ollama",
        llm_model="mistral",
        ollama_url="http://localhost:11434",
    )
    assert settings.tts_backend == "piper"
    assert settings.llm_backend == "ollama"
    assert settings.llm_model == "mistral"


@pytest.mark.unit
def test_settings_defaults():
    """Test settings have reasonable defaults."""
    settings = Settings()
    assert settings.tts_backend in ["piper", "elevenlabs"]
    assert settings.llm_backend in ["anthropic", "ollama"]
    assert settings.llm_model is not None


@pytest.mark.unit
def test_get_settings():
    """Test getting current settings."""
    settings = get_settings()
    assert settings is not None
    assert isinstance(settings, Settings)


@pytest.mark.unit
def test_settings_custom_backend():
    """Test creating settings with custom backend value."""
    settings = Settings(tts_backend="custom_backend")
    assert settings.tts_backend == "custom_backend"


@pytest.mark.unit
def test_settings_ollama_url():
    """Test Ollama URL configuration."""
    settings = Settings(
        llm_backend="ollama",
        ollama_url="http://custom:9000",
    )
    assert settings.ollama_url == "http://custom:9000"
