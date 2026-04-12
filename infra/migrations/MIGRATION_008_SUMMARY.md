# Migration 008: Final Export and Pilot Ready - Summary

## Overview

Migration 008 adds database support for the Final Export and Pilot Ready iteration. This migration creates the foundational tables for export bundles and trace records that enable the system to transition from "preview generation" to "production delivery".

## What's New

### 1. Export Bundles Table (`export_bundles`)

A new table to track all export operations and their results:

**Key Features:**
- Records export configuration (template, resolution, codec, etc.)
- Tracks export status and results
- Stores references to exported video and manifest files
- Links to QA reports for quality validation
- Maintains asset manifest for each export
- Supports versioning for multiple exports of the same episode

**Use Cases:**
- Track export history for each episode
- Query export status and download links
- Manage multiple export versions
- Validate export quality

### 2. Trace Records Table (`trace_records`)

A new table to record data lineage and processing flow:

**Key Features:**
- Records events throughout the workflow
- Tracks source-to-target relationships
- Enables lineage queries (upstream/downstream dependencies)
- Supports debugging and auditing

**Use Cases:**
- Trace data flow from Brief to Final Export
- Query asset lineage (where did this asset come from?)
- Debug workflow issues
- Audit data processing

### 3. Episode Export Tracking

New fields added to the `episodes` table:

- `last_export_at`: Timestamp of the last successful export
- `export_count`: Total number of successful exports

**Use Cases:**
- Display export status in UI
- Track export frequency
- Identify episodes that need re-export

## Database Schema

### export_bundles Table

```sql
CREATE TABLE export_bundles (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL,
    episode_id UUID NOT NULL,
    stage_task_id UUID,
    
    -- Export configuration
    export_version INTEGER NOT NULL DEFAULT 1,
    template_name VARCHAR(64) NOT NULL,
    config_jsonb JSONB NOT NULL DEFAULT '{}',
    
    -- Export results
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    video_storage_key TEXT,
    manifest_storage_key TEXT,
    bundle_size_bytes BIGINT NOT NULL DEFAULT 0,
    video_duration_ms INTEGER,
    
    -- Asset manifest
    asset_ids_jsonb JSONB NOT NULL DEFAULT '[]',
    
    -- Quality information
    qa_report_id UUID,
    quality_score NUMERIC(5, 2),
    
    -- Error information
    error_code VARCHAR(64),
    error_message TEXT,
    
    -- Metadata
    metadata_jsonb JSONB NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);
```

### trace_records Table

```sql
CREATE TABLE trace_records (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL,
    episode_id UUID NOT NULL,
    
    -- Event information
    event_type VARCHAR(64) NOT NULL,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Source and target
    source_type VARCHAR(32) NOT NULL,
    source_id UUID NOT NULL,
    target_type VARCHAR(32) NOT NULL,
    target_id UUID NOT NULL,
    
    -- Metadata
    metadata_jsonb JSONB NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

## Indexes

### Export Bundles Indexes

1. `idx_export_bundles_episode` - Query exports by episode
2. `idx_export_bundles_project` - Query exports by project
3. `idx_export_bundles_status` - Query exports by status

### Trace Records Indexes

1. `idx_trace_records_episode` - Query traces by episode
2. `idx_trace_records_source` - Query traces by source entity
3. `idx_trace_records_target` - Query traces by target entity
4. `idx_trace_records_event_type` - Query traces by event type

## Requirements Implemented

This migration implements the following requirements from the Final Export and Pilot Ready iteration:

- **Requirement 2.1**: ExportBundle data model
- **Requirement 7.1**: Trace and Lineage tracking

## Migration Safety

This migration is **safe to run** because:

1. ✅ Creates new tables (no data loss risk)
2. ✅ Uses `IF NOT EXISTS` for ALTER TABLE statements
3. ✅ All foreign keys use appropriate CASCADE/SET NULL behavior
4. ✅ Includes validation block to verify successful execution
5. ✅ No modifications to existing data

## How to Apply

### Option 1: Using Python Script

```bash
cd infra/migrations
python apply_migrations.py
```

### Option 2: Using psql

```bash
psql -U your_user -d your_database -f infra/migrations/008_final_export_pilot_ready.sql
```

### Option 3: Using Database Client

Copy and paste the SQL from `008_final_export_pilot_ready.sql` into your database client and execute.

## Validation

After applying the migration, verify it was successful:

```bash
cd infra/migrations
python validate_008_migration.py
```

Expected output:
```
✅ Migration 008 validation PASSED!
All required tables, columns, indexes, and constraints are present.
```

## Rollback

If you need to rollback this migration:

```sql
-- Drop new tables
DROP TABLE IF EXISTS trace_records CASCADE;
DROP TABLE IF EXISTS export_bundles CASCADE;

-- Remove new columns from episodes
ALTER TABLE episodes DROP COLUMN IF EXISTS last_export_at;
ALTER TABLE episodes DROP COLUMN IF EXISTS export_count;
```

**⚠️ Warning**: Rollback will delete all export bundle and trace record data!

## Next Steps

After applying this migration:

1. ✅ Update `app/db/models.py` to add `ExportBundleModel` and `TraceRecordModel`
2. ✅ Create `ExportBundleRepository` and `TraceRecordRepository`
3. ✅ Implement `ExportService` and `TraceService`
4. ✅ Implement Final Export Stage
5. ✅ Add Export API endpoints

## Related Files

- Migration file: `infra/migrations/008_final_export_pilot_ready.sql`
- Validation script: `infra/migrations/validate_008_migration.py`
- Requirements: `.kiro/specs/final-export-pilot-ready/requirements.md`
- Design: `.kiro/specs/final-export-pilot-ready/design.md`
- Tasks: `.kiro/specs/final-export-pilot-ready/tasks.md`

## Questions?

If you encounter any issues with this migration, please:

1. Check the validation output
2. Review the migration file for syntax errors
3. Verify database permissions
4. Check database logs for detailed error messages
