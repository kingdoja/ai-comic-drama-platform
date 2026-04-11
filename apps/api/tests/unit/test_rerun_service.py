"""
Unit tests for Rerun Service

Tests the rerun service functionality including:
- Workflow rerun creation
- Shot-level rerun creation
- Rerun history retrieval
- Data protection mechanisms
"""

import uuid
from datetime import datetime
from unittest.mock import Mock, MagicMock

import pytest
from sqlalchemy.orm import Session

from app.db.models import EpisodeModel, ProjectModel, WorkflowRunModel
from app.repositories.workflow_repository import WorkflowRepository
from app.services.rerun_service import RerunService


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def mock_workflow_repo():
    """Create a mock workflow repository."""
    return Mock(spec=WorkflowRepository)


@pytest.fixture
def rerun_service(mock_db, mock_workflow_repo):
    """Create a RerunService instance with mocked dependencies."""
    return RerunService(db=mock_db, workflow_repo=mock_workflow_repo)


@pytest.fixture
def sample_project():
    """Create a sample project."""
    return ProjectModel(
        id=uuid.uuid4(),
        name="Test Project",
        source_mode="original",
        target_platform="web",
        status="active",
    )


@pytest.fixture
def sample_episode(sample_project):
    """Create a sample episode."""
    return EpisodeModel(
        id=uuid.uuid4(),
        project_id=sample_project.id,
        episode_no=1,
        title="Test Episode",
        status="draft",
        current_stage="storyboard",
        target_duration_sec=300,
    )


class TestRerunWorkflow:
    """Tests for rerun_workflow method."""
    
    def test_rerun_workflow_creates_workflow_run(
        self, rerun_service, mock_db, mock_workflow_repo, sample_project, sample_episode
    ):
        """Test that rerun_workflow creates a new WorkflowRun with correct fields."""
        # Setup
        mock_db.get.side_effect = lambda model, id: {
            EpisodeModel: sample_episode,
            ProjectModel: sample_project,
        }.get(model)
        
        parent_workflow = WorkflowRunModel(
            id=uuid.uuid4(),
            project_id=sample_project.id,
            episode_id=sample_episode.id,
            workflow_kind="episode",
            temporal_workflow_id="test-workflow-1",
            temporal_run_id="test-run-1",
            status="succeeded",
        )
        mock_workflow_repo.latest_for_episode.return_value = parent_workflow
        
        # Execute
        result = rerun_service.rerun_workflow(
            episode_id=sample_episode.id,
            from_stage="image_render",
            user_id=uuid.uuid4(),
            reason="Test rerun",
        )
        
        # Verify
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Check that the workflow was created with correct fields
        added_workflow = mock_db.add.call_args[0][0]
        assert isinstance(added_workflow, WorkflowRunModel)
        assert added_workflow.episode_id == sample_episode.id
        assert added_workflow.project_id == sample_project.id
        assert added_workflow.rerun_from_stage == "image_render"
        assert added_workflow.parent_workflow_run_id == parent_workflow.id
        assert added_workflow.rerun_reason == "Test rerun"
        assert added_workflow.rerun_shot_ids_jsonb is None
    
    def test_rerun_workflow_handles_missing_episode(
        self, rerun_service, mock_db
    ):
        """Test that rerun_workflow raises LookupError for missing episode."""
        # Setup
        mock_db.get.return_value = None
        
        # Execute & Verify
        with pytest.raises(LookupError, match="Episode .* not found"):
            rerun_service.rerun_workflow(
                episode_id=uuid.uuid4(),
                from_stage="image_render",
            )
    
    def test_rerun_workflow_rolls_back_on_error(
        self, rerun_service, mock_db, sample_project, sample_episode
    ):
        """Test that rerun_workflow rolls back transaction on error."""
        # Setup
        mock_db.get.side_effect = lambda model, id: {
            EpisodeModel: sample_episode,
            ProjectModel: sample_project,
        }.get(model)
        
        # Make commit raise an error
        mock_db.commit.side_effect = Exception("Database error")
        
        # Execute & Verify
        with pytest.raises(Exception, match="Database error"):
            rerun_service.rerun_workflow(
                episode_id=sample_episode.id,
                from_stage="image_render",
            )
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()


