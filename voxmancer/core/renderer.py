"""Stage 3 — render a Scene to a single audio file, line by line.

Each line is synthesized in its speaker's voice, then the clips are stitched
together with a short beat of silence between them. Concatenation uses pydub,
which needs ffmpeg on the PATH.
"""
from __future__ import annotations

from pathlib import Path

from ..tts.eleven_client import ElevenClient
from ..models import Campaign, Scene


def render_scene(
    scene: Scene,
    campaign: Campaign,
    client: ElevenClient,
    out_path: Path,
    work_dir: Path,
) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)
    by_id = {n.id: n for n in campaign.npcs}

    clips: list[Path] = []
    for i, line in enumerate(scene.lines):
        npc = by_id.get(line.speaker)
        if npc is None or not npc.voice_id:
            raise ValueError(
                f"Line {i}: no voice for speaker '{line.speaker}'. "
                "Is it in the roster, and did voice design run?"
            )
        clip = work_dir / f"{i:03d}_{line.speaker}.mp3"
        client.text_to_speech(npc.voice_id, line.text, str(clip), line.direction)
        clips.append(clip)

    return _concat(clips, out_path)


def _concat(clips: list[Path], out_path: Path) -> Path:
    import subprocess
    import tempfile

    out_path.parent.mkdir(parents=True, exist_ok=True)

    silence_path = out_path.parent / "silence.mp3"
    if not silence_path.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=mono",
                "-t",
                "0.8",  # 800ms silence between speakers for natural pauses
                "-q:a",
                "9",
                "-acodec",
                "libmp3lame",
                str(silence_path),
            ],
            check=True,
            capture_output=True,
        )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for clip in clips:
            f.write(f"file '{clip.absolute()}'\n")
            f.write(f"file '{silence_path.absolute()}'\n")
        concat_file = f.name

    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_file,
                "-c:a",
                "libmp3lame",
                "-q:a",
                "9",
                str(out_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg concat failed: {result.stderr}")
    finally:
        Path(concat_file).unlink()

    return out_path
