# Brief 生成端到端测试指南

## 概述

这个测试会验证从用户输入到 AI 生成 Brief 的完整流程。

## 前置条件

### 1. 数据库已启动

```bash
cd infra/docker
docker-compose up -d postgres
```

验证：
```bash
docker-compose ps
# 应该看到 postgres 容器在运行
```

### 2. 数据库迁移已完成

```bash
cd infra/migrations
alembic upgrade head
```

### 3. LLM 服务已配置

```bash
cd workers/agent-runtime
# 确保 .env 文件存在且包含 QWEN_API_KEY
cat .env | grep QWEN_API_KEY
```

### 4. Python 依赖已安装

```bash
# API 依赖
cd apps/api
pip install -r requirements.txt

# Agent 依赖
cd ../../workers/agent-runtime
pip install -r requirements.txt
```

## 运行测试

### 步骤 1：启动 API 服务

打开一个终端：

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

你应该看到：
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 步骤 2：运行端到端测试

打开另一个终端：

```bash
cd apps/api
python test_brief_e2e.py
```

## 预期结果

测试会执行以下步骤：

1. ✓ 检查 API 健康状态
2. ✓ 创建测试项目
3. ✓ 创建测试剧集
4. ✓ 生成 Brief（10-15秒）
5. ✓ 显示生成的 Brief 内容
6. ✓ 查询生成的 Brief
7. ✓ 显示关键信息

成功输出示例：
```
============================================================
✓ 端到端测试通过！
============================================================

恭喜！你已经有了一个完整可用的 AI Brief 生成系统！
```

## 测试 API 文档

API 服务启动后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 手动测试 API

### 1. 创建项目

```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试项目",
    "description": "手动测试",
    "status": "active"
  }'
```

### 2. 创建剧集

```bash
curl -X POST "http://localhost:8000/api/projects/{project_id}/episodes" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "{project_id}",
    "episode_number": 1,
    "title": "第一集",
    "status": "draft"
  }'
```

### 3. 生成 Brief

```bash
curl -X POST "http://localhost:8000/api/brief/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "{project_id}",
    "episode_id": "{episode_id}",
    "raw_material": "一个关于时间循环的科幻故事...",
    "platform": "douyin",
    "target_duration_sec": 60,
    "target_audience": "18-35岁年轻观众"
  }'
```

### 4. 查询 Brief

```bash
curl "http://localhost:8000/api/brief/{document_id}"
```

## 常见问题

### 问题 1：API 服务无法启动

**错误**：`ModuleNotFoundError: No module named 'app'`

**解决**：确保在 `apps/api` 目录下运行

### 问题 2：数据库连接失败

**错误**：`connection timeout expired`

**解决**：
```bash
cd infra/docker
docker-compose up -d postgres
docker-compose ps
```

### 问题 3：LLM 调用失败

**错误**：`QWEN_API_KEY environment variable not set`

**解决**：
```bash
cd workers/agent-runtime
# 编辑 .env 文件，填入 API Key
nano .env
```

### 问题 4：Brief 生成超时

**错误**：`requests.exceptions.Timeout`

**可能原因**：
- LLM API 响应慢
- 网络问题
- 代理配置问题

**解决**：
- 检查网络连接
- 确认 .env 中的代理设置
- 增加超时时间

### 问题 5：导入错误

**错误**：`ImportError: cannot import name 'BriefAgent'`

**解决**：确保 agent-runtime 依赖已安装
```bash
cd workers/agent-runtime
pip install -r requirements.txt
```

## 性能指标

正常情况下：
- API 响应时间：< 100ms（不含 LLM 调用）
- Brief 生成时间：10-15秒
- Token 使用：800-1200 tokens
- 成本：约 ¥0.004/次

## 下一步

测试通过后，你可以：

1. **添加更多 Agent**
   - Story Bible Agent
   - Character Agent
   - Script Agent
   - Storyboard Agent

2. **创建前端界面**
   - React/Vue 应用
   - 实时显示生成进度
   - 可视化 Brief 内容

3. **添加图像生成**
   - 角色设计
   - 场景图
   - 分镜图

4. **优化和扩展**
   - 添加缓存
   - 实现流式输出
   - 添加用户认证
   - 部署到生产环境

---

**最后更新**：2026-04-06
