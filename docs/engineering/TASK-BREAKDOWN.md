# TASK BREAKDOWN

状态：Draft  
日期：2026-03-30  
适用范围：Iteration 1 - 核心对象与真实 Workspace 骨架

## 1. 文档目的

这份文档把 [DELIVERY-PLAN.md](/d:/ai应用项目/thinking/docs/engineering/DELIVERY-PLAN.md) 中的 `Iteration 1` 再压成一份可以直接开工的开发拆解。

它重点回答五个问题：

1. 这一轮到底先做哪几个开发包
2. 每个开发包具体改哪些文件
3. 哪些任务必须串行，哪些可以并行
4. 每个任务完成后怎么验收
5. 建议如何切 PR，避免一口气改太大

这份文档只覆盖 `Iteration 1`，不提前展开 `Iteration 2` 的文本主链路实现。

---

## 2. Iteration 1 冻结目标

本轮只追求五个结果：

1. `StageTask` 在 ORM / repository / API 聚合中真正存在
2. `Shot` 在数据库、ORM、API、前端中真正存在
3. `ReviewDecision` 在数据库、ORM、API 聚合中真正存在
4. workspace 接口不再返回硬编码 shot 数据
5. 前端能看到真实 workflow / stage / shot / review 基础状态

本轮明确不做：

1. 复杂 provider 接入
2. 完整 agent 执行逻辑
3. image / subtitle / tts / preview 正式链路
4. review 提交流程闭环
5. rerun 真正执行

---

## 3. 当前基线与真实缺口

基于当前代码与文档，Iteration 1 的真实缺口不是“想法不清楚”，而是“系统事实层还没有打通”。

### 3.1 当前已具备

1. `Project`、`Episode`、`WorkflowRun`、`Document`、`Asset`、`QAReport` 基础 ORM
2. 项目 / 剧集 / workflow / workspace API 路由
3. `DatabaseStore.build_workspace()` 的聚合入口
4. `infra/migrations/001_initial_schema.sql` 与 `002_documents_assets_qa.sql` 基础 SQL

### 3.2 当前真实问题

1. [`models.py`](/d:/ai应用项目/thinking/apps/api/app/db/models.py) 缺少 `StageTaskModel`
2. `infra/migrations/001_initial_schema.sql` 已有 `stage_tasks` 表，但 Python ORM 尚未对齐
3. 当前没有 `shots` 表、`review_decisions` 表
4. 当前没有 `ShotRepository`、`StageTaskRepository`、`ReviewDecisionRepository`
5. [`store.py`](/d:/ai应用项目/thinking/apps/api/app/services/store.py) 的 `shots` 仍是硬编码数组
6. [`workspace.py`](/d:/ai应用项目/thinking/apps/api/app/schemas/workspace.py) 的 `shots` 结构过薄，无法承载真实工作台
7. [`page.tsx`](/d:/ai应用项目/thinking/apps/web/app/page.tsx) 的 shot 卡片也是硬编码
8. workflow 创建目前只生成 `WorkflowRun`，不会生成任何 `StageTask`

### 3.3 Iteration 1 的核心判断

本轮不是先做更多页面，而是先让下面这条链路成立：

```text
SQL schema
  -> ORM model
  -> repository
  -> store aggregation
  -> workspace response
  -> frontend rendering
```

只要这条链路打通，当前 Demo 就会从“静态壳子”升级成“真实业务骨架”。

---

## 4. 本轮开发原则

### 4.1 SQL-First，对齐现有迁移风格

仓库已经使用 `infra/migrations/*.sql` 维护 schema，因此 Iteration 1 继续采用 SQL migration 方式，不临时引入 Alembic。

### 4.2 先补事实对象，再补交互

先补 `StageTask`、`Shot`、`ReviewDecision`，再改 workspace 聚合，最后再接前端。

### 4.3 Mock 可以存在，但必须真实入库

即便当前 workflow 还是 mock，也必须能：

1. 生成真实 `WorkflowRun`
2. 生成真实 `StageTask`
3. 写入真实 `Shot`
4. 被 workspace 真查询出来

