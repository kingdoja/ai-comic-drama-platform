# API Contract — AI 漫剧创作者工作台 MVP

## 1. API 风格

1. REST first
2. JSON request / response
3. 长任务由 API 触发 workflow，不直接同步执行
4. 所有关键对象返回稳定 `id` 和 `status`

## 2. 通用响应结构

### 成功响应
```json
{
  "data": {},
  "meta": {
    "request_id": "uuid"
  }
}
```

### 失败响应
```json
{
  "error": {
    "code": "string_code",
    "message": "human readable message",
    "details": {}
  },
  "meta": {
    "request_id": "uuid"
  }
}
```

## 3. 核心资源

1. `projects`
2. `episodes`
3. `documents`
4. `shots`
5. `assets`
6. `workflow-runs`
7. `stage-tasks`
8. `qa-reports`
9. `reviews`

## 4. 项目接口

### `POST /api/projects`
创建项目

### `GET /api/projects`
获取项目列表

### `GET /api/projects/:projectId`
获取项目详情

## 5. 剧集接口

### `POST /api/projects/:projectId/episodes`
创建剧集

### `GET /api/projects/:projectId/episodes/:episodeId`
获取剧集详情

### `GET /api/projects/:projectId/episodes/:episodeId/workspace`
获取工作台聚合数据

返回应包含：
1. project
2. episode
3. current documents
4. current shots
5. current assets
6. qa summary
7. latest workflow state

## 6. 文档接口

### `GET /api/projects/:projectId/episodes/:episodeId/documents`
按类型列出文档

### `PATCH /api/documents/:documentId`
编辑文档

### `POST /api/documents/:documentId/lock`
锁定关键字段

## 7. 分镜接口

### `GET /api/projects/:projectId/episodes/:episodeId/shots`
获取镜头列表

### `PATCH /api/shots/:shotId`
编辑单镜头

### `POST /api/shots/:shotId/lock`
锁定镜头

## 8. 工作流接口

### `POST /api/projects/:projectId/episodes/:episodeId/workflow/start`
启动单集 workflow

### `GET /api/projects/:projectId/episodes/:episodeId/workflow`
查询当前 workflow 状态

### `POST /api/projects/:projectId/episodes/:episodeId/workflow/rerun`
局部重跑

### `POST /api/workflow-runs/:workflowRunId/resume`
人工审核后恢复 workflow

## 9. 资产接口

### `GET /api/projects/:projectId/episodes/:episodeId/assets`
获取资产列表

### `POST /api/assets/:assetId/select`
将候选资产设为主资产

## 10. QA 接口

### `GET /api/projects/:projectId/episodes/:episodeId/qa-reports`
获取 QA 报告

### `POST /api/projects/:projectId/episodes/:episodeId/qa/run`
手动重跑 QA

## 11. 审核接口

### `POST /api/stage-tasks/:stageTaskId/reviews`
审核通过 / 打回

## 12. 导出接口

### `POST /api/projects/:projectId/episodes/:episodeId/export`
触发导出正式单集包

### `GET /api/projects/:projectId/episodes/:episodeId/export`
查询导出结果

## 13. DTO 首批清单

1. `CreateProjectRequest`
2. `CreateEpisodeRequest`
3. `StartEpisodeWorkflowRequest`
4. `RerunStageRequest`
5. `CreateReviewDecisionRequest`
6. `ProjectDetailResponse`
7. `EpisodeWorkspaceResponse`
8. `WorkflowRunResponse`
9. `QAReportResponse`
10. `AssetListResponse`

## 14. 约束

1. API 不直接调用长耗时 agent 任务
2. 所有 workflow 入口都返回可轮询对象
3. 所有编辑动作都要记录版本来源
