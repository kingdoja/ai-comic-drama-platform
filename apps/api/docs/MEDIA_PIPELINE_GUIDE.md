# Media Pipeline Usage Guide

## Overview

The media pipeline transforms a completed text workflow (storyboard + script) into a playable preview video. It runs four stages in sequence:

```
image_render → subtitle → tts → edit_export_preview
```

Each stage is independently fault-tolerant: a failure in one stage is recorded but does not necessarily block subsequent stages.

---

## Prerequisites

| Dependency | Purpose | Install |
|---|---|---|
| PostgreSQL | Database | `docker compose up -d postgres` |
| MinIO (or S3) | Object storage | `docker compose up -d minio` |
| FFmpeg | Video composition | `winget install ffmpeg` / `brew install ffmpeg` |
| Image Provider | Keyframe generation | See [Provider Adapters](PROVIDER_ADAPTERS.md) |
| TTS Provider | Audio synthesis | See [Provider Adapters](PROVIDER_ADAPTERS.md) |

Verify FFmpeg is on PATH:

```bash
ffmpeg -version
```

---

## Configuration

Copy `.env.example` to `.env` and fill in the relevant sections:

```env
# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/thinking

# Object Storage
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
S3_BUCKET=thinking-media
S3_REGION=us-east-1
S3_USE_SSL=false

# Image Provider
IMAGE_PROVIDER=mock              # mock | stable_diffusion
IMAGE_PROVIDER_API_URL=http://localhost:7860
IMAGE_PROVIDER_TIMEOUT=120
IMAGE_PROVIDER_MAX_RETRIES=3

# TTS Provider
TTS_PROVIDER=mock                # mock | azure
TTS_AZURE_SUBSCRIPTION_KEY=
TTS_AZURE_REGION=eastus
TTS_DEFAULT_VOICE=zh-CN-XiaoxiaoNeural
TTS_DEFAULT_LANGUAGE=zh-CN
```

For local development, `IMAGE_PROVIDER=mock` and `TTS_PROVIDER=mock` generate placeholder assets without calling any external API.

---

## Complete Pipeline Flow

### 1. Image Render Stage

Generates a keyframe image for every shot in the episode.

- Reads `visual_spec` from each shot via `ImageRenderInputBuilder`
- Calls the configured Image Provider in parallel (default: 5 concurrent)
- Uploads each image to Object Storage
- Creates an `Asset` record of type `keyframe` with `is_selected=True`

### 2. Subtitle Generation Stage

Generates a single WebVTT subtitle file for the episode.

- Reads `script_draft` and all shots
- Extracts dialogue text per shot
- Calculates timestamps from `shot.duration_ms`
- Uploads the `.vtt` file and creates an `Asset` record of type `subtitle`

### 3. TTS Stage

Synthesizes speech audio for every shot that has dialogue.

- Extracts dialogue from `shot.dialogue_text` (falls back to `script_draft`)
- Calls the configured TTS Provider in parallel (default: 5 concurrent)
- Uploads each audio file and creates an `Asset` record of type `audio`

### 4. Preview Export Stage

Composites all assets into a 720p H.264 preview video.

- Collects the primary (`is_selected=True`) keyframe and audio for each shot
- Downloads all assets to a temporary directory
- Builds per-shot video segments with FFmpeg (still image + audio)
- Concatenates segments and optionally burns in subtitles
- Uploads the final `preview.mp4` and creates an `Asset` record of type `preview`

---

## Running the Pipeline

### Via API

Trigger the media workflow for an episode:

```http
POST /api/v1/episodes/{episode_id}/media-workflow
```

The endpoint creates a `WorkflowRun` and executes all four stages asynchronously.

### Programmatically

