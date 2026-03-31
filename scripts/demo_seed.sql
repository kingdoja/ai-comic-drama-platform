BEGIN;

-- Fixed demo IDs for repeatable local smoke verification.
-- Project:      11111111-1111-1111-1111-111111111111
-- Episode:      22222222-2222-2222-2222-222222222222
-- WorkflowRun:  33333333-3333-3333-3333-333333333333
-- StageTasks:   44444444-4444-4444-4444-444444444441..443
-- Documents:    55555555-5555-5555-5555-555555555551..553
-- Shots:        66666666-6666-6666-6666-666666666661..663
-- Assets:       77777777-7777-7777-7777-777777777771..772
-- QAReport:     88888888-8888-8888-8888-888888888881
-- Review:       99999999-9999-9999-9999-999999999991

DELETE FROM review_decisions
WHERE id = '99999999-9999-9999-9999-999999999991'::uuid
   OR episode_id = '22222222-2222-2222-2222-222222222222'::uuid;

DELETE FROM qa_reports
WHERE id = '88888888-8888-8888-8888-888888888881'::uuid
   OR episode_id = '22222222-2222-2222-2222-222222222222'::uuid;

DELETE FROM assets
WHERE id IN (
    '77777777-7777-7777-7777-777777777771'::uuid,
    '77777777-7777-7777-7777-777777777772'::uuid
)
   OR episode_id = '22222222-2222-2222-2222-222222222222'::uuid;

DELETE FROM documents
WHERE id IN (
    '55555555-5555-5555-5555-555555555551'::uuid,
    '55555555-5555-5555-5555-555555555552'::uuid,
    '55555555-5555-5555-5555-555555555553'::uuid
)
   OR episode_id = '22222222-2222-2222-2222-222222222222'::uuid;

DELETE FROM shots
WHERE id IN (
    '66666666-6666-6666-6666-666666666661'::uuid,
    '66666666-6666-6666-6666-666666666662'::uuid,
    '66666666-6666-6666-6666-666666666663'::uuid
)
   OR episode_id = '22222222-2222-2222-2222-222222222222'::uuid;

DELETE FROM stage_tasks
WHERE id IN (
    '44444444-4444-4444-4444-444444444441'::uuid,
    '44444444-4444-4444-4444-444444444442'::uuid,
    '44444444-4444-4444-4444-444444444443'::uuid
)
   OR workflow_run_id = '33333333-3333-3333-3333-333333333333'::uuid;

DELETE FROM workflow_runs
WHERE id = '33333333-3333-3333-3333-333333333333'::uuid
   OR episode_id = '22222222-2222-2222-2222-222222222222'::uuid;

DELETE FROM episodes
WHERE id = '22222222-2222-2222-2222-222222222222'::uuid;

DELETE FROM projects
WHERE id = '11111111-1111-1111-1111-111111111111'::uuid;

INSERT INTO projects (
    id,
    owner_id,
    name,
    source_mode,
    genre,
    target_platform,
    target_audience,
    status,
    brief_version,
    current_episode_no,
    cover_asset_id,
    metadata_jsonb,
    created_at,
    updated_at
) VALUES (
    '11111111-1111-1111-1111-111111111111'::uuid,
    NULL,
    '演示项目：她不是弃女',
    'adaptation',
    '女频逆袭',
    'douyin',
    '18-30 女性向短剧用户',
    'storyboard_ready',
    1,
    1,
    NULL,
    '{"seed": "demo_seed", "mode": "iteration1"}'::jsonb,
    NOW(),
    NOW()
);

INSERT INTO episodes (
    id,
    project_id,
    episode_no,
    title,
    status,
    current_stage,
    target_duration_sec,
    script_version,
    storyboard_version,
    visual_version,
    audio_version,
    export_version,
    published_at,
    created_at,
    updated_at
) VALUES (
    '22222222-2222-2222-2222-222222222222'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    1,
    'EP01 她不是弃女',
    'storyboard_ready',
    'storyboard',
    73,
    1,
    1,
    0,
    0,
    0,
    NULL,
    NOW(),
    NOW()
);

INSERT INTO workflow_runs (
    id,
    project_id,
    episode_id,
    workflow_kind,
    temporal_workflow_id,
    temporal_run_id,
    status,
    started_by_user_id,
    rerun_from_stage,
    failure_reason,
    started_at,
    finished_at,
    created_at
) VALUES (
    '33333333-3333-3333-3333-333333333333'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    'episode',
    'demo-episode-workflow-ep01',
    'demo-run-ep01-v1',
    'waiting_review',
    NULL,
    NULL,
    NULL,
    NOW() - INTERVAL '15 minutes',
    NULL,
    NOW() - INTERVAL '15 minutes'
);

