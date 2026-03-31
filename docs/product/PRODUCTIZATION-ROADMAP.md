# PRODUCTIZATION ROADMAP

状态：Draft  
日期：2026-03-30  
适用阶段：Demo -> Internal Alpha -> Pilot Beta -> Product V1

## 1. 这份文档解决什么问题

这份路线图不是单纯的开发排期表，而是把当前项目从“前端 + API demo”推进成“可稳定交付单集包的产品系统”的总设计。

它解决四个问题：

1. 这个项目接下来到底要做到什么程度
2. 先做哪些，后做哪些，为什么
3. 每个阶段的验收标准是什么
4. 团队如何避免继续做成“能演示但不能交付”的系统

---

## 2. 当前现状判断

基于当前仓库和已有文档，项目已经具备以下基础：

1. 产品方向明确：目标是 AI 漫剧创作者工作台，而不是泛 AI 生成工具
2. MVP 边界明确：以“单集包”作为最小交付单位
3. API / Workflow / Agent contract 已经有清晰初稿
4. 数据模型已经开始面向真实产品对象设计
5. Web、API、Worker 已经有 monorepo 骨架

但当前仍然是明显的 Demo 阶段，原因如下：

1. Web 主要是静态工作台壳，尚未由真实 workflow 驱动
2. Workspace 聚合仍混合真实数据与占位数据
3. Agent / Media / QA 三类 runtime 仍是 placeholder
4. Workflow 还没有真实执行链路、状态机、重试、回滚、人工审核闭环
5. 媒体资产、QA、rerun、导出还没有形成真正的生产闭环

一句话判断：

> 当前项目已经拥有“产品蓝图”和“工程 contract”，但还没有拥有“可稳定交付的生产系统”。

---

## 3. 产品化总目标

### 3.1 北极星目标

让创作者或小团队能够把一段女频网文章节 / 短剧脚本素材，稳定转成一个可发布的竖屏漫剧单集包。

### 3.2 最小成功单位

不是“一个项目”，而是：

> 一个可预览、可审核、可返工、可导出的单集包

### 3.3 单集包必须包含

1. Project Brief
2. Character Profile
3. Story Bible Summary
4. Episode Script
5. Storyboard / Shot List
6. Visual Spec
7. Shot Images / Keyframes
8. Subtitle File
9. Voice Assets
10. Preview Video
11. QA Report
12. Export Bundle
13. Cover / Title / Publish Copy

---

## 4. 产品化原则

这部分是整个 roadmap 的核心约束，后续所有阶段都必须遵守。

### 4.1 Workflow First

先把流程编排做好，再增加更多 agent 或模型能力。

原因：

1. 漫剧生产天然是阶段式流程，不是开放式聊天
2. 真正难点不在“生成一次内容”，而在“持续稳定生成”
3. 没有 workflow，就没有可重跑、可审核、可追踪

### 4.2 Artifact First

系统核心产物不是聊天记录，而是结构化产物。

核心产物包括：

1. brief
2. story_bible
3. character_profile
4. script_draft
5. shots
6. visual_spec
7. assets
8. qa_report
9. export_bundle

### 4.3 Human In The Loop

高价值节点必须保留人工控制权。

至少保留以下人工门：

1. Brief 确认
2. Character / World 关键字段确认
3. Storyboard 确认
4. Final QA 审核
5. Final Export 审核

### 4.4 Rerun By Stage, Not Rebuild Everything

返工必须是局部重跑，而不是整条链路从头再来。

最关键的局部重跑能力：

1. 从 script 重跑
2. 从 storyboard 重跑
3. 从 visual_spec 重跑
4. 针对单个 shot 重跑 image_render
5. 针对目标片段重跑 tts

### 4.5 Contract Before Intelligence

先稳定输入输出 contract，再替换内部模型实现。

这也是从 `DEV_SPEC` 值得借鉴的最重要方法论之一：

1. mock 可以先存在
2. contract 不能含糊
3. 先让系统有稳定边界，再追求更强模型效果