### 4.4 首页不强行承担工作台职责

建议保留 [`page.tsx`](/d:/ai应用项目/thinking/apps/web/app/page.tsx) 为产品壳页，同时新增最小 workspace 页面，而不是把营销壳页硬改成真实工作台。

---

## 5. 推荐 PR 切分

建议不要把 Iteration 1 一次性做成一个大 PR，而是切成 5 个连续 PR。

| PR | 名称 | 目标 | 依赖 |
|---|---|---|---|
| PR-1 | Data Contract Alignment | 补齐 `StageTask` ORM，新增 `Shot` / `ReviewDecision` SQL 与 ORM | 无 |
| PR-2 | Repository + Schema Layer | 补齐 repository 与 workspace DTO | PR-1 |
| PR-3 | Workflow Persistence Skeleton | 让 workflow 创建时写入 `StageTask`，提供 shot 持久化入口 | PR-2 |
| PR-4 | Real Workspace Aggregation | workspace 聚合改成查询真实 `shots` / `stage_tasks` / `reviews` | PR-3 |
| PR-5 | Web Workspace Integration | 前端接真实 workspace API 并展示真实状态 | PR-4 |

---

## 6. 任务总览

### 6.1 串行主线

```text
TB-01 契约冻结
  -> TB-02 SQL 与 ORM 对齐
  -> TB-03 Repository 补齐
  -> TB-04 Workspace DTO 扩展
  -> TB-05 Workflow 持久化骨架
  -> TB-06 Workspace 聚合改造
  -> TB-07 前端接入真实数据
  -> TB-08 验收与演示数据
```

### 6.2 可并行部分

在 `TB-04` 完成后，可并行：

1. `TB-05 Workflow 持久化骨架`
2. `TB-07 前端接入真实数据`

但前端最终联调仍要等 `TB-06` 完成。

---

## 7. 详细任务拆解

## TB-01：冻结 Iteration 1 的最小契约

### 目标

在写代码前，冻结本轮最小对象字段和 workspace 最小返回结构，避免边改边漂移。

### 产出

1. `StageTaskSummaryResponse`
2. `ShotSummaryResponse` 扩展字段
3. `ReviewDecisionSummaryResponse`
4. workspace 最小返回结构说明

### 需要冻结的字段

#### StageTaskSummaryResponse

建议至少包含：

1. `id`
2. `stage_type`
3. `task_status`
4. `worker_kind`
5. `review_required`
6. `review_status`
7. `started_at`
8. `finished_at`
9. `error_message`

#### ShotSummaryResponse

建议从当前 3 个字段扩成至少：

1. `id`
2. `code`
3. `shot_index`
4. `title`
5. `duration_ms`
6. `status`
7. `stage_task_id`
8. `updated_at`

#### ReviewDecisionSummaryResponse

建议至少包含：

1. `id`
2. `status`
3. `decision_note`
4. `stage_task_id`
5. `created_at`

### 涉及文件

1. [workspace.py](/d:/ai应用项目/thinking/apps/api/app/schemas/workspace.py)
2. [SYSTEM-BLUEPRINT.md](/d:/ai应用项目/thinking/docs/engineering/SYSTEM-BLUEPRINT.md)
3. [DELIVERY-PLAN.md](/d:/ai应用项目/thinking/docs/engineering/DELIVERY-PLAN.md)

### 验收标准

1. 后续开发不再讨论 shot summary 到底有哪些字段
2. workspace 返回结构在本轮内保持稳定

---

## TB-02：补齐 SQL 与 ORM 数据对象

### 目标

让数据库 schema 与 ORM 真正承载 Iteration 1 的核心对象。

### 关键判断

`stage_tasks` 已经存在于 SQL migration 中，因此这里不是重新设计，而是补 ORM 对齐。  
`shots` 与 `review_decisions` 需要新 migration。

### 具体开发动作

