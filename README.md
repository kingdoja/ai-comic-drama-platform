# AI 漫剧创作者工作台

面向“女频网文 / 短剧脚本改编成竖屏漫剧”的 AI 创作者工作台。

## 目录导览

- `apps/`：前端与 API 应用
- `workers/`：Agent、媒体、QA 运行时
- `packages/`：共享 contract、UI、设计 token、配置
- `infra/`：Docker、数据库迁移、Temporal 相关基础设施
- `docs/product/`：产品方案、MVP 执行方案、PRD
- `docs/design/`：设计系统与设计预览
- `docs/engineering/`：API、Workflow、Agent、Local Setup 等工程文档
- `docs/interview/`：面试表达、架构说明等辅助文档

## 关键文档

- 产品总方案：`docs/product/AI漫剧产品设计.md`
- MVP 执行方案：`docs/product/MVP开发执行方案.md`
- MVP PRD：`docs/product/MVP-PRD.md`
- 设计系统：`docs/design/DESIGN.md`
- 设计预览：`docs/design/design-preview.html`
- Agent 协议：`docs/engineering/AGENT-CONTRACT.md`
- Agent 运行机制：`docs/engineering/AGENT运行机制设计.md`
- Workflow 协议：`docs/engineering/WORKFLOW-CONTRACT.md`
- 面试表达：`docs/interview/AGENT内部架构与面试回答.md`

## 根目录保留原则

根目录只保留启动、配置、依赖和仓库级入口文件，避免产品文档和设计稿散落在外层。
