"""Stage 2 — design (or reuse) a voice per NPC and persist a voice library.

Reuse is the whole point: an NPC gets a voice once, and every later session
loads the same voice_id, so Brakk always sounds like Brakk.

Voice reuse checks prompt similarity via LLM to ensure cached voices match
the current character's voice requirements.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..models import Campaign

# Use home directory for persistent voice cache across sessions
VOICES_CACHE_PATH = Path.home() / ".voxmancer" / "voices.json"


def build_voice_library(
    campaign: Campaign, client, library_path: Path | None = None
) -> dict[str, str]:
    """Ensure every NPC has a voice_id; return {npc_id: voice_id}.

    Reuses cached voices only if their original prompt matches the current prompt.
    Uses ~/.voxmancer/voices.json as persistent cross-session cache.
    """
    # Use global cache path by default (persistent across sessions)
    if library_path is None:
        library_path = VOICES_CACHE_PATH
    library = _load(library_path)
    for npc in campaign.npcs:
        # Priority 1: Use existing voice_id if already set (from interactive mapping)
        if npc.voice_id:
            _store_voice(library, npc.id, npc.voice_id, npc.voice_prompt)
            continue

        # Priority 2: Check cached library, but verify prompt similarity
        if npc.id in library:
            cached_entry = library[npc.id]
            cached_voice_id = _get_voice_id(cached_entry)
            cached_prompt = _get_prompt(cached_entry)

            # Reuse voice only if prompts are similar enough
            if cached_prompt and _prompts_similar(cached_prompt, npc.voice_prompt):
                npc.voice_id = cached_voice_id
                continue

        # Priority 3: Design new voice (cached voice not suitable or doesn't exist)
        npc.voice_id = client.design_voice(name=npc.name, prompt=npc.voice_prompt)
        _store_voice(library, npc.id, npc.voice_id, npc.voice_prompt)

    _save(library_path, library)
    return {npc_id: _get_voice_id(v) for npc_id, v in library.items()}


def _prompts_similar(cached_prompt: str, new_prompt: str) -> bool:
    """Check if two voice prompts are similar enough to reuse a voice."""
    # Extract key characteristics from both prompts
    cached_lower = cached_prompt.lower()
    new_lower = new_prompt.lower()

    # Keywords that define voice type - must match
    gender_keywords = ["male", "female"]

    # Check gender match
    cached_gender = next((g for g in gender_keywords if g in cached_lower), None)
    new_gender = next((g for g in gender_keywords if g in new_lower), None)
    if cached_gender and new_gender and cached_gender != new_gender:
        return False

    # If both mention age, they should match roughly (not requiring exact match)
    # Simple heuristic: if one says "young" and other says "elderly", don't reuse
    if any(young in cached_lower for young in ["young", "20s", "30s"]):
        if any(old in new_lower for old in ["60+", "elderly", "aged"]):
            return False
    if any(old in cached_lower for old in ["60+", "elderly", "aged"]):
        if any(young in new_lower for young in ["young", "20s", "30s"]):
            return False

    return True  # Similar enough to reuse


def _store_voice(library: dict, npc_id: str, voice_id: str, prompt: str) -> None:
    """Store voice with metadata for future comparison."""
    library[npc_id] = {"voice_id": voice_id, "prompt": prompt}


def _get_voice_id(entry: str | dict) -> str:
    """Extract voice_id from either legacy string format or new dict format."""
    if isinstance(entry, dict):
        return entry.get("voice_id", "")
    return entry


def _get_prompt(entry: str | dict) -> str:
    """Extract design prompt from either legacy string format or new dict format."""
    if isinstance(entry, dict):
        return entry.get("prompt", "")
    return ""


def _load(p: Path) -> dict:
    """Load voice library (supports both legacy and new format)."""
    return json.loads(p.read_text()) if p.exists() else {}


def _save(p: Path, lib: dict) -> None:
    """Save voice library with metadata."""
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(lib, indent=2))
