# Voxmancer Backend Configuration

You can now swap between hosted APIs, self-hosted Runpod Flash, and **local development** (Ollama) for both **TTS (voice synthesis)** and **LLM (scene generation)**.

## Local Development Quick Start (Fully Local)

Best for testing before deploying to production. Everything runs on your machine — no API keys, no cloud calls.

### Setup

```bash
# 1. Install both local models
pip install TTS          # For Coqui TTS (voice synthesis)
pip install ollama       # For Ollama (scene generation)

# 2. Start Ollama in a terminal (keep it running):
ollama run mistral

# 3. In .env:
TTS_BACKEND=coqui_local
LLM_BACKEND=ollama
VOXMANCER_LLM_MODEL=mistral
COQUI_GPU=true           # Set to false if using CPU only

# 4. Run:
python -m voxmancer.cli render examples/axfori_campaign.yaml --out out/interlude.mp3
```

**First run:** Models download automatically (~3-5 min, one-time)
**Subsequent runs:** Much faster (models cached locally)

## Quick Reference

| Task | Backend | Config | Required Env | Best For |
|------|---------|--------|--------------|----------|
| Voice synthesis | ElevenLabs | `TTS_BACKEND=elevenlabs` | `ELEVENLABS_API_KEY` | Production |
| Voice synthesis | Coqui Local | `TTS_BACKEND=coqui_local` | None (local) | Local Development |
| Voice synthesis | Runpod Flash | `TTS_BACKEND=runpod_flash` | `RUNPOD_FLASH_URL` | Self-hosted |
| Scene generation | Claude | `LLM_BACKEND=anthropic` | `ANTHROPIC_API_KEY` | Production |
| Scene generation | Ollama (local) | `LLM_BACKEND=ollama` | None (local) | Local Development |
| Scene generation | Runpod Flash | `LLM_BACKEND=runpod_flash` | `RUNPOD_LLM_URL` | Self-hosted |

## All Combinations

### 1. Fully Local Development (fastest to start, no API keys needed)
```bash
TTS_BACKEND=coqui_local
LLM_BACKEND=ollama
VOXMANCER_LLM_MODEL=mistral
COQUI_GPU=true
# Then: ollama run mistral
# Everything runs locally, zero cloud calls
```

### 1b. Local LLM + Hosted TTS (faster TTS, local LLM)
```bash
TTS_BACKEND=elevenlabs
LLM_BACKEND=ollama
ELEVENLABS_API_KEY=sk_...
VOXMANCER_LLM_MODEL=mistral
# Then: ollama run mistral
```

### 2. All Hosted (production, high quality)
```bash
TTS_BACKEND=elevenlabs
LLM_BACKEND=anthropic
ELEVENLABS_API_KEY=sk_...
ANTHROPIC_API_KEY=sk_ant_...
VOXMANCER_LLM_MODEL=claude-3-5-sonnet-latest
```

### 3. All Self-Hosted (full control, cheapest at scale)
```bash
TTS_BACKEND=runpod_flash
LLM_BACKEND=runpod_flash
RUNPOD_FLASH_URL=https://your-tts-endpoint.runpod.io
RUNPOD_LLM_URL=https://your-llm-endpoint.runpod.io
VOXMANCER_LLM_MODEL=mistral
```

### 4. Hybrid: Local LLM Dev, Hosted TTS
```bash
TTS_BACKEND=elevenlabs
LLM_BACKEND=ollama
ELEVENLABS_API_KEY=sk_...
VOXMANCER_LLM_MODEL=mistral
# Then: ollama run mistral
```

### 5. Hybrid: Hosted LLM, Self-Hosted TTS
```bash
TTS_BACKEND=runpod_flash
LLM_BACKEND=anthropic
RUNPOD_FLASH_URL=https://your-tts-endpoint.runpod.io
ANTHROPIC_API_KEY=sk_ant_...
VOXMANCER_LLM_MODEL=claude-3-5-sonnet-latest
```

## Runpod Deployment

For full RunPod deployment instructions (Kokoro TTS + Claude LLM), see [../RUNPOD_DEPLOYMENT.md](../RUNPOD_DEPLOYMENT.md).

### Handlers in `voxmancer/serverless/`
- **`runpod_handler.py`** — Full campaign-to-audio handler for complex workflows
- **`flash_handler.py`** — Simple Kokoro TTS-only handler (lightweight)
- **`runpod_llm_backend.py`** — LLM client for calling separate Ollama pod via HTTP

All handlers are production-ready and tested. Use `runpod_handler.handler` as your RunPod Flask entry point.

## Environment Variables

All settings in `.env`:

