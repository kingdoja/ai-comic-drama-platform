# 项目文档中心

欢迎来到 AI 漫剧创作者工作台的文档中心。这里包含了项目的所有文档资料。

## 📖 快速导航

### 🚀 新手入门
- **[项目总览 (README.md)](../README.md)** - 项目介绍、架构概述、快速开始
- **[项目总结 (PROJECT_SUMMARY.md)](./PROJECT_SUMMARY.md)** - 项目核心信息汇总
- **[项目状态分析 (PROJECT_STATUS_ANALYSIS.md)](./PROJECT_STATUS_ANALYSIS.md)** - 当前进度和状态

### 🏗️ 工程技术文档
- **[工程文档索引 (engineering/README.md)](./engineering/README.md)** - 技术文档总览
- **[系统架构蓝图 (engineering/SYSTEM-BLUEPRINT.md)](./engineering/SYSTEM-BLUEPRINT.md)** - 系统设计详解
- **[交付计划 (engineering/DELIVERY-PLAN.md)](./engineering/DELIVERY-PLAN.md)** - 开发路线图
- **[Bug 修复总结 (engineering/BUG_FIX_SUMMARY.md)](./engineering/BUG_FIX_SUMMARY.md)** - 问题修复记录
- **[文档组织规范 (engineering/DOCUMENT_ORGANIZATION.md)](./engineering/DOCUMENT_ORGANIZATION.md)** - 文档结构说明
- **[镜头数据结构 (engineering/SHOT_DATA_STRUCTURE.md)](./engineering/SHOT_DATA_STRUCTURE.md)** - Shot 数据模型
- **[图像渲染输入 (engineering/IMAGE_RENDER_INPUT.md)](./engineering/IMAGE_RENDER_INPUT.md)** - 图像生成规格

### 🚢 部署和运维
- **[部署指南 (deployment/DEPLOYMENT.md)](./deployment/DEPLOYMENT.md)** - 生产环境部署
- **[GitHub 设置 (deployment/GITHUB_SETUP.md)](./deployment/GITHUB_SETUP.md)** - 代码仓库配置

### 💼 产品文档
- **[产品文档目录 (product/)](./product/)** - 产品需求和规格

### 🎨 设计文档
- **[设计文档目录 (design/)](./design/)** - UI/UX 设计资料

### 🎤 面试准备
- **[面试讨论要点 (interview/DISCUSSION_POINTS.md)](./interview/DISCUSSION_POINTS.md)** - 技术面试材料

## 📁 文档目录结构

```
docs/
├── README.md                          # 本文件 - 文档中心首页
├── PROJECT_SUMMARY.md                 # 项目总结
├── PROJECT_STATUS_ANALYSIS.md         # 项目状态分析
│
├── engineering/                       # 工程技术文档
│   ├── README.md                     # 工程文档索引
│   ├── SYSTEM-BLUEPRINT.md           # 系统架构蓝图
│   ├── DELIVERY-PLAN.md              # 交付计划
│   ├── BUG_FIX_SUMMARY.md            # Bug 修复总结
│   ├── DOCUMENT_ORGANIZATION.md      # 文档组织规范
│   ├── SHOT_DATA_STRUCTURE.md        # 镜头数据结构
│   └── IMAGE_RENDER_INPUT.md         # 图像渲染输入
│
├── deployment/                        # 部署和运维文档
│   ├── DEPLOYMENT.md                 # 部署指南
│   └── GITHUB_SETUP.md               # GitHub 设置
│
├── product/                           # 产品文档
│   └── (产品需求文档)
│
├── design/                            # 设计文档
│   └── (UI/UX 设计文档)
│
└── interview/                         # 面试准备材料
    └── DISCUSSION_POINTS.md          # 讨论要点
```

## 🔍 按主题查找文档

