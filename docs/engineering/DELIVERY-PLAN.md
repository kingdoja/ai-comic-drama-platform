# DELIVERY PLAN

状态：Draft  
日期：2026-03-30  
适用范围：AI 漫剧创作者工作台 V1 交付执行计划

## 1. 文档目的

这份文档把产品路线图和工程蓝图进一步压成可执行的开发计划。

它解决六个问题：

1. 接下来先做什么
2. 哪些任务必须先后依赖
3. 每轮迭代的目标是什么
4. 每轮迭代完成的验收标准是什么
5. 哪些事项可以并行
6. 团队如何判断某轮是否真的完成

这份文档默认按“两周一个迭代”组织。

---

## 2. 执行总原则

## 2.1 顺序原则

开发顺序必须遵循：

1. 先补核心对象
2. 再补 workflow 骨架
3. 再补文本主链路
4. 再补媒体链路
5. 再补 QA / 审核 / 导出闭环
6. 最后补 pilot 所需强化能力

## 2.2 完成定义原则

一个迭代只有在以下三个层面都完成时，才算完成：

1. 代码对象存在
2. 主链路可跑通
3. 前端或接口能真实消费结果

## 2.3 Mock 原则

允许 mock，但 mock 必须满足：

1. 输入输出 contract 真实
2. workflow 状态真实
3. 数据持久化真实
4. 将来可无痛替换成真实实现

## 2.4 拆活原则

任务拆分按四条泳道进行：

1. Product / UX
2. Backend / Data
3. Workflow / Runtime
4. Frontend / Workspace

---

## 3. 总交付路径

```text
Phase 0: 冻结边界与总图
    ->
Iteration 1: 核心对象与真实 workspace 骨架
    ->
Iteration 2: 文本主链路 mock 跑通
    ->
Iteration 3: 分镜与 shot 级结构落地
    ->
Iteration 4: 媒体链路打通
    ->
Iteration 5: QA / 审核 / rerun 打通
    ->
Iteration 6: Final export 与 pilot 强化
```

---

## 4. 依赖图

## 4.1 关键依赖关系

```text
StageTask model
   -> Workflow orchestration
   -> Stage execution history
   -> Workspace stage visibility

Shot model
   -> Storyboard persistence
   -> Image render targeting
   -> Shot rerun
   -> Asset selection

ReviewDecision model
   -> Human review gate
   -> Export control

Workflow skeleton
   -> Text chain execution
   -> Media chain execution
   -> QA chain execution

Workspace real aggregation
   -> Frontend usable state
   -> Demo credibility
   -> QA / rerun visibility
```

## 4.2 不可跳过的基石任务

以下任务不能后置：

1. `StageTask` 建模
2. `Shot` 建模
3. `ReviewDecision` 建模
4. episode_workflow 真编排入口
5. workspace 真聚合

---

## 5. 角色与泳道

## 5.1 Product / UX 泳道

负责：

1. 页面优先级
2. 表单字段冻结
3. 人工审核交互
4. workspace 展示结构
5. 验收标准维护

## 5.2 Backend / Data 泳道

负责：

1. 数据模型
2. migration
3. repository / service
4. DTO / schema
5. 聚合接口

## 5.3 Workflow / Runtime 泳道

负责：

1. WorkflowRun / StageTask 执行框架
2. Agent Runtime
3. Media Runtime
4. QA Runtime
5. retry / rerun / gate

## 5.4 Frontend / Workspace 泳道

负责：

1. 项目与剧集页面
2. 工作台数据接入
3. 分镜与资产可视化
4. Preview & QA 视图
5. 导出页

---

## 6. Iteration 0：文档冻结与建模清单

时间建议：第 0 周

### 目标

让团队对边界、系统形态和交付节奏达成一致。

### 任务包

#### Product / UX

1. 冻结 V1 scope
2. 冻结主页面列表
3. 冻结单集包定义

#### Backend / Data

1. 列出现有模型
2. 列出缺失模型
3. 输出 migration backlog

#### Workflow / Runtime

1. 冻结 stage 列表
2. 冻结 workflow 状态机
3. 冻结 rerun 粒度

#### Frontend / Workspace

1. 冻结 workspace 最小字段集合
2. 冻结前端视图分区

### DoD

1. 文档三件套存在：roadmap / scope / blueprint
2. 缺失对象清单明确
3. 第一轮开发不再讨论大边界问题

---

## 7. Iteration 1：核心对象与真实 Workspace 骨架

时间建议：第 1-2 周

### 目标

把系统从“有壳子”推进到“有真实业务骨架”。

### 本轮交付结果

1. `StageTask` 有真实模型
2. `Shot` 有真实模型
3. `ReviewDecision` 有真实模型
4. workspace 不再依赖占位 shot 数据
5. 前端能看到真实 workflow / document / shot / asset 基础状态

### 任务包

#### Product / UX

1. 定义 workspace 的最小展示状态
2. 定义 stage 状态展示规则
3. 定义 review pending 的 UI 占位

#### Backend / Data

