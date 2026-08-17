"""Tests for voice mapper (legacy keyword-based tests)."""
import pytest
from voxmancer.core.voice_mapper import map_voice_prompt_to_piper
from voxmancer.core.voice_mapper_llm import LLMVoiceMapper


@pytest.fixture
def mapper():
    """Create an LLM voice mapper."""
    return LLMVoiceMapper()


@pytest.mark.unit
def test_mapper_has_registry(mapper):
    """Test mapper has voice registry."""
    assert mapper.registry is not None
    voices = mapper.registry.list_voices()
    assert len(voices) > 0


@pytest.mark.unit
def test_mapper_returns_valid_voice(mapper):
    """Test mapper returns valid voice format."""
    from unittest.mock import patch

    with patch.object(mapper, "_call_llm") as mock_llm:
        mock_llm.return_value = (
            '{"voice_id": "en_US-ryan", "quality": "medium", "reasoning": "Test"}'
        )
        result = mapper.map_voice_prompt_to_piper("Test prompt")

    assert result is not None
    assert "-" in result
    assert "en_US-" in result


@pytest.mark.unit
def test_mapper_fallback_on_error(mapper):
    """Test mapper falls back to default on error."""
    from unittest.mock import patch

    with patch.object(mapper, "_call_llm") as mock_llm:
        mock_llm.return_value = "Invalid JSON"
        result = mapper.map_voice_prompt_to_piper("Test prompt")

    assert result == "en_US-ryan-medium"


@pytest.mark.unit
def test_mapper_respects_available_qualities(mapper):
    """Test mapper respects available qualities for voices."""
    from unittest.mock import patch

    # Amy only has low and medium, not high
    with patch.object(mapper, "_call_llm") as mock_llm:
        mock_llm.return_value = '{"voice_id": "en_US-amy", "quality": "high", "reasoning": "Test"}'
        result = mapper.map_voice_prompt_to_piper("Female voice")

    # Should fallback to available quality
    assert "en_US-amy-" in result
    quality = result.split("-")[-1]
    assert quality in ["low", "medium"]


@pytest.mark.unit
def test_map_voice_prompt_module_function():
    """Test module-level map_voice_prompt_to_piper function."""
    from unittest.mock import patch

    with patch("voxmancer.core.voice_mapper.LLMVoiceMapper._call_llm") as mock_llm:
        mock_llm.return_value = (
            '{"voice_id": "en_US-ryan", "quality": "medium", "reasoning": "Test"}'
        )
        result = map_voice_prompt_to_piper("Male warrior")

    assert result is not None
    assert "-" in result


@pytest.mark.unit
def test_mapper_male_elderly(mapper):
    """Test mapping male elderly voice."""
    from unittest.mock import patch

    with patch.object(mapper, "_call_llm") as mock_llm:
        mock_llm.return_value = (
            '{"voice_id": "en_US-john", "quality": "medium", "reasoning": "Elderly male"}'
        )
        result = mapper.map_voice_prompt_to_piper("Male, 60+. Gruff mentor.")

    assert "en_US-john" in result
    assert "-medium" in result


@pytest.mark.unit
def test_mapper_female_adult(mapper):
    """Test mapping female adult voice."""
    from unittest.mock import patch

    with patch.object(mapper, "_call_llm") as mock_llm:
        mock_llm.return_value = (
            '{"voice_id": "en_US-amy", "quality": "medium", "reasoning": "Female adult"}'
        )
        result = mapper.map_voice_prompt_to_piper("Female, 30s. Confident warrior.")

    assert "en_US-amy" in result
    assert "-medium" in result
