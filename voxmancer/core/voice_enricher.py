"""Enrich sparse voice prompts using LLM reasoning."""
from __future__ import annotations

import os

from ..config import get_settings


def enrich_voice_prompt(sparse_prompt: str, npc_name: str = "", npc_role: str = "") -> str:
    """
    Enrich a sparse voice prompt into a detailed, structured description.

    Takes minimal input like "old dwarf, gruff" and expands it using LLM
    into a rich description suitable for TTS voice matching.

    Example:
        Input: "old dwarf, gruff"
        Output: "Male, 60+. An old dwarf blacksmith. Low gravelly voice with weathered
                character. Speaks slowly, deliberately, with underlying warmth beneath
                the grumbling."
    """

    # Check if prompt is already detailed (heuristic: >50 chars AND multiple descriptive elements)
    if len(sparse_prompt) > 80 and any(
        word in sparse_prompt.lower()
        for word in ["voice", "speak", "tone", "emotion", "quality", "accent", "character"]
    ):
        return sparse_prompt  # Already detailed

    # Use LLM to enrich the prompt
    backend = os.getenv("LLM_BACKEND", "ollama").lower()

    if backend == "anthropic":
        return _enrich_with_claude(sparse_prompt, npc_name, npc_role)
    else:
        return _enrich_with_ollama(sparse_prompt, npc_name, npc_role)


def _enrich_with_claude(sparse_prompt: str, npc_name: str = "", npc_role: str = "") -> str:
    """Enrich voice prompt using Anthropic Claude."""
    try:
        from anthropic import Anthropic

        client = Anthropic()
        settings = get_settings()

        if not settings.anthropic_api_key:
            # Fall back to Ollama if no API key
            return _enrich_with_ollama(sparse_prompt, npc_name, npc_role)

        prompt_text = f"""You are a voice director for text-to-speech. A user has provided a sparse voice description for an NPC.
Expand this into a rich, structured voice prompt that describes:
- Gender and age
- Character/persona
- Voice quality (tone, pitch, texture)
- Speaking style (pace, emphasis, emotion)
- Underlying character traits that should come through

Sparse description: "{sparse_prompt}"
"""

        if npc_name:
            prompt_text += f"\nNPC name: {npc_name}"
        if npc_role:
            prompt_text += f"NPC role: {npc_role}"

        prompt_text += """

Return ONLY the enriched voice prompt (2-3 sentences), nothing else."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt_text}],
        )

        return message.content[0].text.strip()

    except Exception as e:
        print(f"⚠️  Claude enrichment failed: {e}")
        return _enrich_with_ollama(sparse_prompt, npc_name, npc_role)


def _enrich_with_ollama(sparse_prompt: str, npc_name: str = "", npc_role: str = "") -> str:
    """Enrich voice prompt using Ollama local LLM."""
    try:
        import requests

        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        model = os.getenv("LLM_MODEL", "mistral")

        prompt_text = f"""You are a voice director. Expand this sparse voice description into a rich, detailed prompt for text-to-speech:

Sparse: "{sparse_prompt}"
"""

        if npc_name:
            prompt_text += f"Name: {npc_name}\n"
        if npc_role:
            prompt_text += f"Role: {npc_role}\n"

        prompt_text += """
Provide a 2-3 sentence rich voice prompt describing gender, age, voice quality, tone, and character. Return ONLY the prompt."""

        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt_text,
                "stream": False,
                "temperature": 0.7,
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            return result if result else sparse_prompt
        else:
            print(f"⚠️  Ollama returned {response.status_code}")
            return sparse_prompt

    except Exception as e:
        print(f"⚠️  Ollama enrichment failed: {e}")
        return sparse_prompt
