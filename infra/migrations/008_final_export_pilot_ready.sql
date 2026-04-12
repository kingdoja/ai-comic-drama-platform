-- Migration 008: Final Export and Pilot Ready
-- This migration adds support for Export Bundles and Trace Records
-- Requirements: 2.1, 7.1

-- ============================================================================
-- Part 1: Create export_bundles table
-- ============================================================================

CREATE TABLE export_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    stage_task_id UUID REFERENCES stage_tasks(id) ON DELETE SET NULL,
    
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
    qa_report_id UUID REFERENCES qa_reports(id) ON DELETE SET NULL,
    quality_score NUMERIC(5, 2),
    
    -- Error information
    error_code VARCHAR(64),
    error_message TEXT,
    
    -- Metadata
    metadata_jsonb JSONB NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- Part 2: Create trace_records table
-- ============================================================================

CREATE TABLE trace_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    
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

-- ============================================================================
-- Part 3: Create indexes for export_bundles
-- ============================================================================

-- Index for querying export bundles by episode
CREATE INDEX idx_export_bundles_episode ON export_bundles(episode_id, created_at DESC);

-- Index for querying export bundles by project
CREATE INDEX idx_export_bundles_project ON export_bundles(project_id, created_at DESC);

-- Index for querying export bundles by status
CREATE INDEX idx_export_bundles_status ON export_bundles(status, created_at DESC);

-- ============================================================================
-- Part 4: Create indexes for trace_records
-- ============================================================================

-- Index for querying trace records by episode
CREATE INDEX idx_trace_records_episode ON trace_records(episode_id, event_timestamp DESC);

-- Index for querying trace records by source
CREATE INDEX idx_trace_records_source ON trace_records(source_type, source_id);

-- Index for querying trace records by target
CREATE INDEX idx_trace_records_target ON trace_records(target_type, target_id);

-- Index for querying trace records by event type
CREATE INDEX idx_trace_records_event_type ON trace_records(event_type, event_timestamp DESC);

-- ============================================================================
-- Part 5: Add export tracking fields to episodes table
-- ============================================================================

-- Add last_export_at to track when the episode was last exported
ALTER TABLE episodes ADD COLUMN IF NOT EXISTS last_export_at TIMESTAMP WITH TIME ZONE;

-- Add export_count to track how many times the episode has been exported
ALTER TABLE episodes ADD COLUMN IF NOT EXISTS export_count INTEGER NOT NULL DEFAULT 0;

-- ============================================================================
-- Part 6: Add comments
-- ============================================================================

COMMENT ON TABLE export_bundles IS 'Export bundle records table, stores configuration and results for each export';
COMMENT ON TABLE trace_records IS 'Trace records table, records data flow and processing paths';

COMMENT ON COLUMN export_bundles.export_version IS 'Export version number, auto-incremented for each new export';
COMMENT ON COLUMN export_bundles.template_name IS 'Export template name (e.g., tiktok, bilibili, youtube)';
COMMENT ON COLUMN export_bundles.config_jsonb IS 'Export configuration (resolution, codec, bitrate, etc.)';
COMMENT ON COLUMN export_bundles.status IS 'Export status: pending, processing, completed, failed';
COMMENT ON COLUMN export_bundles.video_storage_key IS 'Storage key for the exported video file';
COMMENT ON COLUMN export_bundles.manifest_storage_key IS 'Storage key for the manifest.json file';
COMMENT ON COLUMN export_bundles.asset_ids_jsonb IS 'Array of asset IDs included in the export bundle';

COMMENT ON COLUMN trace_records.event_type IS 'Event type (e.g., stage_completed, asset_generated, export_created)';
COMMENT ON COLUMN trace_records.source_type IS 'Source entity type (e.g., stage_task, document, shot)';
COMMENT ON COLUMN trace_records.source_id IS 'Source entity ID';
COMMENT ON COLUMN trace_records.target_type IS 'Target entity type (e.g., document, asset, export_bundle)';
COMMENT ON COLUMN trace_records.target_id IS 'Target entity ID';

COMMENT ON COLUMN episodes.last_export_at IS 'Timestamp of the last successful export';
COMMENT ON COLUMN episodes.export_count IS 'Total number of successful exports for this episode';

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Verify the migration
DO $$
BEGIN
    -- Check if export_bundles table exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'export_bundles'
    ) THEN
        RAISE EXCEPTION 'Migration failed: export_bundles table not created';
    END IF;
    
    -- Check if trace_records table exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'trace_records'
    ) THEN
        RAISE EXCEPTION 'Migration failed: trace_records table not created';
    END IF;
    
    -- Check if episodes.last_export_at column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'episodes' AND column_name = 'last_export_at'
    ) THEN
        RAISE EXCEPTION 'Migration failed: episodes.last_export_at column not created';
    END IF;
    
    -- Check if episodes.export_count column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'episodes' AND column_name = 'export_count'
    ) THEN
        RAISE EXCEPTION 'Migration failed: episodes.export_count column not created';
    END IF;
    
    RAISE NOTICE 'Migration 008 completed successfully';
END $$;
