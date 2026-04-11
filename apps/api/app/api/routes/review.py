"""
Review API endpoints

Implements Requirements 11.3, 6.1, 6.2, 12.1, 12.2
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.review_repository import ReviewRepository
from app.repositories.stage_task_repository import StageTaskRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.review import (
    ReviewDecisionResponse,
    ReviewHistoryItem,
    ReviewHistoryResponse,
    ReviewSubmitRequest,
)
from app.services.review_service import ReviewGateService

router = APIRouter(prefix="/api", tags=["review"])


@router.post(
    "/stage-tasks/{stage_task_id}/review",
    response_model=ReviewDecisionResponse,
    status_code=201,
)
async def submit_review(
    stage_task_id: UUID,
    request: ReviewSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a review decision for a stage task.
    
    Creates a ReviewDecision record and processes the decision:
    - approved: Resume workflow execution
    - rejected: Terminate workflow
    - revision_required: Mark for rerun (caller triggers rerun)
    
    Requirements: 11.3, 6.1, 6.2
    
    Args:
        stage_task_id: ID of the stage task being reviewed
        request: Review decision details
        db: Database session
        
    Returns:
        Created ReviewDecision
        
    Raises:
        404: Stage task not found
        400: Invalid decision or stage task not in review state
    """
    # Initialize repositories and service
    review_repo = ReviewRepository(db)
    stage_task_repo = StageTaskRepository(db)
    workflow_repo = WorkflowRepository(db)
    
    review_service = ReviewGateService(
        db=db,
        review_repo=review_repo,
        stage_task_repo=stage_task_repo,
        workflow_repo=workflow_repo,
    )
    
    try:
        # Submit review (reviewer_user_id is None for now, can be added later)
        review = review_service.submit_review(
            stage_task_id=stage_task_id,
            reviewer_user_id=None,  # TODO: Get from auth context
            decision=request.decision,
            comment=request.comment,
            payload=request.payload,
        )
        
        return ReviewDecisionResponse(
            id=review.id,
            project_id=review.project_id,
            episode_id=review.episode_id,
            stage_task_id=review.stage_task_id,
            reviewer_user_id=review.reviewer_user_id,
            decision=review.decision,
            comment_text=review.comment_text,
            payload_jsonb=review.payload_jsonb,
            created_at=review.created_at,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/episodes/{episode_id}/reviews",
    response_model=ReviewHistoryResponse,
)
async def list_reviews(
    episode_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get all review decisions for an episode.
    
    Returns reviews in reverse chronological order (newest first).
    
    Requirements: 12.1, 12.2
    
    Args:
        episode_id: ID of the episode
        db: Database session
        
    Returns:
        List of review decisions with stage information
    """
    review_repo = ReviewRepository(db)
    stage_task_repo = StageTaskRepository(db)
    
    # Get all reviews for the episode
    reviews = review_repo.list_for_episode(episode_id)
    
    # Build response with stage information
    review_items = []
    for review in reviews:
        # Get stage task to include stage_type
        stage_task = stage_task_repo.get(review.stage_task_id)
        
        review_items.append(
            ReviewHistoryItem(
                id=review.id,
                stage_task_id=review.stage_task_id,
                stage_type=stage_task.stage_type if stage_task else None,
                reviewer_user_id=review.reviewer_user_id,
                decision=review.decision,
                comment_text=review.comment_text,
                created_at=review.created_at,
            )
        )
    
    return ReviewHistoryResponse(
        episode_id=episode_id,
        reviews=review_items,
        total_count=len(review_items),
    )