1. 在 [`models.py`](/d:/ai应用项目/thinking/apps/api/app/db/models.py) 中新增 `StageTaskModel`
2. 在 [`models.py`](/d:/ai应用项目/thinking/apps/api/app/db/models.py) 中新增 `ShotModel`
3. 在 [`models.py`](/d:/ai应用项目/thinking/apps/api/app/db/models.py) 中新增 `ReviewDecisionModel`
4. 创建新 migration：`infra/migrations/003_iteration1_shots_reviews.sql`
5. 视需要为 `assets.shot_id` 增加到 `shots.id` 的外键约束

### 推荐最小字段

#### StageTaskModel

直接对齐现有 `001_initial_schema.sql`：

1. `id`
2. `workflow_run_id`
3. `project_id`
4. `episode_id`
5. `stage_type`
6. `task_status`
7. `agent_name`
8. `worker_kind`
9. `attempt_no`
10. `max_retries`
11. `input_ref_jsonb`
12. `output_ref_jsonb`
13. `review_required`
14. `review_status`
15. `error_code`
16. `error_message`
17. `started_at`
18. `finished_at`
19. `created_at`
20. `updated_at`

#### ShotModel

建议最小字段：

1. `id`
2. `project_id`
3. `episode_id`
4. `stage_task_id`
5. `code`
6. `shot_index`
7. `title`
8. `duration_ms`
9. `status`
10. `metadata_jsonb`
11. `created_at`
12. `updated_at`

#### ReviewDecisionModel

建议最小字段：

1. `id`
2. `project_id`
3. `episode_id`
4. `workflow_run_id`
5. `stage_task_id`
6. `status`
7. `decision_note`
8. `created_by`
9. `created_at`

### 推荐新增文件

1. [models.py](/d:/ai应用项目/thinking/apps/api/app/db/models.py)
2. `d:\ai应用项目\thinking\infra\migrations\003_iteration1_shots_reviews.sql`

### 验收标准

1. ORM 能完整表达 `stage_tasks`
2. 新 migration 能创建 `shots` 与 `review_decisions`
3. `Base.metadata` 与 SQL schema 不再出现 Iteration 1 级别的明显错位

---

## TB-03：补齐 Repository 层

### 目标

让 store/service 不再直接拼 SQLAlchemy 细节，而是通过 repository 操作 `StageTask`、`Shot`、`ReviewDecision`。

### 具体开发动作

1. 新增 `stage_task_repository.py`
2. 新增 `shot_repository.py`
3. 新增 `review_repository.py`
4. 在 [`store.py`](/d:/ai应用项目/thinking/apps/api/app/services/store.py) 中注入新 repository

### 每个 repository 至少要有的方法

#### StageTaskRepository

1. `create(...)`
2. `list_for_workflow(workflow_run_id)`
3. `list_for_episode(episode_id)`
4. `latest_by_stage(episode_id, stage_type)`
5. `update_status(task_id, ...)`

#### ShotRepository

1. `create_many(...)`
2. `list_for_episode(episode_id)`
3. `list_for_stage_task(stage_task_id)`
4. `delete_for_stage_task(stage_task_id)` 或软删除等价能力

#### ReviewDecisionRepository

1. `create(...)`
2. `list_for_episode(episode_id)`
3. `latest_pending_for_episode(episode_id)`

### 涉及文件

1. `d:\ai应用项目\thinking\apps\api\app\repositories\stage_task_repository.py`
2. `d:\ai应用项目\thinking\apps\api\app\repositories\shot_repository.py`
3. `d:\ai应用项目\thinking\apps\api\app\repositories\review_repository.py`
4. [store.py](/d:/ai应用项目/thinking/apps/api/app/services/store.py)

### 验收标准

1. store 层不再通过临时硬编码处理 `Shot`
2. workflow 层具备最小的持久化调用入口

---

## TB-04：扩展 Workspace DTO 与返回契约

### 目标

让 workspace 响应结构足够承载真实工作台，但又不过度超前设计。

### 具体开发动作