### 系统架构和设计
- [系统架构蓝图](./engineering/SYSTEM-BLUEPRINT.md)
- [镜头数据结构](./engineering/SHOT_DATA_STRUCTURE.md)
- [图像渲染输入](./engineering/IMAGE_RENDER_INPUT.md)
- [文档组织规范](./engineering/DOCUMENT_ORGANIZATION.md)

### 开发和实现
- [交付计划](./engineering/DELIVERY-PLAN.md)
- [工程文档索引](./engineering/README.md)
- [Bug 修复总结](./engineering/BUG_FIX_SUMMARY.md)

### 部署和运维
- [部署指南](./deployment/DEPLOYMENT.md)
- [GitHub 设置](./deployment/GITHUB_SETUP.md)

### API 和服务文档
- [API 快速开始](../apps/api/QUICKSTART.md)
- [故障排查指南](../apps/api/TROUBLESHOOTING.md)
- [端到端测试指南](../apps/api/E2E_TEST_GUIDE.md)
- [媒体管道指南](../apps/api/docs/MEDIA_PIPELINE_GUIDE.md)
- [对象存储](../apps/api/docs/OBJECT_STORAGE.md)
- [提供商适配器](../apps/api/docs/PROVIDER_ADAPTERS.md)
- [QA 运行时](../apps/api/docs/QA_RUNTIME.md)
- [审核流程](../apps/api/docs/REVIEW_FLOW.md)
- [重跑指南](../apps/api/docs/RERUN_GUIDE.md)

### Agent 和 Worker 文档
- [Agent Runtime](../workers/agent-runtime/README.md)
- [Agent 迁移指南](../workers/agent-runtime/docs/MIGRATION.md)

### 数据库和迁移
- [迁移文档](../infra/migrations/README.md)
- [Migration 006 总结](../infra/migrations/MIGRATION_006_SUMMARY.md)
- [Migration 006 快速开始](../infra/migrations/QUICK_START_006.md)

### Spec 文档（功能规格）
- [文本管道 Mock](../.kiro/specs/text-pipeline-mock/)
- [项目概览](../.kiro/specs/project-overview/)
- [分镜到资产](../.kiro/specs/storyboard-to-asset/)
- [媒体管道 Alpha](../.kiro/specs/media-pipeline-alpha/)
- [QA/Review/Rerun](../.kiro/specs/qa-review-rerun/)
- [代码重构](../.kiro/specs/code-refactor/)

## 📊 项目当前状态

**最新迭代**: Iteration 5 (QA/Review/Rerun) ✅ 已完成

**核心功能完成度**:
- ✅ 文本生成管道 (Brief → Story Bible → Character → Script → Storyboard)
- ✅ 媒体生成管道 (Image Render → TTS → Subtitle → Preview Export)
- ✅ QA/Review/Rerun 闭环
- ✅ 工作区聚合 API
- ✅ 数据库模型和迁移
- 🔄 前端工作台 (待开发)

**下一步计划**:
- Iteration 6: 资产质量检查和系统优化
- 前端工作台开发
- 真实 LLM 和媒体服务集成

## 🤝 贡献指南

### 添加新文档
1. 确定文档类型和目标目录
2. 遵循现有文档的格式和风格
3. 更新相应的 README.md 索引
4. 在本文件中添加链接

### 文档命名规范
- 使用大写字母和下划线：`DOCUMENT_NAME.md`
- 使用描述性名称
- 避免使用空格和特殊字符

### 文档内容规范
- 使用 Markdown 格式
- 包含清晰的标题层级
- 添加目录（对于长文档）
- 包含代码示例和图表
- 保持更新日期

## 📞 获取帮助

- **技术问题**: 查看 [故障排查指南](../apps/api/TROUBLESHOOTING.md)
- **开发问题**: 查看 [工程文档](./engineering/README.md)
- **产品问题**: 查看 [产品文档](./product/)

---

**最后更新**: 2026-04-11  
**维护者**: 项目团队