1. 新增 `StageTask` 模型与 migration
2. 新增 `Shot` 模型与 migration
3. 新增 `ReviewDecision` 模型与 migration
4. 补充 repository / schema / response DTO
5. 重构 workspace 聚合逻辑

#### Workflow / Runtime

1. 让 workflow 可以写入 WorkflowRun
2. 让每个 stage 生成 StageTask 记录
3. 为 storyboard stage 提供 shot 持久化接口

#### Frontend / Workspace

1. 工作台接入真实 workspace API
2. Storyboard 区展示真实 shot 列表
3. Workflow 区展示当前 stage 状态
4. QA / Review 区展示空态和待接入态

### DoD

1. 数据库中存在真实 `stage_tasks`、`shots`、`review_decisions` 表或等价结构
2. workspace 接口返回真实 shot 数据
3. 前端不再依赖硬编码 shot 数组
4. 可以通过 API 看到 workflow 和 stage 的基础状态

### 风险提醒

1. 不要在这一轮就接入复杂 provider
2. 不要同时做媒体链路
3. 不要把 review 决策逻辑直接写死在前端

---

## 8. Iteration 2：文本主链路 Mock 打通

时间建议：第 3-4 周

### 目标

跑通：

`素材 -> brief -> story_bible -> character -> script -> storyboard`

### 本轮交付结果

1. episode_workflow 可以真实跑过文本链路
2. 每个文本 stage 都会提交 document
3. script / storyboard 能被 workspace 展示
4. storyboards 产出真实 shots

### 任务包

#### Product / UX

1. 定义 Brief / Character / Script / Storyboard 编辑流程
2. 定义字段锁定行为和提示文案

#### Backend / Data

1. document 版本化规则落地
2. document 编辑接口落地
3. document 锁定机制初版落地

#### Workflow / Runtime

1. Agent Runtime 注册 brief handler
2. Agent Runtime 注册 story_bible handler
3. Agent Runtime 注册 character handler
4. Agent Runtime 注册 script handler
5. Agent Runtime 注册 storyboard handler
6. 每个 handler 产出真实 document refs

#### Frontend / Workspace

1. Brief 编辑区接真实数据
2. Character / Story Bible 区接真实数据
3. Script 视图接真实数据
4. Storyboard 视图接真实数据

### DoD

1. 一个剧集可以从 start_workflow 跑到 storyboard 完成
2. 所有文本产物入库
3. 每个 stage 有 StageTask 记录
4. storyboard 输出真实 shot 实体
5. 用户可以在前端看到并编辑关键文本产物

### 风险提醒

1. 先追求结构稳定，不追求文本质量极致
2. 不要在这一轮把 prompt 系统做复杂
3. script 失败必须保护旧版本

---

## 9. Iteration 3：Storyboard 到 Asset 工作台

时间建议：第 5-6 周

### 目标

把 storyboard 变成能驱动后续媒体链路的稳定中枢。

### 本轮交付结果

1. shot 结构稳定
2. visual_spec 可落库
3. storyboard 页面具备镜头级工作能力
4. image_render 已有可接入的输入准备

### 任务包

#### Product / UX

1. 定义 shot 卡片字段
2. 定义 shot 锁定与编辑入口
3. 定义 visual spec 与 shot 的关系展示

#### Backend / Data

1. `visual_spec` 文档类型补齐
2. shot 与 visual spec 引用关系补齐
3. 资产与 shot 的关联字段补齐

#### Workflow / Runtime

1. storyboard stage 输出 `visual_spec`
2. 为 image_render stage 组装输入 refs
3. 定义 shot-level rerun input

#### Frontend / Workspace

1. 分镜页显示 shot 详情
2. 分镜页显示 visual constraint 摘要
3. 为后续资产页预留选主资产区

### DoD

1. storyboard 的结果可直接被 image_render 消费
2. visual_spec 已进入真实数据链
3. 每个 shot 都可以作为后续渲染目标

---

## 10. Iteration 4：媒体链路 Alpha

时间建议：第 7-8 周

### 目标

跑通：

`visual_spec -> image_render -> subtitle -> tts -> preview`

### 本轮交付结果

1. 至少一个项目能产生真实 preview
2. 资产进入对象存储与数据库
3. shot 可以关联候选 keyframe
4. preview 能在工作台播放

### 任务包

#### Product / UX

1. 定义 asset 选择交互
2. 定义 preview 展示与失败提示
3. 定义 subtitle / voice 的可见性层级

#### Backend / Data

1. Object Storage 接入
2. 资产 metadata 完整写入
3. 资产选择接口落地

#### Workflow / Runtime

1. Media Runtime 注册 image render worker
2. Media Runtime 注册 subtitle 生成逻辑
3. Media Runtime 注册 tts worker
4. Media Runtime 注册 preview export worker
5. 各 stage 写回 Asset refs

#### Frontend / Workspace

1. 分镜与资产页展示候选 keyframe
2. 支持主资产选择
3. Preview 页接入真实 preview 资产

### DoD

1. 至少一条样板项目链路能生成 preview
2. image / subtitle / audio / preview 资产都可追踪
3. 工作台能展示主资产与候选资产

