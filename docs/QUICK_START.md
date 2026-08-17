# Quick Start: Local Development

Run Voxmancer locally with **Ollama** (scene generation) and **ElevenLabs** (voice synthesis). For production or RunPod deployment, see [../RUNPOD_DEPLOYMENT.md](../RUNPOD_DEPLOYMENT.md).

## Installation

### 1. Clone & Install with Poetry
```bash
git clone https://github.com/YOUR_USERNAME/voxmancer.git
cd voxmancer

# Minimal install (hosted APIs only)
poetry install

# Or with Kokoro for RunPod
poetry install --extras kokoro
```

### 2. Configure `.env`
```bash
cp .env.example .env

# Add your ElevenLabs API key
# Get it from: https://elevenlabs.io/app/api-keys
ELEVENLABS_API_KEY=sk_...

# Keep other defaults:
TTS_BACKEND=elevenlabs
LLM_BACKEND=ollama
```

### 3. Start Ollama (in another terminal)
```bash
# Install Ollama from https://ollama.ai
# Then run:
ollama serve  # (keeps running)
```

### 4. Run the Demo
```bash
poetry run voxmancer workflow --demo
```

**Expected output:** ~45 seconds
- LLM generates scene dialogue (Ollama Mistral)
- Voices designed and cached (ElevenLabs)
- Audio synthesized (ElevenLabs TTS)
- Output: `out/elevenlabs_at_the_market.mp3`

Listen to it:
```bash
open out/elevenlabs_at_the_market.mp3  # macOS
xdg-open out/elevenlabs_at_the_market.mp3  # Linux
start out/elevenlabs_at_the_market.mp3  # Windows
```

## The Tech Stack

| Component | Service | Runs Where | Cost |
|-----------|---------|------------|------|
| **Scene Generation** | Mistral 7B | Your machine (Ollama) | Free |
| **Voice Design** | ElevenLabs | Cloud API | ~$5/1M chars |
| **Voice Synthesis** | ElevenLabs | Cloud API | ~$5/1M chars |
| **Audio Rendering** | FFmpeg | Your machine | Free |

## Customizing NPCs

Edit `examples/axfori_campaign.yaml` to change voice prompts:

```yaml
npcs:
  - id: brakk-emberhand
    name: "Brakk Emberhand"
    voice_prompt: "Gruff dwarven blacksmith, gravelly voice, warm but direct"
```

Voices are automatically created via ElevenLabs' voice design API and cached in `~/.voxmancer/voices.json` for reuse.

## Running Tests

```bash
# Fast unit tests only
poetry run pytest tests/unit/ -v

# All tests (57 passing)
poetry run pytest tests/ -v

# With coverage
poetry run pytest --cov=voxmancer
```

Tests validate:
- Voice registry and mapping
- Configuration loading
- Data models
- Full E2E workflow

## Switching Backends (Advanced)

All backends available via `.env`:

```bash
# Already configured for local dev:
TTS_BACKEND=elevenlabs
LLM_BACKEND=ollama

# For RunPod deployment:
export TTS_BACKEND=kokoro
export LLM_BACKEND=anthropic
export ANTHROPIC_API_KEY=sk_...

poetry run voxmancer workflow --demo
```

See [BACKEND_CONFIG.md](BACKEND_CONFIG.md) for all options.

## Troubleshooting

### "Ollama not running"
```bash
# In a separate terminal:
ollama serve
```

### "ELEVENLABS_API_KEY not set"
Get your API key from https://elevenlabs.io/app/api-keys and add to `.env`:
```bash
ELEVENLABS_API_KEY=sk_...
```

### "Voice design failed"
Ensure your ElevenLabs account has credits (free tier allows some API calls). Check logs for details.

### "Out of memory during audio synthesis"
Reduce the scene length or use a smaller TTS model. Kokoro is the most efficient.

## What's Next?

- **Edit campaigns** in `examples/` and run your own stories
- **Deploy to RunPod** — See [../RUNPOD_DEPLOYMENT.md](../RUNPOD_DEPLOYMENT.md)
- **Explore backends** — See [BACKEND_CONFIG.md](BACKEND_CONFIG.md)
- **Run tests** — `poetry run pytest tests/ -v`