```bash
# TTS Backend
TTS_BACKEND=elevenlabs              # or "runpod_flash"
ELEVENLABS_API_KEY=sk_...           # if using ElevenLabs TTS
RUNPOD_FLASH_URL=...                # if using Runpod TTS
RUNPOD_API_KEY=...                  # optional auth for Runpod TTS

# LLM Backend
LLM_BACKEND=anthropic               # or "ollama" or "runpod_flash"
ANTHROPIC_API_KEY=sk_ant_...        # if using Claude
VOXMANCER_LLM_MODEL=claude-3-5-sonnet-latest  # or "mistral" for Ollama
OLLAMA_URL=http://localhost:11434   # if using Ollama (default shown)
RUNPOD_LLM_URL=...                  # if using Runpod LLM
RUNPOD_LLM_API_KEY=...              # optional auth for Runpod LLM
```

## Running the App

Same command works regardless of backend:

```bash
python -m voxmancer.cli render examples/axfori_campaign.yaml \
    --scene examples/axfori_interlude.scene.yaml \
    --out out/interlude.mp3
```

The app automatically picks the right backend based on your `.env` settings.

## Ollama Local Development Setup

**Best for fast iteration during development.**

### 1. Install Ollama
```bash
# macOS/Windows/Linux
# https://ollama.ai
```

### 2. Choose a model
Popular models for local development:
- **Mistral 7B** (recommended) — Small, fast, good quality
  ```bash
  ollama run mistral
  ```
- **Llama 2** — Larger, higher quality
  ```bash
  ollama run llama2
  ```
- **Neural Chat** — Optimized for conversation
  ```bash
  ollama run neural-chat
  ```

### 3. Configure voxmancer
In `.env`:
```bash
LLM_BACKEND=ollama
VOXMANCER_LLM_MODEL=mistral
OLLAMA_URL=http://localhost:11434  # default, no need to set unless you changed it
```

### 4. Run
```bash
python -m voxmancer.cli render examples/axfori_campaign.yaml --out out/interlude.mp3
```

**Tips:**
- Keep Ollama running in a terminal: `ollama serve` or use the app
- First request is slow (model loads), subsequent requests are fast
- Runs on CPU or GPU depending on your setup
- Memory usage: ~4GB for Mistral, ~7GB for Llama2

### Switching from Ollama to Production
When ready to deploy:
1. Change `.env` to use `LLM_BACKEND=anthropic` or deploy to `RUNPOD_FLASH_URL`
2. No code changes needed
3. Same render command works

## Coqui TTS Local Development Setup

**Best for testing voice synthesis locally before deploying to Runpod.**

### 1. Install Coqui TTS
```bash
pip install TTS
# First run will download the model (~1-2 GB) — only happens once
```

### 2. Configure voxmancer
In `.env`:
```bash
TTS_BACKEND=coqui_local
COQUI_GPU=true  # Set to false if using CPU only
```

### 3. Run
```bash
python -m voxmancer.cli render examples/axfori_campaign.yaml --out out/interlude.mp3
```

**First run:** Model downloads + caches locally (~1-2 min, one-time)
**Subsequent runs:** Much faster (model cached)

### Model Details

**Coqui XTTS-v2** (what we use):
- Multilingual support
- Expressive voices
- Can do voice cloning from a short reference .wav
- Works on CPU or GPU (slower on CPU, but works)

### Tips

- Keep models downloaded between runs (they cache in `~/.TTS_HOME`)
- First render is slowest (model loading), subsequent ones are faster
- GPU: ~4 GB VRAM for XTTS-v2
- CPU: ~2-3 min per 30-second audio (GPU is ~10-30 seconds)

### Switching from Coqui to Production
When ready to deploy:
1. Change `.env` to use `TTS_BACKEND=elevenlabs` or `TTS_BACKEND=runpod_flash`
2. No code changes needed
3. Same render command works

## Fully Local Development Checklist

For complete local iteration without any cloud:

- [ ] Install Ollama: https://ollama.ai
- [ ] Install Coqui TTS: `pip install TTS`
- [ ] Start Ollama: `ollama run mistral`
- [ ] Set `.env`:
  ```bash
  TTS_BACKEND=coqui_local
  LLM_BACKEND=ollama
  VOXMANCER_LLM_MODEL=mistral
  COQUI_GPU=true
  ```
- [ ] Run: `python -m voxmancer.cli render examples/axfori_campaign.yaml --out out/interlude.mp3`
- [ ] Iterate quickly until happy with output
- [ ] When ready, change `.env` to production backends (Claude, ElevenLabs, or Runpod)
