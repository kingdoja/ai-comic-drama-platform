-- Migration 006: QA / Review / Rerun 闭环
-- This migration adds support for QA Runtime, Review Gate, and Rerun functionality
-- Requirements: 7.1, 7.2, 8.1, 10.5, 12.1, 15.4

-- ============================================================================
-- Part 1: Extend workflow_runs table for rerun support
-- ============================================================================

-- Add parent_workflow_run_id to track rerun relationships
ALTER TABLE workflow_runs
ADD COLUMN IF NOT EXISTS parent_workflow_run_id UUID REFERENCES workflow_runs(id) ON DELETE SET NULL;

-- Add rerun_reason to record why a rerun was triggered
ALTER TABLE workflow_runs
ADD COLUMN IF NOT EXISTS rerun_reason TEXT;

-- Add rerun_shot_ids_jsonb to store which shots to rerun (for partial reruns)
ALTER TABLE workflow_runs
ADD COLUMN IF NOT EXISTS rerun_shot_ids_jsonb JSONB;

-- Add comments to document the new columns
COMMENT ON COLUMN workflow_runs.parent_workflow_run_id IS 'Reference to the parent WorkflowRun if this is a rerun';
COMMENT ON COLUMN workflow_runs.rerun_reason IS 'Reason for triggering the rerun (from review decision or manual trigger)';
COMMENT ON COLUMN workflow_runs.rerun_shot_ids_jsonb IS 'Array of shot IDs to rerun for partial/shot-level reruns';

-- ============================================================================
-- Part 2: Create performance indexes
-- ============================================================================

-- Index for QA reports: optimize queries by episode and creation time
-- Requirement 10.5: Support efficient QA report queries
CREATE INDEX IF NOT EXISTS idx_qa_reports_episode_created_at
    ON qa_reports(episode_id, created_at DESC);

-- Index for review decisions: optimize queries by stage_task and creation time
-- Requirement 12.1: Support efficient review history queries
CREATE INDEX IF NOT EXISTS idx_review_decisions_stage_task_created_at
    ON review_decisions(stage_task_id, created_at DESC);

-- Index for workflow runs: optimize rerun queries by episode and rerun_from_stage
-- Requirement 15.4: Support efficient rerun history queries
CREATE INDEX IF NOT EXISTS idx_workflow_runs_episode_rerun_from_stage
    ON workflow_runs(episode_id, rerun_from_stage)
    WHERE rerun_from_stage IS NOT NULL;

-- Index for workflow runs: optimize parent-child rerun relationship queries
CREATE INDEX IF NOT EXISTS idx_workflow_runs_parent_workflow_run_id
    ON workflow_runs(parent_workflow_run_id)
    WHERE parent_workflow_run_id IS NOT NULL;

-- ============================================================================
-- Part 3: Add GIN index for rerun_shot_ids_jsonb
-- ============================================================================

-- GIN index for efficient JSONB queries on rerun_shot_ids
CREATE INDEX IF NOT EXISTS idx_workflow_runs_rerun_shot_ids
    ON workflow_runs USING GIN(rerun_shot_ids_jsonb)
    WHERE rerun_shot_ids_jsonb IS NOT NULL;

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Verify the migration
DO $$
BEGIN
    -- Check if all columns exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'workflow_runs' AND column_name = 'parent_workflow_run_id'
    ) THEN
        RAISE EXCEPTION 'Migration failed: parent_workflow_run_id column not created';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'workflow_runs' AND column_name = 'rerun_reason'
    ) THEN
        RAISE EXCEPTION 'Migration failed: rerun_reason column not created';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'workflow_runs' AND column_name = 'rerun_shot_ids_jsonb'
    ) THEN
        RAISE EXCEPTION 'Migration failed: rerun_shot_ids_jsonb column not created';
    END IF;
    
    RAISE NOTICE 'Migration 006 completed successfully';
END $$;
