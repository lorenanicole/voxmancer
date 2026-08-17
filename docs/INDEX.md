# Voxmancer Documentation

Welcome to the Voxmancer documentation. Here you'll find guides for local setup, configuration, and deployment.

## Start Here

**New to Voxmancer?** Follow [QUICK_START.md](QUICK_START.md) for a 5-minute local setup with ElevenLabs + Ollama.

## Documentation

### Core Guides
- **[QUICK_START.md](QUICK_START.md)** — Get running locally in 5 minutes
  - Poetry installation
  - ElevenLabs API setup
  - Running the demo workflow
  - Troubleshooting

- **[BACKEND_CONFIG.md](BACKEND_CONFIG.md)** — All backend options
  - TTS backends (ElevenLabs, Kokoro)
  - LLM backends (Claude API, Ollama, RunPod)
  - Environment variables reference
  - Backend combinations for dev/production/hybrid

### Deployment & Production
- **[OLLAMA_RUNPOD_SETUP.md](OLLAMA_RUNPOD_SETUP.md)** — Deploy Ollama Mistral on RunPod
  - Create RunPod account & get credits
  - Deploy Ollama pod from template
  - Pull Mistral model
  - Get invoke URL
  - Test endpoint

- **[../RUNPOD_DEPLOYMENT.md](../RUNPOD_DEPLOYMENT.md)** — Deploy Voxmancer TTS handler
  - Full serverless architecture
  - TTS handler setup & configuration
  - API request/response formats
  - Scaling & cost estimates

### Reference
- **[../README.md](../README.md)** — Project overview
  - What Voxmancer does
  - Architecture & modular design
  - Highlights & features

- **[../tests/README.md](../tests/README.md)** — Test organization
  - Unit, integration, E2E tests
  - Running tests locally
  - Writing new tests

## Quick Reference

### Local Development (5 min)
```bash
poetry install
export ELEVENLABS_API_KEY=sk_...  # Get from elevenlabs.io
ollama serve  # In another terminal
poetry run voxmancer workflow --demo
```

### RunPod Serverless (Kokoro + Claude)
See [../RUNPOD_DEPLOYMENT.md](../RUNPOD_DEPLOYMENT.md)

### All Local, Open-Source (No API keys)
```bash
poetry install --extras kokoro
ollama serve  # In another terminal
export TTS_BACKEND=kokoro
export LLM_BACKEND=ollama
poetry run voxmancer workflow --demo
```

## Architecture

```
voxmancer/
├── core/           # Pipeline stages (scene, voice, render)
├── tts/            # TTS backends (ElevenLabs, Kokoro, Piper, etc.)
├── llm/            # LLM backends (Ollama, RunPod)
├── serverless/     # RunPod handlers
└── main modules    # CLI, config, models, pipeline
```

## Need Help?

- **Setup issues?** → [QUICK_START.md](QUICK_START.md#troubleshooting)
- **Backend questions?** → [BACKEND_CONFIG.md](BACKEND_CONFIG.md)
- **RunPod deployment?** → [../RUNPOD_DEPLOYMENT.md](../RUNPOD_DEPLOYMENT.md)
- **Test questions?** → [../tests/README.md](../tests/README.md)
- **Project overview?** → [../README.md](../README.md)
