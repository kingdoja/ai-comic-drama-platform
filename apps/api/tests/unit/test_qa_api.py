"""
Unit tests for QA Report API endpoints.

Tests the QA report query and detail endpoints.
"""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from app.db.models import EpisodeModel, ProjectModel, QAReportModel
from app.repositories.qa_repository import QARepository


class TestQAReportAPI:
    """Test QA Report API endpoints"""
    
    def test_list_qa_reports_empty(self, db: Session):
        """Test listing QA reports when none exist"""
        # Create test project and episode
        project = ProjectModel(
            id=uuid.uuid4(),
            name="Test Project",
            source_mode="original",
            target_platform="douyin",
            status="draft",
        )
        episode = EpisodeModel(
            id=uuid.uuid4(),
            project_id=project.id,
            episode_no=1,
            target_duration_sec=60,
            status="draft",
        )
        db.add(project)
        db.add(episode)
        db.commit()
        
        # Query reports
        qa_repo = QARepository(db)
        reports = qa_repo.list_for_episode(episode.id)
        
        assert len(reports) == 0
    
    def test_list_qa_reports_with_data(self, db: Session):
        """Test listing QA reports returns data in correct order"""
        # Create test project and episode
        project = ProjectModel(
            id=uuid.uuid4(),
            name="Test Project",
            source_mode="original",
            target_platform="douyin",
            status="draft",
        )
        episode = EpisodeModel(
            id=uuid.uuid4(),
            project_id=project.id,
            episode_no=1,
            target_duration_sec=60,
            status="draft",
        )
        db.add(project)
        db.add(episode)
        db.commit()
        
        # Create QA reports with different timestamps
        report1 = QAReportModel(
            id=uuid.uuid4(),
            project_id=project.id,
            episode_id=episode.id,
            qa_type="rule_check",
            target_ref_type="document",
            result="passed",
            severity="info",
            issue_count=0,
            issues_jsonb=[],
        )
        report2 = QAReportModel(
            id=uuid.uuid4(),
            project_id=project.id,
            episode_id=episode.id,
            qa_type="semantic_check",
            target_ref_type="document",
            result="failed",
            severity="major",
            issue_count=3,
            issues_jsonb=[
                {
                    "type": "missing_field",
                    "severity": "major",
                    "location": "brief.genre",
                    "message": "Genre field is required",
                    "suggestion": "Add genre information"
                }
            ],
        )
        db.add(report1)
        db.add(report2)
        db.commit()
        
        # Query reports
        qa_repo = QARepository(db)
        reports = qa_repo.list_for_episode(episode.id)
        
        # Should return 2 reports in reverse chronological order
        assert len(reports) == 2
        # Most recent first (report2 was added after report1)
        assert reports[0].id == report2.id
        assert reports[1].id == report1.id
    
    def test_get_qa_report_by_id(self, db: Session):
        """Test getting a specific QA report by ID"""
        # Create test project and episode
        project = ProjectModel(
            id=uuid.uuid4(),
            name="Test Project",
            source_mode="original",
            target_platform="douyin",
            status="draft",
        )
        episode = EpisodeModel(
            id=uuid.uuid4(),
            project_id=project.id,
            episode_no=1,
            target_duration_sec=60,
            status="draft",
        )
        db.add(project)
        db.add(episode)
        db.commit()
        
        # Create QA report with issues
        report_id = uuid.uuid4()
        report = QAReportModel(
            id=report_id,
            project_id=project.id,
            episode_id=episode.id,
            qa_type="rule_check",
            target_ref_type="document",
            result="failed",
            severity="critical",
            issue_count=2,
            score=45.5,
            issues_jsonb=[
                {
                    "type": "missing_field",
                    "severity": "critical",
                    "location": "brief.title",
                    "message": "Title is required",
                    "suggestion": "Add a title"
                },
                {
                    "type": "invalid_format",
                    "severity": "major",
                    "location": "brief.duration",
                    "message": "Duration must be positive",
                    "suggestion": "Set duration > 0"
                }
            ],
            rerun_stage_type="brief",
        )
        db.add(report)
        db.commit()
        
        # Query report by ID
        qa_repo = QARepository(db)
        retrieved_report = qa_repo.get_by_id(report_id)
        
        assert retrieved_report is not None
        assert retrieved_report.id == report_id
        assert retrieved_report.qa_type == "rule_check"
        assert retrieved_report.result == "failed"
        assert retrieved_report.severity == "critical"
        assert retrieved_report.issue_count == 2
        assert float(retrieved_report.score) == 45.5
        assert len(retrieved_report.issues_jsonb) == 2
        assert retrieved_report.rerun_stage_type == "brief"
    
    def test_get_qa_report_not_found(self, db: Session):
        """Test getting a non-existent QA report returns None"""
        qa_repo = QARepository(db)
        non_existent_id = uuid.uuid4()
        
        report = qa_repo.get_by_id(non_existent_id)
        
        assert report is None
    
    def test_qa_report_issues_parsing(self, db: Session):
        """Test that issues are correctly stored and retrieved"""
        # Create test project and episode
        project = ProjectModel(
            id=uuid.uuid4(),
            name="Test Project",
            source_mode="original",
            target_platform="douyin",
            status="draft",
        )
        episode = EpisodeModel(
            id=uuid.uuid4(),
            project_id=project.id,
            episode_no=1,
            target_duration_sec=60,
            status="draft",
        )
        db.add(project)
        db.add(episode)
        db.commit()
        
        # Create report with complex issues
        issues = [
            {
                "type": "character_inconsistency",
                "severity": "major",
                "location": "script.scene_1.character_A",
                "message": "Character description differs from profile",
                "suggestion": "Update character description to match profile"
            },
            {
                "type": "timeline_error",
                "severity": "minor",
                "location": "script.scene_2",
                "message": "Timeline inconsistency detected",
                "suggestion": None
            }
        ]
        
        report = QAReportModel(
            id=uuid.uuid4(),
            project_id=project.id,
            episode_id=episode.id,
            qa_type="semantic_check",
            target_ref_type="document",
            result="warning",
            severity="major",
            issue_count=len(issues),
            issues_jsonb=issues,
        )
        db.add(report)
        db.commit()
        
        # Retrieve and verify
        qa_repo = QARepository(db)
        retrieved = qa_repo.get_by_id(report.id)
        
        assert len(retrieved.issues_jsonb) == 2
        assert retrieved.issues_jsonb[0]["type"] == "character_inconsistency"
        assert retrieved.issues_jsonb[0]["severity"] == "major"
        assert retrieved.issues_jsonb[1]["suggestion"] is None
