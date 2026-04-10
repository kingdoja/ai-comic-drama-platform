# Iteration 5: QA / Review / Rerun 闭环 - 设计文档

## 概述

本迭代实现从"能生成"到"能返工、能审核、能放行"的完整质量保证闭环。通过 QA Runtime、Review Gate 和 Rerun 功能，建立可控的迭代优化机制。

关键设计原则：
- **自动化优先**: QA 检查自动执行，减少人工负担
- **人工关卡**: 关键节点需要人工审核决策
- **局部重跑**: 支持 Shot 级别的精细化重跑
- **数据保护**: Rerun 不破坏现有数据
- **历史追踪**: 完整记录迭代历史

## 架构

### QA / Review / Rerun 数据流

```
Workflow Execution
    ↓
Stage Completion
    ↓
QA Runtime (if qa stage)
    ↓
QA Report Generation
    ↓
Review Gate (if review_required)
    ↓
Human Review Decision
    ↓
Decision: Approved → Continue Workflow
Decision: Rejected → Terminate Workflow
Decision: Revision → Trigger Rerun
    ↓
Rerun Workflow
    ↓
Execute from specified stage
    ↓
Generate new versions
```

### 组件关系

```
┌─────────────────────────────────────────────────────────┐
│                  Workflow Orchestrator                  │
│  控制 Stage 执行、QA 检查和 Review Gate                 │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─────────────────┬────────────────────┐
                   ↓                 ↓                    ↓
         ┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
         │ QA Runtime       │ │ Review Gate  │ │ Rerun Service   │
         │                  │ │              │ │                 │
         └────────┬─────────┘ └──────┬───────┘ └────────┬────────┘
                  │                  │                   │
                  ↓                  ↓                   ↓
         ┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
         │ Rule Checker     │ │ Review       │ │ Workflow        │
         │ Semantic Checker │ │ Repository   │ │ Repository      │
         └────────┬─────────┘ └──────┬───────┘ └────────┬────────┘
                  │                  │                   │
                  └──────────────────┴───────────────────┘
                                     ↓
                   ┌──────────────────────────────────────┐
                   │      QA Report Repository            │
                   │  存储所有 QA 检查结果                │
                   └──────────────────────────────────────┘
```


## 组件和接口

### QA Runtime

```python
class QARuntime:
    """
    QA 运行时，负责执行质量检查。
    
    职责：
    1. 执行规则检查
    2. 执行语义检查
    3. 生成 QA 报告
    4. 决定是否阻止 workflow 继续
    """
    
    def execute_qa(
        self,
        episode_id: UUID,
        stage_task_id: UUID,
        qa_type: str
    ) -> QAResult:
        """
        执行 QA 检查。
        
        Args:
            episode_id: Episode ID
            stage_task_id: StageTask ID
            qa_type: QA 类型 (rule_check/semantic_check/asset_check)
            
        Returns:
            QAResult: 检查结果
        """
        pass
    
    def check_rules(
        self,
        target: Union[DocumentModel, ShotModel, AssetModel]
    ) -> List[Issue]:
        """
        执行规则检查。
        
        检查项：
        - 必填字段完整性
        - 数据格式正确性
        - 数值范围合理性
        - 结构完整性
        """
        pass
    
    def check_semantics(
        self,
        episode_id: UUID,
        target: DocumentModel
    ) -> List[Issue]:
        """
        执行语义检查。
        
        检查项：
        - 角色一致性
        - 世界观一致性
        - 情节连贯性
        - 逻辑合理性
        """
        pass
    
    def check_asset_quality(
        self,
        asset: AssetModel
    ) -> List[Issue]:
        """
        检查资产质量。
        
        检查项：
        - 文件完整性
        - 格式正确性
        - 技术指标
        - 可用性
        """
        pass
```


### Review Gate Service

```python
class ReviewGateService:
    """
    审核关卡服务，处理人工审核流程。
    
    职责：
    1. 暂停 workflow 等待审核
    2. 处理审核决策
    3. 恢复或终止 workflow
    4. 记录审核历史
    """
    
    def pause_for_review(
        self,
        stage_task_id: UUID
    ) -> None:
        """
        暂停 workflow 等待审核。
        
        更新 StageTask:
        - review_status = "pending"
        - task_status = "review_pending"
        """
        pass
    
    def submit_review(
        self,
        stage_task_id: UUID,
        reviewer_user_id: UUID,
        decision: str,
        comment: str = None,
        payload: dict = None
    ) -> ReviewDecisionModel:
        """
        提交审核决策。
        
        Args:
            stage_task_id: StageTask ID
            reviewer_user_id: 审核人 ID
            decision: 决策 (approved/rejected/revision_required)
            comment: 审核意见
            payload: 额外数据（如 rerun 参数）
            
        Returns:
            ReviewDecisionModel: 审核记录
        """
        pass
    
    def process_decision(
        self,
        review: ReviewDecisionModel
    ) -> None:
        """
        处理审核决策。
        
        - approved: 恢复 workflow
        - rejected: 终止 workflow
        - revision_required: 触发 rerun
        """
        pass
```