INSERT INTO stage_tasks (
    id,
    workflow_run_id,
    project_id,
    episode_id,
    stage_type,
    task_status,
    agent_name,
    worker_kind,
    attempt_no,
    max_retries,
    input_ref_jsonb,
    output_ref_jsonb,
    review_required,
    review_status,
    error_code,
    error_message,
    started_at,
    finished_at,
    created_at,
    updated_at
) VALUES
(
    '44444444-4444-4444-4444-444444444441'::uuid,
    '33333333-3333-3333-3333-333333333333'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    'brief',
    'succeeded',
    'Brief Agent',
    'agent',
    1,
    3,
    '[{"ref_type": "project", "ref_id": "11111111-1111-1111-1111-111111111111"}]'::jsonb,
    '[{"ref_type": "document", "ref_id": "55555555-5555-5555-5555-555555555551"}]'::jsonb,
    TRUE,
    'approved',
    NULL,
    NULL,
    NOW() - INTERVAL '14 minutes',
    NOW() - INTERVAL '13 minutes',
    NOW() - INTERVAL '14 minutes',
    NOW() - INTERVAL '13 minutes'
),
(
    '44444444-4444-4444-4444-444444444442'::uuid,
    '33333333-3333-3333-3333-333333333333'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    'script',
    'succeeded',
    'Script Agent',
    'agent',
    1,
    3,
    '[{"ref_type": "document", "ref_id": "55555555-5555-5555-5555-555555555551"}]'::jsonb,
    '[{"ref_type": "document", "ref_id": "55555555-5555-5555-5555-555555555552"}]'::jsonb,
    FALSE,
    NULL,
    NULL,
    NULL,
    NOW() - INTERVAL '12 minutes',
    NOW() - INTERVAL '9 minutes',
    NOW() - INTERVAL '12 minutes',
    NOW() - INTERVAL '9 minutes'
),
(
    '44444444-4444-4444-4444-444444444443'::uuid,
    '33333333-3333-3333-3333-333333333333'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    'storyboard',
    'succeeded',
    'Storyboard Agent',
    'agent',
    1,
    3,
    '[{"ref_type": "document", "ref_id": "55555555-5555-5555-5555-555555555552"}]'::jsonb,
    '[{"ref_type": "document", "ref_id": "55555555-5555-5555-5555-555555555553"}, {"ref_type": "shot", "ref_id": "66666666-6666-6666-6666-666666666661"}]'::jsonb,
    TRUE,
    'pending',
    NULL,
    NULL,
    NOW() - INTERVAL '8 minutes',
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '8 minutes',
    NOW() - INTERVAL '5 minutes'
);

INSERT INTO documents (
    id,
    project_id,
    episode_id,
    stage_task_id,
    document_type,
    version,
    status,
    title,
    content_jsonb,
    summary_text,
    created_by,
    created_at,
    updated_at
) VALUES
(
    '55555555-5555-5555-5555-555555555551'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444441'::uuid,
    'brief',
    1,
    'approved',
    'EP01 Brief',
    '{"hook": "弃女身份反转", "target_duration_sec": 73, "tone": "强情绪反转"}'::jsonb,
    '首集围绕身份误判与高强度反转展开。',
    NULL,
    NOW() - INTERVAL '13 minutes',
    NOW() - INTERVAL '13 minutes'
),
(
    '55555555-5555-5555-5555-555555555552'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444442'::uuid,
    'script_draft',
    1,
    'ready',
    'EP01 Script Draft',
    '{"beats": ["女主被当众羞辱", "家族信物反转", "反派短暂失语"]}'::jsonb,
    '三段式短剧冲突脚本，结尾留下下一集钩子。',
    NULL,
    NOW() - INTERVAL '9 minutes',
    NOW() - INTERVAL '9 minutes'
),
(
    '55555555-5555-5555-5555-555555555553'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444443'::uuid,
    'visual_spec',
    1,
    'ready',
    'EP01 Storyboard Visual Spec',
    '{"palette": "冷白+深红", "character_anchor": "红色耳坠", "camera_rule": "多用近景与压迫角度"}'::jsonb,
    '分镜已进入待审核态，视觉约束以角色一致性为核心。',
    NULL,
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '5 minutes'
);

