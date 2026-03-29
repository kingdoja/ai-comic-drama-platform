# Local Setup — AI 漫剧创作者工作台 MVP

## 1. 本地开发目标

开发者应能在本地一套命令拉起：
1. Web
2. API
3. Agent Worker
4. Media Worker
5. QA Worker
6. PostgreSQL
7. Redis
8. MinIO
9. Temporal

## 2. 推荐环境

1. Node.js 22+
2. Python 3.12+
3. Docker Desktop
4. pnpm 或 npm
5. uv 或 pip + venv

## 3. 本地服务

### 基础设施
1. PostgreSQL
2. Redis
3. MinIO
4. Temporal

### 应用服务
1. `apps/web`
2. `apps/api`
3. `workers/agent-runtime`
4. `workers/media-runtime`
5. `workers/qa-runtime`

## 4. 环境变量建议

### Web
1. `NEXT_PUBLIC_API_BASE_URL`

### API
1. `DATABASE_URL`
2. `REDIS_URL`
3. `S3_ENDPOINT`
4. `S3_ACCESS_KEY`
5. `S3_SECRET_KEY`
6. `TEMPORAL_HOST`
7. `LLM_PROVIDER`
8. `IMAGE_PROVIDER`
9. `TTS_PROVIDER`

### Workers
1. `DATABASE_URL`
2. `REDIS_URL`
3. `TEMPORAL_HOST`
4. `S3_*`

## 5. 启动顺序

### 第一步
先启动基础设施：
1. PostgreSQL
2. Redis
3. MinIO
4. Temporal

### 第二步
启动 API

### 第三步
启动 Workers

### 第四步
启动 Web

## 6. 数据初始化

建议准备：
1. 平台模板种子数据
2. 示例项目数据
3. 示例角色卡
4. 示例分镜

## 7. 本地开发约束

1. 所有服务必须能本地独立运行
2. 所有 worker 必须支持热重载或快速重启
3. 所有外部模型先允许 mock 模式
4. 没有模型 key 时，系统也应能跑 demo 数据流

## 8. MVP 阶段的 mock 策略

为了先跑通主链路，允许：
1. brief agent mock
2. character agent mock
3. script agent mock
4. image render mock
5. tts mock

但 contract 不能省略。

## 9. 验收清单

本地环境完成后，至少要验证：
1. 可以创建项目
2. 可以创建剧集
3. 可以启动 episode workflow
4. 可以在数据库看到 stage tasks
5. 可以在对象存储看到示例资产
6. 前端工作台可以读到聚合数据
