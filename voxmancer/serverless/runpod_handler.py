"""RunPod Flash handler for serverless Voxmancer audio drama generation.

Full pipeline: campaign → LLM scene generation → voice design → TTS synthesis → audio MP3.

Setup:
  1. Deploy Ollama Mistral on a separate RunPod pod (see RUNPOD_DEPLOYMENT.md Section 0)
  2. Get the Ollama pod's invoke URL (format: https://xxx-xxx-runpod.io/run)
  3. Deploy this handler to RunPod Flash with environment variables based on TTS backend:

  Option A: ElevenLabs (recommended for quick start)
    - TTS_BACKEND=elevenlabs
    - ELEVENLABS_API_KEY=<your-api-key>
    - LLM_BACKEND=runpod_flash
    - RUNPOD_LLM_URL=<your-ollama-pod-url>

  Option B: Kokoro HTTP (open-source, requires separate Kokoro pod)
    - TTS_BACKEND=kokoro_http
    - RUNPOD_KOKORO_URL=<your-kokoro-pod-url>
    - LLM_BACKEND=runpod_flash
    - RUNPOD_LLM_URL=<your-ollama-pod-url>

  4. Handler path: voxmancer.serverless.runpod_handler.handler

Request format (JSON POST):
  {
    "input": {
      "campaign": {
        "title": "Market Negotiation",
        "lead_character": "Axfori",
        "absence_reason": "Axfori was recovering",
        "npcs": [
          {
            "id": "narrator",
            "name": "Narrator",
            "voice_prompt": "Male, 40s, professional storyteller. Warm, engaging."
          },
          {
            "id": "axfori",
            "name": "Axfori",
            "voice_prompt": "Female, 30s. Confident warrior voice with edge."
          }
        ]
      },
      "scene": {
        "title": "At the Market",
        "premise": "Axfori negotiates with a mysterious merchant over rare supplies"
      }
    }
  }

Response format (JSON):
  {
    "success": true,
    "audio_url": "/tmp/voxmancer_job_xyz/market_negotiation.mp3",
    "scene_title": "At the Market",
    "num_lines": 8,
    "num_voices": 2,
    "generation_time_seconds": 45.2
  }

For deployment details, see RUNPOD_DEPLOYMENT.md in the root directory.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

import yaml

try:
    import boto3
    import uuid
except ImportError:
    boto3 = None
    uuid = None

# Configure logging to stderr (visible in RunPod logs)
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    stream=sys.stderr,
    force=True,
)
logger = logging.getLogger(__name__)


def log_info(msg: str) -> None:
    """Log info message and flush immediately for RunPod serverless."""
    logger.info(msg)
    sys.stderr.flush()


def log_error(msg: str) -> None:
    """Log error message and flush immediately for RunPod serverless."""
    logger.error(msg)
    sys.stderr.flush()


def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """RunPod handler for Voxmancer audio drama generation.

    Args:
        job: RunPod job with structure:
            {
              "id": "job_id",
              "input": {
                "campaign": {...},
                "scene": {...},
                "output_bucket": "s3://bucket" (optional)
              }
            }

    Returns:
        Job result with audio URL and metadata
    """
    start_time = time.time()
    job_id = job.get("id", "unknown")

    try:
        input_data = job.get("input", {})
        log_info(f"Job {job_id} received")

        # Extract campaign and scene from request
        campaign_data = input_data.get("campaign")
        scene_data = input_data.get("scene")

        # Determine output destination
        default_bucket = os.getenv("S3_BUCKET")
        if default_bucket:
            default_bucket = f"s3://{default_bucket}"
            log_info(f"S3 output enabled: {default_bucket}")
        else:
            default_bucket = "local"
            log_info("S3_BUCKET not set, using local output")
        output_bucket = input_data.get("output_bucket", default_bucket)

        if not campaign_data:
            log_error("Missing campaign data")
            return {
                "success": False,
                "error": "Missing 'campaign' in request",
                "job_id": job_id,
            }

        # Validate campaign structure
        campaign = _validate_campaign(campaign_data)
        scene = _validate_scene(scene_data) if scene_data else None
        log_info(f"Campaign '{campaign.get('title')}' validated, output_bucket={output_bucket}")

        # Create temporary files for campaign/scene
        work_dir = Path(f"/tmp/voxmancer_{job_id}")
        work_dir.mkdir(parents=True, exist_ok=True)

        campaign_path = work_dir / "campaign.yaml"
        _save_campaign_yaml(campaign, campaign_path)

        scene_path = None
        if scene:
            scene_path = work_dir / "scene.yaml"
            _save_scene_yaml(scene, scene_path)

        # Run pipeline
        from ..pipeline import run

        safe_title = campaign.get("title", "audio").lower().replace(" ", "_")
        out_path = work_dir / f"{safe_title}.mp3"

        log_info(f"Running pipeline, output will be {out_path}")
        result = run(
            campaign_path=campaign_path,
            out_path=out_path,
            scene_path=scene_path,
            work_dir=work_dir / "work",
        )
        log_info(
            f"Pipeline complete: {len(result.scene.lines)} lines, {len(result.voice_library)} voices"
        )

        # Upload to output bucket if specified
        audio_url = str(out_path)
        if output_bucket and output_bucket != "local":
            log_info(f"Uploading to S3: {output_bucket}")
            audio_url = _upload_to_bucket(out_path, output_bucket, job_id)
            log_info(f"S3 upload complete: {audio_url}")
        else:
            log_info(f"Returning local path: {audio_url}")

        generation_time = time.time() - start_time

        log_info(f"Job {job_id} complete in {generation_time:.2f}s")
        return {
            "success": True,
            "job_id": job_id,
            "audio_url": audio_url,
            "scene_title": result.scene.title,
            "num_lines": len(result.scene.lines),
            "num_voices": len(result.voice_library),
            "generation_time_seconds": round(generation_time, 2),
        }

    except Exception as e:
        logger.exception(f"Handler error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "job_id": job_id,
            "generation_time_seconds": round(time.time() - start_time, 2),
        }


def _validate_campaign(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate campaign structure."""
    required = ["title", "lead_character", "npcs"]
    for field in required:
        if field not in campaign_data:
            raise ValueError(f"Campaign missing required field: {field}")

    return campaign_data