```python
import asyncio
from sqlalchemy.orm import Session
from app.services.media_workflow_service import MediaWorkflowService
from app.services.image_render_stage import ImageRenderStage
from app.services.subtitle_generation_stage import SubtitleGenerationStage
from app.services.tts_stage import TTSStage
from app.services.preview_export_stage import PreviewExportStage
from app.services.object_storage_service import ObjectStorageService
from app.services.image_render_input_builder import ImageRenderInputBuilder
from app.providers.image_provider_factory import ImageProviderFactory
from app.providers.tts_provider_factory import TTSProviderFactory

def run_media_pipeline(db: Session, project, episode, workflow_run):
    storage = ObjectStorageService()
    image_provider = ImageProviderFactory.get_provider()
    tts_provider = TTSProviderFactory.get_provider()

    image_stage = ImageRenderStage(
        db=db,
        image_provider=image_provider,
        storage_service=storage,
        input_builder=ImageRenderInputBuilder(db),
    )
    subtitle_stage = SubtitleGenerationStage(db=db, storage_service=storage)
    tts_stage = TTSStage(db=db, tts_provider=tts_provider, storage_service=storage)
    preview_stage = PreviewExportStage(db=db, storage_service=storage)

    service = MediaWorkflowService(
        db=db,
        image_render_stage=image_stage,
        subtitle_stage=subtitle_stage,
        tts_stage=tts_stage,
        preview_export_stage=preview_stage,
    )

    result = asyncio.run(
        service.execute_media_chain(project=project, episode=episode, workflow_run=workflow_run)
    )
    print(result.status, result.total_assets_created)
```

### Restarting from a Specific Stage

Pass `start_stage` to skip already-completed stages:

```python
result = await service.execute_media_chain(
    project=project,
    episode=episode,
    workflow_run=workflow_run,
    start_stage="tts",   # skip image_render and subtitle
)
```

Valid values: `image_render`, `subtitle`, `tts`, `edit_export_preview`.

---

## Checking Results

### Workflow Status

After execution, `WorkflowRun.status` is set to one of:

| Status | Meaning |
|---|---|
| `media_ready` | All stages succeeded |
| `media_partial` | Some stages succeeded, some failed |
| `media_failed` | All stages failed |

### Stage Metrics

Each stage creates a `StageTask` record with `metrics_jsonb`:

```json
{
  "duration_ms": 12000,
  "provider_calls": 10,
  "success_count": 9,
  "failure_count": 1,
  "estimated_cost_usd": 0.45,
  "retry_count": 2
}
```

Query via:

```http
GET /api/v1/stage-tasks/{stage_task_id}
```

### Preview Video

```http
GET /api/v1/episodes/{episode_id}/preview
```

Returns the preview URL, duration, resolution, and generation time.

---

## Concurrency and Performance

| Stage | Default concurrency | Config key |
|---|---|---|
| Image Render | 5 shots in parallel | `max_concurrent` arg |
| TTS | 5 shots in parallel | `max_concurrent` arg |

Reduce concurrency if you hit provider rate limits:

```python
result = await image_stage.execute(
    episode_id=episode.id,
    project_id=project.id,
    stage_task_id=stage_task.id,
    max_concurrent=2,   # slower but avoids 429s
)
```

---

## Error Handling

### Retry Behaviour

All provider calls use exponential backoff:

| Attempt | Wait before retry |
|---|---|
| 1st retry | 1 s |
| 2nd retry | 2 s |
| 3rd retry | 4 s |
| After 3 failures | Record error, continue with next shot |

Permanent errors (HTTP 400, 401, 403) are not retried.

### Partial Failures

A single shot failure does not abort the stage. The stage returns `partial_success` and continues processing remaining shots. The preview video is still generated from whichever shots succeeded.

### FFmpeg Errors

If FFmpeg is not installed or fails:

```
RuntimeError: FFmpeg executable not found. Please install FFmpeg and ensure it is on PATH.
```

Install FFmpeg and verify with `ffmpeg -version`. Temporary files are preserved in the system temp directory for debugging when FFmpeg fails.

---

## Common Issues

### "No shots found for episode"

The episode has no shots yet. Run the text pipeline (storyboard agent) first.

### "No keyframe assets found for episode"

The Image Render Stage has not run or all shots failed. Check `StageTask` records for error details.

### Provider returns 429 Too Many Requests

Reduce `max_concurrent` or add delays between batches. The retry logic handles transient 429s automatically.

### Preview video is silent

No audio assets were created (TTS stage may have been skipped or all shots lack dialogue). The preview is still generated with silent video segments.

### MinIO connection refused

Ensure MinIO is running:

```bash
docker compose -f infra/docker/docker-compose.yml up -d minio
```

---

## Related Documentation

- [Object Storage Service](OBJECT_STORAGE.md)
- [Provider Adapters](PROVIDER_ADAPTERS.md)
- [Image Provider Adapter](IMAGE_PROVIDER_ADAPTER.md)
- [Requirements](../../.kiro/specs/media-pipeline-alpha/requirements.md)
- [Design](../../.kiro/specs/media-pipeline-alpha/design.md)
