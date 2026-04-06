-- Migration 004: Add performance indexes for workspace queries
-- This migration adds specific indexes to optimize workspace aggregation queries

-- Index for documents query: get latest version by episode and type
-- Requirement 8.2: Workspace returns latest document version
CREATE INDEX IF NOT EXISTS idx_documents_episode_type_version
    ON documents(episode_id, document_type, version DESC);

-- Index for shots query: get shots ordered by scene and shot number
-- Requirement 8.3: Workspace returns complete shot list
CREATE INDEX IF NOT EXISTS idx_shots_episode_scene_shot
    ON shots(episode_id, scene_no, shot_no);

-- Index for stage_tasks query: get tasks by workflow and stage type
-- Requirement 8.4: Workspace returns workflow status with stage tasks
CREATE INDEX IF NOT EXISTS idx_stage_tasks_workflow_stage_created
    ON stage_tasks(workflow_run_id, stage_type, created_at);
