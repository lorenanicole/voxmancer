"""Tests for voice registry."""
import pytest
from voxmancer.core.voice_registry import VoiceRegistry


@pytest.fixture
def registry():
    """Create a voice registry instance."""
    return VoiceRegistry()


@pytest.mark.unit
def test_registry_loads(registry):
    """Test that registry loads without errors."""
    assert registry is not None
    assert registry._registry is not None


@pytest.mark.unit
def test_list_voices(registry):
    """Test listing voices."""
    voices = registry.list_voices()
    assert len(voices) > 0
    assert all("id" in v for v in voices)


@pytest.mark.unit
def test_voices_for_accent(registry):
    """Test getting voices for specific accent."""
    us_voices = registry.voices_for_accent("en_US")
    assert len(us_voices) > 0
    assert all(v.get("accent") == "en_US" for v in us_voices)


@pytest.mark.unit
def test_voices_for_language(registry):
    """Test getting voices for specific language."""
    en_voices = registry.voices_for_language("en")
    assert len(en_voices) > 0
    assert all(v.get("language") == "en" for v in en_voices)


@pytest.mark.unit
def test_get_voice(registry):
    """Test getting specific voice."""
    voice = registry.get_voice("en_US-ryan")
    assert voice is not None
    assert voice["gender"] == "male"
    assert voice["accent"] == "en_US"


@pytest.mark.unit
def test_get_voice_not_found(registry):
    """Test getting non-existent voice."""
    voice = registry.get_voice("nonexistent-voice")
    assert voice is None


@pytest.mark.unit
def test_available_accents(registry):
    """Test getting available accents."""
    accents = registry.available_accents("en")
    assert len(accents) > 0
    assert "en_US" in accents


@pytest.mark.unit
def test_available_languages(registry):
    """Test getting available languages."""
    langs = registry.available_languages()
    assert len(langs) > 0
    assert "en" in langs


@pytest.mark.unit
def test_get_download_url(registry):
    """Test getting download URL for a voice."""
    url = registry.get_download_url("en_US-ryan", "medium")
    assert url is not None
    assert "huggingface.co" in url
    assert "ryan" in url
    assert "medium" in url


@pytest.mark.unit
def test_voice_qualities(registry):
    """Test that voices have all quality levels."""
    voice = registry.get_voice("en_US-ryan")
    assert voice is not None
    assert "urls" in voice
    assert "low" in voice["urls"]
    assert "medium" in voice["urls"]
    assert "high" in voice["urls"]