1. 在 [`workspace.py`](/d:/ai应用项目/thinking/apps/api/app/schemas/workspace.py) 中新增 `StageTaskSummaryResponse`
2. 在 [`workspace.py`](/d:/ai应用项目/thinking/apps/api/app/schemas/workspace.py) 中新增 `ReviewDecisionSummaryResponse`
3. 扩展 `ShotSummaryResponse`
4. 为 `EpisodeWorkspaceResponse` 增加：
   - `stage_tasks`
   - `review_summary` 或 `pending_reviews`

### 推荐返回结构

```text
EpisodeWorkspaceResponse
  - project
  - episode
  - documents
  - stage_tasks
  - shots
  - assets
  - qa_summary
  - review_summary
  - latest_workflow
  - generated_at
  - metadata
```

### 设计要求

1. DTO 名称和字段语义要直接面向前端消费
2. 不把底层 ORM 字段原封不动暴露到 API
3. review 先做 summary，不急着做完整 decision history 页面

### 涉及文件

1. [workspace.py](/d:/ai应用项目/thinking/apps/api/app/schemas/workspace.py)

### 验收标准

1. 前端不用猜测 stage status 应该从哪里拿
2. workspace 响应足够支撑真实 shot 列表和 stage 状态区

---

## TB-05：落 Workflow 持久化骨架

### 目标

让 workflow 创建时不只生成 `WorkflowRun`，还要能落最小 `StageTask` 记录，并为后续 storyboard 持久化 shots 留好入口。

### 具体开发动作

1. 扩展 [`workflow_repository.py`](/d:/ai应用项目/thinking/apps/api/app/repositories/workflow_repository.py)
2. 在 `store.start_workflow(...)` 中补最小 stage task 创建逻辑
3. 约定启动 workflow 时至少创建一个当前 stage 的 `StageTask`
4. 增加一个 mock 的 shot 写入入口，供后续 storyboard stage 使用

### 推荐实现方式

最小方案，不引入真正 workflow 引擎：

1. `POST /workflow/start` 创建 `WorkflowRun`
2. 同时创建首个 `StageTask`
3. `StageTask.task_status` 初始值设为 `pending` 或 `running`
4. `metadata` 中记录 `mode=mock-persistence`

### 可选补位

如果实现成本可控，建议增加一个独立服务：

1. `app/services/workflow_service.py`

作用：

1. 统一 workflow 创建
2. 统一 stage task 初始化
3. 避免 route/store/repository 职责继续混杂

### 涉及文件

1. [workflow_repository.py](/d:/ai应用项目/thinking/apps/api/app/repositories/workflow_repository.py)
2. [store.py](/d:/ai应用项目/thinking/apps/api/app/services/store.py)
3. 可选：`d:\ai应用项目\thinking\apps\api\app\services\workflow_service.py`

### 验收标准

1. 启动 workflow 后，数据库里能看到 `WorkflowRun`
2. 启动 workflow 后，数据库里能看到至少一个对应 `StageTask`
3. workspace 能查询到 stage task 状态

---

## TB-06：重构 Workspace 聚合逻辑

### 目标

把 [`store.py`](/d:/ai应用项目/thinking/apps/api/app/services/store.py) 的 workspace 聚合从“假数据拼接”改成“真实对象聚合”。

### 当前必须替换的假数据

当前这段硬编码必须移除：

1. `SHOT_01`
2. `SHOT_02`
3. `SHOT_03`

### 具体开发动作

1. 从 repository 读取真实 `shots`
2. 从 repository 读取当前 episode 的 `stage_tasks`
3. 从 repository 读取当前 episode 的 `review_decisions`
4. 聚合 selected assets
5. 构造新的 `EpisodeWorkspaceResponse`

### 推荐聚合规则

#### stage_tasks

1. 默认返回当前 episode 最近一次 `WorkflowRun` 关联的 stage tasks
2. 按创建时间升序或阶段顺序返回

#### shots

1. 返回当前 episode 最新 storyboard 对应的 shots
2. 在 Iteration 1 不做复杂版本比较
3. 先按 `shot_index` 升序返回

