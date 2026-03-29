# Workflow Contract — AI 漫剧创作者工作台 MVP

## 1. 总体原则

1. 项目级和剧集级 workflow 分离
2. MVP 先重点做剧集级 workflow
3. 每个 stage 都必须有稳定输入输出
4. 每个 stage 都必须可单独重跑

## 2. Workflow 类型

### `project_workflow`
用途：
项目初始化、长期状态维护

### `episode_workflow`
用途：
生成单集包，是 MVP 主 workflow

### `rerun_workflow`
用途：
从指定 stage 或指定镜头恢复

## 3. `episode_workflow` 阶段

执行顺序：
1. `brief`
2. `story_bible`
3. `character`
4. `script`
5. `storyboard`
6. `visual_spec`
7. `image_render`
8. `subtitle`
9. `tts`
10. `edit_export_preview`
11. `qa`
12. `human_review_gate`
13. `export_final`

## 4. Workflow 输入

### `EpisodeWorkflowInput`
```json
{
  "project_id": "uuid",
  "episode_id": "uuid",
  "start_stage": "brief",
  "triggered_by": "user_uuid",
  "source_refs": [],
  "options": {
    "force_regenerate": false
  }
}
```

## 5. Stage Task 通用输入

### `StageTaskInput`
```json
{
  "workflow_run_id": "uuid",
  "project_id": "uuid",
  "episode_id": "uuid",
  "stage_type": "script",
  "input_refs": [],
  "locked_refs": [],
  "constraints": {},
  "target_ref_ids": []
}
```

## 6. Stage Task 通用输出

### `StageTaskOutput`
```json
{
  "status": "succeeded",
  "document_refs": [],
  "asset_refs": [],
  "qa_refs": [],
  "warnings": [],
  "metrics": {
    "duration_ms": 0
  }
}
```

## 7. 各阶段 contract

### `brief`
输入：
1. 原始素材
2. 平台
3. 时长目标

输出：
1. `brief` document
2. 风险列表

### `story_bible`
输入：
1. brief
2. 原始素材摘要

输出：
1. `story_bible` document

### `character`
输入：
1. brief
2. story_bible

输出：
1. `character_profile` document

### `script`
输入：
1. brief
2. story_bible
3. character_profile

输出：
1. `script_draft` document

### `storyboard`
输入：
1. script_draft
2. 平台节奏模板

输出：
1. `shots`
2. `visual_spec` document

### `image_render`
输入：
1. visual_spec
2. locked character refs
3. selected shots

输出：
1. `shot_image` assets

### `subtitle`
输入：
1. script_draft
2. shots

输出：
1. `subtitle_script` document
2. `subtitle_file` asset

### `tts`
输入：
1. subtitle_script
2. character voice config

输出：
1. `audio_voice` assets

### `edit_export_preview`
输入：
1. selected shot_image assets
2. subtitle_file
3. audio_voice assets

输出：
1. `preview_video` asset

### `qa`
输入：
1. preview_video
2. selected assets
3. current documents

输出：
1. `qa_report`
2. rerun suggestion

### `human_review_gate`
输入：
1. latest qa report
2. preview_video

输出：
1. review decision

### `export_final`
输入：
1. approved preview
2. selected assets
3. publish metadata

输出：
1. final_video
2. cover_image
3. export_bundle

## 8. 失败恢复规则

1. `brief` 失败：可重试 1 到 3 次
2. `script` 失败：保留旧版本，不覆盖
3. `image_render` 失败：支持只重跑目标镜头
4. `tts` 失败：支持只重跑目标片段
5. `qa` 失败：workflow 进入 `waiting_review` 或 `needs_revision`

## 9. Human Review Gate

审批节点至少有：
1. Brief 确认
2. Storyboard 确认
3. Final QA 确认

审批动作：
1. `approved`
2. `request_changes`
3. `rejected`

## 10. Rerun Contract

### `RerunStageInput`
```json
{
  "project_id": "uuid",
  "episode_id": "uuid",
  "rerun_stage": "image_render",
  "target_ref_ids": ["shot_uuid_1"],
  "reuse_previous_assets": true,
  "triggered_by": "user_uuid"
}
```

规则：
1. 只重跑目标阶段及其必要下游
2. 已选资产默认复用
3. 非目标镜头不应被覆盖

## 11. 状态机映射

1. `brief` -> `brief_confirmed`
2. `story_bible` + `character` -> `bible_ready`
3. `script` -> `episode_writing`
4. `storyboard` -> `storyboard_ready`
5. `image_render` -> `visual_generating`
6. `tts` -> `audio_ready`
7. `edit_export_preview` -> `cut_ready`
8. `qa` -> `qa_approved` or `needs_revision`
9. `export_final` -> `published`

## 12. MVP 工程要求

1. Workflow 实现先允许部分 stage 用 mock 输出
2. Contract 先稳定，再逐步替换内部实现
3. Temporal workflow 只编排，不承载大块业务逻辑
