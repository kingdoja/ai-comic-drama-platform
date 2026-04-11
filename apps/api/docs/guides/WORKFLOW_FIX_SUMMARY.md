# 工作流测试问题修复总结

## 问题描述

运行 `test_full_workflow.py` 时，工作流在 brief 阶段就暂停了，导致后续的角色、剧本和分镜文档都没有生成。

## 根本原因

`TextWorkflowService.execute_text_chain()` 方法在遇到需要审核的阶段（`review_required=True`）时会暂停工作流并返回，等待人工审核。Brief 和 Storyboard 阶段被设置为需要审核。

```python
# 在 text_workflow_service.py 中
if stage_task.review_required:
    logger.info(f"Stage {stage_type} requires review - pausing workflow")
    stage_task.task_status = "review_pending"
    stage_task.review_status = "pending"
    workflow.status = "waiting_review"
    db.commit()
    return {"workflow_status": workflow.status, "paused_at_stage": stage_type}
```

## 解决方案

### 1. 修改测试脚本添加自动审核循环

在 `test_full_workflow.py` 中添加了自动审核机制：

```python
while iteration < max_iterations:
    # 执行工作流
    result = workflow_service.execute_text_chain(...)
    
    if result["workflow_status"] == "waiting_review":
        paused_stage = result.get("paused_at_stage")
        
        # 查找待审核的 stage_task
        stage_task = stage_task_repo.latest_by_stage(
            episode_id=episode_id,
            stage_type=paused_stage
        )
        
        # 创建审核记录并批准
        review_repo.create(
            stage_task_id=stage_task.id,
            project_id=stage_task.project_id,
            episode_id=stage_task.episode_id,
            decision="approved",
            comment_text="自动测试批准",
            payload_jsonb={},
            commit=False
        )
        
        # 更新状态
        stage_task.review_status = "approved"
        stage_task.task_status = "succeeded"
        workflow.status = "running"
        db.commit()
        
        # 继续下一阶段
        current_stage = next_stage
```

### 2. 安装缺失的依赖

```bash
pip install dashscope
```

## 测试结果

修复后的工作流成功执行了前三个阶段：

1. ✓ **Brief 阶段** - 完成并自动批准
   - 生成了核心创意文档
   - 包含故事类型、目标受众、主要冲突、核心卖点

2. ✓ **Story Bible 阶段** - 完成
   - 生成了世界观和规则文档
   - 包含世界设定、核心规则、叙事风格

3. ✓ **Character 阶段** - 完成
   - 生成了角色档案文档
   - 包含角色信息、目标、视觉锚点

4. ✗ **Script 阶段** - 失败
   - 验证错误：缺少必需的 'dialogue' 字段
   - 这是 Script Agent 输出格式的问题，需要单独修复

## 创建的新文件

### 1. `test_workflow_demo.py`
简化版的演示脚本，只执行前三个阶段（Brief, Story Bible, Character），避免 Script Agent 的格式问题。

运行方式：
```bash
cd apps/api
.venv\Scripts\Activate.ps1
python test_workflow_demo.py
```

## 下一步工作

### 1. 修复 Script Agent
Script Agent 生成的输出缺少 `dialogue` 字段，需要：
- 检查 Script Agent 的 prompt
- 确保输出包含所有必需字段
- 添加更好的错误处理

### 2. 完成 Storyboard Agent
确保 Storyboard Agent 能够正确生成分镜文档。

### 3. 端到端测试
修复所有 Agent 后，运行完整的端到端测试。

## 文件修改清单

- ✓ `apps/api/test_full_workflow.py` - 添加自动审核循环
- ✓ `apps/api/test_workflow_demo.py` - 新建简化演示脚本
- ✓ `apps/api/WORKFLOW_FIX_SUMMARY.md` - 本文档

## 验证步骤

1. 确保 PostgreSQL 运行：`docker-compose up -d postgres`
2. 确保数据库迁移已运行
3. 确保 LLM API Key 已配置：`workers/agent-runtime/.env`
4. 运行演示脚本：`python test_workflow_demo.py`

## 总结

问题的核心是工作流的审核机制设计为需要人工干预，而测试脚本没有模拟这个审核过程。通过添加自动审核循环，测试脚本现在可以自动批准每个阶段并继续执行后续阶段，成功生成了 Brief、Story Bible 和 Character 文档。