class TestRerunShots:
    """Tests for rerun_shots method."""
    
    def test_rerun_shots_creates_workflow_run(
        self, rerun_service, mock_db, mock_workflow_repo, sample_project, sample_episode
    ):
        """Test that rerun_shots creates a new WorkflowRun with shot IDs."""
        # Setup
        mock_db.get.side_effect = lambda model, id: {
            EpisodeModel: sample_episode,
            ProjectModel: sample_project,
        }.get(model)
        
        parent_workflow = WorkflowRunModel(
            id=uuid.uuid4(),
            project_id=sample_project.id,
            episode_id=sample_episode.id,
            workflow_kind="episode",
            temporal_workflow_id="test-workflow-1",
            temporal_run_id="test-run-1",
            status="succeeded",
        )
        mock_workflow_repo.latest_for_episode.return_value = parent_workflow
        
        shot_ids = [uuid.uuid4(), uuid.uuid4()]
        
        # Execute
        result = rerun_service.rerun_shots(
            episode_id=sample_episode.id,
            shot_ids=shot_ids,
            stage_type="image_render",
            user_id=uuid.uuid4(),
        )
        
        # Verify
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Check that the workflow was created with correct fields
        added_workflow = mock_db.add.call_args[0][0]
        assert isinstance(added_workflow, WorkflowRunModel)
        assert added_workflow.episode_id == sample_episode.id
        assert added_workflow.rerun_from_stage == "image_render"
        assert added_workflow.parent_workflow_run_id == parent_workflow.id
        assert added_workflow.rerun_shot_ids_jsonb == [str(sid) for sid in shot_ids]
        assert "Shot-level rerun" in added_workflow.rerun_reason
    
    def test_rerun_shots_validates_empty_shot_ids(
        self, rerun_service, mock_db
    ):
        """Test that rerun_shots raises ValueError for empty shot_ids."""
        with pytest.raises(ValueError, match="shot_ids cannot be empty"):
            rerun_service.rerun_shots(
                episode_id=uuid.uuid4(),
                shot_ids=[],
                stage_type="image_render",
            )
    
    def test_rerun_shots_validates_stage_type(
        self, rerun_service, mock_db, sample_project, sample_episode
    ):
        """Test that rerun_shots validates stage_type."""
        # Setup
        mock_db.get.side_effect = lambda model, id: {
            EpisodeModel: sample_episode,
            ProjectModel: sample_project,
        }.get(model)
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Invalid stage_type"):
            rerun_service.rerun_shots(
                episode_id=sample_episode.id,
                shot_ids=[uuid.uuid4()],
                stage_type="invalid_stage",
            )
    
    def test_rerun_shots_rolls_back_on_error(
        self, rerun_service, mock_db, sample_project, sample_episode
    ):
        """Test that rerun_shots rolls back transaction on error."""
        # Setup
        mock_db.get.side_effect = lambda model, id: {
            EpisodeModel: sample_episode,
            ProjectModel: sample_project,
        }.get(model)
        
        # Make commit raise an error
        mock_db.commit.side_effect = Exception("Database error")
        
        # Execute & Verify
        with pytest.raises(Exception, match="Database error"):
            rerun_service.rerun_shots(
                episode_id=sample_episode.id,
                shot_ids=[uuid.uuid4()],
                stage_type="image_render",
            )
        
        # Verify rollback was called
        mock_db.rollback.assert_called_once()
    
    def test_rerun_shots_supports_batch_processing(
        self, rerun_service, mock_db, mock_workflow_repo, sample_project, sample_episode
    ):
        """Test that rerun_shots supports batch processing of multiple shots (Requirement 8.5)."""
        # Setup
        mock_db.get.side_effect = lambda model, id: {
            EpisodeModel: sample_episode,
            ProjectModel: sample_project,
        }.get(model)
        
        parent_workflow = WorkflowRunModel(
            id=uuid.uuid4(),
            project_id=sample_project.id,
            episode_id=sample_episode.id,
            workflow_kind="episode",
            temporal_workflow_id="test-workflow-1",
            temporal_run_id="test-run-1",
            status="succeeded",
        )
        mock_workflow_repo.latest_for_episode.return_value = parent_workflow
        
        # Create a batch of 5 shots
        shot_ids = [uuid.uuid4() for _ in range(5)]
        
        # Execute
        result = rerun_service.rerun_shots(
            episode_id=sample_episode.id,
            shot_ids=shot_ids,
            stage_type="tts",
            user_id=uuid.uuid4(),
        )
        
        # Verify
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Check that the workflow was created with all shot IDs
        added_workflow = mock_db.add.call_args[0][0]
        assert isinstance(added_workflow, WorkflowRunModel)
        assert len(added_workflow.rerun_shot_ids_jsonb) == 5
        assert added_workflow.rerun_shot_ids_jsonb == [str(sid) for sid in shot_ids]
        assert "5 shot(s)" in added_workflow.rerun_reason


class TestGetRerunHistory:
    """Tests for get_rerun_history method."""
    
    def test_get_rerun_history_returns_workflows(
        self, rerun_service, mock_db, sample_episode
    ):
        """Test that get_rerun_history returns workflow runs."""
        # Setup
        workflows = [
            WorkflowRunModel(
                id=uuid.uuid4(),
                project_id=uuid.uuid4(),
                episode_id=sample_episode.id,
                workflow_kind="episode",
                temporal_workflow_id=f"test-workflow-{i}",
                temporal_run_id=f"test-run-{i}",
                status="succeeded",
                rerun_from_stage="image_render" if i > 0 else None,
            )
            for i in range(3)
        ]
        
        # Mock the database query
        mock_scalars = Mock()
        mock_scalars.all.return_value = workflows
        mock_db.scalars.return_value = mock_scalars
        
        # Execute
        result = rerun_service.get_rerun_history(sample_episode.id)
        
        # Verify
        assert len(result) == 3
        assert all(isinstance(w, WorkflowRunModel) for w in result)
        
        # Verify that the query was executed
        mock_db.scalars.assert_called_once()
