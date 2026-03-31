CREATE TABLE IF NOT EXISTS shots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    stage_task_id UUID REFERENCES stage_tasks(id) ON DELETE SET NULL,
    scene_no INTEGER NOT NULL,
    shot_no INTEGER NOT NULL,
    shot_code VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    duration_ms INTEGER NOT NULL,
    camera_size VARCHAR(32),
    camera_angle VARCHAR(32),
    movement_type VARCHAR(32),
    characters_jsonb JSONB NOT NULL DEFAULT '[]'::jsonb,
    action_text TEXT,
    dialogue_text TEXT,
    visual_constraints_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_shots_episode_version_code UNIQUE (episode_id, version, shot_code)
);

CREATE INDEX IF NOT EXISTS idx_shots_project_episode_scene_shot
    ON shots(project_id, episode_id, scene_no, shot_no);
CREATE INDEX IF NOT EXISTS idx_shots_stage_task_id
    ON shots(stage_task_id);
CREATE INDEX IF NOT EXISTS idx_shots_episode_version
    ON shots(episode_id, version DESC);

CREATE TABLE IF NOT EXISTS review_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    stage_task_id UUID NOT NULL REFERENCES stage_tasks(id) ON DELETE CASCADE,
    reviewer_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    decision VARCHAR(16) NOT NULL,
    comment_text TEXT,
    payload_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_review_decisions_project_episode_created_at
    ON review_decisions(project_id, episode_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_review_decisions_stage_task_created_at
    ON review_decisions(stage_task_id, created_at DESC);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_assets_shot_id'
    ) THEN
        ALTER TABLE assets
            ADD CONSTRAINT fk_assets_shot_id
            FOREIGN KEY (shot_id) REFERENCES shots(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_assets_shot_id_asset_type
    ON assets(shot_id, asset_type);
