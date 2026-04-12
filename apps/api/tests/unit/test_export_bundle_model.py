"""
Unit tests for ExportBundleModel.

Tests verify that the ExportBundleModel is correctly defined with all required fields,
proper types, and foreign key relationships.
"""
import uuid
from datetime import datetime

import pytest
from sqlalchemy import inspect

from app.db.models import ExportBundleModel


def test_export_bundle_model_has_all_required_fields():
    """Verify ExportBundleModel has all required fields from requirements 2.1, 2.2, 2.3, 2.4."""
    mapper = inspect(ExportBundleModel)
    column_names = {col.key for col in mapper.columns}
    
    required_fields = {
        'id', 'project_id', 'episode_id', 'stage_task_id',
        'export_version', 'template_name', 'config_jsonb',
        'status', 'video_storage_key', 'manifest_storage_key',
        'bundle_size_bytes', 'video_duration_ms',
        'asset_ids_jsonb',
        'qa_report_id', 'quality_score',
        'error_code', 'error_message',
        'metadata_jsonb',
        'created_at', 'completed_at'
    }
    
    assert required_fields.issubset(column_names), f"Missing fields: {required_fields - column_names}"


def test_export_bundle_model_table_name():
    """Verify table name is correct."""
    assert ExportBundleModel.__tablename__ == "export_bundles"


def test_export_bundle_model_has_table_comment():
    """Verify table has a comment."""
    assert ExportBundleModel.__table_args__ is not None
    assert "comment" in ExportBundleModel.__table_args__


def test_export_bundle_model_foreign_keys():
    """Verify foreign key relationships are correctly defined."""
    mapper = inspect(ExportBundleModel)
    foreign_keys = {fk.parent.name: fk.column.table.name for fk in mapper.tables[0].foreign_keys}
    
    assert 'project_id' in foreign_keys
    assert foreign_keys['project_id'] == 'projects'
    
    assert 'episode_id' in foreign_keys
    assert foreign_keys['episode_id'] == 'episodes'
    
    assert 'stage_task_id' in foreign_keys
    assert foreign_keys['stage_task_id'] == 'stage_tasks'
    
    assert 'qa_report_id' in foreign_keys
    assert foreign_keys['qa_report_id'] == 'qa_reports'


def test_export_bundle_model_instantiation():
    """Verify model can be instantiated with required fields."""
    project_id = uuid.uuid4()
    episode_id = uuid.uuid4()
    
    bundle = ExportBundleModel(
        project_id=project_id,
        episode_id=episode_id,
        template_name="douyin",
        export_version=1,
        status="pending"
    )
    
    assert bundle.project_id == project_id
    assert bundle.episode_id == episode_id
    assert bundle.template_name == "douyin"
    assert bundle.export_version == 1
    assert bundle.status == "pending"
    assert bundle.config_jsonb == {}
    assert bundle.asset_ids_jsonb == []
    assert bundle.metadata_jsonb == {}
    assert bundle.bundle_size_bytes == 0


def test_export_bundle_model_optional_fields():
    """Verify optional fields can be None."""
    bundle = ExportBundleModel(
        project_id=uuid.uuid4(),
        episode_id=uuid.uuid4(),
        template_name="bilibili"
    )
    
    assert bundle.stage_task_id is None
    assert bundle.video_storage_key is None
    assert bundle.manifest_storage_key is None
    assert bundle.video_duration_ms is None
    assert bundle.qa_report_id is None
    assert bundle.quality_score is None
    assert bundle.error_code is None
    assert bundle.error_message is None
    assert bundle.completed_at is None
