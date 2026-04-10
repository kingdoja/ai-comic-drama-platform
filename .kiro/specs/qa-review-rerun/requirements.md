# Iteration 5: QA / Review / Rerun 闭环 - 需求文档

## 简介

本迭代的目标是把系统从"能生成"升级为"能返工、能审核、能放行"。通过实现 QA Runtime、Human Review Gate 和 Rerun 功能，建立完整的质量保证和迭代优化闭环。

本迭代是系统从"单向生产"向"可控迭代"转型的关键里程碑，将首次实现人工介入、质量检查和局部重跑能力。

## 术语表

- **QA Runtime**: 质量保证运行时，负责执行自动化质量检查
- **QA Report**: 质量检查报告，记录检查结果、问题和建议
- **Rule Check**: 规则检查，验证内容是否符合预定义规则
- **Semantic Check**: 语义检查，验证内容的语义一致性和合理性
- **Review Gate**: 审核关卡，workflow 中需要人工审核的节点
- **Review Decision**: 审核决策，人工审核的结果（通过/打回/拒绝）
- **Rerun**: 重跑，从指定 Stage 重新执行 workflow
- **Partial Rerun**: 局部重跑，只重跑指定的 Shot 或资产
- **Workflow Pause**: Workflow 暂停，等待人工审核
- **Workflow Resume**: Workflow 恢复，审核通过后继续执行
- **Issue**: 问题，QA 检查发现的具体问题项
- **Severity**: 严重程度，问题的严重等级（critical/major/minor/info）
- **Target Reference**: 目标引用，QA 检查的目标对象（Document/Shot/Asset）


## 需求

### 需求 1: QA Runtime 基础框架

**用户故事**: 作为系统开发者，我想要实现 QA Runtime 框架，以便自动检查生成内容的质量。

#### 验收标准

1. WHEN QA Stage 执行 THEN System SHALL 创建 QAReport 记录并记录检查结果
2. WHEN QA 检查完成 THEN System SHALL 将结果写入 QAReport 的 issues_jsonb 字段
3. WHEN QA 发现问题 THEN System SHALL 记录问题的 severity、issue_count 和详细描述
4. WHEN QA 检查失败 THEN System SHALL 设置 result 为 "failed" 并记录失败原因
5. WHEN QA 检查通过 THEN System SHALL 设置 result 为 "passed" 并允许 workflow 继续

### 需求 2: 规则检查实现

**用户故事**: 作为内容创作者，我想要系统自动检查内容是否符合预定义规则，以便及早发现格式和结构问题。

#### 验收标准

1. WHEN 检查 Brief THEN System SHALL 验证必填字段是否完整
2. WHEN 检查 Character Profile THEN System SHALL 验证角色数量是否符合要求
3. WHEN 检查 Script THEN System SHALL 验证场景和对白结构是否正确
4. WHEN 检查 Storyboard THEN System SHALL 验证 Shot 数量和时长是否合理
5. WHEN 规则检查失败 THEN System SHALL 记录具体违反的规则和位置

### 需求 3: 语义一致性检查

**用户故事**: 作为内容创作者，我想要系统检查内容的语义一致性，以便发现逻辑矛盾和不合理之处。

#### 验收标准

1. WHEN 检查角色一致性 THEN System SHALL 验证角色在不同文档中的描述是否一致
2. WHEN 检查世界观一致性 THEN System SHALL 验证内容是否违反 Story Bible 的设定
3. WHEN 检查情节连贯性 THEN System SHALL 验证场景转换是否合理
4. WHEN 发现语义问题 THEN System SHALL 记录问题类型、位置和建议修改方向
5. WHEN 语义检查完成 THEN System SHALL 生成可读的问题摘要


### 需求 4: 媒体资产质量检查

**用户故事**: 作为内容创作者，我想要系统检查生成的媒体资产质量，以便发现技术问题。

#### 验收标准

