# Agent Contract — AI 漫剧创作者工作台 MVP

## 1. 目标

统一所有 agent 的输入、输出、状态和职责边界，避免每个 agent 自己发明协议。

## 2. 通用 Agent 输入

```json
{
  "task_id": "uuid",
  "project_id": "uuid",
  "episode_id": "uuid",
  "stage_type": "script",
  "input_refs": [],
  "locked_refs": [],
  "constraints": {},
  "target_ref_ids": []
}
```

## 3. 通用 Agent 输出

```json
{
  "status": "succeeded",
  "document_refs": [],
  "asset_refs": [],
  "warnings": [],
  "quality_notes": [],
  "metrics": {
    "duration_ms": 0,
    "token_usage": 0
  }
}
```

## 4. 通用内部流程

1. Loader
2. Normalizer
3. Planner
4. Generator
5. Critic
6. Validator
7. Committer

## 5. MVP Agent 列表

1. Brief Agent
2. Story Bible Agent
3. Character Agent
4. Script Agent
5. Storyboard Agent
6. Subtitle Agent
7. QA Agent

## 6. 各 Agent 责任

### Brief Agent
输入：原始素材、平台、时长目标
输出：brief 文档

### Story Bible Agent
输入：brief、素材摘要
输出：story_bible 文档

### Character Agent
输入：brief、story_bible
输出：character_profile 文档

### Script Agent
输入：brief、story_bible、character_profile
输出：script_draft 文档

### Storyboard Agent
输入：script_draft
输出：shots、visual_spec 文档

### Subtitle Agent
输入：script_draft、shots
输出：subtitle_script 文档

### QA Agent
输入：preview_video、documents、assets
输出：qa_report

## 7. 约束

1. agent 不直接推进状态机
2. agent 不直接决定审批结果
3. agent 输出必须结构化
4. agent 失败必须返回可观测错误
