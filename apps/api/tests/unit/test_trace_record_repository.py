"""
Unit tests for TraceRecord Repository.

Tests Requirements:
- 7.1: Record trace events and query by episode
- 7.2: Query lineage relationships
- 7.3: Query by source and target entities
- 7.4: Support upstream, downstream, and bidirectional lineage queries
"""
import uuid
from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.db.models import ProjectModel, EpisodeModel, TraceRecordModel
from app.repositories.trace_record_repository import TraceRecordRepository


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
def trace_record_repository(test_session: Session):
    """Create a trace record repository instance."""
    return TraceRecordRepository(test_session)


def test_create_trace_record(trace_record_repository, test_project, test_episode):
    """Test creating a trace record."""
    source_id = uuid.uuid4()
    target_id = uuid.uuid4()
    metadata = {
        "stage_type": "image_render",
        "duration_ms": 5000
    }
    
    trace_record = trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=source_id,
        target_type="asset",
        target_id=target_id,
        metadata_jsonb=metadata
    )
    
    assert trace_record.id is not None
    assert trace_record.project_id == test_project.id
    assert trace_record.episode_id == test_episode.id
    assert trace_record.event_type == "asset_generation"
    assert trace_record.source_type == "shot"
    assert trace_record.source_id == source_id
    assert trace_record.target_type == "asset"
    assert trace_record.target_id == target_id
    assert trace_record.metadata_jsonb == metadata
    assert trace_record.event_timestamp is not None


def test_get_by_episode(trace_record_repository, test_project, test_episode):
    """Test retrieving all trace records for an episode."""
    # Create multiple trace records
    for i in range(5):
        source_id = uuid.uuid4()
        target_id = uuid.uuid4()
        trace_record_repository.create(
            project_id=test_project.id,
            episode_id=test_episode.id,
            event_type="stage_execution",
            source_type="document",
            source_id=source_id,
            target_type="shot",
            target_id=target_id
        )
    
    records = trace_record_repository.get_by_episode(test_episode.id)
    
    assert len(records) == 5
    # Should be ordered by event_timestamp ascending
    for i in range(len(records) - 1):
        assert records[i].event_timestamp <= records[i + 1].event_timestamp


def test_get_by_source(trace_record_repository, test_project, test_episode):
    """Test retrieving trace records by source entity."""
    source_id = uuid.uuid4()
    
    # Create multiple trace records with the same source
    for i in range(3):
        target_id = uuid.uuid4()
        trace_record_repository.create(
            project_id=test_project.id,
            episode_id=test_episode.id,
            event_type="asset_generation",
            source_type="shot",
            source_id=source_id,
            target_type="asset",
            target_id=target_id
        )
    
    # Create a record with a different source
    other_source_id = uuid.uuid4()
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=other_source_id,
        target_type="asset",
        target_id=uuid.uuid4()
    )
    
    records = trace_record_repository.get_by_source("shot", source_id)
    
    assert len(records) == 3
    for record in records:
        assert record.source_type == "shot"
        assert record.source_id == source_id


def test_get_by_target(trace_record_repository, test_project, test_episode):
    """Test retrieving trace records by target entity."""
    target_id = uuid.uuid4()
    
    # Create multiple trace records with the same target
    for i in range(3):
        source_id = uuid.uuid4()
        trace_record_repository.create(
            project_id=test_project.id,
            episode_id=test_episode.id,
            event_type="transformation",
            source_type="document",
            source_id=source_id,
            target_type="document",
            target_id=target_id
        )
    
    # Create a record with a different target
    other_target_id = uuid.uuid4()
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="transformation",
        source_type="document",
        source_id=uuid.uuid4(),
        target_type="document",
        target_id=other_target_id
    )
    
    records = trace_record_repository.get_by_target("document", target_id)
    
    assert len(records) == 3
    for record in records:
        assert record.target_type == "document"
        assert record.target_id == target_id


def test_get_lineage_backward(trace_record_repository, test_project, test_episode):
    """Test getting backward (upstream) lineage."""
    # Create a simple lineage chain: doc1 -> shot1 -> asset1
    doc_id = uuid.uuid4()
    shot_id = uuid.uuid4()
    asset_id = uuid.uuid4()
    
    # doc1 -> shot1
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="stage_execution",
        source_type="document",
        source_id=doc_id,
        target_type="shot",
        target_id=shot_id
    )
    
    # shot1 -> asset1
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=shot_id,
        target_type="asset",
        target_id=asset_id
    )
    
    # Query backward lineage from asset1
    lineage = trace_record_repository.get_lineage(
        entity_type="asset",
        entity_id=asset_id,
        direction="backward"
    )
    
    assert lineage["root"]["type"] == "asset"
    assert lineage["root"]["id"] == str(asset_id)
    assert lineage["direction"] == "backward"
    
    # Should have 3 nodes: asset1, shot1, doc1
    assert len(lineage["nodes"]) == 3
    node_types = {(node["type"], uuid.UUID(node["id"])) for node in lineage["nodes"]}
    assert ("asset", asset_id) in node_types
    assert ("shot", shot_id) in node_types
    assert ("document", doc_id) in node_types
    
    # Should have 2 edges: doc1->shot1, shot1->asset1
    assert len(lineage["edges"]) == 2


