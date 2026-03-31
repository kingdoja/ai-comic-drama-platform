# SYSTEM BLUEPRINT

状态：Draft  
日期：2026-03-30  
适用范围：AI 漫剧创作者工作台 V1 工程总图

## 1. 文档目的

这份文档定义 V1 的目标系统形态，用于统一产品、后端、前端、workflow、agent、media、QA 的工程认知。

它回答七个问题：

1. 系统边界在哪里
2. 模块怎么拆
3. 数据怎么流动
4. workflow 怎样编排
5. 哪些对象必须持久化
6. 哪些运行时负责什么职责
7. 当前代码离目标态还差哪些关键块

这份文档是工程总图，不替代以下文档：

1. `API-CONTRACT.md`：接口契约
2. `WORKFLOW-CONTRACT.md`：流程契约
3. `AGENT-CONTRACT.md`：agent 契约
4. `V1-SCOPE.md`：产品边界
5. `PRODUCTIZATION-ROADMAP.md`：阶段路线图

---

## 2. 北极星工程目标

系统必须支持以下最小闭环：

```text
素材输入
  -> 文本结构化生产
  -> 分镜与视觉规格
  -> 媒体资产生成
  -> 预览合成
  -> QA 报告
  -> 人工审核
  -> 正式导出
```

工程上最重要的不是“某一步生成得多聪明”，而是：

1. 每一步都有稳定输入输出
2. 每一步都可追踪
3. 每一步都可重跑
4. 每一步都不会无声失败
5. 关键对象都有版本与归属

---

## 3. 设计原则

## 3.1 Workflow First

主业务流程必须由 workflow 驱动，而不是由 API、脚本或 worker 自行串接。

## 3.2 Artifact First

系统事实来源是结构化产物，不是聊天上下文。

## 3.3 Runtime Separation

文本生成、媒体执行、QA 评估应拆成独立 runtime，而不是塞进一个“大 worker”。

## 3.4 Replaceable Providers

Provider 可以替换，但业务对象和系统 contract 不能频繁变。

## 3.5 Explicit State

项目、剧集、workflow、stage、资产、审核状态都必须显式建模。

## 3.6 Human Gate Is Architectural

人工审核不是 UI 补丁，而是 workflow 的正式节点。

## 3.7 Observability Is Required

日志、trace、任务状态、资产 lineage、失败原因都属于系统本体。

---

## 4. 系统边界

## 4.1 In Scope

V1 系统内部负责：

1. 项目和剧集生命周期
2. episode_workflow / rerun_workflow 编排
3. 文本型 agent 执行
4. 媒体型 worker 执行
5. QA 评估与报告
6. 审核控制与导出控制
7. 结构化数据和资产元数据管理
8. 预览与正式导出包管理

## 4.2 Out of Scope

V1 不在系统内负责：

1. 多平台正式发布
2. 大规模运营分析
3. 企业级权限流
4. 外部素材抓取平台
5. 自动商业结算

## 4.3 外部依赖边界

外部系统仅通过适配层接入：

1. LLM provider
2. Image provider
3. TTS provider
4. FFmpeg 或同类导出工具
5. Temporal
6. PostgreSQL
7. Redis
8. Object Storage

---

## 5. 目标系统全景图

```text
+--------------------------------------------------------------------------------+
|                                 Web Application                                |
|  Project List | Project Setup | Workspace | Storyboard | Preview QA | Export   |
+------------------------------------------+-------------------------------------+
                                           |
                                           v
+--------------------------------------------------------------------------------+
|                                     API Layer                                  |
|  REST endpoints | DTO schemas | auth placeholder | workspace aggregation        |
+------------------------------------------+-------------------------------------+
                                           |
                                           v
+--------------------------------------------------------------------------------+
|                                  Workflow Layer                                |
|  project_workflow | episode_workflow | rerun_workflow | review gates | retries  |
+-------------------+------------------+----------------+--------------+----------+
                    |                  |                |                         
                    v                  v                v                         
+-------------------------+ +-------------------------+ +------------------------+
|      Agent Runtime      | |      Media Runtime      | |       QA Runtime       |
| brief/story/script/...  | | image/tts/export        | | rule + semantic checks |
+-------------------------+ +-------------------------+ +------------------------+
                    \                |                 /
                     \               |                /
                      v              v               v
+--------------------------------------------------------------------------------+
|                                   Data Layer                                   |
|  PostgreSQL | Object Storage | Redis | Trace/Logs | Versioning | Metadata      |
+--------------------------------------------------------------------------------+
```

---

## 6. 分层设计