### 4.6 Observability Is In Scope

Trace、QA、成本、错误定位不是后补项，而是产品能力的一部分。

---

## 5. 产品成熟度模型

项目不应该从 Demo 直接跳到“完整产品”，而应该分四级演进。

### Level 0: Demo

定义：

1. 能演示工作台概念
2. 能展示产品流程
3. 能用 mock 数据支撑叙事

局限：

1. 不能稳定交付真实单集包
2. 失败无法定位
3. 数据不可复用

### Level 1: Internal Alpha

定义：

1. 团队内部可跑通完整单集闭环
2. 部分 stage 可用 mock
3. 所有 stage 必须有真实 contract 和真实状态推进

验收：

1. 能创建项目和剧集
2. 能启动 episode workflow
3. 能看到真实 stage 状态变化
4. 能拿到第一版 preview

### Level 2: Pilot Beta

定义：

1. 小团队可以真实试用
2. 可以稳定完成单集包生产
3. 有局部重跑、QA、审核、导出闭环

验收：

1. 同一项目可重复生产多集
2. 同一阶段失败可定位、可恢复
3. 资产和版本不会互相覆盖

### Level 3: Product V1

定义：

1. 可以作为垂直产品对外试点或收费
2. 有模板化、权限、成本控制、可观测、运营指标
3. 具备“稳定交付”而不只是“生成内容”

---

## 6. V1 产品边界

### 6.1 V1 必做

1. 项目创建与素材导入
2. Brief 生成、编辑、确认
3. Character / Story Bible 生成、编辑、锁定
4. Script 生成、编辑、版本化
5. Storyboard 生成、镜头稳定 ID、镜头编辑
6. Visual Spec 生成
7. Keyframe 渲染
8. Subtitle 生成
9. TTS 生成
10. Preview 合成
11. QA 报告
12. Human Review Gate
13. Export Final
14. Stage 级 / Shot 级局部重跑
15. 基础 Trace、日志、成本记录

### 6.2 V1 明确不做

1. 多平台一键发布
2. 多人实时协作编辑
3. 多集自动批量工厂
4. 智能投放分析
5. 高级商业化计费系统
6. 复杂 provider 自动路由矩阵
7. agent 自由协商式多智能体聊天

### 6.3 V1 的产品定位

V1 不是“全自动内容工厂”，而是：

> 面向创作者和小团队的、可控的 AI 单集生产系统

---

## 7. 目标系统蓝图

### 7.1 系统层次

```text
+--------------------------------------------------------------+
|                        Product Layer                         |
|  Project / Episode / Workspace / Review / Export / QA UI    |
+--------------------------------------------------------------+
|                       Workflow Layer                         |
|  episode_workflow / rerun_workflow / gates / retries        |
+--------------------------------------------------------------+
|                       Runtime Layer                          |
|  Agent Runtime / Media Runtime / QA Runtime                 |
+--------------------------------------------------------------+
|                        Data Layer                            |
|  PostgreSQL / Object Storage / Redis / Trace / Versioning   |
+--------------------------------------------------------------+
|                     Integration Layer                        |
|  LLM / Image / TTS / FFmpeg / Temporal / External Providers |
+--------------------------------------------------------------+
```

### 7.2 主数据对象

1. Project
2. Episode
3. WorkflowRun
4. StageTask
5. Document
6. Shot
7. Asset
8. QAReport
9. ReviewDecision
10. ExportBundle

### 7.3 核心状态流

```text
Draft Project
    |
    v
Episode Created
    |
    v
Workflow Started
    |
    v
Brief -> Story Bible -> Character -> Script -> Storyboard
    |
    v
Visual Spec -> Image Render -> Subtitle -> TTS -> Preview Export
    |
    v
QA
    |
    +--> needs_revision --> rerun_workflow --> back to target stage
    |
    +--> approved --> human_review_gate
                          |
                          v
                      export_final
                          |
                          v
                     Episode Package Ready
```

---

## 8. 分阶段路线图

