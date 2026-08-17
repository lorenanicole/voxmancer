"""Voxmancer CLI (stdlib argparse — no extra deps).

    python -m voxmancer.cli preview examples/axfori_campaign.yaml
    python -m voxmancer.cli render  examples/axfori_campaign.yaml \\
        --scene examples/axfori_interlude.scene.yaml --out out/interlude.mp3
    python -m voxmancer.cli workflow  # Interactive end-to-end
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .interactive_workflow import interactive_workflow
from .pipeline import load_campaign, run


def _preview(args: argparse.Namespace) -> None:
    """Load a campaign and print the cast. Makes no API calls."""
    c = load_campaign(args.campaign)
    print(c.title)
    print(f"  lead (away): {c.lead_character} — {c.absence_reason.strip()}")
    print("  cast:")
    for n in c.npcs:
        print(f"    - {n.id}: {n.name} — {n.personality}")


def _render(args: argparse.Namespace) -> None:
    """Generate (or load) an interlude and voice it end to end."""
    result = run(args.campaign, args.out, scene_path=args.scene)
    print(
        f"wrote {result.audio_path} — "
        f"{len(result.scene.lines)} lines, {len(result.voice_library)} voices."
    )


def _workflow(args: argparse.Namespace) -> None:
    """Interactive end-to-end workflow: NPCs → scene → audio."""
    import os

    # Override TTS_BACKEND if --backend flag provided
    if args.backend:
        os.environ["TTS_BACKEND"] = args.backend

    interactive_workflow(demo=args.demo)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="voxmancer", description="Forge voices for your D&D NPCs.")
    sub = p.add_subparsers(dest="command", required=True)

    pv = sub.add_parser("preview", help="print the cast; no API calls")
    pv.add_argument("campaign", type=Path)
    pv.set_defaults(func=_preview)

    rn = sub.add_parser("render", help="voice an interlude end to end")
    rn.add_argument("campaign", type=Path)
    rn.add_argument("--out", type=Path, default=Path("out/interlude.mp3"))
    rn.add_argument(
        "--scene", type=Path, default=None, help="hand-written scene yaml; skips the LLM"
    )
    rn.set_defaults(func=_render)

    wf = sub.add_parser("workflow", help="interactive end-to-end: NPCs → scene → audio")
    wf.add_argument("--demo", action="store_true", help="use demo values (skip prompts)")
    wf.add_argument(
        "--backend",
        choices=["elevenlabs", "kokoro", "piper"],
        default=None,
        help="override TTS_BACKEND (from .env by default)",
    )
    wf.set_defaults(func=_workflow)

    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
