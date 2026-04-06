# Requirements Document

## Introduction

本需求文档定义 AI 漫剧创作者工作台的文本主链路功能。文本主链路是系统的核心能力，负责将原始素材（小说章节或剧本）转化为结构化的分镜脚本，为后续的媒体生成提供基础。

本功能是 Iteration 2 的交付目标，旨在打通从素材输入到分镜输出的完整文本生产流程，验证 workflow 编排、agent 协作和数据持久化的可行性。

## Glossary

- **System**: AI 漫剧创作者工作台
- **Episode Workflow**: 单集生产的完整工作流程
- **Stage**: Workflow 中的一个执行阶段
- **Agent Runtime**: 负责执行文本型 stage 的运行时环境
- **Document**: 结构化的文本产物，包括 brief、story_bible、character_profile、script_draft、visual_spec 等
- **Shot**: 分镜级对象，包含镜头编号、时长、角色、动作、视觉约束等信息
- **StageTask**: 单个 stage 的执行记录，是 workflow 的最小执行粒度
- **Locked Refs**: 被锁定的引用对象，后续 stage 不能修改
- **Brief**: 项目改编方向文档，包含题材、受众、卖点、风险等信息
- **Story Bible**: 世界观和故事规则文档，是全局一致性的基础
- **Character Profile**: 角色卡文档，包含角色目标、动机、说话风格、视觉锚点等
- **Script Draft**: 单集剧本文档，包含场次结构、台词、情绪节拍等
- **Visual Spec**: 视觉规格文档，包含每个镜头的视觉约束和渲染要求
- **Workspace**: 工作台聚合视图，展示项目、剧集、文档、镜头、资产等信息

## Requirements

### Requirement 1

**User Story:** 作为创作者，我希望系统能够启动 episode workflow 并执行文本主链路，以便将原始素材转化为可用的分镜脚本。

#### Acceptance Criteria

1. WHEN 用户通过 API 启动 episode workflow THEN the System SHALL 创建 WorkflowRun 记录并开始执行文本主链路 stages
2. WHEN workflow 执行过程中 THEN the System SHALL 按照 brief → story_bible → character → script → storyboard 的顺序依次执行各个 stage
3. WHEN 某个 stage 执行完成 THEN the System SHALL 创建对应的 StageTask 记录并更新状态
4. WHEN 所有文本 stages 执行完成 THEN the System SHALL 将 workflow 状态更新为相应的完成状态
5. WHEN workflow 执行失败 THEN the System SHALL 记录失败原因并保留已生成的中间产物

### Requirement 2

**User Story:** 作为创作者，我希望 Brief Agent 能够分析原始素材并生成改编方向文档，以便确认项目的核心方向和风险。

#### Acceptance Criteria

1. WHEN Brief Agent 接收到原始素材和项目配置 THEN the System SHALL 提取故事主线、角色关系和核心冲突
2. WHEN Brief Agent 生成 brief 文档 THEN the System SHALL 包含题材、目标受众、核心卖点、改编风险、目标风格等结构化字段
3. WHEN brief 文档生成完成 THEN the System SHALL 将文档持久化到数据库并关联到对应的 episode 和 stage_task
4. WHEN brief 文档包含必填字段缺失 THEN the System SHALL 拒绝提交并返回校验错误
5. WHEN brief 生成失败 THEN the System SHALL 保留错误信息并允许重试

### Requirement 3

**User Story:** 作为创作者，我希望 Story Bible Agent 能够建立世界观和故事规则，以便为后续创作提供一致性约束。

#### Acceptance Criteria

1. WHEN Story Bible Agent 接收到 brief 和原始素材摘要 THEN the System SHALL 提取世界规则、时间线和关系基线
2. WHEN Story Bible Agent 生成 story_bible 文档 THEN the System SHALL 包含世界规则、禁止冲突项和关键设定等结构化字段
3. WHEN story_bible 文档生成完成 THEN the System SHALL 将文档持久化并标记为后续 stages 的约束来源
4. WHEN story_bible 包含的规则与 brief 冲突 THEN the System SHALL 在 warnings 中记录冲突项
5. WHEN story_bible 生成失败 THEN the System SHALL 保留 brief 文档不受影响

### Requirement 4

**User Story:** 作为创作者，我希望 Character Agent 能够生成角色卡，以便稳定角色定义并为后续创作提供角色约束。

#### Acceptance Criteria

1. WHEN Character Agent 接收到 brief 和 story_bible THEN the System SHALL 识别主要角色并为每个角色生成结构化卡片
2. WHEN Character Agent 生成 character_profile 文档 THEN the System SHALL 包含角色目标、动机、说话风格、视觉锚点和关系表等字段
3. WHEN character_profile 文档生成完成 THEN the System SHALL 将关键字段标记为可锁定状态
4. WHEN 角色视觉锚点缺失 THEN the System SHALL 在 warnings 中记录缺失项但仍允许提交
5. WHEN character_profile 生成失败 THEN the System SHALL 保留已生成的 brief 和 story_bible 文档

### Requirement 5

**User Story:** 作为创作者，我希望 Script Agent 能够将素材改编成单集剧本，以便推进到分镜阶段。

#### Acceptance Criteria

1. WHEN Script Agent 接收到 brief、story_bible 和 character_profile THEN the System SHALL 生成包含场次结构和台词的剧本
2. WHEN Script Agent 生成 script_draft 文档 THEN the System SHALL 包含场次列表、每场目标、台词、情绪节拍等结构化字段
3. WHEN script_draft 文档生成完成 THEN the System SHALL 将文档持久化并更新 episode 的 script_version
4. WHEN script_draft 与 character_profile 中的角色设定冲突 THEN the System SHALL 在 warnings 中记录冲突但仍允许提交
5. WHEN script 生成失败 THEN the System SHALL 保留旧版本 script_draft 不被覆盖