## Phase 0：产品化基线

时间建议：2026-03-30 到 2026-04-12

### 目标

冻结第一阶段产品边界、技术边界和交付边界。

### 要交付的正式产物

1. `PRODUCTIZATION-ROADMAP.md`
2. `V1-SCOPE.md`
3. `SYSTEM-BLUEPRINT.md`
4. `DELIVERY-PLAN.md`
5. 数据模型补充说明
6. workflow 状态机补充说明

### 本阶段要解决的问题

1. 什么叫“单集包完成”
2. 哪些 stage 允许 mock
3. 哪些对象需要版本化
4. 哪些动作必须人工确认
5. rerun 粒度到什么层级

### 退出标准

1. 团队对 V1 做什么 / 不做什么没有歧义
2. 每个 stage 的输入输出都有 schema 边界
3. 每个核心对象都有归属与存储位置
4. 可以开始稳定拆分开发任务

---

## Phase 1：文本主链路 Alpha

时间建议：2026-04-13 到 2026-05-10

### 目标

先跑通内容结构主链路：

`素材 -> brief -> story_bible -> character -> script -> storyboard`

### 重点建设

#### 产品侧

1. 项目创建页
2. 素材导入流程
3. 项目工作台基础态
4. Brief / Character / Script / Storyboard 编辑界面

#### 工程侧

1. PostgreSQL migrations
2. Project / Episode / Document / WorkflowRun / StageTask 基础模型落库
3. API 返回真实 workspace 聚合数据
4. Temporal episode_workflow 基础编排
5. Agent Runtime 注册文本型 stage handler

#### 能力侧

1. brief mock handler
2. story_bible mock handler
3. character mock handler
4. script mock handler
5. storyboard mock handler

### 本阶段不追求

1. 高质量图片
2. 真实 TTS
3. 高级 QA
4. 花哨前端交互

### 退出标准

1. 用户能真实创建项目和剧集
2. 用户能启动 workflow 并看到阶段推进
3. 每个文本 stage 都会产出真实 document 记录
4. Document 支持编辑、锁定、版本化
5. Storyboard 有稳定 shot id

---

## Phase 2：媒体主链路 Alpha

时间建议：2026-05-11 到 2026-06-07

### 目标

跑通从 visual_spec 到 preview 的媒体闭环。

### 重点建设

#### 产品侧

1. 分镜页升级为镜头资产工作台
2. Preview & QA 页面开始接真实数据
3. 资产选择、主资产切换、失败提示

#### 工程侧

1. Object Storage 接入
2. Asset 表和对象存储引用联动
3. Media Runtime 接入 image / tts / ffmpeg adapter
4. visual_spec、image_render、subtitle、tts、edit_export_preview 几个 stage 的真实任务链

#### 能力侧

1. visual_spec handler
2. image_render worker
3. subtitle generator
4. tts worker
5. preview export worker

### 方法约束

1. 先接 1 家主 LLM provider
2. 先接 1 家 image provider
3. 先接 1 家 TTS provider
4. adapter 接口抽象保留，但实现不追求多供应商并发

### 退出标准

1. 至少一个项目能产出真实 keyframe
2. 至少一个项目能产出真实 preview 视频
3. 每个 shot 的渲染结果进入资产库
4. 失败时不会覆盖其他已选资产
5. 同一个 shot 支持单独重跑

---

## Phase 3：QA / 审核 / 局部重跑闭环

时间建议：2026-06-08 到 2026-06-28

### 目标

把系统从“能生成”推进到“能交付”。

### 重点建设

#### 产品侧

1. QA 页面展示真实问题列表
2. Human Review Gate 操作页
3. rerun 入口和 rerun 结果对比
4. Export 页面展示正式导出包

#### 工程侧

1. QA Runtime 落地
2. Rule checks + semantic checks + report aggregator
3. rerun_workflow
4. 审核决策写回 workflow 状态
5. export_final 闭环

#### 能力侧

1. QA 问题映射到 rerun stage
2. 按目标 shot / stage 重跑
3. 人工审核通过后才允许 final export

