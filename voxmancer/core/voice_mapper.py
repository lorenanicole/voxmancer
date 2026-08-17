"""Voice prompt mapper using LLM for intelligent voice selection.

This module maps voice descriptions to actual Piper TTS voices using an LLM
to intelligently match prompts to available pre-trained voices. It mimics the
functionality of commercial TTS services like ElevenLabs.
"""
from __future__ import annotations

from .voice_mapper_llm import LLMVoiceMapper


def map_voice_prompt_to_piper(prompt: str) -> str:
    """
    Map a voice prompt to a Piper voice using LLM intelligence.

    The LLM analyzes the voice description and selects the best matching
    pre-trained voice from available Piper voices, handling:
    - Gender preferences (male, female)
    - Age characteristics (elderly, young, adult)
    - Accent preferences (British, American, etc.)
    - Quality levels (low, medium, high)
    - Any other voice characteristics

    Args:
        prompt: Voice description (e.g., "English female with low gravelly voice")

    Returns:
        Voice ID with quality (e.g., "en_US-amy-medium")

    Example:
        >>> result = map_voice_prompt_to_piper("British male, elderly, warm")
        >>> print(result)  # "en_US-john-medium"
    """
    mapper = LLMVoiceMapper()
    return mapper.map_voice_prompt_to_piper(prompt)


def list_piper_voices(language: str = "en") -> dict:
    """List all voices for a language."""
    from .voice_registry import VoiceRegistry

    registry = VoiceRegistry()
    voices = registry.voices_for_language(language)
    return {v["id"]: v for v in voices}
