"""
Preview API routes.

Implements Requirements:
- 14.1: Display latest preview video
- 14.3: Show generation status and estimated completion time
- 14.4: Show failure reason and provide retry entry point
- 14.5: Show preview metadata (duration, resolution, generation time)
"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_store
from app.repositories.asset_repository import AssetRepository
from app.repositories.stage_task_repository import StageTaskRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.common import SuccessEnvelope
from app.schemas.preview import (
    PreviewAssetResponse,
    PreviewResponse,
    PreviewStageTaskResponse,
    PreviewStatusResponse,
)
from app.services.store import DatabaseStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["preview"])

# Stage types that are part of the media pipeline, in execution order
_MEDIA_STAGE_SEQUENCE = [
    "image_render",
    "subtitle",
    "tts",
    "edit_export_preview",
]

# Terminal statuses for a stage task
_TERMINAL_STATUSES = {"succeeded", "failed", "skipped"}


def _get_preview_url(storage_key: str, store: DatabaseStore) -> str | None:
    """
    Generate a presigned URL for a preview asset's storage key.
    Returns None if the storage service is unavailable.
    """
    try:
        from app.services.object_storage_service import ObjectStorageService
        svc = ObjectStorageService()
        return svc.get_url(storage_key, expires_in=3600)
    except Exception as exc:
        logger.warning("Could not generate presigned URL for %s: %s", storage_key, exc)
        return None


def _build_stage_task_response(task) -> PreviewStageTaskResponse:
    return PreviewStageTaskResponse(
        id=task.id,
        task_status=task.task_status,
        started_at=task.started_at,
        finished_at=task.finished_at,
        error_message=task.error_message,
        metrics=task.metrics_jsonb or {},
    )


# ---------------------------------------------------------------------------
# GET /episodes/{episode_id}/preview
# ---------------------------------------------------------------------------

@router.get("/episodes/{episode_id}/preview", response_model=SuccessEnvelope)
def get_episode_preview(
    episode_id: UUID,
    store: DatabaseStore = Depends(get_store),
) -> SuccessEnvelope:
    """
    Get the latest preview video for an episode.

    Returns the preview video URL, asset metadata, and generation status.

    Implements Requirements: 14.1, 14.5
    """
    # Verify episode exists
    episode = store.get_episode(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    asset_repo = AssetRepository(store.db)
    stage_task_repo = StageTaskRepository(store.db)

    # Find the most recent selected preview asset for this episode (Req 14.1)
    selected_assets = asset_repo.list_selected_for_episode(episode_id)
    preview_asset = next(
        (a for a in selected_assets if a.asset_type == "preview"), None
    )

    # Find the latest preview export stage task for status context
    preview_task = stage_task_repo.latest_by_stage(episode_id, "edit_export_preview")

    # Determine overall status
    if preview_asset is not None:
        status = "ready"
        message = "Preview is ready."
        preview_url = _get_preview_url(preview_asset.storage_key, store)
        asset_response = PreviewAssetResponse(
            id=preview_asset.id,
            storage_key=preview_asset.storage_key,
            mime_type=preview_asset.mime_type,
            size_bytes=preview_asset.size_bytes,
            duration_ms=preview_asset.duration_ms,
            width=preview_asset.width,
            height=preview_asset.height,
            created_at=preview_asset.created_at,
        )
    elif preview_task is not None and preview_task.task_status in ("pending", "running"):
        status = "generating"
        message = "Preview is being generated."
        preview_url = None
        asset_response = None
    elif preview_task is not None and preview_task.task_status == "failed":
        status = "failed"
        message = preview_task.error_message or "Preview generation failed."
        preview_url = None
        asset_response = None
    else:
        status = "not_started"
        message = "Preview has not been generated yet."
        preview_url = None
        asset_response = None

    stage_task_response = (
        _build_stage_task_response(preview_task) if preview_task else None
    )

    response = PreviewResponse(
        episode_id=episode_id,
        status=status,
        preview_url=preview_url,
        asset=asset_response,
        stage_task=stage_task_response,
        message=message,
        generated_at=preview_asset.created_at if preview_asset else None,
    )

    return SuccessEnvelope(data=response)


# ---------------------------------------------------------------------------
# GET /episodes/{episode_id}/preview/status
# ---------------------------------------------------------------------------

@router.get("/episodes/{episode_id}/preview/status", response_model=SuccessEnvelope)
def get_episode_preview_status(
    episode_id: UUID,
    store: DatabaseStore = Depends(get_store),
) -> SuccessEnvelope:
    """
    Query the preview generation status for an episode.

    Returns progress information, current stage, and estimated completion time.

    Implements Requirements: 14.3
    """
    # Verify episode exists
    episode = store.get_episode(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    stage_task_repo = StageTaskRepository(store.db)
    asset_repo = AssetRepository(store.db)

    # Collect the latest stage task for each media stage
    media_tasks = []
    for stage_type in _MEDIA_STAGE_SEQUENCE:
        task = stage_task_repo.latest_by_stage(episode_id, stage_type)
        if task is not None:
            media_tasks.append(task)

    # Check if preview asset already exists
    selected_assets = asset_repo.list_selected_for_episode(episode_id)
    preview_asset = next(
        (a for a in selected_assets if a.asset_type == "preview"), None
    )

    if preview_asset is not None:
        # Pipeline finished successfully
        overall_status = "ready"
        progress_pct = 100
        current_stage = None
        estimated_completion_at = None
        message = "Preview is ready."
    elif not media_tasks:
        overall_status = "not_started"
        progress_pct = 0
        current_stage = None
        estimated_completion_at = None
        message = "Media pipeline has not been started."
    else:
        # Determine progress from completed vs total stages
        completed = sum(
            1 for t in media_tasks if t.task_status == "succeeded"
        )
        failed_tasks = [t for t in media_tasks if t.task_status == "failed"]
        running_tasks = [t for t in media_tasks if t.task_status == "running"]

        total = len(_MEDIA_STAGE_SEQUENCE)
        progress_pct = int((completed / total) * 100)

        if failed_tasks:
            overall_status = "failed"
            current_stage = failed_tasks[-1].stage_type
            estimated_completion_at = None
            message = (
                f"Stage '{current_stage}' failed: "
                f"{failed_tasks[-1].error_message or 'unknown error'}"
            )
        elif running_tasks:
            overall_status = "generating"
            current_stage = running_tasks[0].stage_type
            # Rough estimate: assume each stage takes ~60 s
            remaining_stages = total - completed
            from datetime import datetime, timedelta
            estimated_completion_at = datetime.utcnow() + timedelta(
                seconds=remaining_stages * 60
            )
            message = f"Running stage: {current_stage}"
        else:
            # All known tasks are in terminal state but no preview asset yet
            overall_status = "generating"
            current_stage = None
            estimated_completion_at = None
            message = "Pipeline stages completed; awaiting preview asset."

    stage_task_responses = [_build_stage_task_response(t) for t in media_tasks]

    response = PreviewStatusResponse(
        episode_id=episode_id,
        status=overall_status,
        progress_pct=progress_pct,
        current_stage=current_stage,
        estimated_completion_at=estimated_completion_at,
        stage_tasks=stage_task_responses,
        message=message,
    )

    return SuccessEnvelope(data=response)


# ---------------------------------------------------------------------------
# POST /episodes/{episode_id}/preview/retry
# ---------------------------------------------------------------------------

@router.post("/episodes/{episode_id}/preview/retry", response_model=SuccessEnvelope)
def retry_preview_generation(
    episode_id: UUID,
    store: DatabaseStore = Depends(get_store),
) -> SuccessEnvelope:
    """
    Trigger a retry of the preview export stage for an episode.

    Only allowed when the latest preview export stage task has failed.

    Implements Requirements: 14.4
    """
    # Verify episode exists
    episode = store.get_episode(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    stage_task_repo = StageTaskRepository(store.db)
    workflow_repo = WorkflowRepository(store.db)

    preview_task = stage_task_repo.latest_by_stage(episode_id, "edit_export_preview")

    if preview_task is None:
        raise HTTPException(
            status_code=400,
            detail="No preview export stage task found. Start the media workflow first.",
        )

    if preview_task.task_status != "failed":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Preview export stage is currently '{preview_task.task_status}'. "
                "Retry is only available when the stage has failed."
            ),
        )

    # Log the retry attempt (Req 14.4)
    logger.info(
        "Preview retry requested for episode %s. Previous task %s failed with: %s",
        episode_id,
        preview_task.id,
        preview_task.error_message,
    )

    # Reset the failed stage task to pending so the workflow engine can pick it up
    stage_task_repo.update_status(
        preview_task.id,
        "pending",
        error_message=None,
        error_code=None,
    )

    from app.schemas.preview import PreviewRetryResponse

    response = PreviewRetryResponse(
        episode_id=episode_id,
        stage_task_id=preview_task.id,
        message=(
            "Preview export stage has been reset to pending. "
            "The workflow engine will retry the stage shortly."
        ),
    )

    return SuccessEnvelope(data=response)
