"""
Unit tests for ExportBundle Repository.

Tests Requirements:
- 2.1: Create ExportBundle record
- 2.2: Save export configuration and metadata
- 2.4: Query export bundles
- 2.5: Query by Episode and Project
- 6.1: Export history query
- 6.2: Pagination and filtering
- 6.5: Delete export bundle
"""
import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.db.models import ProjectModel, EpisodeModel, ExportBundleModel
from app.repositories.export_bundle_repository import ExportBundleRepository


@pytest.fixture
def test_project(test_session: Session):
    """Create a test project."""
    project = ProjectModel(
        id=uuid.uuid4(),
        name="Test Project",
        source_mode="original",
        target_platform="mobile",
        status="draft"
    )
    test_session.add(project)
    test_session.commit()
    test_session.refresh(project)
    return project


@pytest.fixture
def test_episode(test_session: Session, test_project):
    """Create a test episode."""
    episode = EpisodeModel(
        id=uuid.uuid4(),
        project_id=test_project.id,
        episode_no=1,
        title="Test Episode",
        status="draft",
        current_stage="final_export",
        target_duration_sec=60
    )
    test_session.add(episode)
    test_session.commit()
    test_session.refresh(episode)
    return episode


@pytest.fixture
def export_bundle_repository(test_session: Session):
    """Create an export bundle repository instance."""
    return ExportBundleRepository(test_session)


def test_create_export_bundle(export_bundle_repository, test_project, test_episode):
    """Test creating an export bundle record."""
    config = {
        "resolution": [1920, 1080],
        "aspect_ratio": "16:9",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "bitrate": "6M",
        "frame_rate": 30
    }
    
    metadata = {
        "shots_count": 10,
        "assets_count": 25
    }
    
    export_bundle = export_bundle_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        template_name="bilibili",
        config_jsonb=config,
        export_version=1,
        status="pending",
        metadata_jsonb=metadata
    )
    
    assert export_bundle.id is not None
    assert export_bundle.project_id == test_project.id
    assert export_bundle.episode_id == test_episode.id
    assert export_bundle.template_name == "bilibili"
    assert export_bundle.config_jsonb == config
    assert export_bundle.export_version == 1
    assert export_bundle.status == "pending"
    assert export_bundle.metadata_jsonb == metadata


def test_get_by_id(export_bundle_repository, test_project, test_episode):
    """Test retrieving an export bundle by ID."""
    config = {"resolution": [1080, 1920], "aspect_ratio": "9:16"}
    
    created_bundle = export_bundle_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        template_name="douyin",
        config_jsonb=config
    )
    
    retrieved_bundle = export_bundle_repository.get_by_id(created_bundle.id)
    
    assert retrieved_bundle is not None
    assert retrieved_bundle.id == created_bundle.id
    assert retrieved_bundle.template_name == "douyin"
    assert retrieved_bundle.config_jsonb == config


def test_get_by_id_not_found(export_bundle_repository):
    """Test retrieving a non-existent export bundle."""
    non_existent_id = uuid.uuid4()
    result = export_bundle_repository.get_by_id(non_existent_id)
    
    assert result is None


def test_get_by_episode(export_bundle_repository, test_project, test_episode):
    """Test retrieving all export bundles for an episode."""
    # Create multiple export bundles
    for i in range(3):
        export_bundle_repository.create(
            project_id=test_project.id,
            episode_id=test_episode.id,
            template_name="bilibili",
            config_jsonb={},
            export_version=i + 1
        )
    
    bundles = export_bundle_repository.get_by_episode(test_episode.id)
    
    assert len(bundles) == 3
    # Should be ordered by created_at descending (newest first)
    assert bundles[0].export_version == 3
    assert bundles[1].export_version == 2
    assert bundles[2].export_version == 1


def test_get_by_project(export_bundle_repository, test_project, test_session):
    """Test retrieving all export bundles for a project."""
    # Create multiple episodes
    episodes = []
    for i in range(2):
        episode = EpisodeModel(
            id=uuid.uuid4(),
            project_id=test_project.id,
            episode_no=i + 1,
            title=f"Episode {i + 1}",
            status="draft",
            current_stage="final_export",
            target_duration_sec=60
        )
        test_session.add(episode)
        episodes.append(episode)
    test_session.commit()
    
    # Create export bundles for each episode
    for episode in episodes:
        export_bundle_repository.create(
            project_id=test_project.id,
            episode_id=episode.id,
            template_name="youtube",
            config_jsonb={}
        )
    
    bundles = export_bundle_repository.get_by_project(test_project.id)
    
    assert len(bundles) == 2