### 退出标准

1. QA 不只是一个分数，而是结构化报告
2. QA 失败可以明确指向返工阶段
3. 审核动作会改变系统状态
4. 能导出完整单集包
5. 局部重跑后 downstream 可正确刷新

---

## Phase 4：Pilot Beta

时间建议：2026-06-29 到 2026-08-09

### 目标

让小团队真实使用，不只是内部演示。

### 重点建设

1. 模板化项目创建
2. 样板工程 / 示例项目
3. 成本、耗时、失败率可视化
4. Provider 失败降级策略
5. Review / QA / Export 的历史记录
6. 基础权限模型
7. 日志与 trace 面板

### 退出标准

1. 同一团队可连续完成多个项目
2. 平均单集生产链路稳定
3. 系统中断后可以恢复
4. 失败分布可观测
5. 团队可以开始小规模试点

---

## Phase 5：Product V1

时间建议：2026-08-10 以后

### 目标

形成一个可以对外试点、可收费的垂直产品版本。

### 重点建设

1. 角色模板 / 风格模板 / 平台模板
2. 更稳定的 provider 适配层
3. 项目级与组织级权限
4. 成本预算与配额控制
5. 产能与质量指标面板
6. 导出标准化与运营交接能力

### 进入 V1 的最低条件

1. 单集包交付成功率稳定
2. 关键失败可恢复
3. 返工成本可控
4. 创作者不需要工程师手工介入即可完成主要流程

---

## 9. 五条并行工作流

为了防止 roadmap 只剩下阶段顺序，下面把实际落地拆成五条持续并行的工作流。

### 9.1 产品工作流

负责：

1. scope 控制
2. 用户路径
3. 关键交互
4. 验收标准
5. 非目标范围控制

关键产物：

1. PRD
2. 用户流
3. 页面优先级
4. 验收清单

### 9.2 工程平台工作流

负责：

1. monorepo 稳定性
2. migrations
3. infra 本地环境
4. workflow 编排
5. 版本与存储

关键产物：

1. 本地环境一键启动
2. workflow 骨架
3. stage 执行框架
4. trace / logging / retry

### 9.3 内容智能工作流

负责：

1. brief / story / character / script / storyboard agent
2. prompt contract
3. 文本生成质量
4. 可编辑与锁定策略

关键产物：

1. 文本 stage handler
2. prompt contract
3. 质量回归用例

### 9.4 媒体执行工作流

负责：

1. visual_spec
2. image render
3. subtitle
4. tts
5. preview / export

关键产物：

1. adapter 层
2. 资产版本化
3. rerun 粒度设计

### 9.5 QA 与运营工作流

负责：

1. QA 报告
2. 审核与放行
3. 成本与时长追踪
4. pilot 期样板项目
5. 用户试点反馈

---

## 10. 里程碑定义

### M1：文本链路打通

定义：

素材可以稳定走到 storyboard。

### M2：预览链路打通

定义：

可以从 storyboard 走到真实 preview。

### M3：可交付闭环打通

定义：

可以 QA、审核、重跑、导出单集包。

### M4：Pilot Ready

定义：

小团队可连续使用，不需要工程师手工兜底大部分流程。

### M5：Product V1 Ready

定义：

具备对外试点能力和收费基础能力。

---

## 11. 验收指标体系

## 11.1 交付指标

1. 单集包完成率
2. 单集包导出成功率
3. 平均单集生产时长
4. 从创建项目到预览生成的耗时

## 11.2 质量指标

1. QA 首次通过率
2. 人工审核通过率
3. 角色一致性问题率
4. 字幕 / 配音 /画面错配率

## 11.3 返工指标

1. 平均 rerun 次数
2. 平均 shot 重跑次数
3. 平均 script 重跑次数
4. rerun 后成功率

## 11.4 平台指标

1. stage 成功率
2. stage 平均耗时
3. provider 调用成功率
4. 单集平均成本

---

## 12. 风险清单

