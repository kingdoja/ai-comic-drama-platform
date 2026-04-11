"""
Rerun API endpoints

Implements Requirements 7.1, 7.2, 8.1, 8.2, 12.1, 12.2, 12.3
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.rerun import (
    RerunHistoryItem,
    RerunHistoryResponse,
    RerunShotsRequest,
    RerunWorkflowRequest,
    RerunWorkflowResponse,
)
from app.services.rerun_service import RerunService

router = APIRouter(prefix="/api", tags=["rerun"])


@router.post(
    "/episodes/{episode_id}/rerun",
    response_model=RerunWorkflowResponse,
    status_code=201,
)
async def rerun_workflow(
    episode_id: UUID,
    request: RerunWorkflowRequest,
    db: Session = Depends(get_db),
):
    """
    Create a workflow rerun from a specified stage.
    
    Creates a new WorkflowRun that will execute from the specified stage onwards.
    All artifacts from stages before from_stage are preserved.
    
    Requirements: 7.1, 7.2
    
    Args:
        episode_id: ID of the episode to rerun
        request: Rerun request with from_stage and optional reason
        db: Database session
        
    Returns:
        Created WorkflowRun
        
    Raises:
        404: Episode not found
        400: Invalid stage or other validation error
    """
    workflow_repo = WorkflowRepository(db)
    rerun_service = RerunService(
        db=db,
        workflow_repo=workflow_repo,
    )
    
    try:
        # Create rerun workflow
        workflow = rerun_service.rerun_workflow(
            episode_id=episode_id,
            from_stage=request.from_stage,
            user_id=None,  # TODO: Get from auth context
            reason=request.reason,
        )
        
        # Convert rerun_shot_ids_jsonb to UUID list if present
        rerun_shot_ids = None
        if workflow.rerun_shot_ids_jsonb:
            rerun_shot_ids = [UUID(shot_id) for shot_id in workflow.rerun_shot_ids_jsonb]
        
        return RerunWorkflowResponse(
            id=workflow.id,
            episode_id=workflow.episode_id,
            workflow_kind=workflow.workflow_kind,
            status=workflow.status,
            rerun_from_stage=workflow.rerun_from_stage,
            parent_workflow_run_id=workflow.parent_workflow_run_id,
            rerun_reason=workflow.rerun_reason,
            rerun_shot_ids=rerun_shot_ids,
            started_at=workflow.started_at,
        )
        
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/episodes/{episode_id}/rerun-shots",
    response_model=RerunWorkflowResponse,
    status_code=201,
)
async def rerun_shots(
    episode_id: UUID,
    request: RerunShotsRequest,
    db: Session = Depends(get_db),
):
    """
    Create a shot-level rerun for specific shots.
    
    Creates a new WorkflowRun that will only process the specified shots
    for the given stage. Other shots' assets are preserved.
    
    Requirements: 8.1, 8.2
    
    Args:
        episode_id: ID of the episode
        request: Rerun request with shot_ids and stage_type
        db: Database session
        
    Returns:
        Created WorkflowRun
        
    Raises:
        404: Episode not found
        400: Invalid shot_ids or stage_type
    """
    workflow_repo = WorkflowRepository(db)
    rerun_service = RerunService(
        db=db,
        workflow_repo=workflow_repo,
    )
    
    try:
        # Create shot rerun workflow
        workflow = rerun_service.rerun_shots(
            episode_id=episode_id,
            shot_ids=request.shot_ids,
            stage_type=request.stage_type,
            user_id=None,  # TODO: Get from auth context
        )
        
        # Convert rerun_shot_ids_jsonb to UUID list
        rerun_shot_ids = None
        if workflow.rerun_shot_ids_jsonb:
            rerun_shot_ids = [UUID(shot_id) for shot_id in workflow.rerun_shot_ids_jsonb]
        
        return RerunWorkflowResponse(
            id=workflow.id,
            episode_id=workflow.episode_id,
            workflow_kind=workflow.workflow_kind,
            status=workflow.status,
            rerun_from_stage=workflow.rerun_from_stage,
            parent_workflow_run_id=workflow.parent_workflow_run_id,
            rerun_reason=workflow.rerun_reason,
            rerun_shot_ids=rerun_shot_ids,
            started_at=workflow.started_at,
        )
        
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/episodes/{episode_id}/rerun-history",
    response_model=RerunHistoryResponse,
)
async def get_rerun_history(
    episode_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get rerun history for an episode.
    
    Returns all WorkflowRun records for the episode, ordered by most recent first.
    Rerun workflows can be identified by the rerun_from_stage field.
    
    Requirements: 12.1, 12.2, 12.3
    
    Args:
        episode_id: ID of the episode
        db: Database session
        
    Returns:
        List of workflow runs including reruns
    """
    workflow_repo = WorkflowRepository(db)
    rerun_service = RerunService(
        db=db,
        workflow_repo=workflow_repo,
    )
    
    # Get all workflow runs for the episode
    workflows = rerun_service.get_rerun_history(episode_id)
    
    # Build response
    workflow_items = []
    rerun_count = 0
    
    for workflow in workflows:
        # Determine if this is a rerun
        is_rerun = workflow.rerun_from_stage is not None
        if is_rerun:
            rerun_count += 1
        
        # Convert rerun_shot_ids_jsonb to UUID list if present
        rerun_shot_ids = None
        if workflow.rerun_shot_ids_jsonb:
            rerun_shot_ids = [UUID(shot_id) for shot_id in workflow.rerun_shot_ids_jsonb]
        
        workflow_items.append(
            RerunHistoryItem(
                id=workflow.id,
                workflow_kind=workflow.workflow_kind,
                status=workflow.status,
                rerun_from_stage=workflow.rerun_from_stage,
                parent_workflow_run_id=workflow.parent_workflow_run_id,
                rerun_reason=workflow.rerun_reason,
                rerun_shot_ids=rerun_shot_ids,
                is_rerun=is_rerun,
                started_at=workflow.started_at,
                completed_at=workflow.completed_at,
                failure_reason=workflow.failure_reason,
            )
        )
    
    return RerunHistoryResponse(
        episode_id=episode_id,
        workflow_runs=workflow_items,
        total_count=len(workflow_items),
        rerun_count=rerun_count,
    )
