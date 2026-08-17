# Voxmancer on RunPod Serverless

Deploy Voxmancer as serverless microservices on RunPod:
- **Pod A (LLM)**: Ollama Mistral for scene generation
- **Pod B (TTS)**: Voxmancer Handler with ElevenLabs TTS + S3 upload

Audio files auto-upload to S3 with public HTTPS URLs. Independent pod architecture for cost control and scaling.

## Architecture

```
Client Request (JSON)
    ↓
RunPod Flash Handler (Pod B)
    ├─ Scene Generation (calls Pod A via HTTP)
    │  └─ Pod A: Ollama Mistral on RunPod GPU
    ├─ Voice Design (core/voice_designer.py)
    │  └─ Text prompt → ElevenLabs voice mapping + caching
    ├─ TTS Synthesis (tts/eleven_client.py)
    │  └─ ElevenLabs API → MP3 audio
    └─ S3 Upload (voxmancer/serverless/runpod_handler.py)
       └─ Auto-upload to S3 with public-read bucket policy
    ↓
Response: Public HTTPS URL to MP3 (e.g., https://bucket.s3.region.amazonaws.com/mp3/xxxxx.mp3)
```

**Modular design** allows swapping backends via `.env` without code changes.

## Prerequisites

1. **RunPod Account** with Flash access
2. **GitHub Repository** with this codebase
3. **Two RunPod Pods** (both serverless):
   - **Pod A (LLM)**: Ollama Mistral for scene generation
   - **Pod B (TTS)**: This Voxmancer handler (Kokoro TTS)
4. **Optional API Key**:
   - `ELEVENLABS_API_KEY` (if using ElevenLabs instead of Kokoro)

## Deployment Steps

### 0. Deploy Ollama Mistral on RunPod (Required First)

This is the LLM backend for scene generation.

**[See detailed guide: docs/OLLAMA_RUNPOD_SETUP.md](docs/OLLAMA_RUNPOD_SETUP.md)**

Quick summary:
1. Go to https://runpod.io/console/pods → "New Pod"
2. Search for "Ollama" template → Deploy
3. Select GPU (L40 or H100 recommended)
4. Once running, SSH in: `ollama pull mistral`
5. Note the pod's **HTTP invoke URL** (format: `https://xxx-xxx-runpod.io`)
6. Keep this URL for Step 2 (configure TTS handler environment)

### 1. Prepare Repository

```bash
# Ensure everything is committed
git add .
git commit -m "RunPod Flask deployment ready"
git push origin main
```

### 2. Create RunPod Flash Endpoint

1. Go to https://runpod.io/console/serverless
2. Click "New Endpoint"
3. Select **Flash** template
4. Configure:

**Image**: Use Python 3.11 base
```
python:3.11-slim
```

**Container Image**:
```
lorenanicole/voxmancer-serverless:latest
```

**Environment Variables** (RunPod injects AWS credentials automatically):
```
TTS_BACKEND=elevenlabs
LLM_BACKEND=runpod_flash
ELEVENLABS_API_KEY=sk_...
RUNPOD_LLM_URL=https://your-ollama-pod-url.runpod.io/run
S3_BUCKET=your-bucket-name
AWS_DEFAULT_REGION=us-east-2
PYTHONUNBUFFERED=1
```

**Handler Path**:
```
voxmancer.serverless.runpod_handler.handler
```

**Note**: RunPod auto-injects `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from your account. Just set `S3_BUCKET` and audio uploads work automatically.

### 3. Test Locally

```bash
# Set env vars
export TTS_BACKEND=kokoro
export LLM_BACKEND=anthropic
export ANTHROPIC_API_KEY=your_key_here

# Run handler test
python -m voxmancer.runpod_handler
```

## API Usage

### Request Format

```bash
curl -X POST https://api.runpod.io/v2/YOUR_ENDPOINT_ID/run \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "campaign": {
        "title": "Market Negotiation",
        "lead_character": "Axfori",
        "absence_reason": "Axfori is present",
        "npcs": [
          {
            "id": "narrator",
            "name": "Narrator",
            "species": "storyteller",
            "role": "narration",
            "personality": "measured",
            "voice_prompt": "Male, 40s, professional storyteller. Warm, engaging, with natural pacing and dramatic timing."
          },
          {
            "id": "axfori",
            "name": "Axfori",
            "species": "human",
            "role": "protagonist",
            "personality": "brave, determined",
            "voice_prompt": "Female, 30s. Confident warrior voice with edge. Strong, decisive delivery."
          }
        ]
      },
      "scene": {
        "title": "The Market Exchange",
        "premise": "Axfori negotiates with a mysterious merchant over rare supplies"
      },
      "output_bucket": "s3://my-bucket/audio" (optional)
    }
  }'
```

### Response Format

**Success** (with S3 upload):
```json
{
  "success": true,
  "job_id": "17c229fd-6276-4311-a1f3-4db01a50d861-u2",
  "audio_url": "https://your-bucket.s3.us-east-2.amazonaws.com/mp3/034fc29fed3e4efcb996995c8303d77e.mp3",
  "scene_title": "A Serendipitous Encounter",
  "num_lines": 8,
  "num_voices": 3,
  "generation_time_seconds": 19.65
}
```

**Audio URL is public and downloadable** (bucket policy allows public read access to mp3/ folder).

**Error**:
```json
{
  "success": false,
  "error": "Missing 'campaign' in request",
  "job_id": "job_12345",
  "generation_time_seconds": 2.1
}
```

## Configuration

### TTS Backends

| Backend    | Quality | Speed | Cost    | Use Case |
|-----------|---------|-------|---------|----------|
| `elevenlabs` | Excellent | Medium | API credits | Default for RunPod (high-quality voices) |
| `kokoro`  | Good    | Fast  | Free*   | Alternative for budget-conscious deployment |
| `piper`   | Good    | Slow  | Free    | Local development only |

*Kokoro runs on RunPod GPU, you only pay for compute time. ElevenLabs requires API key but produces superior voice quality.

### LLM Backends

| Backend    | Quality | Speed | Cost   |
|-----------|---------|-------|--------|
| `anthropic` | Excellent | Medium | API credits |
| `ollama`   | Good    | Fast  | Free*  |

*Requires separate Ollama pod on RunPod.

## Scaling & Cost

- **Cold start**: ~3-5 seconds (Flask initialization)
- **Typical generation**: 30-60 seconds (scene + audio)
- **Total request time**: ~40-70 seconds
- **Cost**: RunPod Flash pricing (usually $0.00001-0.0002/sec)

## Monitoring

Check logs in RunPod console:
- Deployment logs
- Inference logs
- Error logs

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "kokoro not found" | Ensure `--extras kokoro` in build script |
| "ANTHROPIC_API_KEY not set" | Add to RunPod environment variables |
| Timeout on long scenes | Increase RunPod timeout setting (default 600s) |
| Out of memory | Reduce batch size or upgrade pod tier |

## Production Checklist

- [ ] Test with multiple campaign formats
- [ ] Monitor cost per request
- [ ] Set up error alerting
- [ ] Configure output bucket for audio storage
- [ ] Document API for clients
- [ ] Set up rate limiting if needed
- [ ] Test failover/recovery
