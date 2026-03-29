CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID REFERENCES episodes(id) ON DELETE CASCADE,
    stage_task_id UUID REFERENCES stage_tasks(id) ON DELETE SET NULL,
    document_type VARCHAR(32) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    title VARCHAR(200),
    content_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb,
    summary_text TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_project_episode_type_version ON documents(project_id, episode_id, document_type, version DESC);
CREATE INDEX IF NOT EXISTS idx_documents_stage_task_id ON documents(stage_task_id);
CREATE INDEX IF NOT EXISTS idx_documents_content_jsonb ON documents USING GIN(content_jsonb);

CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID REFERENCES episodes(id) ON DELETE CASCADE,
    stage_task_id UUID REFERENCES stage_tasks(id) ON DELETE SET NULL,
    shot_id UUID,
    asset_type VARCHAR(32) NOT NULL,
    storage_key TEXT NOT NULL,
    mime_type VARCHAR(120) NOT NULL,
    size_bytes BIGINT NOT NULL DEFAULT 0,
    duration_ms INTEGER,
    width INTEGER,
    height INTEGER,
    checksum_sha256 CHAR(64),
    quality_score NUMERIC(5,2),
    is_selected BOOLEAN NOT NULL DEFAULT FALSE,
    version INTEGER NOT NULL DEFAULT 1,
    metadata_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assets_project_episode_type_created_at ON assets(project_id, episode_id, asset_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assets_stage_task_id ON assets(stage_task_id);

CREATE TABLE IF NOT EXISTS qa_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    stage_task_id UUID REFERENCES stage_tasks(id) ON DELETE SET NULL,
    qa_type VARCHAR(32) NOT NULL,
    target_ref_type VARCHAR(32) NOT NULL,
    target_ref_id UUID,
    result VARCHAR(16) NOT NULL,
    score NUMERIC(5,2),
    severity VARCHAR(16) NOT NULL,
    issue_count INTEGER NOT NULL DEFAULT 0,
    issues_jsonb JSONB NOT NULL DEFAULT '[]'::jsonb,
    rerun_stage_type VARCHAR(32),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_qa_reports_project_episode_type_created_at ON qa_reports(project_id, episode_id, qa_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_qa_reports_result_severity ON qa_reports(result, severity);
