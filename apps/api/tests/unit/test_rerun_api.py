"""
Unit tests for Rerun API endpoints

Tests Requirements 7.1, 7.2, 8.1, 8.2, 12.1, 12.2, 12.3
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import WorkflowRunModel, EpisodeModel, ProjectModel


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestRerunAPI:
    """Test suite for Rerun API endpoints"""
    
    def test_rerun_workflow_success(self, client, test_session):
        """
        Test creating a workflow rerun.
        
        Validates Requirements 7.1, 7.2:
        - POST /episodes/{episode_id}/rerun
        - Accept from_stage parameter
        - Create rerun WorkflowRun
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        project = ProjectModel(
            id=project_id,
            name="Test Project",
            description="Test",
        )
        test_session.add(project)
        
        episode = EpisodeModel(
            id=episode_id,
            project_id=project_id,
            episode_number=1,
            title="Test Episode",
        )
        test_session.add(episode)
        
        # Create initial workflow
        initial_workflow = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="completed",
        )
        test_session.add(initial_workflow)
        test_session.commit()
        
        # Execute
        response = client.post(
            f"/api/episodes/{episode_id}/rerun",
            json={
                "from_stage": "script",
                "reason": "Need to adjust dialogue",
            }
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["episode_id"] == str(episode_id)
        assert data["workflow_kind"] == "episode"
        assert data["status"] == "running"
        assert data["rerun_from_stage"] == "script"
        assert data["rerun_reason"] == "Need to adjust dialogue"
        assert data["parent_workflow_run_id"] == str(initial_workflow.id)
        assert data["rerun_shot_ids"] is None
        assert "id" in data
        assert "started_at" in data
    
    def test_rerun_workflow_episode_not_found(self, client, test_session):
        """Test error when episode doesn't exist."""
        # Execute with non-existent episode
        response = client.post(
            f"/api/episodes/{uuid4()}/rerun",
            json={
                "from_stage": "brief",
            }
        )
        
        # Verify error response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_rerun_workflow_without_reason(self, client, test_session):
        """Test creating rerun without optional reason."""
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        project = ProjectModel(
            id=project_id,
            name="Test Project",
            description="Test",
        )
        test_session.add(project)
        
        episode = EpisodeModel(
            id=episode_id,
            project_id=project_id,
            episode_number=1,
            title="Test Episode",
        )
        test_session.add(episode)
        test_session.commit()
        
        # Execute without reason
        response = client.post(
            f"/api/episodes/{episode_id}/rerun",
            json={
                "from_stage": "storyboard",
            }
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["rerun_from_stage"] == "storyboard"
        assert data["rerun_reason"] is None
    
    def test_rerun_shots_success(self, client, test_session):
        """
        Test creating a shot-level rerun.
        
        Validates Requirements 8.1, 8.2:
        - POST /episodes/{episode_id}/rerun-shots
        - Accept shot_ids and stage_type
        - Create shot rerun WorkflowRun
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        shot_id1 = uuid4()
        shot_id2 = uuid4()
        
        project = ProjectModel(
            id=project_id,
            name="Test Project",
            description="Test",
        )
        test_session.add(project)
        
        episode = EpisodeModel(
            id=episode_id,
            project_id=project_id,
            episode_number=1,
            title="Test Episode",
        )
        test_session.add(episode)
        test_session.commit()
        
        # Execute
        response = client.post(
            f"/api/episodes/{episode_id}/rerun-shots",
            json={
                "shot_ids": [str(shot_id1), str(shot_id2)],
                "stage_type": "image_render",
            }
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["episode_id"] == str(episode_id)
        assert data["workflow_kind"] == "episode"
        assert data["status"] == "running"
        assert data["rerun_from_stage"] == "image_render"
        assert len(data["rerun_shot_ids"]) == 2
        assert str(shot_id1) in [str(sid) for sid in data["rerun_shot_ids"]]
        assert str(shot_id2) in [str(sid) for sid in data["rerun_shot_ids"]]
        assert "Shot-level rerun" in data["rerun_reason"]
        assert "id" in data
        assert "started_at" in data
    
    def test_rerun_shots_empty_list(self, client, test_session):
        """Test error when shot_ids list is empty."""
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        project = ProjectModel(
            id=project_id,
            name="Test Project",
            description="Test",
        )
        test_session.add(project)
        
        episode = EpisodeModel(
            id=episode_id,
            project_id=project_id,
            episode_number=1,
            title="Test Episode",
        )
        test_session.add(episode)
        test_session.commit()
        
        # Execute with empty shot_ids
        response = client.post(
            f"/api/episodes/{episode_id}/rerun-shots",
            json={
                "shot_ids": [],
                "stage_type": "image_render",
            }
        )
        
        # Verify error response
        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"].lower()
    
    def test_rerun_shots_invalid_stage_type(self, client, test_session):
        """Test error when stage_type is invalid for shot rerun."""
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        shot_id = uuid4()
        
        project = ProjectModel(
            id=project_id,
            name="Test Project",
            description="Test",
        )
        test_session.add(project)
        
        episode = EpisodeModel(
            id=episode_id,
            project_id=project_id,
            episode_number=1,
            title="Test Episode",
        )
        test_session.add(episode)
        test_session.commit()
        
        # Execute with invalid stage_type (should be validation error from schema)
        response = client.post(
            f"/api/episodes/{episode_id}/rerun-shots",
            json={
                "shot_ids": [str(shot_id)],
                "stage_type": "brief",  # Invalid for shot rerun
            }
        )
        
        # Verify error response (422 for validation error)
        assert response.status_code == 422
    
    def test_get_rerun_history_empty(self, client, test_session):
        """
        Test getting rerun history when no workflows exist.
        
        Validates Requirements 12.1, 12.2, 12.3:
        - GET /episodes/{episode_id}/rerun-history
        - Return empty list
        """
        episode_id = uuid4()
        
        # Execute
        response = client.get(f"/api/episodes/{episode_id}/rerun-history")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["episode_id"] == str(episode_id)
        assert data["workflow_runs"] == []
        assert data["total_count"] == 0
        assert data["rerun_count"] == 0
    
    def test_get_rerun_history_with_data(self, client, test_session):
        """
        Test getting rerun history with multiple workflows.
        
        Validates Requirements 12.1, 12.2, 12.3:
        - Return all workflow runs
        - Identify reruns
        - Sort by started_at DESC
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        project = ProjectModel(
            id=project_id,
            name="Test Project",
            description="Test",
        )
        test_session.add(project)
        
        episode = EpisodeModel(
            id=episode_id,
            project_id=project_id,
            episode_number=1,
            title="Test Episode",
        )
        test_session.add(episode)
        test_session.flush()
        
        # Create initial workflow
        workflow1 = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="completed",
            rerun_from_stage=None,  # Initial run
            parent_workflow_run_id=None,
        )
        test_session.add(workflow1)
        test_session.flush()
        
        # Create rerun workflow
        workflow2 = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="running",
            rerun_from_stage="script",
            parent_workflow_run_id=workflow1.id,
            rerun_reason="Adjust dialogue",
        )
        test_session.add(workflow2)
        test_session.flush()
        
        # Create shot rerun workflow
        shot_id1 = uuid4()
        shot_id2 = uuid4()
        workflow3 = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="completed",
            rerun_from_stage="image_render",
            parent_workflow_run_id=workflow2.id,
            rerun_reason="Shot-level rerun for 2 shot(s)",
            rerun_shot_ids_jsonb=[str(shot_id1), str(shot_id2)],
        )
        test_session.add(workflow3)
        test_session.commit()
        
        # Execute
        response = client.get(f"/api/episodes/{episode_id}/rerun-history")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["episode_id"] == str(episode_id)
        assert data["total_count"] == 3
        assert data["rerun_count"] == 2  # workflow2 and workflow3 are reruns
        assert len(data["workflow_runs"]) == 3
        
        # Verify workflow data
        workflows = data["workflow_runs"]
        
        # Find each workflow in the response
        initial_run = next(w for w in workflows if w["id"] == str(workflow1.id))
        full_rerun = next(w for w in workflows if w["id"] == str(workflow2.id))
        shot_rerun = next(w for w in workflows if w["id"] == str(workflow3.id))
        
        # Verify initial run
        assert initial_run["is_rerun"] is False
        assert initial_run["rerun_from_stage"] is None
        assert initial_run["parent_workflow_run_id"] is None
        assert initial_run["rerun_shot_ids"] is None
        
        # Verify full rerun
        assert full_rerun["is_rerun"] is True
        assert full_rerun["rerun_from_stage"] == "script"
        assert full_rerun["parent_workflow_run_id"] == str(workflow1.id)
        assert full_rerun["rerun_reason"] == "Adjust dialogue"
        assert full_rerun["rerun_shot_ids"] is None
        
        # Verify shot rerun
        assert shot_rerun["is_rerun"] is True
        assert shot_rerun["rerun_from_stage"] == "image_render"
        assert shot_rerun["parent_workflow_run_id"] == str(workflow2.id)
        assert len(shot_rerun["rerun_shot_ids"]) == 2
        assert str(shot_id1) in [str(sid) for sid in shot_rerun["rerun_shot_ids"]]
        
        # Verify sorting (newest first)
        # workflow3 was created last, so it should be first
        assert workflows[0]["id"] == str(workflow3.id)
    
    def test_get_rerun_history_distinguishes_rerun_types(self, client, test_session):
        """
        Test that rerun history distinguishes between full and shot-level reruns.
        
        Validates Requirements 12.3:
        - Identify rerun type (full vs shot-level)
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        project = ProjectModel(
            id=project_id,
            name="Test Project",
            description="Test",
        )
        test_session.add(project)
        
        episode = EpisodeModel(
            id=episode_id,
            project_id=project_id,
            episode_number=1,
            title="Test Episode",
        )
        test_session.add(episode)
        test_session.flush()
        
        # Create full rerun (no shot_ids)
        full_rerun = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="completed",
            rerun_from_stage="storyboard",
            rerun_shot_ids_jsonb=None,
        )
        test_session.add(full_rerun)
        
        # Create shot-level rerun (with shot_ids)
        shot_rerun = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="completed",
            rerun_from_stage="tts",
            rerun_shot_ids_jsonb=[str(uuid4())],
        )
        test_session.add(shot_rerun)
        test_session.commit()
        
        # Execute
        response = client.get(f"/api/episodes/{episode_id}/rerun-history")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        
        workflows = data["workflow_runs"]
        full_rerun_data = next(w for w in workflows if w["id"] == str(full_rerun.id))
        shot_rerun_data = next(w for w in workflows if w["id"] == str(shot_rerun.id))
        
        # Full rerun should have no shot_ids
        assert full_rerun_data["rerun_shot_ids"] is None
        
        # Shot rerun should have shot_ids
        assert shot_rerun_data["rerun_shot_ids"] is not None
        assert len(shot_rerun_data["rerun_shot_ids"]) == 1