### Requirement 6

**User Story:** 作为创作者，我希望 Storyboard Agent 能够将剧本拆分成镜头级执行计划，以便为后续媒体生成提供精确指导。

#### Acceptance Criteria

1. WHEN Storyboard Agent 接收到 script_draft 和平台约束 THEN the System SHALL 将剧本拆分成结构化的 shot 列表
2. WHEN Storyboard Agent 生成 shots THEN the System SHALL 为每个 shot 分配唯一 id、镜头编号、时长、景别、角色、动作和视觉约束
3. WHEN shots 生成完成 THEN the System SHALL 将 shot 记录持久化到数据库并关联到 episode
4. WHEN Storyboard Agent 生成 visual_spec 文档 THEN the System SHALL 包含每个 shot 的渲染规格和视觉约束
5. WHEN shots 的总时长超过目标时长 THEN the System SHALL 在 warnings 中记录超时但仍允许提交

### Requirement 7

**User Story:** 作为创作者，我希望每个 agent 都能进行内容一致性检查，以便防止生成内容偏离原始设定。

#### Acceptance Criteria

1. WHEN 任何 agent 生成内容 THEN the System SHALL 检查生成内容是否与 brief 核心卖点一致
2. WHEN 任何 agent 生成内容涉及角色 THEN the System SHALL 检查角色行为是否与 character_profile 设定一致
3. WHEN 任何 agent 生成内容涉及世界规则 THEN the System SHALL 检查是否违反 story_bible 中的禁止冲突项
4. WHEN 一致性检查发现偏离 THEN the System SHALL 在 warnings 中记录偏离项并提供修正建议
5. WHEN locked_refs 中的字段被修改 THEN the System SHALL 拒绝提交并返回校验错误

### Requirement 8

**User Story:** 作为创作者，我希望能够通过 workspace API 查看文本主链路的执行状态和产物，以便了解当前进度和结果。

#### Acceptance Criteria

1. WHEN 用户请求 workspace 数据 THEN the System SHALL 返回 project、episode、latest workflow、current documents 和 shots 的聚合视图
2. WHEN workspace 包含 documents THEN the System SHALL 按类型分组并返回最新版本的文档内容
3. WHEN workspace 包含 shots THEN the System SHALL 返回完整的 shot 列表及其关联的视觉约束
4. WHEN workspace 包含 workflow 状态 THEN the System SHALL 返回当前执行的 stage 和各 stage 的状态
5. WHEN workspace 数据不存在 THEN the System SHALL 返回 404 错误

### Requirement 9

**User Story:** 作为创作者，我希望能够编辑已生成的文档，以便修正 AI 生成的错误或调整内容方向。

#### Acceptance Criteria

1. WHEN 用户通过 API 编辑 document THEN the System SHALL 创建新版本而不是覆盖旧版本
2. WHEN document 被编辑 THEN the System SHALL 记录编辑来源（用户编辑 vs AI 生成）
3. WHEN document 包含 locked 字段 THEN the System SHALL 拒绝对 locked 字段的修改
4. WHEN document 编辑后 THEN the System SHALL 更新 document 的 updated_at 时间戳
5. WHEN document 编辑导致 schema 校验失败 THEN the System SHALL 拒绝编辑并返回校验错误

### Requirement 10

**User Story:** 作为开发者，我希望每个 agent 都遵循统一的内部流水线，以便保证代码结构一致性和可维护性。

#### Acceptance Criteria

1. WHEN 任何 agent 执行 THEN the System SHALL 按照 Loader → Normalizer → Planner → Generator → Critic → Validator → Committer 的顺序执行
2. WHEN Loader 阶段执行 THEN the System SHALL 从数据库加载 input_refs 和 locked_refs
3. WHEN Generator 阶段执行 THEN the System SHALL 调用 LLM 并传入 stage-specific prompt 和 output schema
4. WHEN Validator 阶段执行 THEN the System SHALL 校验输出的 JSON schema 和必填字段
5. WHEN Committer 阶段执行 THEN the System SHALL 将结果持久化到数据库并返回 document_refs

### Requirement 11

**User Story:** 作为开发者，我希望 workflow 编排逻辑与 agent 执行逻辑分离，以便独立测试和维护各个组件。

#### Acceptance Criteria

1. WHEN workflow 编排器决定执行某个 stage THEN the System SHALL 构造 StageTaskInput 并调用对应的 agent handler
2. WHEN agent handler 执行完成 THEN the System SHALL 返回 StageTaskOutput 而不是直接修改数据库状态
3. WHEN workflow 编排器接收到 StageTaskOutput THEN the System SHALL 根据 status 决定是否继续下一个 stage
4. WHEN stage 执行失败 THEN the System SHALL 由 workflow 编排器决定是否重试而不是由 agent 自行重试
5. WHEN workflow 需要暂停等待人工审核 THEN the System SHALL 由 workflow 编排器控制暂停而不是由 agent 控制

### Requirement 12

**User Story:** 作为开发者，我希望系统能够记录详细的执行日志和指标，以便追踪问题和优化性能。

#### Acceptance Criteria

1. WHEN 任何 stage 开始执行 THEN the System SHALL 记录 stage_type、started_at 和 attempt_no
2. WHEN 任何 stage 执行完成 THEN the System SHALL 记录 finished_at、duration_ms 和 token_usage
3. WHEN 任何 stage 执行失败 THEN the System SHALL 记录 error_code、error_message 和失败时的上下文信息
4. WHEN LLM 被调用 THEN the System SHALL 记录 prompt、model、temperature 和 response
5. WHEN document 被提交 THEN the System SHALL 记录 document_type、version 和 created_by
