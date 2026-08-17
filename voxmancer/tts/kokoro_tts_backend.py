"""Open-source TTS backend using Kokoro with voice customization.

Kokoro is a lightweight (82M parameter) text-to-speech model that supports
voice customization via text prompts describing voice characteristics.

Setup:
  1. Install: poetry install --extras kokoro
  2. Set: TTS_BACKEND=kokoro
  3. Run (no additional downloads needed)
"""
from __future__ import annotations

from pathlib import Path


class KokoroTTSClient:
    """Open-source TTS using Kokoro with voice customization."""

    def __init__(self) -> None:
        try:
            import kokoro

            self.kokoro = kokoro
        except ImportError:
            raise RuntimeError("Kokoro not installed. Install with: poetry install --extras kokoro")

        # Kokoro voice presets that can be customized
        self.available_voices = {
            "af": "Female voice",
            "am": "Male voice",
            "bf": "Female voice",
            "bm": "Male voice",
        }
        self._voice_cache = {}

    def design_voice(self, name: str, prompt: str) -> str:
        """Map a voice prompt to a Kokoro voice preset.

        Returns a voice identifier that combines preset + customization info.
        For Kokoro, we use the voice mapper to select appropriate presets
        based on the prompt description.
        """
        # Use voice mapper to select appropriate preset from prompt
        # Kokoro has limited presets (af, am, bf, bm) so we map to these
        voice_id = self._map_prompt_to_kokoro_voice(prompt)
        self._voice_cache[name] = {"prompt": prompt, "voice_id": voice_id}
        return voice_id

    def _map_prompt_to_kokoro_voice(self, prompt: str) -> str:
        """Map voice prompt to a Kokoro voice preset.

        Kokoro has 4 main voices (af, am, bf, bm).
        We select based on gender indicators in the prompt.
        """
        prompt_lower = prompt.lower()

        # Detect gender from prompt
        if "female" in prompt_lower or "woman" in prompt_lower or "girl" in prompt_lower:
            # Female voices: af (American), bf (British)
            if "american" in prompt_lower or "us" in prompt_lower:
                return "af"  # American female
            else:
                return "bf"  # British/other female
        else:
            # Male voices: am (American), bm (British)
            if "american" in prompt_lower or "us" in prompt_lower:
                return "am"  # American male
            else:
                return "bm"  # British/other male

    def text_to_speech(
        self, voice_id: str, text: str, out_path: str, direction: str | None = None
    ) -> str:
        """Synthesize speech using Kokoro.

        Args:
            voice_id: Kokoro voice preset (af, am, bf, bm)
            text: Text to synthesize
            out_path: Output audio file path
            direction: Acting direction (prepended to text)

        Returns:
            Path to generated audio file
        """
        if direction:
            text = f"({direction}) {text}"

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            # Kokoro synthesis
            generator = self.kokoro.generate(text, voice=voice_id, speed=1.0)

            # Save audio to file
            audio_data = generator.audio if hasattr(generator, "audio") else generator

            # Kokoro returns audio as numpy array, convert to wav
            import scipy.io.wavfile
            import numpy as np

            if isinstance(audio_data, np.ndarray):
                # Write as WAV first, then convert to MP3 if needed
                wav_path = str(out_path).replace(".mp3", ".wav")
                scipy.io.wavfile.write(wav_path, 24000, audio_data)

                # Convert WAV to MP3 using FFmpeg
                import subprocess

                subprocess.run(
                    ["ffmpeg", "-i", wav_path, "-q:a", "9", "-acodec", "libmp3lame", out_path],
                    check=True,
                    capture_output=True,
                )
                Path(wav_path).unlink()  # Clean up temp WAV

            return out_path

        except Exception as e:
            raise RuntimeError(f"Kokoro TTS synthesis failed: {e}")

    def sound_effect(self, prompt: str, out_path: str) -> str:
        """Generate ambient sound effect from text prompt.

        Kokoro is a TTS model, not designed for sound effects.
        This is a placeholder that generates silence or uses TTS as fallback.
        """
        # For now, generate a brief neutral speech as placeholder
        return self.text_to_speech("af", f"ambient: {prompt}", out_path)