def test_get_lineage_forward(trace_record_repository, test_project, test_episode):
    """Test getting forward (downstream) lineage."""
    # Create a simple lineage chain: doc1 -> shot1 -> asset1
    doc_id = uuid.uuid4()
    shot_id = uuid.uuid4()
    asset_id = uuid.uuid4()
    
    # doc1 -> shot1
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="stage_execution",
        source_type="document",
        source_id=doc_id,
        target_type="shot",
        target_id=shot_id
    )
    
    # shot1 -> asset1
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=shot_id,
        target_type="asset",
        target_id=asset_id
    )
    
    # Query forward lineage from doc1
    lineage = trace_record_repository.get_lineage(
        entity_type="document",
        entity_id=doc_id,
        direction="forward"
    )
    
    assert lineage["root"]["type"] == "document"
    assert lineage["root"]["id"] == str(doc_id)
    assert lineage["direction"] == "forward"
    
    # Should have 3 nodes: doc1, shot1, asset1
    assert len(lineage["nodes"]) == 3
    node_types = {(node["type"], uuid.UUID(node["id"])) for node in lineage["nodes"]}
    assert ("document", doc_id) in node_types
    assert ("shot", shot_id) in node_types
    assert ("asset", asset_id) in node_types
    
    # Should have 2 edges
    assert len(lineage["edges"]) == 2


def test_get_lineage_both_directions(trace_record_repository, test_project, test_episode):
    """Test getting bidirectional lineage."""
    # Create a lineage chain: doc1 -> shot1 -> asset1 -> export1
    doc_id = uuid.uuid4()
    shot_id = uuid.uuid4()
    asset_id = uuid.uuid4()
    export_id = uuid.uuid4()
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="stage_execution",
        source_type="document",
        source_id=doc_id,
        target_type="shot",
        target_id=shot_id
    )
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=shot_id,
        target_type="asset",
        target_id=asset_id
    )
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="transformation",
        source_type="asset",
        source_id=asset_id,
        target_type="asset",
        target_id=export_id
    )
    
    # Query both directions from shot1
    lineage = trace_record_repository.get_lineage(
        entity_type="shot",
        entity_id=shot_id,
        direction="both"
    )
    
    assert lineage["root"]["type"] == "shot"
    assert lineage["root"]["id"] == str(shot_id)
    assert lineage["direction"] == "both"
    
    # Should have 4 nodes: doc1, shot1, asset1, export1
    assert len(lineage["nodes"]) == 4
    node_types = {(node["type"], uuid.UUID(node["id"])) for node in lineage["nodes"]}
    assert ("document", doc_id) in node_types
    assert ("shot", shot_id) in node_types
    assert ("asset", asset_id) in node_types
    assert ("asset", export_id) in node_types
    
    # Should have 3 edges
    assert len(lineage["edges"]) == 3


def test_get_lineage_complex_graph(trace_record_repository, test_project, test_episode):
    """Test getting lineage for a complex graph with multiple branches."""
    # Create a more complex graph:
    #       doc1
    #      /    \
    #   shot1  shot2
    #      \    /
    #      asset1
    
    doc_id = uuid.uuid4()
    shot1_id = uuid.uuid4()
    shot2_id = uuid.uuid4()
    asset_id = uuid.uuid4()
    
    # doc1 -> shot1
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="stage_execution",
        source_type="document",
        source_id=doc_id,
        target_type="shot",
        target_id=shot1_id
    )
    
    # doc1 -> shot2
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="stage_execution",
        source_type="document",
        source_id=doc_id,
        target_type="shot",
        target_id=shot2_id
    )
    
    # shot1 -> asset1
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=shot1_id,
        target_type="asset",
        target_id=asset_id
    )
    
    # shot2 -> asset1
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=shot2_id,
        target_type="asset",
        target_id=asset_id
    )
    
    # Query backward lineage from asset1
    lineage = trace_record_repository.get_lineage(
        entity_type="asset",
        entity_id=asset_id,
        direction="backward"
    )
    
    # Should have 4 nodes: asset1, shot1, shot2, doc1
    assert len(lineage["nodes"]) == 4
    node_types = {(node["type"], uuid.UUID(node["id"])) for node in lineage["nodes"]}
    assert ("asset", asset_id) in node_types
    assert ("shot", shot1_id) in node_types
    assert ("shot", shot2_id) in node_types
    assert ("document", doc_id) in node_types
    
    # Should have 4 edges
    assert len(lineage["edges"]) == 4


