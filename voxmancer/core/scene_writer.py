"""Stage 1 — an LLM writes the interlude Scene from a Campaign.

The LLM call is a PLACEHOLDER; swap in your provider (Anthropic shown). The
prompt-building is real, so you can inspect exactly what gets sent.
"""
from __future__ import annotations


from ..config import get_settings
from ..models import Campaign, Scene

SYSTEM = (
    "You are a Dungeon Master's writing assistant. Given a campaign, its cast of "
    "NPCs, and a premise, write a short, vivid interlude that happens while the "
    "lead character is away. Keep each NPC's voice distinct. Return ONLY JSON of "
    'the form {"title": str, "summary": str, "lines": [{"speaker": str, "text": '
    'str, "direction": str|null}]}. Each `speaker` must be an NPC id from the '
    'roster (a "narrator" id is allowed).'
)


def _get_llm_client():
    """Return the configured LLM client (Anthropic, Ollama, or Runpod Flash)."""
    settings = get_settings()
    backend = settings.llm_backend.lower()

    if backend == "ollama":
        from ..llm.ollama_llm_backend import OllamaLLMClient

        return OllamaLLMClient()
    elif backend == "runpod_flash":
        from ..llm.runpod_llm_backend import RunpodLLMClient

        return RunpodLLMClient()
    elif backend == "anthropic":
        from anthropic import Anthropic

        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set (see .env.example).")
        return Anthropic(api_key=settings.anthropic_api_key)
    else:
        raise ValueError(
            f"Unknown LLM_BACKEND: {backend}. Choose 'anthropic', 'ollama', or 'runpod_flash'."
        )


def write_scene(campaign: Campaign) -> Scene:
    """Generate a Scene for `campaign.interlude_premise`."""
    import json

    prompt = build_prompt(campaign)
    settings = get_settings()
    client = _get_llm_client()
    backend = settings.llm_backend.lower()

    # Handle different LLM backend interfaces
    if backend == "ollama":
        msg = client.messages_create(
            model=settings.llm_model,
            system=SYSTEM,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
    else:
        # Anthropic and Runpod use .messages.create()
        msg = client.messages.create(
            model=settings.llm_model,
            system=SYSTEM,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

    return Scene(**json.loads(msg.content[0].text))


def build_prompt(campaign: Campaign) -> str:
    roster = "\n".join(
        f"- {n.id}: {n.name}, {(n.age or '').strip()} {n.species} — {n.role}. "
        f"Personality: {n.personality}."
        for n in campaign.npcs
    )
    return (
        f"Campaign: {campaign.title}\n"
        f"Setting: {campaign.setting}\n"
        f"Lead character (currently away): {campaign.lead_character} "
        f"— {campaign.absence_reason}\n\n"
        f"NPC roster:\n{roster}\n\n"
        f"Premise for this interlude: {campaign.interlude_premise}\n\n"
        "Write 8-14 dialogue lines."
    )