### Rerun Service

```python
class RerunService:
    """
    重跑服务，处理 workflow 和 Shot 级别的重跑。
    
    职责：
    1. 创建 rerun WorkflowRun
    2. 执行 workflow rerun
    3. 执行 Shot 级别 rerun
    4. 保护现有数据
    """
    
    def rerun_workflow(
        self,
        episode_id: UUID,
        from_stage: str,
        user_id: UUID = None,
        reason: str = None
    ) -> WorkflowRunModel:
        """
        从指定 Stage 重跑 workflow。
        
        Args:
            episode_id: Episode ID
            from_stage: 起始 Stage
            user_id: 发起人 ID
            reason: 重跑原因
            
        Returns:
            WorkflowRunModel: 新的 WorkflowRun
            
        流程：
        1. 创建新 WorkflowRun，设置 rerun_from_stage
        2. 从 from_stage 开始执行所有后续 Stage
        3. 保留 from_stage 之前的所有产物
        4. 生成新版本的产物
        """
        pass
    
    def rerun_shots(
        self,
        episode_id: UUID,
        shot_ids: List[UUID],
        stage_type: str,
        user_id: UUID = None
    ) -> WorkflowRunModel:
        """
        重跑指定 Shot 的指定 Stage。
        
        Args:
            episode_id: Episode ID
            shot_ids: Shot ID 列表
            stage_type: Stage 类型 (image_render/tts)
            user_id: 发起人 ID
            
        Returns:
            WorkflowRunModel: 新的 WorkflowRun
            
        流程：
        1. 创建新 WorkflowRun
        2. 只处理指定的 Shot
        3. 为这些 Shot 生成新 Asset
        4. 保留其他 Shot 的现有 Asset
        """
        pass
    
    def get_rerun_history(
        self,
        episode_id: UUID
    ) -> List[WorkflowRunModel]:
        """
        获取 rerun 历史。
        
        Returns:
            按时间倒序的 WorkflowRun 列表
        """
        pass
```


## 数据模型

### QAReport 字段说明

```python
class QAReportModel:
    id: UUID
    project_id: UUID
    episode_id: UUID
    stage_task_id: UUID  # 关联的 StageTask
    qa_type: str  # rule_check, semantic_check, asset_check
    target_ref_type: str  # document, shot, asset, episode
    target_ref_id: UUID  # 检查目标的 ID
    result: str  # passed, failed, warning
    score: float  # 质量评分 (0-100)
    severity: str  # info, minor, major, critical
    issue_count: int  # 问题数量
    issues_jsonb: list  # 问题详情列表
    # [{
    #   "type": "missing_field",
    #   "severity": "major",
    #   "location": "brief.genre",
    #   "message": "Genre field is required",
    #   "suggestion": "Add genre information"
    # }]
    rerun_stage_type: str  # 建议重跑的 Stage
    created_at: datetime
```

### ReviewDecision 字段说明

```python
class ReviewDecisionModel:
    id: UUID
    project_id: UUID
    episode_id: UUID
    stage_task_id: UUID
    reviewer_user_id: UUID
    decision: str  # approved, rejected, revision_required
    comment_text: str  # 审核意见
    payload_jsonb: dict  # 额外数据
    # {
    #   "rerun_from_stage": "image_render",
    #   "rerun_shot_ids": ["uuid1", "uuid2"],
    #   "reason": "需要调整角色表情"
    # }
    created_at: datetime
```

### WorkflowRun 扩展字段

```python
class WorkflowRunModel:
    # 现有字段
    id: UUID
    project_id: UUID
    episode_id: UUID
    workflow_kind: str
    status: str
    
    # Rerun 相关字段
    rerun_from_stage: str  # 从哪个 Stage 开始重跑
    parent_workflow_run_id: UUID  # 父 WorkflowRun (如果是 rerun)
    rerun_reason: str  # 重跑原因
    rerun_shot_ids_jsonb: list  # 指定重跑的 Shot IDs
```


## 正确性属性

*属性是系统在所有有效执行中应该保持的特征或行为，是人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: QA 报告完整性
*对于任何*完成的 QA 检查，应该生成包含所有检查项结果的 QAReport
**验证需求**: 需求 1.1, 1.2, 1.3

### 属性 2: Review 决策唯一性
*对于任何*StageTask，最多只有一个有效的 ReviewDecision
**验证需求**: 需求 6.1, 6.4

### 属性 3: Rerun 数据隔离
*对于任何*rerun WorkflowRun，不应该修改 rerun_from_stage 之前的任何产物
**验证需求**: 需求 9.2, 9.3