def test_get_lineage_prevents_cycles(trace_record_repository, test_project, test_episode):
    """Test that lineage query handles cycles gracefully."""
    # Create a cycle: doc1 -> shot1 -> asset1 -> doc1
    doc_id = uuid.uuid4()
    shot_id = uuid.uuid4()
    asset_id = uuid.uuid4()
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="stage_execution",
        source_type="document",
        source_id=doc_id,
        target_type="shot",
        target_id=shot_id
    )
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=shot_id,
        target_type="asset",
        target_id=asset_id
    )
    
    # Create a cycle back to doc1
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="transformation",
        source_type="asset",
        source_id=asset_id,
        target_type="document",
        target_id=doc_id
    )
    
    # Query should not infinite loop
    lineage = trace_record_repository.get_lineage(
        entity_type="document",
        entity_id=doc_id,
        direction="both"
    )
    
    # Should have 3 unique nodes despite the cycle
    assert len(lineage["nodes"]) == 3
    node_types = {(node["type"], uuid.UUID(node["id"])) for node in lineage["nodes"]}
    assert ("document", doc_id) in node_types
    assert ("shot", shot_id) in node_types
    assert ("asset", asset_id) in node_types


def test_get_lineage_respects_max_depth(trace_record_repository, test_project, test_episode):
    """Test that lineage query respects max_depth parameter."""
    # Create a long chain: doc1 -> shot1 -> asset1 -> asset2 -> asset3
    doc_id = uuid.uuid4()
    shot_id = uuid.uuid4()
    asset1_id = uuid.uuid4()
    asset2_id = uuid.uuid4()
    asset3_id = uuid.uuid4()
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="stage_execution",
        source_type="document",
        source_id=doc_id,
        target_type="shot",
        target_id=shot_id
    )
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=shot_id,
        target_type="asset",
        target_id=asset1_id
    )
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="transformation",
        source_type="asset",
        source_id=asset1_id,
        target_type="asset",
        target_id=asset2_id
    )
    
    trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="transformation",
        source_type="asset",
        source_id=asset2_id,
        target_type="asset",
        target_id=asset3_id
    )
    
    # Query with max_depth=2 from asset3
    lineage = trace_record_repository.get_lineage(
        entity_type="asset",
        entity_id=asset3_id,
        direction="backward",
        max_depth=2
    )
    
    # Should only traverse 2 levels: asset3 -> asset2 -> asset1
    # Should NOT reach shot1 or doc1
    assert len(lineage["nodes"]) == 3
    node_ids = {uuid.UUID(node["id"]) for node in lineage["nodes"]}
    assert asset3_id in node_ids
    assert asset2_id in node_ids
    assert asset1_id in node_ids
    assert shot_id not in node_ids
    assert doc_id not in node_ids


def test_get_lineage_empty_result(trace_record_repository, test_project, test_episode):
    """Test getting lineage for an entity with no connections."""
    isolated_id = uuid.uuid4()
    
    lineage = trace_record_repository.get_lineage(
        entity_type="asset",
        entity_id=isolated_id,
        direction="both"
    )
    
    # Should only have the root node itself
    assert len(lineage["nodes"]) == 1
    assert lineage["nodes"][0]["type"] == "asset"
    assert lineage["nodes"][0]["id"] == str(isolated_id)
    
    # Should have no edges
    assert len(lineage["edges"]) == 0


def test_trace_record_metadata(trace_record_repository, test_project, test_episode):
    """Test that metadata is properly stored and retrieved."""
    source_id = uuid.uuid4()
    target_id = uuid.uuid4()
    
    metadata = {
        "stage_type": "tts",
        "input_params": {"voice": "en-US-Neural", "speed": 1.0},
        "output_metrics": {"duration_ms": 3000, "file_size": 48000},
        "duration_ms": 5000
    }
    
    trace_record = trace_record_repository.create(
        project_id=test_project.id,
        episode_id=test_episode.id,
        event_type="asset_generation",
        source_type="shot",
        source_id=source_id,
        target_type="asset",
        target_id=target_id,
        metadata_jsonb=metadata
    )
    
    # Verify metadata is stored correctly
    assert trace_record.metadata_jsonb == metadata
    assert trace_record.metadata_jsonb["stage_type"] == "tts"
    assert trace_record.metadata_jsonb["input_params"]["voice"] == "en-US-Neural"
    assert trace_record.metadata_jsonb["output_metrics"]["duration_ms"] == 3000
