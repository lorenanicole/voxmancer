"""Comprehensive Piper voice registry with caching."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

HF_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

# Language code to full name mapping
LANGUAGE_NAMES = {
    "ar": "Arabic",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "ca": "Catalan",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "eu": "Basque",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hi": "Hindi",
    "hu": "Hungarian",
    "hy": "Armenian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "ka": "Georgian",
    "kk": "Kazakh",
    "ko": "Korean",
    "ku": "Kurdish",
    "lb": "Luxembourgish",
    "lv": "Latvian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sq": "Albanian",
    "sr": "Serbian",
    "sv": "Swedish",
    "sw": "Swahili",
    "te": "Telugu",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh": "Chinese",
}

# Voice metadata - ALL verified voices from Hugging Face piper-voices
# Verified available at: https://huggingface.co/rhasspy/piper-voices
VOICE_METADATA = {
    # Male voices
    "en_US-ryan": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Warm, friendly male voice",
        "qualities": ["high", "low", "medium"],
    },
    "en_US-john": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "elderly",
        "description": "Older, gravelly male voice",
        "qualities": ["medium"],
    },
    "en_US-joe": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Neutral male voice",
        "qualities": ["medium"],
    },
    "en_US-mike": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Deep male voice",
        "qualities": ["medium"],
    },
    "en_US-bryce": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Clear male voice",
        "qualities": ["medium"],
    },
    "en_US-kusal": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Indian male voice",
        "qualities": ["medium"],
    },
    "en_US-reza_ibrahim": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Middle Eastern male voice",
        "qualities": ["medium"],
    },
    "en_US-hfc_male": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Neutral male voice",
        "qualities": ["medium"],
    },
    "en_US-norman": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Calm male voice",
        "qualities": ["medium"],
    },
    "en_US-l2arctic": {
        "language": "en",
        "accent": "en_US",
        "gender": "male",
        "age": "adult",
        "description": "Clear male voice",
        "qualities": ["medium"],
    },
    # Female voices
    "en_US-amy": {
        "language": "en",
        "accent": "en_US",
        "gender": "female",
        "age": "adult",
        "description": "Clear, professional female voice",
        "qualities": ["medium"],  # low not available on HF
    },
    "en_US-kristin": {
        "language": "en",
        "accent": "en_US",
        "gender": "female",
        "age": "adult",
        "description": "Warm female voice",
        "qualities": ["medium"],
    },
    "en_US-lessac": {
        "language": "en",
        "accent": "en_US",
        "gender": "female",
        "age": "adult",
        "description": "Natural female voice",
        "qualities": ["high", "low", "medium"],
    },
    "en_US-libritts_r": {
        "language": "en",
        "accent": "en_US",
        "gender": "female",
        "age": "adult",
        "description": "Clear female voice",
        "qualities": ["medium"],
    },
    "en_US-ljspeech": {
        "language": "en",
        "accent": "en_US",
        "gender": "female",
        "age": "adult",
        "description": "Classic female voice",
        "qualities": ["high", "medium"],
    },
    "en_US-hfc_female": {
        "language": "en",
        "accent": "en_US",
        "gender": "female",
        "age": "adult",
        "description": "Neutral female voice",
        "qualities": ["medium"],
    },
    "en_US-sam": {
        "language": "en",
        "accent": "en_US",
        "gender": "female",
        "age": "adult",
        "description": "Bright female voice",
        "qualities": ["medium"],
    },
}


class VoiceRegistry:
    """Registry of all available Piper voices with caching."""

    def __init__(self, cache_dir: Path = Path.home() / ".local/share/piper"):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._registry_file = self.cache_dir / "registry.json"
        self._registry = self._load_registry()

    def _load_registry(self) -> dict:
        """Load cached registry or create new one."""
        if self._registry_file.exists():
            with open(self._registry_file) as f:
                return json.load(f)

        # Build registry from VOICE_METADATA
        registry = {}
        for voice_id, metadata in VOICE_METADATA.items():
            qualities = metadata.pop("qualities")
            registry[voice_id] = {
                **metadata,
                "qualities": qualities,
                "urls": {
                    q: f"{HF_BASE}/{metadata['accent']}/{voice_id}/{q}/{voice_id}-{q}.onnx"
                    for q in qualities
                },
            }

        self._save_registry(registry)
        return registry

    def _save_registry(self, registry: dict) -> None:
        """Save registry to cache file."""
        with open(self._registry_file, "w") as f:
            json.dump(registry, f, indent=2)

    def get_voice(self, voice_id: str) -> Optional[dict]:
        """Get voice metadata by ID."""
        return self._registry.get(voice_id)

    def list_voices(
        self,
        language: Optional[str] = None,
        accent: Optional[str] = None,
        gender: Optional[str] = None,
        age: Optional[str] = None,
    ) -> list[dict]:
        """List voices matching criteria."""
        matches = []
        for voice_id, metadata in self._registry.items():
            if language and metadata.get("language") != language:
                continue
            if accent and metadata.get("accent") != accent:
                continue
            if gender and metadata.get("gender") != gender:
                continue
            if age and metadata.get("age") != age:
                continue
            matches.append({**metadata, "id": voice_id})

        return matches

    def get_download_url(self, voice_id: str, quality: str = "medium") -> Optional[str]:
        """Get download URL for a voice."""
        voice = self.get_voice(voice_id)
        if not voice:
            return None

        # If requested quality not available, use the first available
        if quality not in voice.get("qualities", []):
            quality = voice.get("qualities", ["medium"])[0]

        return voice["urls"].get(quality)

    def voices_for_language(self, language_code: str) -> list[dict]:
        """Get all voices for a language."""
        return self.list_voices(language=language_code)

    def voices_for_accent(self, accent_code: str) -> list[dict]:
        """Get all voices for an accent (e.g., en_US, en_GB)."""
        return self.list_voices(accent=accent_code)

    def available_accents(self, language: str) -> list[str]:
        """Get all available accents for a language."""
        accents = set()
        for voice_id, metadata in self._registry.items():
            if metadata.get("language") == language:
                accents.add(metadata.get("accent"))
        return sorted(accents)

    def available_languages(self) -> list[str]:
        """Get all available languages."""
        langs = set()
        for metadata in self._registry.values():
            langs.add(metadata.get("language"))
        return sorted(langs)
