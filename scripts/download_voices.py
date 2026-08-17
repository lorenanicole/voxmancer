#!/usr/bin/env python3
"""Pre-download all Piper voices for demo purposes."""
import subprocess
from pathlib import Path

PIPER_VOICES_HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US"

# All verified voices with their available qualities
VOICES = {
    "en_US-ryan": ["low", "medium", "high"],
    "en_US-john": ["medium"],
    "en_US-joe": ["medium"],
    "en_US-mike": ["medium"],
    "en_US-bryce": ["medium"],
    "en_US-kusal": ["medium"],
    "en_US-reza_ibrahim": ["medium"],
    "en_US-hfc_male": ["medium"],
    "en_US-arctic": ["medium"],
    "en_US-norman": ["medium"],
    "en_US-l2arctic": ["medium"],
    "en_US-amy": ["low", "medium"],
    "en_US-kristin": ["medium"],
    "en_US-lessac": ["low", "medium", "high"],
    "en_US-libritts_r": ["medium"],
    "en_US-ljspeech": ["medium", "high"],
    "en_US-hfc_female": ["medium"],
    "en_US-sam": ["medium"],
}

voices_dir = Path.home() / ".local/share/piper"
voices_dir.mkdir(parents=True, exist_ok=True)

total = sum(len(q) for q in VOICES.values())
downloaded = 0

print(f"🎙️ Downloading {total} Piper voices...\n")

for voice_id, qualities in sorted(VOICES.items()):
    for quality in qualities:
        voice_path = voices_dir / f"{voice_id}-{quality}.onnx"
        config_path = voices_dir / f"{voice_id}-{quality}.onnx.json"

        # Skip if already downloaded (real files are > 50MB)
        if voice_path.exists() and voice_path.stat().st_size > 50_000_000:
            print(f"✓ {voice_id}-{quality} (cached)")
            downloaded += 1
            continue

        print(f"  Downloading {voice_id}-{quality}...", end=" ", flush=True)

        # Extract speaker name from voice_id (e.g., "en_US-ryan" -> "ryan")
        speaker_name = voice_id.split("-", 1)[1]

        # Download model
        url = f"{PIPER_VOICES_HF}/{speaker_name}/{quality}/{voice_id}-{quality}.onnx"
        try:
            result = subprocess.run(
                ["curl", "-L", "-o", str(voice_path), url],
                capture_output=True,
                timeout=300,
                check=True,
            )
            size = voice_path.stat().st_size / (1024 * 1024)
            print(f"✓ ({size:.1f}MB)")
            downloaded += 1
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed")
            voice_path.unlink(missing_ok=True)
            continue

        # Create config file
        config_data = """{
  "audio": {"sample_rate": 22050},
  "espeak": {"voice": "en-us"},
  "inference": {
    "length_scale": 1.0,
    "noise_scale": 0.667,
    "noise_w_scale": 0.8,
    "speakers_file": null
  },
  "model": {"architecture": "glow-tts", "num_speakers": 1},
  "num_symbols": 148,
  "num_speakers": 1,
  "phoneme_id_map": {},
  "version": "1.0.0"
}"""
        config_path.write_text(config_data)

print(f"\n✅ Downloaded {downloaded}/{total} voices")
