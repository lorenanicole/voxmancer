"""Integration tests for voice mapping and rendering pipeline."""
import pytest
from voxmancer.core.voice_mapper_llm import LLMVoiceMapper
from voxmancer.core.voice_registry import VoiceRegistry


@pytest.mark.integration
@pytest.mark.timeout(15)
def test_llm_mapper_with_registry(mocker):
    """Test LLM voice mapper working with registry."""
    registry = VoiceRegistry()
    mapper = LLMVoiceMapper()

    # Mock the LLM call
    mock_response = '{"voice_id": "en_US-ryan", "quality": "medium", "reasoning": "Matches male"}'
    mocker.patch.object(mapper, "_call_llm", return_value=mock_response)

    # Test full pipeline
    result = mapper.map_voice_prompt_to_piper("Male storyteller")

    assert result == "en_US-ryan-medium"
    voice = registry.get_voice("en_US-ryan")
    assert voice is not None
    assert "medium" in voice["qualities"]


@pytest.mark.integration
@pytest.mark.timeout(15)
def test_llm_mapper_respects_registry_constraints(mocker):
    """Test that LLM mapper respects voice quality constraints from registry."""
    mapper = LLMVoiceMapper()

    # LLM suggests high quality for Amy, but Amy only has low/medium
    mock_response = (
        '{"voice_id": "en_US-amy", "quality": "high", "reasoning": "High quality female"}'
    )
    mocker.patch.object(mapper, "_call_llm", return_value=mock_response)

    result = mapper.map_voice_prompt_to_piper("Female with high quality")

    # Should fallback to available quality
    assert "en_US-amy-" in result
    quality = result.split("-")[-1]
    assert quality in ["low", "medium"]


@pytest.mark.integration
@pytest.mark.timeout(15)
def test_registry_lists_only_available_voices():
    """Test that registry only exposes voices with available models."""
    registry = VoiceRegistry()

    # Get all voices
    voices = registry.list_voices()
    voice_ids = [v["id"] for v in voices]

    # Verify essential voices are present
    assert "en_US-ryan" in voice_ids
    assert "en_US-amy" in voice_ids
    assert "en_US-john" in voice_ids

    # Verify each voice has qualities
    for voice_id in ["en_US-ryan", "en_US-amy", "en_US-john"]:
        voice = registry.get_voice(voice_id)
        assert voice is not None
        assert len(voice.get("qualities", [])) > 0


@pytest.mark.integration
@pytest.mark.timeout(15)
def test_download_url_generation():
    """Test that registry generates valid download URLs."""
    registry = VoiceRegistry()

    for voice_id in ["en_US-ryan", "en_US-amy", "en_US-john"]:
        voice = registry.get_voice(voice_id)
        for quality in voice["qualities"]:
            url = registry.get_download_url(voice_id, quality)
            assert url is not None
            assert "huggingface.co" in url
            assert voice_id in url
            assert quality in url
