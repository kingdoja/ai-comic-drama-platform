"""
Test script to verify workspace integration changes.
This tests the schema and logic without requiring database connection.
"""
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.workspace import (
    EpisodeWorkspaceResponse,
    WorkspaceQAResponse,
    WorkspaceReviewResponse,
    QAReportSummaryResponse,
    MediaStatusResponse,
)
from app.schemas.project import ProjectResponse, EpisodeResponse


def test_workspace_schema_with_new_fields():
    """Test that workspace schema includes new QA and rerun fields."""
    
    # Create mock project and episode
    project = ProjectResponse(
        id=uuid4(),
        name="Test Project",
        source_mode="original",
        target_platform="web",
        status="draft",
        brief_version=1,
        current_episode_no=1,
        metadata_jsonb={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    episode = EpisodeResponse(
        id=uuid4(),
        project_id=project.id,
        episode_no=1,
        title="Test Episode",
        status="draft",
        current_stage="brief",
        target_duration_sec=300,
        script_version=1,
        storyboard_version=1,
        visual_version=1,
        audio_version=1,
        export_version=1,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    # Create QA summary with critical issues
    qa_report = QAReportSummaryResponse(
        id=uuid4(),
        qa_type="rule_check",
        result="fail",
        severity="critical",
        issue_count=3,
        rerun_stage_type="brief",
        created_at=datetime.now(timezone.utc),
    )
    
    qa_summary = WorkspaceQAResponse(
        result="fail",
        issue_count=5,
        critical_issue_count=3,
        has_critical_issues=True,
        reports=[qa_report],
    )
    
    # Create workspace response
    workspace = EpisodeWorkspaceResponse(
        project=project,
        episode=episode,
        documents=[],
        stage_tasks=[],
        shots=[],
        assets=[],
        qa_summary=qa_summary,
        review_summary=WorkspaceReviewResponse(),
        rerun_count=2,
        latest_workflow=None,
        media_status=MediaStatusResponse(),
        generated_at=datetime.now(timezone.utc),
        metadata={},
    )
    
    # Verify new fields are present
    assert workspace.rerun_count == 2, "rerun_count should be 2"
    assert workspace.qa_summary.critical_issue_count == 3, "critical_issue_count should be 3"
    assert workspace.qa_summary.has_critical_issues is True, "has_critical_issues should be True"
    
    print("✓ Workspace schema includes rerun_count field")
    print("✓ QA summary includes critical_issue_count field")
    print("✓ QA summary includes has_critical_issues field")
    print("✓ All new fields are working correctly")
    
    # Test serialization
    workspace_dict = workspace.model_dump()
    assert "rerun_count" in workspace_dict, "rerun_count should be in serialized output"
    assert "critical_issue_count" in workspace_dict["qa_summary"], "critical_issue_count should be in qa_summary"
    assert "has_critical_issues" in workspace_dict["qa_summary"], "has_critical_issues should be in qa_summary"
    
    print("✓ Workspace serialization includes all new fields")
    
    return True


if __name__ == "__main__":
    try:
        test_workspace_schema_with_new_fields()
        print("\n✅ All workspace integration tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