## 6.1 Product Layer

职责：

1. 给用户提供工作台和编辑界面
2. 展示 workflow 当前状态
3. 管理人工审核和返工动作
4. 展示 preview、QA、导出结果

不负责：

1. 直接执行长任务
2. 串业务流程
3. 直接访问外部 provider

建议前端拆分：

1. projects
2. workspace
3. documents
4. storyboard-assets
5. preview-qa
6. export

## 6.2 API Layer

职责：

1. 接收用户命令
2. 校验输入
3. 启动 workflow
4. 返回聚合 DTO
5. 写入轻量同步动作，例如编辑、锁定、选择主资产

不负责：

1. 长耗时 agent 逻辑
2. 长耗时媒体生成
3. workflow 状态推进细节

## 6.3 Workflow Layer

职责：

1. 编排 stage 执行顺序
2. 管理 stage 依赖
3. 处理失败重试
4. 控制 human review gate
5. 控制 rerun 范围
6. 管理状态机推进

不负责：

1. 生成文本内容本身
2. 画图、TTS、合成的执行细节
3. 复杂 UI 逻辑

## 6.4 Agent Runtime

职责：

1. 执行文本型 stage
2. 读取上下文 refs
3. 组装 prompt / constraints / schema
4. 调用 LLM
5. 校验输出
6. 提交 document 产物

V1 包含的主 agent：

1. Brief Agent
2. Story Bible Agent
3. Character Agent
4. Script Agent
5. Storyboard Agent
6. Subtitle Agent

## 6.5 Media Runtime

职责：

1. 执行 visual_spec 消费
2. 调用 image provider
3. 调用 TTS provider
4. 合成 preview/final export
5. 提交 asset 产物

V1 包含的主 worker：

1. Image Render Worker
2. TTS Worker
3. Export Worker

## 6.6 QA Runtime

职责：

1. 执行规则型检查
2. 执行语义型检查
3. 聚合 QA 结果
4. 输出 rerun 建议
5. 生成结构化 QA report

---

## 7. 核心业务对象

## 7.1 当前已在代码中出现的对象

当前模型中已经出现：

1. `Project`
2. `Episode`
3. `WorkflowRun`
4. `Document`
5. `Asset`
6. `QAReport`

## 7.2 V1 还必须补齐的对象

以下对象在蓝图中是必须的，但当前实现尚未完整落地：

1. `StageTask`
2. `Shot`
3. `ReviewDecision`
4. `ExportBundle`
5. `DocumentLock`
6. `AssetSelectionHistory`
7. `WorkflowEvent` 或等价 trace/event 存储

## 7.3 对象职责说明

### Project
项目级容器，记录题材、平台、目标受众、项目状态。

### Episode
单集级容器，是 V1 主交付单元。

### WorkflowRun
一次 workflow 执行实例，记录运行状态和 Temporal 关联信息。

### StageTask
单个 stage 的执行记录，应该是 workflow 的最小执行粒度对象。

### Document
文本型产物，包含 brief、story_bible、character_profile、script_draft、visual_spec、subtitle_script 等。

### Shot
分镜级对象，是 image_render 和局部 rerun 的关键锚点。

### Asset
媒体型产物，包含关键帧、音频、字幕文件、preview、final_video、cover 等。

### QAReport
质量检查结果，包含问题清单、严重级别、返工建议。

### ReviewDecision
人工审核动作记录，决定 workflow 是否继续。

### ExportBundle
正式导出结果，用于交付与追踪。

---

## 8. 数据模型建议

## 8.1 对象关系图

```text
Project
  |
  +-- Episode
        |
        +-- WorkflowRun
        |      |
        |      +-- StageTask
        |
        +-- Document
        |
        +-- Shot
        |     |
        |     +-- Asset (shot scoped)
        |
        +-- Asset (episode scoped)
        |
        +-- QAReport
        |
        +-- ReviewDecision
        |
        +-- ExportBundle
```

## 8.2 版本策略

### Document 版本策略

1. 每次成功提交形成新版本
2. 已确认版本不可被静默覆盖
3. 编辑与生成都要带来源标记

### Asset 版本策略

1. 同一 shot 可存在多个候选资产
2. 通过 `is_selected` 或等价机制标记主资产
3. rerun 默认只影响目标范围

### Workflow / Stage 版本策略

1. 每次启动 workflow 形成独立 `WorkflowRun`
2. 每次 stage 执行形成独立 `StageTask`
3. rerun 不是修改旧任务，而是创建新任务与新结果

---

## 9. 主流程蓝图

## 9.1 Episode Workflow 主时序