#### review_summary

1. 没有 review 时返回空态
2. 有 review 但未处理时显示 `pending`
3. 只展示最新一条 summary 即可

### 涉及文件

1. [store.py](/d:/ai应用项目/thinking/apps/api/app/services/store.py)

### 验收标准

1. workspace API 再也不返回硬编码 shots
2. API 能返回真实 `stage_tasks`
3. API 能返回真实 `review_summary`
4. workspace 数据全部来自数据库查询

---

## TB-07：前端接入真实 Workspace

### 目标

让前端至少有一个页面可以展示真实 workspace 数据，而不是继续依赖静态数组。

### 实施建议

不建议直接把首页强行改成动态工作台。  
建议新增一个最小 workspace 页面，并保留首页作为产品壳页。

### 推荐页面结构

建议新增其中一个：

1. `apps/web/app/projects/[projectId]/episodes/[episodeId]/page.tsx`
2. 或 `apps/web/app/workspace/[projectId]/[episodeId]/page.tsx`

### 具体开发动作

1. 新增 Web API client，例如 `apps/web/lib/api.ts`
2. 从 workspace 接口获取数据
3. 用真实 `shots` 渲染 shot 卡片
4. 用真实 `stage_tasks` 渲染 stage 状态区
5. 用真实 `review_summary` 渲染 Review 空态 / pending 态

### 首页处理建议

[`page.tsx`](/d:/ai应用项目/thinking/apps/web/app/page.tsx) 可以只做两件事：

1. 保留当前视觉壳子
2. 增加一个跳转到真实 workspace 的入口

### 涉及文件

1. [page.tsx](/d:/ai应用项目/thinking/apps/web/app/page.tsx)
2. `d:\ai应用项目\thinking\apps\web\lib\api.ts`
3. `d:\ai应用项目\thinking\apps\web\app\projects\[projectId]\episodes\[episodeId]\page.tsx`

### 验收标准

1. 前端至少一个页面不再使用硬编码 shots
2. 前端能渲染 stage 状态
3. Review 区能显示空态或 pending 态

---

## TB-08：演示数据、验证脚本与完成验收

### 目标

让 Iteration 1 交付时不仅“代码存在”，而且“演示可信”。

### 具体开发动作

1. 准备一组最小演示数据：
   - 1 个 project
   - 1 个 episode
   - 1 个 workflow_run
   - 2 到 3 个 stage_tasks
   - 3 个 shots
   - 1 条 pending review decision
2. 验证 workflow start 能写入 workflow + stage_task
3. 验证 workspace API 能查出真实 shots
4. 验证前端页面展示真实数据

### 推荐验证方式

如果本轮还没有正式测试框架，至少补以下两类验证：

1. API smoke 验证
2. 手工演示回归清单

### 最小 smoke 清单

1. `POST /api/projects`
2. `POST /api/projects/{project_id}/episodes`
3. `POST /api/projects/{project_id}/episodes/{episode_id}/workflow/start`
4. `GET /api/projects/{project_id}/episodes/{episode_id}/workspace`

### 推荐新增文档或脚本

可选增加：

1. `docs/engineering/ITERATION1-SMOKE-CHECKLIST.md`
2. `scripts/demo_seed.sql` 或等价 seed 方案

### 验收标准

1. 真实数据可被插入并被查出
2. 前端看到的是数据库状态，不是手写常量
3. 演示不依赖手工改代码切换状态

---

## 8. 任务与文件映射表

| 任务 | 必改文件 | 建议新增文件 |
|---|---|---|
| TB-01 | `apps/api/app/schemas/workspace.py` | 无 |
| TB-02 | `apps/api/app/db/models.py` | `infra/migrations/003_iteration1_shots_reviews.sql` |
| TB-03 | `apps/api/app/services/store.py` | `stage_task_repository.py` `shot_repository.py` `review_repository.py` |
| TB-04 | `apps/api/app/schemas/workspace.py` | 无 |
| TB-05 | `apps/api/app/repositories/workflow_repository.py` `apps/api/app/services/store.py` | `apps/api/app/services/workflow_service.py` |
| TB-06 | `apps/api/app/services/store.py` | 无 |
| TB-07 | `apps/web/app/page.tsx` | `apps/web/lib/api.ts` `apps/web/app/projects/[projectId]/episodes/[episodeId]/page.tsx` |
| TB-08 | 视实现而定 | `scripts/demo_seed.sql` `docs/engineering/ITERATION1-SMOKE-CHECKLIST.md` |

