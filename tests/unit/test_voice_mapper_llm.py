"""Tests for LLM-based voice mapper."""
import pytest
from unittest.mock import patch
from voxmancer.core.voice_mapper_llm import LLMVoiceMapper


@pytest.fixture
def mapper():
    """Create an LLM voice mapper."""
    return LLMVoiceMapper()


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    return {
        "voice_id": "en_US-ryan",
        "quality": "medium",
        "reasoning": "Best matches calm storyteller",
    }


@pytest.mark.unit
def test_mapper_initialization(mapper):
    """Test that mapper initializes correctly."""
    assert mapper is not None
    assert mapper.registry is not None
    assert mapper.settings is not None


@pytest.mark.unit
def test_mapper_has_available_voices(mapper):
    """Test that mapper can see available voices."""
    voices = mapper.registry.list_voices()
    assert len(voices) > 0
    voice_ids = [v["id"] for v in voices]
    assert "en_US-ryan" in voice_ids
    assert "en_US-amy" in voice_ids
    assert "en_US-john" in voice_ids


@pytest.mark.unit
def test_fallback_voice(mapper):
    """Test fallback voice when LLM fails."""
    fallback = mapper._fallback_voice()
    assert fallback == "en_US-ryan-medium"
    assert "-" in fallback


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_map_with_male_prompt(mock_call, mapper):
    """Test mapping male voice prompt."""
    mock_call.return_value = (
        '{"voice_id": "en_US-ryan", "quality": "medium", "reasoning": "Male voice"}'
    )

    result = mapper.map_voice_prompt_to_piper("Male storyteller")
    assert result == "en_US-ryan-medium"


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_map_with_female_prompt(mock_call, mapper):
    """Test mapping female voice prompt."""
    mock_call.return_value = (
        '{"voice_id": "en_US-amy", "quality": "medium", "reasoning": "Female voice"}'
    )

    result = mapper.map_voice_prompt_to_piper("Female warrior")
    assert result == "en_US-amy-medium"


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_map_with_elderly_prompt(mock_call, mapper):
    """Test mapping elderly voice prompt."""
    mock_call.return_value = (
        '{"voice_id": "en_US-john", "quality": "medium", "reasoning": "Elderly male"}'
    )

    result = mapper.map_voice_prompt_to_piper("Elderly merchant")
    assert result == "en_US-john-medium"


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_quality_fallback_when_unavailable(mock_call, mapper):
    """Test that unavailable quality falls back to available one."""
    # Amy only has low and medium, not high
    mock_call.return_value = '{"voice_id": "en_US-amy", "quality": "high", "reasoning": "Female"}'

    result = mapper.map_voice_prompt_to_piper("Female voice")
    # Should fallback to low (first available for amy)
    assert result.startswith("en_US-amy-")
    quality = result.split("-")[-1]
    assert quality in ["low", "medium"]


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_invalid_voice_uses_fallback(mock_call, mapper):
    """Test that invalid voice ID falls back to default."""
    mock_call.return_value = (
        '{"voice_id": "nonexistent-voice", "quality": "medium", "reasoning": "Invalid"}'
    )

    result = mapper.map_voice_prompt_to_piper("Some voice")
    assert result == "en_US-ryan-medium"


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_malformed_json_uses_fallback(mock_call, mapper):
    """Test that malformed JSON response uses fallback."""
    mock_call.return_value = "This is not JSON"

    result = mapper.map_voice_prompt_to_piper("Some voice")
    assert result == "en_US-ryan-medium"


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_complex_prompt(mock_call, mapper):
    """Test mapping complex voice prompt."""
    complex_prompt = "British elderly female with warm, soothing tone. Slightly posh accent. Professional but friendly."
    mock_call.return_value = (
        '{"voice_id": "en_US-amy", "quality": "medium", "reasoning": "Warm female voice"}'
    )

    result = mapper.map_voice_prompt_to_piper(complex_prompt)
    assert "-" in result
    assert "en_US-" in result


@pytest.mark.unit
def test_ollama_backend_call(mapper):
    """Test Ollama backend call (if available)."""
    if mapper.settings.llm_backend.lower() != "ollama":
        pytest.skip("Ollama backend not configured")

    try:
        response = mapper._call_ollama("Test prompt")
        assert response is not None
        assert isinstance(response, str)
    except Exception as e:
        pytest.skip(f"Ollama not available: {e}")


@pytest.mark.unit
def test_anthropic_backend_call(mapper):
    """Test Anthropic backend call (if configured)."""
    if mapper.settings.llm_backend.lower() != "anthropic":
        pytest.skip("Anthropic backend not configured")

    try:
        response = mapper._call_anthropic("Test prompt")
        assert response is not None
        assert isinstance(response, str)
    except Exception as e:
        pytest.skip(f"Anthropic not available: {e}")


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_module_level_function(mock_call):
    """Test module-level map_voice_prompt_to_piper function."""
    from voxmancer.core.voice_mapper import map_voice_prompt_to_piper

    mock_call.return_value = '{"voice_id": "en_US-ryan", "quality": "medium", "reasoning": "Test"}'

    result = map_voice_prompt_to_piper("Test prompt")
    assert result is not None
    assert "-" in result


@patch("voxmancer.core.voice_mapper_llm.LLMVoiceMapper._call_llm")
@pytest.mark.unit
def test_multiple_mappings_consistency(mock_call, mapper):
    """Test that same prompt returns consistent results."""
    prompt = "Male narrator with warm voice"
    mock_call.return_value = (
        '{"voice_id": "en_US-ryan", "quality": "medium", "reasoning": "Matches"}'
    )

    result1 = mapper.map_voice_prompt_to_piper(prompt)
    result2 = mapper.map_voice_prompt_to_piper(prompt)

    assert result1 == result2
    assert result1 == "en_US-ryan-medium"
