"""
Rerun Service

Handles workflow and shot-level reruns with data protection.

Implements Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3, 9.5
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import (
    EpisodeModel,
    ProjectModel,
    WorkflowRunModel,
)
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow import StartEpisodeWorkflowRequest


class RerunService:
    """
    Rerun Service - handles workflow and shot-level reruns.
    
    Responsibilities:
    1. Create rerun WorkflowRun records (Requirements 7.1, 7.2)
    2. Execute workflow reruns from specified stage (Requirements 7.3, 7.4)
    3. Execute shot-level reruns (Requirements 8.1, 8.2, 8.3)
    4. Protect existing data during reruns (Requirements 7.5, 9.2, 9.3, 9.5)
    5. Track rerun history (Requirements 7.1, 7.2)
    """
    
    def __init__(
        self,
        db: Session,
        workflow_repo: WorkflowRepository,
    ):
        """
        Initialize the Rerun Service.
        
        Args:
            db: Database session
            workflow_repo: Workflow repository instance
        """
        self.db = db
        self.workflow_repo = workflow_repo
    
    def execute_rerun(
        self,
        workflow_run: WorkflowRunModel,
        text_workflow_service=None,
        media_workflow_service=None,
    ):
        """
        Execute a rerun workflow.
        
        Implements Requirements: 7.3, 7.4, 7.5, 8.2, 8.3, 9.1, 9.2, 9.3
        
        This method executes the workflow from the rerun_from_stage onwards.
        It preserves all artifacts from stages before rerun_from_stage.
        For shot-level reruns, it only processes the specified shots.
        Uses database transactions to ensure data protection.
        
        Args:
            workflow_run: WorkflowRun to execute
            text_workflow_service: TextWorkflowService instance (optional)
            media_workflow_service: MediaWorkflowService instance (optional)
            
        Returns:
            Updated WorkflowRun model
            
        Raises:
            ValueError: If rerun_from_stage is not set
            LookupError: If episode or project not found
            Exception: If execution fails (will rollback)
        """
        try:
            if not workflow_run.rerun_from_stage:
                raise ValueError("rerun_from_stage must be set for rerun execution")
            
            # Get episode and project
            episode = self.db.get(EpisodeModel, workflow_run.episode_id)
            if episode is None:
                raise LookupError(f"Episode {workflow_run.episode_id} not found")
            
            project = self.db.get(ProjectModel, workflow_run.project_id)
            if project is None:
                raise LookupError(f"Project {workflow_run.project_id} not found")
            
            # Determine which workflow service to use based on stage type
            from app.services.text_workflow_service import TEXT_STAGE_SEQUENCE
            from app.services.media_workflow_service import MEDIA_STAGE_SEQUENCE
            
            start_stage = workflow_run.rerun_from_stage
            
            # Check if this is a shot-level rerun (Requirements 8.2, 8.3)
            shot_ids = None
            if workflow_run.rerun_shot_ids_jsonb:
                # Convert string UUIDs back to UUID objects
                shot_ids = [UUID(shot_id) for shot_id in workflow_run.rerun_shot_ids_jsonb]
            
            # Execute the appropriate workflow chain
            if start_stage in TEXT_STAGE_SEQUENCE:
                if text_workflow_service is None:
                    raise ValueError("text_workflow_service is required for text stage reruns")
                
                # Text stages don't support shot-level reruns
                if shot_ids:
                    raise ValueError("Shot-level reruns are not supported for text stages")
                
                # Execute text workflow from start_stage (Requirements 7.3, 7.4)
                text_workflow_service.execute_text_chain(
                    project=project,
                    episode=episode,
                    workflow_run=workflow_run,
                    start_stage=start_stage,
                )
                
            elif start_stage in MEDIA_STAGE_SEQUENCE:
                if media_workflow_service is None:
                    raise ValueError("media_workflow_service is required for media stage reruns")
                
                # Execute media workflow from start_stage (Requirements 7.3, 7.4, 8.2, 8.3)
                # Pass shot_ids for shot-level reruns
                # Note: This is async, so we need to handle it appropriately
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # For shot-level reruns, we need to pass the shot_ids to the media workflow
                # The media workflow will need to be updated to accept and use shot_ids
                result = loop.run_until_complete(
                    media_workflow_service.execute_media_chain(
                        project=project,
                        episode=episode,
                        workflow_run=workflow_run,
                        start_stage=start_stage,
                        shot_ids=shot_ids,  # Pass shot_ids for filtering
                    )
                )
            else:
                raise ValueError(f"Unknown stage type: {start_stage}")
            
            # Refresh and return the workflow run
            self.db.refresh(workflow_run)
            return workflow_run
            
        except Exception as e:
            # Rollback on any error (Requirement 7.5, 9.3)
            self.db.rollback()
            # Update workflow status to failed
            try:
                self.workflow_repo.update_status(
                    workflow_run.id,
                    "failed",
                    failure_reason=str(e),
                    commit=True,
                )
            except:
                pass  # If we can't update status, that's okay
            raise
    
    def rerun_workflow(
        self,
        episode_id: UUID,
        from_stage: str,
        user_id: Optional[UUID] = None,
        reason: Optional[str] = None,
        parent_workflow_run_id: Optional[UUID] = None,
    ) -> WorkflowRunModel:
        """
        Create a rerun WorkflowRun from a specified stage.
        
        Implements Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 9.1, 9.2, 9.3
        
        This method creates a new WorkflowRun that will execute from the specified
        stage onwards. It preserves all artifacts from stages before from_stage.
        Uses database transactions to ensure data protection.
        
        Args:
            episode_id: Episode ID to rerun
            from_stage: Stage to start rerun from
            user_id: User who initiated the rerun
            reason: Reason for the rerun
            parent_workflow_run_id: Parent WorkflowRun ID (if this is a rerun)
            
        Returns:
            Created WorkflowRun model
            
        Raises:
            LookupError: If episode not found
            Exception: If transaction fails (will rollback)
        """
        try:
            # Begin transaction (Requirement 7.5, 9.3)
            # Get episode and project
            episode = self.db.get(EpisodeModel, episode_id)
            if episode is None:
                raise LookupError(f"Episode {episode_id} not found")
            
            project = self.db.get(ProjectModel, episode.project_id)
            if project is None:
                raise LookupError(f"Project {episode.project_id} not found")
            
            # If parent_workflow_run_id not provided, get the latest workflow run
            if parent_workflow_run_id is None:
                latest_workflow = self.workflow_repo.latest_for_episode(episode_id)
                if latest_workflow:
                    parent_workflow_run_id = latest_workflow.id
            
            # Create new WorkflowRun with rerun fields (Requirements 7.1, 7.2)
            workflow = WorkflowRunModel(
                project_id=project.id,
                episode_id=episode_id,
                workflow_kind="episode",
                temporal_workflow_id=f"episode-{episode_id}-rerun-{uuid.uuid4()}",
                temporal_run_id=str(uuid.uuid4()),
                status="running",
                started_by_user_id=user_id,
                rerun_from_stage=from_stage,
                parent_workflow_run_id=parent_workflow_run_id,
                rerun_reason=reason,
                rerun_shot_ids_jsonb=None,  # Not a shot-level rerun
            )
            
            self.db.add(workflow)
            self.db.commit()
            self.db.refresh(workflow)
            
            return workflow
            
        except Exception as e:
            # Rollback on any error (Requirement 7.5, 9.3)
            self.db.rollback()
            raise
    
    def rerun_shots(
        self,
        episode_id: UUID,
        shot_ids: List[UUID],
        stage_type: str,
        user_id: Optional[UUID] = None,
    ) -> WorkflowRunModel:
        """
        Create a rerun WorkflowRun for specific shots.
        
        Implements Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.3
        
        This method creates a new WorkflowRun that will only process the specified
        shots for the given stage. Other shots' assets are preserved.
        Uses database transactions to ensure data protection.
        
        Args:
            episode_id: Episode ID
            shot_ids: List of Shot IDs to rerun
            stage_type: Stage type to rerun (e.g., "image_render", "tts")
            user_id: User who initiated the rerun
            
        Returns:
            Created WorkflowRun model
            
        Raises:
            LookupError: If episode not found
            ValueError: If shot_ids is empty or stage_type is invalid
            Exception: If transaction fails (will rollback)
        """
        try:
            # Begin transaction (Requirement 9.3)
            if not shot_ids:
                raise ValueError("shot_ids cannot be empty")
            
            # Validate stage_type
            valid_shot_stages = ["image_render", "tts"]
            if stage_type not in valid_shot_stages:
                raise ValueError(
                    f"Invalid stage_type for shot rerun: {stage_type}. "
                    f"Must be one of {valid_shot_stages}"
                )
            
            # Get episode and project
            episode = self.db.get(EpisodeModel, episode_id)
            if episode is None:
                raise LookupError(f"Episode {episode_id} not found")
            
            project = self.db.get(ProjectModel, episode.project_id)
            if project is None:
                raise LookupError(f"Project {episode.project_id} not found")
            
            # Get parent workflow run
            parent_workflow = self.workflow_repo.latest_for_episode(episode_id)
            parent_workflow_run_id = parent_workflow.id if parent_workflow else None
            
            # Create new WorkflowRun for shot rerun (Requirements 8.1, 8.2)
            workflow = WorkflowRunModel(
                project_id=project.id,
                episode_id=episode_id,
                workflow_kind="episode",
                temporal_workflow_id=f"episode-{episode_id}-shot-rerun-{uuid.uuid4()}",
                temporal_run_id=str(uuid.uuid4()),
                status="running",
                started_by_user_id=user_id,
                rerun_from_stage=stage_type,
                parent_workflow_run_id=parent_workflow_run_id,
                rerun_reason=f"Shot-level rerun for {len(shot_ids)} shot(s)",
                rerun_shot_ids_jsonb=[str(shot_id) for shot_id in shot_ids],
            )
            
            self.db.add(workflow)
            self.db.commit()
            self.db.refresh(workflow)
            
            return workflow
            
        except Exception as e:
            # Rollback on any error (Requirement 9.3)
            self.db.rollback()
            raise
    
    def get_rerun_history(
        self,
        episode_id: UUID,
    ) -> List[WorkflowRunModel]:
        """
        Get rerun history for an episode.
        
        Implements Requirements: 7.1, 7.2, 12.1, 12.2, 12.3
        
        Returns all WorkflowRun records for the episode, ordered by most recent first.
        Rerun workflows can be identified by the rerun_from_stage field.
        
        Args:
            episode_id: Episode ID
            
        Returns:
            List of WorkflowRun models ordered by started_at DESC
        """
        from sqlalchemy import select
        
        stmt = (
            select(WorkflowRunModel)
            .where(WorkflowRunModel.episode_id == episode_id)
            .order_by(WorkflowRunModel.started_at.desc())
        )
        
        workflows = self.db.scalars(stmt).all()
        return list(workflows)
