"""Tests for data models."""
import pytest
from voxmancer.models import NPCBrief, Scene, Campaign, DialogueLine


@pytest.mark.unit
def test_npc_brief_creation():
    """Test creating an NPC."""
    npc = NPCBrief(
        id="narrator",
        name="Narrator",
        species="storyteller",
        role="narration",
        personality="measured, atmospheric",
        voice_prompt="A calm, cinematic storyteller.",
    )
    assert npc.id == "narrator"
    assert npc.name == "Narrator"
    assert npc.species == "storyteller"
    assert npc.role == "narration"


@pytest.mark.unit
def test_npc_brief_optional_fields():
    """Test NPC with optional fields."""
    npc = NPCBrief(
        id="axfori",
        name="Axfori",
        species="human",
        role="protagonist",
        personality="brave",
        voice_prompt="Female warrior",
        age="30s",
        voice_id="en_US-amy-medium",
    )
    assert npc.age == "30s"
    assert npc.voice_id == "en_US-amy-medium"


@pytest.mark.unit
def test_dialogue_line_creation():
    """Test creating a dialogue line."""
    line = DialogueLine(
        speaker="axfori",
        text="What supplies do you have?",
        direction="curious",
    )
    assert line.speaker == "axfori"
    assert line.text == "What supplies do you have?"
    assert line.direction == "curious"


@pytest.mark.unit
def test_dialogue_line_no_direction():
    """Test dialogue line without direction."""
    line = DialogueLine(speaker="narrator", text="The scene unfolds...")
    assert line.speaker == "narrator"
    assert line.direction is None


@pytest.mark.unit
def test_scene_creation():
    """Test creating a scene."""
    lines = [
        DialogueLine(speaker="narrator", text="In the market..."),
        DialogueLine(speaker="axfori", text="Hello!", direction="cheerful"),
    ]
    scene = Scene(
        title="Market Meeting",
        summary="Axfori meets a merchant",
        lines=lines,
    )
    assert scene.title == "Market Meeting"
    assert len(scene.lines) == 2
    assert scene.lines[0].speaker == "narrator"


@pytest.mark.unit
def test_campaign_creation():
    """Test creating a campaign."""
    npcs = [
        NPCBrief(
            id="narrator",
            name="Narrator",
            species="storyteller",
            role="narration",
            personality="measured",
            voice_prompt="Calm voice",
        ),
    ]
    campaign = Campaign(
        title="Test Campaign",
        lead_character="Hero",
        absence_reason="Recovering",
        npcs=npcs,
    )
    assert campaign.title == "Test Campaign"
    assert campaign.lead_character == "Hero"
    assert len(campaign.npcs) == 1


@pytest.mark.unit
def test_campaign_with_setting():
    """Test campaign with setting."""
    campaign = Campaign(
        title="Adventure",
        lead_character="Knight",
        absence_reason="Away",
        npcs=[],
        setting="Dark castle",
    )
    assert campaign.setting == "Dark castle"
