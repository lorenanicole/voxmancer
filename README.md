# Voxmancer 🎭

**Generate AI-powered D&D audio dramas with custom voice design.**

Voxmancer turns a D&D campaign and written scene into a voiced audio drama with distinct, consistent NPC voices. Choose your backend:
- **Local**: ElevenLabs (best quality), Piper (lightweight), Kokoro (open-source)
- **Serverless**: Deploy to RunPod Flash with ElevenLabs TTS + Ollama LLM, auto-upload to S3

It started with a real question at my table: *what happened in town while my character, Axfori, was laid up with wound-fever for a tenday?* Voxmancer answers it — in the NPCs' own voices.

---

## Quick Start

### Local (ElevenLabs + Ollama)

```bash
# Install
poetry install
cp .env.example .env

# Add your ElevenLabs API key to .env
# ELEVENLABS_API_KEY=sk_...

# Start Ollama in another terminal
ollama serve

# Run demo
poetry run voxmancer workflow --demo

# Listen to output
open out/elevenlabs_at_the_market.mp3
```

### RunPod Cloud (ElevenLabs TTS + Ollama LLM + S3 Storage)

```bash
# See full deployment guide
cat RUNPOD_DEPLOYMENT.md

# Quick: Deploy to RunPod Flash with this repo
# Pod A: Ollama Mistral (LLM for scene generation)
# Pod B: Voxmancer Handler (TTS + S3 upload)
# Set env: TTS_BACKEND=elevenlabs, ELEVENLABS_API_KEY=..., S3_BUCKET=your-bucket
# Audio auto-uploads to S3 with public HTTPS URLs
```

### Test Locally

```bash
poetry run pytest tests/unit -v
poetry run invoke test-fast
```

---

## How It Works

```
Campaign YAML (NPCs + Setting)
    ↓
[Scene Generation]
  Local: Ollama Mistral
  Cloud: Claude API
    ↓
[Voice Design & Caching]
  Map prompt → voice_id
  Cache in voices.json
    ↓
[TTS Synthesis]
  ElevenLabs / Kokoro / Piper
    ↓
[Audio Rendering]
  FFmpeg concatenate + silence
    ↓
Audio Drama MP3
```

1. **Scene generation** — LLM writes dialogue from campaign premise
2. **Voice mapping** — Text prompts → voice IDs (intelligent reuse)
3. **Voice caching** — Consistent voices across sessions (voices.json)
4. **TTS synthesis** — Backend renders audio from dialogue
5. **Concatenation** — FFmpeg stitches clips with silence

---

## Backends

| Backend | Setup | Cost | Quality | Use Case |
|---------|-------|------|---------|----------|
| **ElevenLabs** | API key | $$ | ⭐⭐⭐⭐⭐ | Best quality, voice design, production |
| **Kokoro** | `--extras kokoro` | Free* | ⭐⭐⭐⭐ | RunPod serverless, open-source, efficient |

**Why two backends?**
- **ElevenLabs** — Superior voice quality and voice design via prompt engineering
- **Kokoro** — Lightweight, open-source TTS optimized for RunPod serverless deployment

*Kokoro uses RunPod GPU compute time (cheaper than API costs)

**Switch backends anytime:**
```bash
export TTS_BACKEND=elevenlabs  # or kokoro, piper, parler
poetry run voxmancer workflow --demo --backend kokoro  # CLI override
```

---

## Customizing NPCs

Edit `examples/axfori_campaign.yaml`:

```yaml
npcs:
  - id: brakk-emberhand
    name: "Brakk Emberhand"
    voice_prompt: "An old dwarven blacksmith. Gravelly, warm, gruff."
```

Voices are automatically generated and cached. Run again and they stay consistent.

---

## Architecture

**Modular folder structure** (`voxmancer/`):
- **`core/`** — Pipeline stages: scene generation, voice mapping, rendering
- **`tts/`** — TTS backends: ElevenLabs, Kokoro, Piper, Parler, Coqui
- **`llm/`** — LLM backends: Ollama, RunPod
- **`serverless/`** — RunPod Flash handlers

**Key features:**
- **Pluggable TTS backends** — Swap via `.env`, no code changes
- **Pluggable LLM backends** — Local (Ollama) or cloud (Claude, RunPod)
- **Voice caching** — Consistent voices across sessions via `voices.json`
- **Intelligent voice reuse** — Prompt similarity checking before creating new voices
- **Decoupled stages** — Skip LLM, use hand-written scenes, change backends independently
- **FFmpeg rendering** — Audio concatenation with silence (no GPU required)

---

## Deployment

### Local Development
```bash
poetry install
poetry run voxmancer workflow --demo
```

### RunPod Flash (Serverless)
See `RUNPOD_DEPLOYMENT.md` for detailed guide.

### Docker (Local Testing)
```bash
docker build -t voxmancer .
docker run voxmancer poetry run pytest tests/unit -v
```

## Testing

```bash
# Unit tests only (fast, no external deps)
poetry run pytest tests/unit -v

# All tests with coverage
poetry run pytest --cov=voxmancer

# Pre-commit lint + format checks
poetry run ruff check voxmancer/
poetry run ruff format --check voxmancer/

# Or use invoke tasks
poetry run invoke test-unit
poetry run invoke lint
poetry run invoke format
```

**CI/CD:** GitHub Actions runs unit tests on every PR (see `.github/workflows/tests.yml`)

## Documentation

- `README.md` — This file (overview & quick start)
- `RUNPOD_DEPLOYMENT.md` — Serverless deployment guide
- `docs/` — Detailed guides:
  - `QUICK_START.md` — Local setup (Ollama + ElevenLabs)
  - `BACKEND_CONFIG.md` — All backend options
- `.env.example` — Configuration template
- `voxmancer/models.py` — Data models (Campaign, Scene, NPC, DialogueLine)
- `examples/` — Sample campaigns & generated scenes
- `tests/README.md` — Test organization & running

## Highlights

**Multi-backend architecture:**
- **Pluggable LLM:** Ollama (local), Claude API (hosted), RunPod (serverless)
- **Pluggable TTS:** ElevenLabs (best quality), Kokoro (open-source), Piper, Parler, Coqui
- **Pluggable rendering:** FFmpeg-based audio concatenation

**Production-ready:**
- **Voice caching** with `voices.json` for cross-session consistency
- **Intelligent reuse:** Prompt similarity checking before voice creation
- **Serverless deployment** to RunPod Flash (no Docker required)
- **GitHub Actions CI/CD** with unit tests on PRs
- **Comprehensive test suite** (57 passing tests)
- **Modular architecture** for easy extension

**For the RunPod DevRel Hiring Exercise:**
This demonstrates:
- Multi-stage ML pipeline orchestration (Scene → Voice → Audio)
- Serverless GPU deployment with Flask handlers
- Voice design via prompt engineering
- Production-grade testing (unit, integration, E2E)
- Open-source backend integration (Kokoro TTS)
- Cost-efficient architecture (pay-per-compute vs API costs)

---

**Ready to add voices to your D&D campaign. Supports local development and cloud deployment.**
