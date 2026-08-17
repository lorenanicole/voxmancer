"""Stage 4 (optional but the point) — the 'is this voice actually right?' eval.

This is the DevRel / evaluation angle, and the most interesting part of the
project: don't *assume* a generated voice matches its brief — measure it.

Two checks worth building:

1. Brief-match — does the rendered clip sound like NPCBrief.voice_prompt?
   Approach: transcribe the clip (an STT model) to confirm intelligibility,
   and/or ask a judge model to rate perceived age / tone / accent against the
   brief on a 0-1 scale. Cheap, and it catches "the old dwarf sounds 25".

2. Cross-session consistency — does an NPC sound the SAME as last time?
   Approach: keep one reference clip per voice_id; compare speaker-embedding
   similarity (e.g. resemblyzer / pyannote) between the reference and the new
   clip. Flag drift below a threshold.

Both are PLACEHOLDERS. Wiring up even #1 turns this from a toy into a portfolio
piece — and "here's the eval I built to trust the output" is exactly the story
that lands in an interview.
"""
from __future__ import annotations

from pathlib import Path

from ..models import NPCBrief, VoiceCheck


def check_voice(npc: NPCBrief, clip_path: Path, reference_clip: Path | None = None) -> VoiceCheck:
    raise NotImplementedError(
        "Implement the consistency eval — see this module's docstring for two "
        "concrete approaches (brief-match and cross-session similarity)."
    )
