# Deploy Ollama Mistral on RunPod

This guide walks through deploying Ollama Mistral as a serverless endpoint on RunPod. The Voxmancer TTS handler will call this pod for scene generation.

## Overview

```
Voxmancer TTS Handler (Pod B)
         ↓ (HTTP POST with prompt)
    Ollama Mistral Pod (Pod A)
         ↓ (Returns generated scene)
Voxmancer TTS Handler continues
```

## Step 1: Create RunPod Account & Get Free Credits

1. Go to https://runpod.io
2. Sign up for a free account
3. Share your email with `jessica.garson@runpod.io` for DevRel free credits

## Step 2: Deploy Ollama Mistral Pod

### 2a. Navigate to RunPod Pods

1. Go to https://runpod.io/console/pods
2. Click **"New Pod"** (top right)

### 2b. Select Ollama Template

1. Search for **"Ollama"** in the template search
2. Click the official **"Ollama"** community template
3. Click **"Deploy"**

### 2c. Configure Pod Settings

**Pod Configuration:**
- **GPU**: Select a GPU tier (L40 or H100 recommended for Mistral)
  - L40 (24GB VRAM) — Good for Mistral
  - H100 (80GB VRAM) — Best performance
  - RTX A40 (48GB) — Budget option
- **vCPU**: At least 4
- **Memory**: At least 16GB RAM
- **Storage**: 20GB (for model cache)

**Network:**
- Enable "Expose HTTP Port"
- HTTP Port: `11434` (default Ollama port)

**Billing:**
- Serverless (cheaper, scales to zero)
- On-demand (always running)

For DevRel demo: Use **Serverless** (pay only when in use)

### 2d. Launch Pod

1. Click **"Deploy"**
2. Wait for pod to start (~2-3 minutes)
3. Pod will show "Running" status

## Step 3: Pull Mistral Model

### 3a. Open Pod Terminal

Once pod is running:
1. Click the pod name
2. Click **"Connect"** → **"HTTP"**
3. Or use the pod's exposed URL

### 3b. SSH into Pod

Option A (RunPod Web Terminal):
1. In pod details, click **"Connect"** → **"Web Terminal"**
2. You'll get an SSH command

Option B (Local SSH):
```bash
ssh root@<pod-ip> -p 22
# Password is shown in pod details
```

### 3c. Pull Mistral Model

In the pod terminal:
```bash
# Download Mistral model (takes 5-10 minutes first time)
ollama pull mistral

# Verify it's loaded
ollama list
# Should show: mistral     latest    ...
```

### 3d. Start Ollama Service

If not already running:
```bash
ollama serve
# Should show: Ollama server is running on 0.0.0.0:11434
```

## Step 4: Get Pod Invoke URL

### Via RunPod Web Console

1. Go to pod details page
2. Under **"Network"**, find the **HTTP endpoint**
3. It will look like: `https://abc123-xyz.runpod.io`

### Test the Endpoint

```bash
# Test Ollama is accessible
curl -X POST https://abc123-xyz.runpod.io/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "prompt": "Why is the sky blue?",
    "stream": false
  }'

# Should return JSON with the generated response
```

## Step 5: Configure Voxmancer Handler

Now use this URL when deploying the Voxmancer TTS handler:

**.env for Voxmancer Handler Pod:**
```bash
TTS_BACKEND=kokoro
LLM_BACKEND=runpod_flash
RUNPOD_LLM_URL=https://abc123-xyz.runpod.io
PYTHONUNBUFFERED=1
```

## Step 6: Test Ollama Pod

Before deploying Voxmancer handler, test the Ollama pod with a sample request:

```bash
curl -X POST https://abc123-xyz.runpod.io/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "prompt": "Write a short D&D scene with a narrator and a merchant. Return JSON format.",
    "stream": false,
    "temperature": 0.7,
    "top_p": 0.9
  }'
```

Expected response time: 5-15 seconds (depending on GPU)

## Troubleshooting

### Pod won't start
- Check you have enough credits
- Try a different GPU tier
- Check RunPod's status page

### Model download fails
- Pod needs good internet connection
- Try manually in pod terminal: `ollama pull mistral`
- Check pod storage isn't full: `df -h`

### Endpoint returns 404
- Make sure pod HTTP port is exposed (11434)
- Try: `curl https://your-pod-url/api/tags` (should list models)
- Ollama service might not be running: `ollama serve`

### Slow responses
- Upgrade to larger GPU (L40 minimum)
- Reduce model size: try `ollama pull neural-chat` (smaller, faster)
- Check pod logs for errors

## Cost Estimation

**Serverless Pod (pay-per-compute):**
- Mistral inference: ~$0.0001/second
- Typical scene generation (10-20 sec): $0.001-0.002
- With DevRel credits: Free during demo

**On-demand Pod (always running):**
- L40 GPU: ~$0.25/hour
- H100 GPU: ~$1.29/hour

**Recommendation:** Use Serverless for development/demo, On-demand for production.

## Next Steps

Once Ollama pod is running and tested:
1. Save the invoke URL
2. Deploy Voxmancer TTS handler (see ../RUNPOD_DEPLOYMENT.md)
3. Configure handler with `RUNPOD_LLM_URL`
4. Test end-to-end scene → audio generation

## Resources

- RunPod Docs: https://docs.runpod.io
- Ollama Docs: https://ollama.ai/docs
- Mistral Model: https://huggingface.co/mistralai/Mistral-7B