INSERT INTO shots (
    id,
    project_id,
    episode_id,
    stage_task_id,
    scene_no,
    shot_no,
    shot_code,
    status,
    duration_ms,
    camera_size,
    camera_angle,
    movement_type,
    characters_jsonb,
    action_text,
    dialogue_text,
    visual_constraints_jsonb,
    version,
    created_at,
    updated_at
) VALUES
(
    '66666666-6666-6666-6666-666666666661'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444443'::uuid,
    1,
    1,
    'SHOT_01',
    'ready',
    6000,
    'close_up',
    'eye_level',
    'push_in',
    '["女主"]'::jsonb,
    '女主在大厅中央抬头，耳坠成为视觉锚点。',
    '你们说我是弃女？',
    '{"wardrobe": "素白长裙", "anchor": "红色耳坠", "lighting": "冷白主光"}'::jsonb,
    1,
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '5 minutes'
),
(
    '66666666-6666-6666-6666-666666666662'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444443'::uuid,
    1,
    2,
    'SHOT_02',
    'ready',
    5000,
    'medium',
    'low_angle',
    'static',
    '["反派", "女主"]'::jsonb,
    '反派向前逼近，画面压迫感增强。',
    '你配提这个身份？',
    '{"blocking": "反派前压", "background": "宗祠屏风", "emotion": "威压"}'::jsonb,
    1,
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '5 minutes'
),
(
    '66666666-6666-6666-6666-666666666663'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444443'::uuid,
    1,
    3,
    'SHOT_03',
    'warning',
    7000,
    'close_up',
    'high_angle',
    'tilt_down',
    '["女主", "长辈"]'::jsonb,
    '家族信物落入镜头，长辈神色变化。',
    '现在，还要说我是弃女吗？',
    '{"prop": "家族玉佩", "timing_risk": "停顿略长", "anchor": "耳坠+玉佩"}'::jsonb,
    1,
    NOW() - INTERVAL '5 minutes',
    NOW() - INTERVAL '5 minutes'
);

INSERT INTO assets (
    id,
    project_id,
    episode_id,
    stage_task_id,
    shot_id,
    asset_type,
    storage_key,
    mime_type,
    size_bytes,
    duration_ms,
    width,
    height,
    checksum_sha256,
    quality_score,
    is_selected,
    version,
    metadata_jsonb,
    created_at
) VALUES
(
    '77777777-7777-7777-7777-777777777771'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444443'::uuid,
    '66666666-6666-6666-6666-666666666661'::uuid,
    'shot_image',
    'demo/ep01/shot-01-selected.png',
    'image/png',
    348120,
    NULL,
    1024,
    1792,
    NULL,
    92.50,
    TRUE,
    1,
    '{"provider": "mock-image", "seed": "iteration1"}'::jsonb,
    NOW() - INTERVAL '4 minutes'
),
(
    '77777777-7777-7777-7777-777777777772'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444443'::uuid,
    NULL,
    'preview_video',
    'demo/ep01/preview-v1.mp4',
    'video/mp4',
    5242880,
    73000,
    1080,
    1920,
    NULL,
    88.10,
    TRUE,
    1,
    '{"provider": "mock-export", "status": "preview-only"}'::jsonb,
    NOW() - INTERVAL '3 minutes'
);

INSERT INTO qa_reports (
    id,
    project_id,
    episode_id,
    stage_task_id,
    qa_type,
    target_ref_type,
    target_ref_id,
    result,
    score,
    severity,
    issue_count,
    issues_jsonb,
    rerun_stage_type,
    created_at
) VALUES (
    '88888888-8888-8888-8888-888888888881'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    NULL,
    'preview_consistency',
    'episode',
    '22222222-2222-2222-2222-222222222222'::uuid,
    'warn',
    84.50,
    'medium',
    1,
    '[{"code": "SHOT_03_DURATION", "message": "第三镜头停顿略长，建议回流 storyboard 或 image_render 校正节奏。"}]'::jsonb,
    'storyboard',
    NOW() - INTERVAL '2 minutes'
);

INSERT INTO review_decisions (
    id,
    project_id,
    episode_id,
    stage_task_id,
    reviewer_user_id,
    decision,
    comment_text,
    payload_jsonb,
    created_at
) VALUES (
    '99999999-9999-9999-9999-999999999991'::uuid,
    '11111111-1111-1111-1111-111111111111'::uuid,
    '22222222-2222-2222-2222-222222222222'::uuid,
    '44444444-4444-4444-4444-444444444441'::uuid,
    NULL,
    'approved',
    'Brief 结构通过，可以进入脚本和分镜阶段。',
    '{"source": "demo_seed", "scope": "brief_gate"}'::jsonb,
    NOW() - INTERVAL '11 minutes'
);

COMMIT;