### 属性 4: QA 阻止导出
*对于任何*QA 结果为 "failed" 且 severity 为 "critical" 的 Episode，不应该允许执行 export_final
**验证需求**: 需求 13.1, 13.2

### 属性 5: Review Gate 暂停
*对于任何*标记为 review_required 的 StageTask，workflow 应该在该 Stage 完成后暂停
**验证需求**: 需求 5.1, 5.2

### 属性 6: Shot Rerun 隔离
*对于任何*Shot 级别 rerun，只有指定的 Shot 应该生成新 Asset，其他 Shot 的 Asset 保持不变
**验证需求**: 需求 8.1, 8.3

### 属性 7: Rerun 版本递增
*对于任何*rerun 生成的 Document 或 Asset，版本号应该大于之前的版本
**验证需求**: 需求 9.5

### 属性 8: QA 问题严重性排序
*对于任何*QA 报告，issues 列表应该按 severity 排序（critical > major > minor > info）
**验证需求**: 需求 10.2


## 错误处理

### QA 检查超时

**场景**: QA 检查执行时间过长

**处理**:
1. 设置 30 秒超时限制
2. 超时后标记为 "timeout"
3. 记录已完成的检查项
4. 允许用户重试

### Review 提交失败

**场景**: 用户提交审核决策时网络异常

**处理**:
1. 保留用户输入的决策和意见
2. 提示用户重试
3. 不改变 StageTask 状态
4. 记录失败日志

### Rerun 执行失败

**场景**: Rerun 过程中 Provider 调用失败

**处理**:
1. 保留失败前的所有产物
2. 记录失败的 Stage 和原因
3. 不覆盖任何现有数据
4. 允许用户再次 rerun

### 数据一致性保护

**场景**: Rerun 过程中系统异常

**处理**:
1. 使用数据库事务保护
2. 失败时回滚所有更改
3. 保持现有数据完整性
4. 记录异常堆栈

## 测试策略

### 单元测试

1. **QA Runtime 测试**
   - 测试规则检查逻辑
   - 测试语义检查逻辑
   - 测试资产质量检查
   - 测试 QA 报告生成

2. **Review Gate 测试**
   - 测试 workflow 暂停
   - 测试审核决策处理
   - 测试 workflow 恢复
   - 测试审核历史记录

3. **Rerun Service 测试**
   - 测试 workflow rerun
   - 测试 Shot 级别 rerun
   - 测试数据隔离
   - 测试版本管理

### 集成测试

1. **端到端 QA 流程测试**
   - 创建测试数据
   - 执行 QA 检查
   - 验证 QA 报告
   - 验证阻止逻辑

2. **Review 流程测试**
   - 触发 review gate
   - 提交审核决策
   - 验证 workflow 状态变化
   - 验证 rerun 触发

3. **Rerun 流程测试**
   - 执行 workflow rerun
   - 验证数据隔离
   - 验证版本管理
   - 验证历史记录


## 性能考虑

### QA 检查性能

- 规则检查: < 5 秒
- 语义检查: < 15 秒
- 资产检查: < 10 秒
- 总体目标: < 30 秒

### Rerun 性能

- Shot 级别 rerun: 只调用必要的 Provider
- 批量 rerun: 支持并行处理（最多 5 个并发）
- 数据查询: 使用索引优化

### 数据库优化

- qa_reports 索引: (episode_id, created_at DESC)
- review_decisions 索引: (stage_task_id, created_at DESC)
- workflow_runs 索引: (episode_id, rerun_from_stage, created_at DESC)

## 可扩展性

### 支持更多 QA 检查类型

通过扩展 QARuntime 即可支持新检查：
- 内容审核（敏感词检查）
- 版权检查
- 品牌一致性检查
- 自定义规则检查

### 支持更多 Review 决策类型

扩展 decision 枚举：
- conditional_approval（有条件通过）
- escalate（升级审核）
- defer（延期决策）

### 支持更细粒度的 Rerun

扩展 rerun 目标：
- Document 字段级别 rerun
- Asset 类型级别 rerun
- 时间范围 rerun

## 安全性

### 审核权限控制

- 验证审核人权限
- 记录审核操作日志
- 防止未授权审核

### Rerun 权限控制

- 限制 rerun 发起人
- 记录 rerun 操作日志
- 防止恶意 rerun

### 数据保护

- Rerun 不删除历史数据
- 使用事务保护数据一致性
- 定期备份关键数据

## 实现优先级

### 高优先级（本迭代必须完成）

1. QA Runtime 基础框架
2. 规则检查实现
3. Review Gate 实现
4. Workflow Rerun 功能
5. QA 报告展示

### 中优先级（本迭代尽量完成）

1. 语义一致性检查
2. Shot 级别 Rerun
3. Review 界面集成
4. Rerun 历史追踪

### 低优先级（可推迟到后续迭代）

1. 媒体资产质量检查
2. 高级语义检查
3. 性能优化
4. 自定义规则引擎