## 12.1 产品风险

1. 目标过大，过早滑向“全自动工厂”
2. 前端视觉做得很满，但主链路仍不可交付
3. 用户能生成内容，但不能稳定返工

应对：

1. 严格以单集包为边界
2. 每个阶段必须有退出标准
3. 所有新增需求先判断是否破坏 V1 scope

## 12.2 工程风险

1. 过早接入太多 provider
2. workflow 逻辑散落在 API / worker / script 中
3. 资产版本和主资产选择逻辑混乱

应对：

1. 单供应商起步
2. workflow orchestration 集中化
3. 资产与文档统一版本策略

## 12.3 AI 风险

1. 剧情质量不稳定
2. 人设漂移
3. 图像连续性差
4. TTS 与字幕错位

应对：

1. lock 关键字段
2. visual_spec 与 render 分离
3. QA 必须落到结构化问题
4. rerun 精确到 stage / shot

---

## 13. 与 DEV_SPEC 方法论的映射

虽然 `DEV_SPEC` 属于另一个 RAG/MCP 项目，但其中有四条方法论可以直接复用到本项目。

### 13.1 先定 contract，再替换实现

映射到本项目：

1. 先稳定 workflow contract
2. 先稳定 agent input / output schema
3. 先稳定 asset / qa / export contract
4. mock 可先跑，但接口不反复摇摆

### 13.2 系统必须可插拔

映射到本项目：

1. LLM provider 可替换
2. image provider 可替换
3. TTS provider 可替换
4. export 工具链可替换
5. QA evaluator 可替换

### 13.3 可观测性必须早做

映射到本项目：

1. stage trace
2. asset lineage
3. prompt lineage
4. cost logging
5. QA history

### 13.4 里程碑以“能力完成”切分

映射到本项目：

1. 不是“页面做完”
2. 不是“接了某个模型”
3. 而是“能完成某个交付能力”

---

## 14. 接下来两周的实际动作

为了让 roadmap 不是空文档，先给出一个立刻可执行的两周动作清单。

### Week 1

1. 冻结 V1 scope
2. 补齐 `SYSTEM-BLUEPRINT.md`
3. 补齐 `DELIVERY-PLAN.md`
4. 明确 `Shot`、`StageTask`、`ReviewDecision` 等缺失模型
5. 把 workspace 假数据替换为真实聚合结构

### Week 2

1. 跑通 `brief -> story_bible -> character -> script -> storyboard` mock workflow
2. 打通 API 与前端工作台的真实数据读取
3. 明确 document version / lock 行为
4. 增加 workflow run 可视状态
5. 准备一个样板项目作为端到端验收用例

---

## 15. 推荐执行节奏

### 15.1 迭代节奏

建议使用两周一个迭代。

每个迭代必须有：

1. 一个主交付能力
2. 一个 demo 场景
3. 一套验收标准
4. 一个风险复盘

### 15.2 周会视角

不要按“写了多少代码”汇报，而按：

1. 本周打通了哪条能力链
2. 哪个 stage 还是假实现
3. 哪个环节失败最频繁
4. 哪个对象还没有版本 / 回滚 / 锁定

### 15.3 每阶段结项问题

每完成一个阶段，都回答这四个问题：

1. 用户现在能多做成什么
2. 哪条链路从 mock 变成真了
3. 哪个失败现在可以被定位
4. 哪个返工现在可以只局部处理

---

## 16. 最终判断

这个项目最有价值的方向，不是继续堆一个更完整的 demo，而是把它做成：

> 一个以单集包交付为中心、以 workflow 为骨架、以 artifact 为事实来源、支持人工把关与局部重跑的 AI 漫剧生产系统。

只要主链路走通，这个项目后续自然可以继续扩到：

1. 多集生产
2. 模板市场
3. 多平台分发
4. 团队协作
5. 数据复盘闭环
6. 半自动内容工厂

但在 V1 之前，最重要的事情只有一件：

**先把“一个单集包稳定做出来”做成产品能力。**