def _validate_scene(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate scene structure."""
    if "title" not in scene_data:
        scene_data["title"] = "Generated Scene"
    if "premise" not in scene_data:
        raise ValueError("Scene must have 'premise' field")

    return scene_data


def _save_campaign_yaml(campaign: Dict[str, Any], path: Path) -> None:
    """Save campaign as YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # Add defaults if missing
    if "absence_reason" not in campaign:
        campaign["absence_reason"] = f"{campaign['lead_character']} is present"
    if "setting" not in campaign:
        campaign["setting"] = "A mysterious location"
    if "interlude_premise" not in campaign:
        campaign["interlude_premise"] = campaign.get("premise", "An interesting encounter")

    with open(path, "w") as f:
        yaml.dump(campaign, f, default_flow_style=False, sort_keys=False)


def _save_scene_yaml(scene: Dict[str, Any], path: Path) -> None:
    """Save scene as YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        yaml.dump(scene, f, default_flow_style=False, sort_keys=False)


def _upload_to_bucket(local_path: Path, bucket_url: str, job_id: str) -> str:
    """Upload audio file to S3 bucket and return public download URL.

    Args:
        bucket_url: S3 bucket URL (s3://bucket-name or bucket-name)
    """
    if not boto3 or not uuid:
        raise RuntimeError("boto3 not installed; cannot upload to S3")

    try:
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        # Use bucket_url if provided, fall back to S3_BUCKET env var
        bucket_name = bucket_url or os.getenv("S3_BUCKET", "")
        bucket_name = bucket_name.removeprefix("s3://")
        log_info(f"Region: {region}, Bucket: {bucket_name}")

        if not bucket_name:
            raise RuntimeError("S3_BUCKET environment variable not set")

        s3 = boto3.client("s3", region_name=region)
        log_info("S3 client initialized")

        # Read MP3 bytes and upload
        with open(local_path, "rb") as f:
            mp3_bytes = f.read()
        log_info(f"Read {len(mp3_bytes)} bytes from {local_path.name}")

        key = f"mp3/{uuid.uuid4().hex}.mp3"
        log_info(f"Uploading to s3://{bucket_name}/{key}")
        # Note: Public read access is enabled via S3 bucket policy, not ACL.
        # If the returned URL returns 403 Access Denied, ensure your bucket
        # policy allows s3:GetObject on the mp3/* path.
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=mp3_bytes,
            ContentType="audio/mpeg",
        )

        # Return public download URL (requires bucket policy for public read)
        public_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
        log_info(f"Upload complete: {public_url}")
        return public_url
    except Exception as e:
        log_error(f"Upload error: {e}")
        raise RuntimeError(f"Failed to upload to S3: {e}")


# For local testing without RunPod
if __name__ == "__main__":
    # Test with example data
    test_job = {
        "id": "test_job",
        "input": {
            "campaign": {
                "title": "Test Campaign",
                "lead_character": "Hero",
                "absence_reason": "Hero is present",
                "npcs": [
                    {
                        "id": "narrator",
                        "name": "Narrator",
                        "species": "storyteller",
                        "role": "narration",
                        "personality": "calm",
                        "voice_prompt": "Male, professional narrator",
                    }
                ],
            },
            "scene": {
                "title": "Test Scene",
                "premise": "A test of the system",
            },
        },
    }

    result = handler(test_job)
    print(json.dumps(result, indent=2))
