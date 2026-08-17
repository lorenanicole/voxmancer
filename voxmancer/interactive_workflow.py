"""Interactive end-to-end workflow: NPCs → scene → audio."""
from __future__ import annotations

from pathlib import Path

from .models import Campaign, NPCBrief
from .pipeline import run
from .core.voice_enricher import enrich_voice_prompt
from .core.voice_mapper import map_voice_prompt_to_piper


def interactive_workflow(work_dir: Path = Path(".voxmancer"), demo: bool = False) -> None:
    """Guide user through: NPCs → scene premise → render → MP3.

    Args:
        demo: If True, use predefined demo values (skip interactive prompts)
    """

    print("\n" + "=" * 60)
    print("🎭 VOXMANCER INTERACTIVE WORKFLOW")
    print("=" * 60)
    print("\nLet's create your D&D audio drama.\n")

    if demo:
        return _demo_workflow(work_dir)

    # Step 1: Campaign & Scene info
    campaign_title = input("Campaign name (e.g., 'Axfori's Adventures'): ").strip()
    if not campaign_title:
        campaign_title = "Untitled Campaign"

    scene_title = input("Scene title (e.g., 'At the Market'): ").strip()
    if not scene_title:
        scene_title = "A Scene"

    lead_character = input("Lead character name (e.g., 'Axfori'): ").strip()
    if not lead_character:
        lead_character = "The Hero"

    # Ask if lead character is in the scene
    lead_in_scene = (
        input(f"Is {lead_character} in this scene? (y/n, default y): ").strip().lower() != "n"
    )

    # Only ask absence reason if lead is NOT in scene
    if lead_in_scene:
        absence_reason = f"{lead_character} is present in the scene"
    else:
        absence_reason = input(
            f"Why is {lead_character} absent? (e.g., 'recovering at the temple'): "
        ).strip()
        if not absence_reason:
            absence_reason = "away from the scene"

    # Step 2: Define NPCs
    print("\n" + "-" * 60)
    print("Define your NPCs (press Enter with empty name to finish)")
    print("-" * 60)

    npcs: list[NPCBrief] = []
    npc_count = 0

    while True:
        npc_count += 1
        print(f"\n[NPC #{npc_count}]")

        npc_id = input("  NPC ID (e.g., 'brakk-emberhand'): ").strip()
        if not npc_id:
            break

        name = input("  Full name: ").strip() or npc_id
        species = input("  Species (e.g., 'dwarf'): ").strip() or "human"
        role = input("  Role (e.g., 'blacksmith, mentor'): ").strip()
        personality = input("  Personality (e.g., 'gruff, loyal'): ").strip()

        print("\n  Voice Prompt (multi-line, press Enter twice to finish):")
        print("  Example: 'Male, 60+. Gruff mentor. Low gravelly voice.'")
        voice_lines = []
        while True:
            line = input("  ").strip()
            if not line:
                if voice_lines:
                    break
                print("  (Please enter at least one line)")
                continue
            voice_lines.append(line)

        voice_prompt = " ".join(voice_lines)

        # Enrich sparse voice prompt if needed
        if len(voice_prompt) < 80:
            print("\n  Enriching voice prompt with LLM...")
            enriched = enrich_voice_prompt(voice_prompt, name, role)
            print(f"  Original: {voice_prompt}")
            print(f"  Enriched: {enriched}")
            voice_prompt = enriched

        npc = NPCBrief(
            id=npc_id,
            name=name,
            species=species,
            role=role,
            personality=personality,
            voice_prompt=voice_prompt,
        )
        npcs.append(npc)
        print(f"  ✓ Added {name}")

    if not npcs:
        print("\n❌ No NPCs defined. Exiting.")
        return

    # Auto-add narrator if not already defined
    if not any(npc.id == "narrator" for npc in npcs):
        narrator = NPCBrief(
            id="narrator",
            name="Narrator",
            species="storyteller",
            role="narration",
            personality="measured, atmospheric",
            voice_prompt="A calm, cinematic storyteller. Unhurried, low, warm — the voice of firelight and rain.",
        )
        npcs.insert(0, narrator)
        print("\n✓ Added narrator (auto)")

    # Step 3: Setting and scene premise
    print("\n" + "-" * 60)
    print(f"Scene: {scene_title}")
    print("-" * 60)

    setting = (
        input("Where does this scene take place? (tavern, market, forest, etc.): ").strip()
        or "A tavern"
    )

    scene_premise = (
        input("What happens in this scene? (1-2 sentences): ").strip()
        or "An interesting encounter."
    )

    # Step 4: Show summary
    print("\n" + "-" * 60)
    print("Scene Summary")
    print("-" * 60)
    print(f"  Campaign: {campaign_title}")
    print(f"  Scene: {scene_title}")
    print(f"  Setting: {setting}")
    print(f"  Lead character: {lead_character} ({'in scene' if lead_in_scene else 'absent'})")
    print(f"  NPCs: {', '.join(npc.name for npc in npcs)}")
    print(f"  Premise: {scene_premise}")

    # Step 5: Backend selection
    print("\n" + "-" * 60)
    print("Backend Selection")
    print("-" * 60)
    print("1. Piper (CPU-friendly, pre-trained voices)")
    print("2. Parler (GPU-friendly, text-prompt based)")
    print("3. ElevenLabs (cloud API, highest quality)")
    backend_choice = input("\nChoose backend (1-3, default 1): ").strip() or "1"

    tts_backend_map = {"1": "piper", "2": "parler", "3": "elevenlabs"}
    tts_backend = tts_backend_map.get(backend_choice, "piper")

    # Step 5: Create campaign
    campaign = Campaign(
        title=campaign_title,
        lead_character=lead_character,
        absence_reason=absence_reason,
        npcs=npcs,
    )

    # Step 6: Map voices to backend
    print("\n" + "-" * 60)
    print("Mapping Voices")
    print("-" * 60)

    if tts_backend == "piper":
        print("\nMapping voice prompts to Piper voices...")
        for npc in campaign.npcs:
            piper_voice = map_voice_prompt_to_piper(npc.voice_prompt)
            npc.voice_id = piper_voice
            print(f"  {npc.name} → {piper_voice}")
    else:
        print(f"\nUsing {tts_backend} for voice generation...")
        print("(Voices will be generated on first render)")

    # Step 7: Generate scene
    print("\n" + "-" * 60)
    print("Generating Scene")
    print("-" * 60)
    print(f"Premise: {scene_premise}")
    print("Using Ollama Mistral to write dialogue...\n")

    # Step 8: Render
    print("-" * 60)
    print("Rendering Audio")
    print("-" * 60)

    safe_scene_title = scene_title.lower().replace(" ", "_").replace("'", "")
    out_path = Path("out") / f"{tts_backend}_{safe_scene_title}.mp3"

    try:
        # Temporarily set backend in environment
        import os

        old_backend = os.environ.get("TTS_BACKEND")
        os.environ["TTS_BACKEND"] = tts_backend

        result = run(
            campaign_path=_create_temp_campaign(campaign, setting, scene_premise),
            out_path=out_path,
            work_dir=work_dir,
        )

        if old_backend:
            os.environ["TTS_BACKEND"] = old_backend
        elif "TTS_BACKEND" in os.environ:
            del os.environ["TTS_BACKEND"]

        print("\n✅ Success!")
        print(f"   Audio: {result.audio_path}")
        print(f"   Lines: {len(result.scene.lines)}")
        print(f"   Voices: {len(result.voice_library)}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


def _demo_workflow(work_dir: Path) -> None:
    """Run demo workflow with predefined values (no interactive prompts)."""
    import os

    print("🎬 Running DEMO mode (predefined values)\n")

    # Predefined demo data
    campaign_title = "Axfori's Market Day"
    scene_title = "At the Market"
    lead_character = "Axfori"
    setting = "A bustling market square"
    scene_premise = "Axfori negotiates with a mysterious merchant over rare supplies"

    # Use TTS_BACKEND from .env, default to piper
    tts_backend = os.environ.get("TTS_BACKEND", "piper").lower()

    # Demo NPC voices created via ElevenLabs Voice Design
    # These voice_ids were created from custom prompts and will be cached for reuse
    npcs = [
        NPCBrief(
            id="narrator",
            name="Narrator",
            species="storyteller",
            role="narration",
            personality="measured, atmospheric",
            voice_prompt="English. Male, 40s. Premium quality. Professional storyteller voice. Warm, engaging, with natural pacing and dramatic timing. Clear enunciation perfect for narration. Think: podcast host meets fantasy audiobook narrator. Authoritative yet approachable, capable of building tension and wonder.",
            voice_id="Q5zbZ6T7eyWJVLdK6afB" if tts_backend == "elevenlabs" else None,
        ),
        NPCBrief(
            id="axfori",
            name="Axfori",
            species="human",
            role="protagonist",
            personality="brave, determined, pragmatic",
            voice_prompt="English. Female, 30s. Premium quality. Confident warrior voice with edge. Strong, decisive delivery with underlying determination. Slightly husky tone, battle-hardened but not cold. Sharp, commanding presence—someone you don't want to cross but can trust. Quick-paced speech with natural confidence and presence.",
            voice_id="qgkR3bMrLY4ubF6WL7sL" if tts_backend == "elevenlabs" else None,
        ),
        NPCBrief(
            id="merchant",
            name="Mysterious Merchant",
            species="human",
            role="merchant",
            personality="mysterious, clever, secretive",
            voice_prompt="English. Male, 50s. Premium quality. Enigmatic merchant character voice. Silky smooth yet slightly mysterious delivery with knowing undertones. Worldly, intelligent, with calculated pauses for effect. Faint exotic accent hint. Charismatic without being trustworthy. Someone who has seen everything and plays every angle.",
            voice_id="gRZJvE4lKVC8U4YyHa9q" if tts_backend == "elevenlabs" else None,
        ),
    ]

    absence_reason = f"{lead_character} is present in the scene"

    print(f"Campaign: {campaign_title}")
    print(f"Scene: {scene_title}")
    print(f"NPCs: {', '.join(npc.name for npc in npcs)}")
    print(f"Setting: {setting}")
    print(f"Premise: {scene_premise}")
    backend_desc = (
        "cloud API, highest quality"
        if tts_backend == "elevenlabs"
        else "CPU-friendly, pre-trained voices"
    )
    print(f"Backend: {tts_backend.capitalize()} ({backend_desc})\n")

    # Create campaign
    campaign = Campaign(
        title=campaign_title,
        lead_character=lead_character,
        absence_reason=absence_reason,
        npcs=npcs,
    )

    # Map voices (only for Piper; ElevenLabs designs on first render)
    print("-" * 60)
    print("Mapping Voices")
    print("-" * 60)
    if tts_backend == "piper":
        print("\nMapping voice prompts to Piper voices...")
        for npc in campaign.npcs:
            piper_voice = map_voice_prompt_to_piper(npc.voice_prompt)
            npc.voice_id = piper_voice
            print(f"  {npc.name} → {piper_voice}")
    else:
        print(f"\nUsing {tts_backend} for voice generation...")
        print("(Voices will be designed and cached on first render)")

    # Generate scene
    print("\n" + "-" * 60)
    print("Generating Scene")
    print("-" * 60)
    print(f"Premise: {scene_premise}")
    print("Using Ollama Mistral to write dialogue...\n")

    # Render
    print("-" * 60)
    print("Rendering Audio")
    print("-" * 60)

    safe_scene_title = scene_title.lower().replace(" ", "_").replace("'", "")
    out_path = Path("out") / f"{tts_backend}_{safe_scene_title}.mp3"

    try:
        old_backend = os.environ.get("TTS_BACKEND")
        os.environ["TTS_BACKEND"] = tts_backend

        campaign_path = _create_temp_campaign(campaign, setting, scene_premise)
        result = run(
            campaign_path=campaign_path,
            out_path=out_path,
            work_dir=work_dir,
        )

        if old_backend:
            os.environ["TTS_BACKEND"] = old_backend
        elif "TTS_BACKEND" in os.environ:
            del os.environ["TTS_BACKEND"]

        # Save example files for reuse
        example_dir = Path("examples")
        example_dir.mkdir(exist_ok=True)

        safe_title = scene_title.lower().replace(" ", "_").replace("'", "")
        campaign_output = example_dir / f"{safe_title}.campaign.yaml"
        scene_output = example_dir / f"{safe_title}.scene.yaml"

        # Copy campaign file
        import shutil

        shutil.copy(campaign_path, campaign_output)

        # Save generated scene
        import yaml

        with open(scene_output, "w") as f:
            scene_dict = {
                "title": result.scene.title,
                "lines": [
                    {
                        "speaker": line.speaker,
                        "text": line.text,
                        "direction": line.direction,
                    }
                    for line in result.scene.lines
                ],
            }
            yaml.dump(scene_dict, f, default_flow_style=False, sort_keys=False)

        print("\n✅ Success!")
        print(f"   Audio: {result.audio_path}")
        print(f"   Lines: {len(result.scene.lines)}")
        print(f"   Voices: {len(result.voice_library)}")
        print("\n📁 Example files saved:")
        print(f"   Campaign: {campaign_output}")
        print(f"   Scene: {scene_output}")
        print(f"\n🎧 Listen: open {result.audio_path}")
        print("\n💡 Rerun with these files:")
        print(f"   poetry run voxmancer render {campaign_output} {scene_output} -o out/rerun.mp3")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


def _create_temp_campaign(
    campaign: Campaign, setting: str = "", interlude_premise: str = ""
) -> Path:
    """Save campaign to temp file with proper structure."""
    import yaml

    temp_path = Path(".voxmancer") / "_interactive_campaign.yaml"
    temp_path.parent.mkdir(exist_ok=True)

    with open(temp_path, "w") as f:
        data = {
            "title": campaign.title,
            "setting": setting or campaign.title,
            "lead_character": campaign.lead_character,
            "absence_reason": campaign.absence_reason,
            "interlude_premise": interlude_premise or "An interlude while the lead is away.",
            "npcs": [
                {
                    "id": npc.id,
                    "name": npc.name,
                    "species": npc.species,
                    "role": npc.role,
                    "personality": npc.personality,
                    "voice_prompt": npc.voice_prompt,
                }
                for npc in campaign.npcs
            ],
        }
        yaml.dump(data, f, default_flow_style=False)

    return temp_path