1. WHEN 检查图像资产 THEN System SHALL 验证分辨率、格式和文件完整性
2. WHEN 检查音频资产 THEN System SHALL 验证时长、格式和音质指标
3. WHEN 检查字幕资产 THEN System SHALL 验证时间轴连续性和文本完整性
4. WHEN 检查预览视频 THEN System SHALL 验证视频可播放性和基础质量指标
5. WHEN 资产检查失败 THEN System SHALL 记录失败的资产 ID 和具体问题

### 需求 5: Review Gate 实现

**用户故事**: 作为内容创作者，我想要在关键节点进行人工审核，以便控制内容质量和方向。

#### 验收标准

1. WHEN Stage 标记为 review_required THEN System SHALL 在 Stage 完成后暂停 workflow
2. WHEN Workflow 暂停 THEN System SHALL 更新 StageTask 的 review_status 为 "pending"
3. WHEN 用户提交审核决策 THEN System SHALL 创建 ReviewDecision 记录
4. WHEN 审核决策为 "approved" THEN System SHALL 恢复 workflow 执行
5. WHEN 审核决策为 "rejected" THEN System SHALL 终止 workflow 并记录原因

### 需求 6: 审核决策处理

**用户故事**: 作为内容创作者，我想要提交审核意见和决策，以便指导系统下一步行动。

#### 验收标准

1. WHEN 用户提交审核 THEN System SHALL 记录 reviewer_user_id 和 decision
2. WHEN 用户提供审核意见 THEN System SHALL 保存 comment_text 到 ReviewDecision
3. WHEN 审核决策为 "revision_required" THEN System SHALL 记录需要修改的内容
4. WHEN 审核完成 THEN System SHALL 更新 StageTask 的 review_status
5. WHEN 审核打回 THEN System SHALL 在 QAReport 中记录 rerun_stage_type


### 需求 7: Workflow Rerun 功能

**用户故事**: 作为内容创作者，我想要从指定 Stage 重新执行 workflow，以便修复问题或优化结果。

#### 验收标准

1. WHEN 用户请求 rerun THEN System SHALL 创建新的 WorkflowRun 记录
2. WHEN 创建 rerun WorkflowRun THEN System SHALL 设置 rerun_from_stage 字段
3. WHEN Rerun 执行 THEN System SHALL 从指定 Stage 开始执行后续所有 Stage
4. WHEN Rerun 完成 THEN System SHALL 保留旧版本的 Document 和 Asset
5. WHEN Rerun 失败 THEN System SHALL 记录失败原因并保持旧版本可用

### 需求 8: Shot 级别 Rerun

**用户故事**: 作为内容创作者，我想要只重跑指定的 Shot，以便节省时间和成本。

#### 验收标准

1. WHEN 用户指定 Shot 重跑 THEN System SHALL 只处理指定的 Shot
2. WHEN Shot 重跑执行 THEN System SHALL 为指定 Shot 生成新的 Asset
3. WHEN Shot 重跑完成 THEN System SHALL 保留其他 Shot 的现有 Asset
4. WHEN Shot 重跑失败 THEN System SHALL 保留该 Shot 的旧 Asset
5. WHEN 多个 Shot 重跑 THEN System SHALL 支持批量处理

### 需求 9: Rerun 输入保护

**用户故事**: 作为系统开发者，我想要保护 rerun 的输入数据，以便确保重跑使用正确的上下文。

#### 验收标准

1. WHEN Rerun 执行 THEN System SHALL 使用最新版本的输入 Document
2. WHEN Rerun 某个 Stage THEN System SHALL 不修改该 Stage 之前的产物
3. WHEN Rerun 失败 THEN System SHALL 不覆盖任何现有数据
4. WHEN Rerun 涉及锁定字段 THEN System SHALL 保持锁定字段不变
5. WHEN Rerun 完成 THEN System SHALL 更新版本号并保留历史版本


### 需求 10: QA 报告展示

