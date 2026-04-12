#!/usr/bin/env python3
"""
Validation script for Migration 008: Final Export and Pilot Ready
"""

import re
import sys


def validate_migration_008():
    """Validate the structure and content of migration 008"""
    
    print("Validating Migration 008: Final Export and Pilot Ready")
    print("=" * 60)
    
    try:
        with open('008_final_export_pilot_ready.sql', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("✗ Migration file not found: 008_final_export_pilot_ready.sql")
        return False
    
    all_checks_passed = True
    
    # Check for required tables
    print("\n1. Checking table definitions...")
    tables = ['export_bundles', 'trace_records']
    for table in tables:
        if f'CREATE TABLE {table}' in content:
            print(f"  ✓ Table '{table}' defined")
        else:
            print(f"  ✗ Table '{table}' NOT found")
            all_checks_passed = False
    
    # Check for required columns in export_bundles
    print("\n2. Checking export_bundles columns...")
    export_bundle_columns = [
        'id', 'project_id', 'episode_id', 'stage_task_id',
        'export_version', 'template_name', 'config_jsonb',
        'status', 'video_storage_key', 'manifest_storage_key',
        'bundle_size_bytes', 'video_duration_ms', 'asset_ids_jsonb',
        'qa_report_id', 'quality_score', 'error_code', 'error_message',
        'metadata_jsonb', 'created_at', 'completed_at'
    ]
    for col in export_bundle_columns:
        # Simple check - just verify the column name appears in the file
        if col in content:
            print(f"  ✓ Column '{col}' present")
        else:
            print(f"  ✗ Column '{col}' NOT found")
            all_checks_passed = False
    
    # Check for required columns in trace_records
    print("\n3. Checking trace_records columns...")
    trace_record_columns = [
        'id', 'project_id', 'episode_id', 'event_type', 'event_timestamp',
        'source_type', 'source_id', 'target_type', 'target_id',
        'metadata_jsonb', 'created_at'
    ]
    for col in trace_record_columns:
        if col in content:
            print(f"  ✓ Column '{col}' present")
        else:
            print(f"  ✗ Column '{col}' NOT found")
            all_checks_passed = False
    
    # Check for required indexes
    print("\n4. Checking indexes...")
    indexes = [
        'idx_export_bundles_episode',
        'idx_export_bundles_project',
        'idx_export_bundles_status',
        'idx_trace_records_episode',
        'idx_trace_records_source',
        'idx_trace_records_target',
        'idx_trace_records_event_type'
    ]
    for idx in indexes:
        if f'CREATE INDEX {idx}' in content:
            print(f"  ✓ Index '{idx}' defined")
        else:
            print(f"  ✗ Index '{idx}' NOT found")
            all_checks_passed = False
    
    # Check for episodes table alterations
    print("\n5. Checking episodes table alterations...")
    if 'ALTER TABLE episodes ADD COLUMN IF NOT EXISTS last_export_at' in content:
        print("  ✓ episodes.last_export_at column added")
    else:
        print("  ✗ episodes.last_export_at NOT found")
        all_checks_passed = False
    
    if 'ALTER TABLE episodes ADD COLUMN IF NOT EXISTS export_count' in content:
        print("  ✓ episodes.export_count column added")
    else:
        print("  ✗ episodes.export_count NOT found")
        all_checks_passed = False
    
    # Check for foreign key constraints
    print("\n6. Checking foreign key constraints...")
    fk_patterns = [
        r'REFERENCES projects\(id\)',
        r'REFERENCES episodes\(id\)',
        r'REFERENCES stage_tasks\(id\)',
        r'REFERENCES qa_reports\(id\)'
    ]
    for pattern in fk_patterns:
        if re.search(pattern, content):
            print(f"  ✓ Foreign key constraint found: {pattern}")
        else:
            print(f"  ✗ Foreign key constraint NOT found: {pattern}")
            all_checks_passed = False
    
    # Check for comments
    print("\n7. Checking table and column comments...")
    if 'COMMENT ON TABLE export_bundles' in content:
        print("  ✓ export_bundles table comment added")
    else:
        print("  ✗ export_bundles table comment NOT found")
        all_checks_passed = False
    
    if 'COMMENT ON TABLE trace_records' in content:
        print("  ✓ trace_records table comment added")
    else:
        print("  ✗ trace_records table comment NOT found")
        all_checks_passed = False
    
    # Check for validation block
    print("\n8. Checking validation block...")
    if 'DO $$' in content and 'RAISE NOTICE' in content:
        print("  ✓ Validation block present")
    else:
        print("  ✗ Validation block NOT found")
        all_checks_passed = False
    
    # Check for CASCADE delete behavior
    print("\n9. Checking CASCADE delete behavior...")
    if 'ON DELETE CASCADE' in content:
        print("  ✓ CASCADE delete behavior defined")
    else:
        print("  ✗ CASCADE delete behavior NOT found")
        all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✅ Migration 008 validation PASSED!")
        print("All required tables, columns, indexes, and constraints are present.")
        return True
    else:
        print("❌ Migration 008 validation FAILED!")
        print("Some required elements are missing. Please review the errors above.")
        return False


if __name__ == '__main__':
    success = validate_migration_008()
    sys.exit(0 if success else 1)
