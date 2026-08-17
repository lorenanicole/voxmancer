"""LLM-based voice mapper using Mistral to intelligently match prompts to Piper voices."""
from __future__ import annotations

import json
from .voice_registry import VoiceRegistry
from ..config import get_settings


class LLMVoiceMapper:
    """Uses LLM to intelligently map voice prompts to available Piper voices."""

    def __init__(self):
        self.registry = VoiceRegistry()
        self.settings = get_settings()

    def map_voice_prompt_to_piper(self, prompt: str) -> str:
        """
        Use LLM to map voice prompt to best available Piper voice.

        Args:
            prompt: Voice description (e.g., "English female with low gravelly voice")

        Returns:
            Voice ID with quality (e.g., "en_US-amy-medium")
        """
        # Get available voices with their metadata
        voices = self.registry.list_voices()
        voices_data = []
        for v in voices:
            voice_meta = self.registry.get_voice(v["id"])
            voices_data.append(
                {
                    "id": v["id"],
                    "description": v.get("description", ""),
                    "gender": v.get("gender", ""),
                    "age": v.get("age", ""),
                    "accent": v.get("accent", ""),
                    "available_qualities": voice_meta.get("qualities", ["medium"]),
                }
            )

        voices_json = json.dumps(voices_data, indent=2)

        # Ask LLM to choose best matching voice
        llm_prompt = f"""You are a voice matching expert. Given a voice description and a list of available pre-trained voices, select the best matching voice.

VOICE PROMPT: {prompt}

AVAILABLE VOICES (with their available qualities):
{voices_json}

IMPORTANT: You MUST choose a quality that is listed in the voice's "available_qualities" field. Do not suggest qualities that are not available for that voice.

Respond with ONLY a JSON object in this format:
{{
  "voice_id": "en_US-amy",
  "quality": "medium",
  "reasoning": "Brief explanation of why this voice matches"
}}

Rules:
- Choose a voice_id from the list above
- Choose a quality ONLY from that voice's available_qualities
- If the requested quality is not available, pick the closest available alternative
- Prioritize gender and age match over quality preference"""

        try:
            # Call LLM
            response = self._call_llm(llm_prompt)
            result = json.loads(response)

            voice_id = result["voice_id"]
            quality = result["quality"]

            # Validate voice exists and quality is available
            voice = self.registry.get_voice(voice_id)
            if not voice:
                return self._fallback_voice()

            # Check quality is available, fallback to first available
            available_qualities = voice.get("qualities", ["medium"])
            if quality not in available_qualities:
                quality = available_qualities[0]

            return f"{voice_id}-{quality}"

        except Exception as e:
            print(f"⚠️  LLM voice mapping failed ({e}), using fallback...")
            return self._fallback_voice()

    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM backend."""
        backend = self.settings.llm_backend.lower()

        if backend == "ollama":
            return self._call_ollama(prompt)
        elif backend == "anthropic":
            return self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported LLM backend: {backend}")

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama LLM."""
        from .ollama_llm_backend import OllamaLLMClient

        client = OllamaLLMClient()
        msg = client.messages_create(
            model=self.settings.llm_model,
            system="You are a voice matching expert.",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text

    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude."""
        from anthropic import Anthropic

        if not self.settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        client = Anthropic(api_key=self.settings.anthropic_api_key)
        msg = client.messages.create(
            model=self.settings.llm_model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text

    def _fallback_voice(self) -> str:
        """Return a safe fallback voice when LLM fails."""
        return "en_US-ryan-medium"


# Module-level function for backward compatibility
_mapper = None


def map_voice_prompt_to_piper(prompt: str) -> str:
    """Map voice prompt to Piper voice using LLM."""
    global _mapper
    if _mapper is None:
        _mapper = LLMVoiceMapper()
    return _mapper.map_voice_prompt_to_piper(prompt)
