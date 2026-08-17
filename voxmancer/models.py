"""Core data models for Voxmancer.

Everything the pipeline passes around is a typed Pydantic model, so a bad
campaign file fails loudly at load time instead of deep inside an API call.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class NPCBrief(BaseModel):
    """One non-player character: who they are and, crucially, how they SOUND."""

    id: str = Field(..., description="stable slug, e.g. 'brakk-emberhand'")
    name: str
    species: str = "human"
    role: str = Field("", description="what they are in the story: blacksmith, healer, rival")
    age: str | None = Field(None, description="young / middle-aged / old")
    personality: str = Field(..., description="a few adjectives / temperament")
    voice_prompt: str = Field(
        ...,
        description="how they SOUND — this string is fed to ElevenLabs Voice Design",
    )
    accent: str | None = None

    # Populated after voice design; persisted to the voice library so the NPC
    # sounds the same in every future session.
    voice_id: str | None = None


class DialogueLine(BaseModel):
    """A single spoken line in a scene."""

    speaker: str = Field(..., description="an NPCBrief.id (a 'narrator' NPC is allowed)")
    text: str
    direction: str | None = Field(None, description="acting note, e.g. '(wary, low)'")


class Scene(BaseModel):
    """An interlude: an ordered list of lines to be voiced."""

    title: str
    summary: str = ""
    lines: list[DialogueLine] = Field(default_factory=list)


class Campaign(BaseModel):
    """The whole input: the world, the absent lead, and the cast."""

    title: str
    setting: str = ""
    lead_character: str = Field(..., description="the PC who is 'away' — e.g. Axfori")
    absence_reason: str = Field("", description="why the lead is off-screen")
    interlude_premise: str = Field("", description="what the generated scene should cover")
    npcs: list[NPCBrief] = Field(default_factory=list)


class VoiceCheck(BaseModel):
    """Result of the consistency eval for one NPC's rendered audio."""

    npc_id: str
    matches_brief: bool
    score: float = Field(..., ge=0.0, le=1.0)
    notes: str = ""


class RenderResult(BaseModel):
    """What a full pipeline run returns."""

    audio_path: str
    scene: Scene
    voice_library: dict[str, str] = Field(default_factory=dict)  # npc_id -> voice_id
    checks: list[VoiceCheck] = Field(default_factory=list)