### 风险提醒

1. 一轮只接一套 provider 组合
2. 不要引入多 provider 自动路由
3. 先把链路打通，再优化质量

---

## 11. Iteration 5：QA / Review / Rerun 闭环

时间建议：第 9-10 周

### 目标

把系统从“能生成”升级为“能返工、能审核、能放行”。

### 本轮交付结果

1. QA Runtime 产出真实 QA 报告
2. Human Review Gate 接入 workflow
3. rerun_workflow 可用
4. 问题能映射到返工节点

### 任务包

#### Product / UX

1. 定义 QA 报告结构展示
2. 定义审核通过 / 打回 / 拒绝交互
3. 定义 rerun 入口与提示

#### Backend / Data

1. QAReport 字段补强
2. ReviewDecision 提交接口落地
3. rerun 请求数据结构补强

#### Workflow / Runtime

1. QA Runtime 实现 rule checks
2. QA Runtime 实现基础 semantic checks
3. review gate 控制 workflow 暂停与恢复
4. rerun_workflow 创建新 WorkflowRun 和新 StageTask

#### Frontend / Workspace

1. Preview & QA 页显示真实报告
2. 审核按钮接真实接口
3. rerun 入口接真实接口
4. rerun 后刷新新版本状态

### DoD

1. QA 失败会阻止 final export
2. 审核动作会改变 workflow 状态
3. 指定 shot 可以重跑 image_render
4. rerun 不覆盖非目标对象
5. 用户能看懂为什么被打回

---

## 12. Iteration 6：Final Export 与 Pilot Ready 强化

时间建议：第 11-12 周

### 目标

让系统具备最小 pilot 条件。

### 本轮交付结果

1. final export 闭环打通
2. 样板项目可重复成功运行
3. 最低可观测能力可用
4. 可以开始小范围试点

### 任务包

#### Product / UX

1. 导出页完成真实接入
2. 导出结果和产物列表展示
3. 样板项目说明与 onboarding 提示

#### Backend / Data

1. `ExportBundle` 或等价记录落地
2. export 历史可查询
3. workflow / stage / asset 基础统计可查询

#### Workflow / Runtime

1. export_final stage 落地
2. trace / lineage / rerun history 基础能力落地
3. provider 失败降级规则补强

#### Frontend / Workspace

1. 导出页显示 final 结果
2. 工作台显示最近失败 stage
3. 工作台显示 rerun 后新旧版本差异入口占位

### DoD

1. 最终单集包可导出
2. 一条样板链路可重复成功运行至少两次
3. 能回答“卡在哪一步”“为什么失败”“重跑后发生了什么”
4. pilot 演示不需要工程师手工改库救火

---

## 13. 并行任务策略

## 13.1 可以并行的任务

1. 前端 workspace 接入 与 后端 workspace 聚合改造
2. 文本 stage handler 开发 与 document 编辑接口开发
3. image worker 开发 与 对象存储接入
4. QA 页面开发 与 QA Runtime 初版开发

## 13.2 不建议并行的任务

1. 在 `StageTask` 未落地前并行做复杂 workflow
2. 在 `Shot` 未落地前并行做 image_render 正式链路
3. 在 review gate 未落地前并行做 final export

---

## 14. 每轮验收模板

每轮结束都按下面模板检查：

### 能力是否成立

1. 这一轮真正打通了哪条能力链
2. 用户能多完成什么动作
3. 系统新增了哪些真实对象

### 风险是否下降

1. 哪个失败现在可以定位
2. 哪个返工现在可以局部完成
3. 哪个假数据已经被替换掉

### 演示是否可信

1. 前端看到的是不是系统真实状态
2. 演示流程是不是不依赖手工改数据
3. 样板项目能不能重复跑

---

## 15. 推荐任务优先级

如果开发资源有限，严格按以下顺序推进：

1. `StageTask`
2. `Shot`
3. `ReviewDecision`
4. workspace 真聚合
5. episode_workflow 文本链路
6. visual_spec + storyboard 稳定化
7. image_render / subtitle / tts / preview
8. QA / rerun / review gate
9. final export
10. trace / pilot 强化

---

## 16. 里程碑通过条件

## M1 通过条件

1. 文本链路走到 storyboard
2. workspace 可显示真实 documents 与 shots

## M2 通过条件

1. preview 可生成
2. 资产入库可见

## M3 通过条件

1. QA / review / rerun / export 闭环可用
2. 单集包能真正交付

## M4 通过条件

1. 样板项目稳定重复运行
2. 系统可以进入 pilot 试用

---

## 17. 最终执行结论

这份计划的核心不是“排满任务”，而是让开发始终围绕一个稳定逻辑推进：

> 先补核心对象，再跑 workflow，再让前端看到真实状态，再逐步把 mock 替换成真实执行，最终把单集包交付闭环做实。

如果后续执行过程中出现新需求，优先问一句：

**它是帮助我们更快做成 M1 / M2 / M3，还是在分散主链路注意力？**

如果是后者，就不进入当前迭代。