```text
User
  -> API.start_workflow
  -> Workflow Engine.create WorkflowRun
  -> brief StageTask
  -> story_bible StageTask
  -> character StageTask
  -> script StageTask
  -> storyboard StageTask
  -> visual_spec StageTask
  -> image_render StageTask
  -> subtitle StageTask
  -> tts StageTask
  -> edit_export_preview StageTask
  -> qa StageTask
  -> human_review_gate
  -> export_final StageTask
  -> Episode Package Ready
```

## 9.2 文本型 stage 内部流

```text
StageTaskInput
  -> Loader
  -> Normalizer
  -> Planner
  -> Generator
  -> Critic
  -> Validator
  -> Committer
  -> Document refs + metrics
```

## 9.3 媒体型 stage 内部流

```text
StageTaskInput
  -> Resolve refs
  -> Build provider payload
  -> Provider execution
  -> Validate asset metadata
  -> Upload object
  -> Commit asset record
  -> Asset refs + metrics
```

## 9.4 QA stage 内部流

```text
Preview + Documents + Assets
  -> Rule checks
  -> Semantic checks
  -> Severity aggregation
  -> Rerun mapping
  -> QAReport commit
```

---

## 10. Rerun 蓝图

## 10.1 Rerun 原则

1. rerun 只针对目标 stage 和必要下游
2. rerun 不覆盖非目标对象
3. rerun 优先复用已选资产与已确认文档
4. rerun 结果必须可与旧结果并存

## 10.2 两类关键 rerun

### Stage rerun

例如：

1. 重新生成 script
2. 重新生成 storyboard
3. 重新执行 qa

### Targeted rerun

例如：

1. 重跑指定 shot 的 image_render
2. 重跑指定片段的 tts

## 10.3 Rerun 数据流

```text
User triggers rerun
  -> API validates target
  -> Workflow Engine creates rerun WorkflowRun
  -> Build StageTaskInput with target_ref_ids
  -> Execute target stage
  -> Execute necessary downstream stages
  -> Commit new artifacts
  -> Preserve old selected artifacts unless replaced intentionally
```

---

## 11. 状态机蓝图

## 11.1 Episode 状态机

```text
draft
  -> brief_pending
  -> brief_confirmed
  -> bible_ready
  -> episode_writing
  -> storyboard_ready
  -> visual_generating
  -> audio_ready
  -> cut_ready
  -> qa_approved / needs_revision
  -> review_pending
  -> export_ready
  -> published
```

## 11.2 WorkflowRun 状态机

```text
created
  -> running
  -> waiting_review
  -> succeeded
  -> failed
  -> canceled
```

## 11.3 StageTask 状态机

```text
pending
  -> running
  -> succeeded
  -> failed
  -> skipped
  -> blocked
```

## 11.4 ReviewDecision 状态机

```text
submitted
  -> approved
  -> request_changes
  -> rejected
```

---

## 12. API 与系统交互边界

## 12.1 API 应该做的事

1. 新建项目 / 剧集
2. 启动 workflow
3. 查询 workflow 状态
4. 查询 workspace
5. 编辑 document
6. 锁定 document / shot
7. 选择主资产
8. 提交 review decision
9. 发起 rerun

## 12.2 API 不应该做的事

1. 同步执行 agent
2. 同步执行 image render
3. 同步执行 TTS
4. 同步执行 export
5. 内嵌复杂 workflow 逻辑

---

## 13. Workspace 聚合蓝图

Workspace 是前端工作的主入口，必须是一个聚合视图，而不是简单 CRUD 的拼装。

## 13.1 Workspace 最低组成

1. Project
2. Episode
3. Latest WorkflowRun
4. Current documents by type
5. Current shots
6. Current selected assets
7. QA summary
8. Pending review actions
9. Rerun entry metadata

## 13.2 Workspace 聚合流

```text
API GET workspace
  -> load project
  -> load episode
  -> load latest workflow
  -> load current documents
  -> load shots
  -> load selected assets
  -> load latest QA report
  -> load pending reviews
  -> return EpisodeWorkspaceResponse
```

## 13.3 当前实现差距

当前 `workspace` 已有基本聚合方向，但仍存在差距：

1. `shots` 还是占位数据，不是数据库实体
2. 缺失 review pending 信息
3. 缺失 stage task 级可视状态
4. 缺失导出状态聚合

---

## 14. 运行时职责总表

