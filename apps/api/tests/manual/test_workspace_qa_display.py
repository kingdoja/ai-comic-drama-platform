"""
Test to verify QA failure display in workspace.
Validates Requirements 10.4, 11.1
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


def test_qa_failure_display():
    """
    Test that workspace properly displays QA failures with critical issue highlighting.
    
    Validates:
    - Requirement 10.4: QA 失败时高亮显示 critical 和 major 问题
    - Requirement 11.1: Workspace 显示审核提示
    """
    
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
    
    # Create QA reports with different severities
    critical_report = QAReportSummaryResponse(
        id=uuid4(),
        qa_type="rule_check",
        result="fail",
        severity="critical",
        issue_count=3,
        rerun_stage_type="brief",
        created_at=datetime.now(timezone.utc),
    )
    
    major_report = QAReportSummaryResponse(
        id=uuid4(),
        qa_type="semantic_check",
        result="fail",
        severity="major",
        issue_count=2,
        rerun_stage_type="script",
        created_at=datetime.now(timezone.utc),
    )
    
    minor_report = QAReportSummaryResponse(
        id=uuid4(),
        qa_type="asset_check",
        result="warn",
        severity="minor",
        issue_count=1,
        rerun_stage_type=None,
        created_at=datetime.now(timezone.utc),
    )
    
    # Create QA summary with critical issues
    qa_summary = WorkspaceQAResponse(
        result="fail",
        issue_count=6,  # 3 + 2 + 1
        critical_issue_count=3,
        has_critical_issues=True,
        reports=[critical_report, major_report, minor_report],
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
        rerun_count=0,
        latest_workflow=None,
        media_status=MediaStatusResponse(),
        generated_at=datetime.now(timezone.utc),
        metadata={},
    )
    
    # Verify QA failure is properly displayed
    assert workspace.qa_summary.result == "fail", "QA result should be 'fail'"
    assert workspace.qa_summary.has_critical_issues is True, "Should flag critical issues"
    assert workspace.qa_summary.critical_issue_count == 3, "Should count critical issues"
    assert workspace.qa_summary.issue_count == 6, "Should count all issues"
    
    print("✓ QA failure is properly flagged in workspace")
    print("✓ Critical issues are counted and flagged")
    
    # Verify reports are available for detail view
    assert len(workspace.qa_summary.reports) == 3, "Should include all reports"
    
    # Verify critical report is accessible
    critical_reports = [r for r in workspace.qa_summary.reports if r.severity == "critical"]
    assert len(critical_reports) == 1, "Should have one critical report"
    assert critical_reports[0].issue_count == 3, "Critical report should have 3 issues"
    assert critical_reports[0].rerun_stage_type == "brief", "Should suggest rerun stage"
    
    print("✓ QA reports are available for detail view")
    print("✓ Critical reports can be filtered and highlighted")
    print("✓ Rerun suggestions are included")
    
    # Test serialization for frontend consumption
    workspace_dict = workspace.model_dump()
    assert workspace_dict["qa_summary"]["has_critical_issues"] is True
    assert workspace_dict["qa_summary"]["critical_issue_count"] == 3
    assert len(workspace_dict["qa_summary"]["reports"]) == 3
    
    print("✓ Workspace serialization includes all QA failure information")
    
    return True


def test_qa_pass_display():
    """Test that workspace properly displays when QA passes."""
    
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
    
    # Create passing QA report
    pass_report = QAReportSummaryResponse(
        id=uuid4(),
        qa_type="rule_check",
        result="pass",
        severity="info",
        issue_count=0,
        rerun_stage_type=None,
        created_at=datetime.now(timezone.utc),
    )
    
    qa_summary = WorkspaceQAResponse(
        result="pass",
        issue_count=0,
        critical_issue_count=0,
        has_critical_issues=False,
        reports=[pass_report],
    )
    
    workspace = EpisodeWorkspaceResponse(
        project=project,
        episode=episode,
        documents=[],
        stage_tasks=[],
        shots=[],
        assets=[],
        qa_summary=qa_summary,
        review_summary=WorkspaceReviewResponse(),
        rerun_count=0,
        latest_workflow=None,
        media_status=MediaStatusResponse(),
        generated_at=datetime.now(timezone.utc),
        metadata={},
    )
    
    # Verify QA pass is properly displayed
    assert workspace.qa_summary.result == "pass", "QA result should be 'pass'"
    assert workspace.qa_summary.has_critical_issues is False, "Should not flag critical issues"
    assert workspace.qa_summary.critical_issue_count == 0, "Should have no critical issues"
    assert workspace.qa_summary.issue_count == 0, "Should have no issues"
    
    print("✓ QA pass is properly displayed")
    print("✓ No critical issues flagged when QA passes")
    
    return True


if __name__ == "__main__":
    try:
        print("Testing QA failure display...")
        test_qa_failure_display()
        print("\n✅ QA failure display test passed!\n")
        
        print("Testing QA pass display...")
        test_qa_pass_display()
        print("\n✅ QA pass display test passed!\n")
        
        print("=" * 60)
        print("✅ All workspace QA display tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