---

## 9. 推荐开发顺序

如果按最小返工路线推进，建议严格按下面顺序做：

1. `TB-01` 冻结 workspace 最小契约
2. `TB-02` 补齐 `StageTaskModel`、`ShotModel`、`ReviewDecisionModel`
3. `TB-03` 补 repository
4. `TB-04` 扩 DTO
5. `TB-05` 让 workflow start 真正写出 `StageTask`
6. `TB-06` 替换 workspace 假 shots
7. `TB-07` 前端接真实页面
8. `TB-08` 做演示验收

---

## 10. 每个 PR 的完成定义

## PR-1 完成定义

1. `StageTaskModel` 已写入 ORM
2. `ShotModel` 已写入 ORM
3. `ReviewDecisionModel` 已写入 ORM
4. 新 migration 已创建

## PR-2 完成定义

1. 三个新 repository 可用
2. workspace schema 可表达真实 stage / shot / review

## PR-3 完成定义

1. `start_workflow` 能写 `WorkflowRun`
2. `start_workflow` 能写 `StageTask`

## PR-4 完成定义

1. workspace API 不再返回任何硬编码 shot 数据
2. workspace API 返回真实 `stage_tasks` 与 `review_summary`

## PR-5 完成定义

1. 前端至少一个页面展示真实 workspace
2. 前端 shot 列表来自接口，不来自常量

---

## 11. 风险点与避免方式

### 风险 1：同时改模型、接口、前端，PR 过大

避免方式：

1. 严格按 PR-1 到 PR-5 切分
2. 每个 PR 都要能独立验证

### 风险 2：过早设计过多字段，导致改不动

避免方式：

1. `Shot` 先只保留工作台展示必需字段
2. `ReviewDecision` 先只做 summary 所需字段

### 风险 3：为了演示继续保留假数据兜底

避免方式：

1. 明确删除 [`store.py`](/d:/ai应用项目/thinking/apps/api/app/services/store.py) 中的硬编码 `shots`
2. 明确删除或隔离 [`page.tsx`](/d:/ai应用项目/thinking/apps/web/app/page.tsx) 中的硬编码 shot 渲染逻辑

### 风险 4：workflow 逻辑继续散落在 route/store/repository

避免方式：

1. 如果时间允许，尽早引入 `workflow_service.py`
2. 让 route 只做输入校验，store/service 负责 orchestration

---

## 12. Iteration 1 最终 DoD

Iteration 1 只有满足下面全部条件，才算真正完成：

1. 数据库中存在并可查询：
   - `workflow_runs`
   - `stage_tasks`
   - `shots`
   - `review_decisions`
2. `POST /workflow/start` 会创建真实 `WorkflowRun` 与 `StageTask`
3. `GET /workspace` 返回真实 `stage_tasks`、`shots`、`review_summary`
4. 前端至少一个页面展示真实 workspace 数据
5. 前端不再依赖硬编码 shot 数组
6. 演示流程不需要工程师改代码才能看到状态变化

---

## 13. 最终执行建议

如果你准备直接开做，最稳的开工顺序是：

1. 先做 `PR-1 Data Contract Alignment`
2. 接着做 `PR-2 Repository + Schema Layer`
3. 然后把 `workflow start -> StageTask` 打通
4. 再替换 workspace 假数据
5. 最后接前端页面

换句话说，Iteration 1 的本质不是“补三个模型”，而是：

> 把真实业务对象第一次贯通到数据库、API 和前端，让系统开始对真实状态负责。