| Runtime | 负责 | 不负责 |
|---|---|---|
| API | 接口、校验、聚合、命令入口 | 长耗时执行、workflow 主逻辑 |
| Workflow | 编排、状态推进、重试、gate | 内容生成、媒体执行 |
| Agent Runtime | 文本生成 stage | 推进状态机、审核决策 |
| Media Runtime | 图像、TTS、导出 | 文本规划与长链业务决策 |
| QA Runtime | 质检与报告 | 直接替用户修改内容 |

---

## 15. Provider 适配层蓝图

## 15.1 适配层目的

业务层永远面向统一 contract，不直接绑定某个 provider SDK。

## 15.2 建议适配层

1. `llm_adapter`
2. `image_adapter`
3. `tts_adapter`
4. `storage_adapter`
5. `export_adapter`
6. `qa_evaluator_adapter`

## 15.3 适配层规则

1. provider 特定参数不要渗透到 domain object
2. 业务代码只依赖内部 DTO
3. 调用耗时、失败原因、request id 要可记录

---

## 16. 失败处理蓝图

## 16.1 失败分类

### 输入失败

例如：

1. 素材为空
2. refs 缺失
3. 锁定对象不存在

### provider 失败

例如：

1. LLM 超时
2. Image provider 返回错误
3. TTS 返回空音频

### 校验失败

例如：

1. schema 不合法
2. 必填字段缺失
3. shot 输出不完整

### 系统失败

例如：

1. 存储失败
2. 数据库写入失败
3. workflow 中断

## 16.2 失败处理原则

1. 每个失败都必须落日志
2. 每个失败都必须归属到 stage task
3. 每个失败都必须可让前端感知状态
4. 失败默认不能静默吞掉

## 16.3 三类关键保护

1. `script` 失败不覆盖旧版本
2. `image_render` 失败不影响其他 shot
3. `qa` 失败进入 review 或 revision 状态，不直接推进导出

---

## 17. 可观测性蓝图

## 17.1 必须记录的信号

1. workflow start / finish
2. stage start / finish / fail
3. provider request id
4. token / duration / cost
5. asset lineage
6. rerun lineage
7. review decisions

## 17.2 最低可见面板

V1 至少要能看到：

1. 当前 workflow 卡在哪一步
2. 最近一次失败在哪个 stage
3. 哪些资产是当前主资产
4. QA 为什么没通过
5. 哪些对象是 rerun 生成的新版本

---

## 18. 部署与本地拓扑

## 18.1 本地拓扑

```text
Web
  -> API
      -> PostgreSQL
      -> Redis
      -> Temporal
      -> Object Storage
      -> Agent Runtime
      -> Media Runtime
      -> QA Runtime
```

## 18.2 部署建议

V1 建议保持单仓、多进程、多 runtime 的部署方式，而不是过早微服务化。

建议拆成以下部署单元：

1. Web
2. API
3. Temporal Worker: Agent Runtime
4. Temporal Worker: Media Runtime
5. Temporal Worker: QA Runtime
6. PostgreSQL
7. Redis
8. Object Storage

## 18.3 为什么不建议更早拆更多服务

1. 当前最重要的是主链路稳定，不是组织复杂度
2. 服务过多会增加调试和部署成本
3. V1 的系统复杂度还不足以证明微服务收益

---

## 19. 当前实现与目标态差距

## 19.1 当前已具备

1. monorepo 骨架
2. 基础 API 路由
3. 部分数据库模型
4. workspace 聚合雏形
5. 产品与工程 contract 初稿

## 19.2 关键缺口

1. `StageTask` 模型未落地
2. `Shot` 模型未落地
3. `ReviewDecision` 模型未落地
4. worker 仍是 placeholder
5. workflow 真实编排未落地
6. workspace 仍缺真实 shot / review / export 数据
7. trace / lineage / rerun 记录未成体系

## 19.3 优先补齐顺序

1. 核心对象补齐：StageTask / Shot / ReviewDecision
2. WorkflowRun 与 StageTask 真实联动
3. 文本 stage mock workflow 跑通
4. workspace 真聚合替换占位数据
5. Media / QA runtime 逐步接入

---

## 20. 最终蓝图结论

这个系统的正确工程形态不是：

1. 一个 API 里面顺手调几个模型
2. 一个前端页面拼一些假数据
3. 一组 agent 自由对话后碰碰运气产出结果

而应该是：

> 一个由 workflow 编排驱动、由 artifact 作为事实来源、由多 runtime 分工执行、由显式状态机控制推进、支持审核和局部重跑的 AI 单集生产系统。

如果后续实现始终围绕这张蓝图推进，系统会自然具备：

1. 可交付性
2. 可追踪性
3. 可返工性
4. 可扩展性
5. 可产品化能力
