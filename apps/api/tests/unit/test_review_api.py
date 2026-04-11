"""
Unit tests for Review API endpoints

Tests Requirements 11.3, 6.1, 6.2, 12.1, 12.2
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import StageTaskModel, WorkflowRunModel, ReviewDecisionModel


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestReviewAPI:
    """Test suite for Review API endpoints"""
    
    def test_submit_review_approved(self, client, test_session):
        """
        Test submitting an approved review.
        
        Validates Requirements 11.3, 6.1, 6.2:
        - POST /stage-tasks/{stage_task_id}/review
        - Accept decision and comment
        - Create ReviewDecision
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        workflow = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="waiting_review",
        )
        test_session.add(workflow)
        test_session.flush()
        
        stage_task = StageTaskModel(
            id=uuid4(),
            workflow_run_id=workflow.id,
            project_id=project_id,
            episode_id=episode_id,
            stage_type="brief",
            task_status="review_pending",
            worker_kind="agent",
            review_required=True,
            review_status="pending",
        )
        test_session.add(stage_task)
        test_session.commit()
        
        # Execute
        response = client.post(
            f"/api/stage-tasks/{stage_task.id}/review",
            json={
                "decision": "approved",
                "comment": "Looks great!",
            }
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["decision"] == "approved"
        assert data["comment_text"] == "Looks great!"
        assert data["stage_task_id"] == str(stage_task.id)
        assert data["episode_id"] == str(episode_id)
        assert "id" in data
        assert "created_at" in data
        
        # Verify database state
        test_session.refresh(stage_task)
        assert stage_task.review_status == "approved"
        assert stage_task.task_status == "completed"
        
        test_session.refresh(workflow)
        assert workflow.status == "running"
    
    def test_submit_review_rejected(self, client, test_session):
        """
        Test submitting a rejected review.
        
        Validates Requirements 11.3, 6.1:
        - Reject decision terminates workflow
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        workflow = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="waiting_review",
        )
        test_session.add(workflow)
        test_session.flush()
        
        stage_task = StageTaskModel(
            id=uuid4(),
            workflow_run_id=workflow.id,
            project_id=project_id,
            episode_id=episode_id,
            stage_type="script",
            task_status="review_pending",
            worker_kind="agent",
            review_required=True,
            review_status="pending",
        )
        test_session.add(stage_task)
        test_session.commit()
        
        # Execute
        response = client.post(
            f"/api/stage-tasks/{stage_task.id}/review",
            json={
                "decision": "rejected",
                "comment": "Quality not acceptable",
            }
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["decision"] == "rejected"
        assert data["comment_text"] == "Quality not acceptable"
        
        # Verify workflow terminated
        test_session.refresh(workflow)
        assert workflow.status == "failed"
    
    def test_submit_review_revision_required(self, client, test_session):
        """
        Test submitting a revision_required review with rerun payload.
        
        Validates Requirements 6.2:
        - revision_required decision with payload
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        workflow = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="waiting_review",
        )
        test_session.add(workflow)
        test_session.flush()
        
        stage_task = StageTaskModel(
            id=uuid4(),
            workflow_run_id=workflow.id,
            project_id=project_id,
            episode_id=episode_id,
            stage_type="storyboard",
            task_status="review_pending",
            worker_kind="agent",
            review_required=True,
            review_status="pending",
        )
        test_session.add(stage_task)
        test_session.commit()
        
        # Execute
        response = client.post(
            f"/api/stage-tasks/{stage_task.id}/review",
            json={
                "decision": "revision_required",
                "comment": "Please adjust character expressions",
                "payload": {
                    "rerun_from_stage": "storyboard",
                    "reason": "Character expressions need work",
                }
            }
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["decision"] == "revision_required"
        assert data["comment_text"] == "Please adjust character expressions"
        assert data["payload_jsonb"]["rerun_from_stage"] == "storyboard"
        
        # Verify stage task marked for revision
        test_session.refresh(stage_task)
        assert stage_task.review_status == "revision_required"
    
    def test_submit_review_invalid_decision(self, client, test_session):
        """Test that invalid decision values are rejected."""
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        workflow = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="waiting_review",
        )
        test_session.add(workflow)
        test_session.flush()
        
        stage_task = StageTaskModel(
            id=uuid4(),
            workflow_run_id=workflow.id,
            project_id=project_id,
            episode_id=episode_id,
            stage_type="brief",
            task_status="review_pending",
            worker_kind="agent",
            review_required=True,
            review_status="pending",
        )
        test_session.add(stage_task)
        test_session.commit()
        
        # Execute with invalid decision
        response = client.post(
            f"/api/stage-tasks/{stage_task.id}/review",
            json={
                "decision": "maybe",  # Invalid
                "comment": "Not sure",
            }
        )
        
        # Verify error response
        assert response.status_code == 422  # Validation error
    
    def test_submit_review_stage_task_not_found(self, client, test_session):
        """Test error when stage task doesn't exist."""
        # Execute with non-existent stage task
        response = client.post(
            f"/api/stage-tasks/{uuid4()}/review",
            json={
                "decision": "approved",
                "comment": "Looks good",
            }
        )
        
        # Verify error response
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_reviews_empty(self, client, test_session):
        """
        Test listing reviews when none exist.
        
        Validates Requirements 12.1, 12.2:
        - GET /episodes/{episode_id}/reviews
        - Return empty list
        """
        episode_id = uuid4()
        
        # Execute
        response = client.get(f"/api/episodes/{episode_id}/reviews")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["episode_id"] == str(episode_id)
        assert data["reviews"] == []
        assert data["total_count"] == 0
    
    def test_list_reviews_with_data(self, client, test_session):
        """
        Test listing reviews with multiple reviews.
        
        Validates Requirements 12.1, 12.2:
        - Return all reviews for episode
        - Sort by created_at DESC
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        workflow = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="waiting_review",
        )
        test_session.add(workflow)
        test_session.flush()
        
        # Create stage tasks
        stage_task1 = StageTaskModel(
            id=uuid4(),
            workflow_run_id=workflow.id,
            project_id=project_id,
            episode_id=episode_id,
            stage_type="brief",
            task_status="completed",
            worker_kind="agent",
            review_required=True,
            review_status="approved",
        )
        
        stage_task2 = StageTaskModel(
            id=uuid4(),
            workflow_run_id=workflow.id,
            project_id=project_id,
            episode_id=episode_id,
            stage_type="script",
            task_status="failed",
            worker_kind="agent",
            review_required=True,
            review_status="rejected",
        )
        
        test_session.add_all([stage_task1, stage_task2])
        test_session.flush()
        
        # Create review decisions
        review1 = ReviewDecisionModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            stage_task_id=stage_task1.id,
            reviewer_user_id=None,
            decision="approved",
            comment_text="Good work",
            payload_jsonb={},
        )
        
        review2 = ReviewDecisionModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            stage_task_id=stage_task2.id,
            reviewer_user_id=None,
            decision="rejected",
            comment_text="Needs improvement",
            payload_jsonb={},
        )
        
        test_session.add_all([review1, review2])
        test_session.commit()
        
        # Execute
        response = client.get(f"/api/episodes/{episode_id}/reviews")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["episode_id"] == str(episode_id)
        assert data["total_count"] == 2
        assert len(data["reviews"]) == 2
        
        # Verify review data
        reviews = data["reviews"]
        assert reviews[0]["decision"] in ["approved", "rejected"]
        assert reviews[0]["stage_type"] in ["brief", "script"]
        assert "created_at" in reviews[0]
        
        # Verify sorting (newest first)
        # Since we created review2 after review1, it should come first
        assert reviews[0]["id"] == str(review2.id)
        assert reviews[1]["id"] == str(review1.id)
    
    def test_list_reviews_includes_stage_type(self, client, test_session):
        """
        Test that review history includes stage_type from stage task.
        
        Validates Requirements 12.1:
        - Include stage information in review history
        """
        # Setup
        project_id = uuid4()
        episode_id = uuid4()
        
        workflow = WorkflowRunModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            workflow_kind="episode",
            temporal_workflow_id=f"test-{uuid4()}",
            temporal_run_id=str(uuid4()),
            status="waiting_review",
        )
        test_session.add(workflow)
        test_session.flush()
        
        stage_task = StageTaskModel(
            id=uuid4(),
            workflow_run_id=workflow.id,
            project_id=project_id,
            episode_id=episode_id,
            stage_type="storyboard",
            task_status="completed",
            worker_kind="agent",
            review_required=True,
            review_status="approved",
        )
        test_session.add(stage_task)
        test_session.flush()
        
        review = ReviewDecisionModel(
            id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            stage_task_id=stage_task.id,
            reviewer_user_id=None,
            decision="approved",
            comment_text="Excellent storyboard",
            payload_jsonb={},
        )
        test_session.add(review)
        test_session.commit()
        
        # Execute
        response = client.get(f"/api/episodes/{episode_id}/reviews")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert len(data["reviews"]) == 1
        assert data["reviews"][0]["stage_type"] == "storyboard"
        assert data["reviews"][0]["decision"] == "approved"