def test_get_history_with_filters(export_bundle_repository, test_project, test_episode):
    """Test getting export history with various filters."""
    # Create export bundles with different statuses
    statuses = ["pending", "processing", "completed", "failed"]
    for status in statuses:
        export_bundle_repository.create(
            project_id=test_project.id,
            episode_id=test_episode.id,
            template_name="bilibili",
            config_jsonb={},
            status=status
        )
    
    # Test filter by episode
    episode_bundles = export_bundle_repository.get_history(episode_id=test_episode.id)
    assert len(episode_bundles) == 4
    
    # Test filter by project
    project_bundles = export_bundle_repository.get_history(project_id=test_project.id)
    assert len(project_bundles) == 4
    
    # Test filter by status
    completed_bundles = export_bundle_repository.get_history(status="completed")
    assert len(completed_bundles) == 1
    assert completed_bundles[0].status == "completed"
    
    # Test pagination
    page1 = export_bundle_repository.get_history(limit=2, offset=0)
    assert len(page1) == 2
    
    page2 = export_bundle_repository.get_history(limit=2, offset=2)
    assert len(page2) == 2


def test_update_status_success(export_bundle_repository, test_project, test_episode):
    """Test updating export bundle status to completed."""
    bundle = export_bundle_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        template_name="bilibili",
        config_jsonb={},
        status="pending"
    )
    
    completed_at = datetime.utcnow()
    updated_bundle = export_bundle_repository.update_status(
        export_bundle_id=bundle.id,
        status="completed",
        video_storage_key="exports/video_123.mp4",
        manifest_storage_key="exports/manifest_123.json",
        bundle_size_bytes=52428800,
        video_duration_ms=60000,
        completed_at=completed_at
    )
    
    assert updated_bundle is not None
    assert updated_bundle.status == "completed"
    assert updated_bundle.video_storage_key == "exports/video_123.mp4"
    assert updated_bundle.manifest_storage_key == "exports/manifest_123.json"
    assert updated_bundle.bundle_size_bytes == 52428800
    assert updated_bundle.video_duration_ms == 60000
    assert updated_bundle.completed_at == completed_at


def test_update_status_failure(export_bundle_repository, test_project, test_episode):
    """Test updating export bundle status to failed with error details."""
    bundle = export_bundle_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        template_name="douyin",
        config_jsonb={},
        status="processing"
    )
    
    updated_bundle = export_bundle_repository.update_status(
        export_bundle_id=bundle.id,
        status="failed",
        error_code="FFMPEG_ERROR",
        error_message="FFmpeg encoding failed: invalid codec parameters"
    )
    
    assert updated_bundle is not None
    assert updated_bundle.status == "failed"
    assert updated_bundle.error_code == "FFMPEG_ERROR"
    assert updated_bundle.error_message == "FFmpeg encoding failed: invalid codec parameters"


def test_update_status_not_found(export_bundle_repository):
    """Test updating status of non-existent export bundle."""
    non_existent_id = uuid.uuid4()
    result = export_bundle_repository.update_status(
        export_bundle_id=non_existent_id,
        status="completed"
    )
    
    assert result is None


def test_delete_export_bundle(export_bundle_repository, test_project, test_episode):
    """Test deleting an export bundle."""
    bundle = export_bundle_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        template_name="youtube",
        config_jsonb={}
    )
    
    # Delete the bundle
    result = export_bundle_repository.delete(bundle.id)
    assert result is True
    
    # Verify it's deleted
    retrieved = export_bundle_repository.get_by_id(bundle.id)
    assert retrieved is None


def test_delete_not_found(export_bundle_repository):
    """Test deleting a non-existent export bundle."""
    non_existent_id = uuid.uuid4()
    result = export_bundle_repository.delete(non_existent_id)
    
    assert result is False


def test_export_version_increment(export_bundle_repository, test_project, test_episode):
    """Test creating multiple export versions for the same episode."""
    # Create version 1
    v1 = export_bundle_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        template_name="bilibili",
        config_jsonb={},
        export_version=1
    )
    
    # Create version 2
    v2 = export_bundle_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        template_name="bilibili",
        config_jsonb={},
        export_version=2
    )
    
    # Create version 3
    v3 = export_bundle_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        template_name="bilibili",
        config_jsonb={},
        export_version=3
    )
    
    bundles = export_bundle_repository.get_by_episode(test_episode.id)
    
    assert len(bundles) == 3
    # Should be ordered by created_at descending
    assert bundles[0].export_version == 3
    assert bundles[1].export_version == 2
    assert bundles[2].export_version == 1
