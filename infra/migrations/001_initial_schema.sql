CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) UNIQUE NOT NULL,
    display_name VARCHAR(120) NOT NULL,
    avatar_url TEXT,
    role VARCHAR(32) NOT NULL DEFAULT 'creator',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(200) NOT NULL,
    source_mode VARCHAR(32) NOT NULL,
    genre VARCHAR(64),
    target_platform VARCHAR(32) NOT NULL,
    target_audience VARCHAR(128),
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    brief_version INTEGER NOT NULL DEFAULT 0,
    current_episode_no INTEGER NOT NULL DEFAULT 1,
    cover_asset_id UUID,
    metadata_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_status_updated_at ON projects(status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_target_platform_genre ON projects(target_platform, genre);

CREATE TABLE IF NOT EXISTS episodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_no INTEGER NOT NULL,
    title VARCHAR(200),
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    current_stage VARCHAR(32) NOT NULL DEFAULT 'brief',
    target_duration_sec INTEGER NOT NULL,
    script_version INTEGER NOT NULL DEFAULT 0,
    storyboard_version INTEGER NOT NULL DEFAULT 0,
    visual_version INTEGER NOT NULL DEFAULT 0,
    audio_version INTEGER NOT NULL DEFAULT 0,
    export_version INTEGER NOT NULL DEFAULT 0,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_episodes_project_episode_no UNIQUE(project_id, episode_no)
);

CREATE INDEX IF NOT EXISTS idx_episodes_project_status ON episodes(project_id, status);

CREATE TABLE IF NOT EXISTS workflow_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    workflow_kind VARCHAR(32) NOT NULL,
    temporal_workflow_id VARCHAR(128) UNIQUE NOT NULL,
    temporal_run_id VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    started_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    rerun_from_stage VARCHAR(32),
    failure_reason TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_project_episode_created_at ON workflow_runs(project_id, episode_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_status_started_at ON workflow_runs(status, started_at DESC);

CREATE TABLE IF NOT EXISTS stage_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_run_id UUID NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    stage_type VARCHAR(32) NOT NULL,
    task_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    agent_name VARCHAR(64),
    worker_kind VARCHAR(32) NOT NULL,
    attempt_no INTEGER NOT NULL DEFAULT 1,
    max_retries INTEGER NOT NULL DEFAULT 3,
    input_ref_jsonb JSONB NOT NULL DEFAULT '[]'::jsonb,
    output_ref_jsonb JSONB NOT NULL DEFAULT '[]'::jsonb,
    review_required BOOLEAN NOT NULL DEFAULT FALSE,
    review_status VARCHAR(32),
    error_code VARCHAR(64),
    error_message TEXT,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stage_tasks_workflow_created_at ON stage_tasks(workflow_run_id, created_at);
CREATE INDEX IF NOT EXISTS idx_stage_tasks_project_episode_stage ON stage_tasks(project_id, episode_id, stage_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_stage_tasks_status_worker_kind ON stage_tasks(task_status, worker_kind);