**用户故事**: 作为内容创作者，我想要查看详细的 QA 报告，以便了解内容存在的问题。

#### 验收标准

1. WHEN 用户查询 QA 报告 THEN System SHALL 返回所有检查项的结果
2. WHEN 展示 QA 报告 THEN System SHALL 按 severity 排序问题列表
3. WHEN 展示问题详情 THEN System SHALL 包含问题位置、描述和建议
4. WHEN QA 失败 THEN System SHALL 高亮显示 critical 和 major 问题
5. WHEN 查看历史报告 THEN System SHALL 支持查询指定 Episode 的所有 QA 记录

### 需求 11: Review 界面集成

**用户故事**: 作为内容创作者，我想要在工作台看到审核入口，以便及时处理待审核内容。

#### 验收标准

1. WHEN Workflow 暂停等待审核 THEN System SHALL 在 Workspace 显示审核提示
2. WHEN 用户进入审核页面 THEN System SHALL 展示待审核的内容和 QA 报告
3. WHEN 用户提交审核决策 THEN System SHALL 提供 approve/reject/revision 选项
4. WHEN 用户选择 revision THEN System SHALL 提供 rerun 入口和参数配置
5. WHEN 审核完成 THEN System SHALL 更新 Workspace 状态并通知用户

### 需求 12: Rerun 历史追踪

**用户故事**: 作为内容创作者，我想要查看 rerun 历史，以便了解内容的迭代过程。

#### 验收标准

1. WHEN 查询 Episode THEN System SHALL 返回所有 WorkflowRun 记录
2. WHEN 展示 WorkflowRun 列表 THEN System SHALL 标识哪些是 rerun
3. WHEN 查看 rerun 详情 THEN System SHALL 显示 rerun_from_stage 和原因
4. WHEN 比较版本 THEN System SHALL 支持查看 rerun 前后的差异
5. WHEN 查询失败历史 THEN System SHALL 展示所有失败的 WorkflowRun 和原因


### 需求 13: QA 与 Export 的关联

**用户故事**: 作为系统开发者，我想要 QA 结果影响导出决策，以便确保只有合格内容可以导出。

#### 验收标准

1. WHEN QA 检查失败 THEN System SHALL 阻止 final export Stage 执行
2. WHEN QA 有 critical 问题 THEN System SHALL 要求修复后才能导出
3. WHEN QA 通过 THEN System SHALL 允许进入 export_final Stage
4. WHEN 导出前 THEN System SHALL 验证最新 QA 报告的状态
5. WHEN 强制导出 THEN System SHALL 记录跳过 QA 的原因和审批人

### 需求 14: 错误恢复和重试

**用户故事**: 作为系统开发者，我想要实现健壮的错误恢复机制，以便处理 QA 和 Rerun 过程中的异常。

#### 验收标准

1. WHEN QA 检查超时 THEN System SHALL 记录超时并标记为 "timeout"
2. WHEN QA 检查异常 THEN System SHALL 记录异常信息并允许重试
3. WHEN Rerun 失败 THEN System SHALL 保留失败记录并允许再次 rerun
4. WHEN Review 提交失败 THEN System SHALL 保留用户输入并提示重试
5. WHEN 系统异常 THEN System SHALL 不破坏现有数据的完整性

### 需求 15: 性能和成本优化

**用户故事**: 作为系统开发者，我想要优化 QA 和 Rerun 的性能，以便提高用户体验。

#### 验收标准

1. WHEN 执行 QA 检查 THEN System SHALL 在 30 秒内完成基础检查
2. WHEN 执行 Shot 级 Rerun THEN System SHALL 只调用必要的 Provider
3. WHEN 批量 Rerun THEN System SHALL 支持并行处理
4. WHEN 查询 QA 报告 THEN System SHALL 使用索引优化查询性能
5. WHEN 记录 Rerun 历史 THEN System SHALL 定期清理过期的临时数据

