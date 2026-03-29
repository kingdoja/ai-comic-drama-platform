# AI 漫剧创作者工作台 MVP 开发执行方案

## 1. 先说结论

### 1.1 现在这些文件够不够开工
够开工，但不够“一口气把整个产品做完”。

你现在已经有两份很关键的源文件：

1. [AI漫剧产品设计.md](./AI漫剧产品设计.md)
2. [DESIGN.md](../design/DESIGN.md)

它们已经覆盖了：
1. 产品定位
2. MVP 边界
3. agent 架构
4. 技术栈
5. 工程架构
6. 设计系统方向
7. 数据表初稿
8. 页面模式与设计约束

所以现在**足够开始做 MVP 骨架和第一轮核心开发**。

### 1.2 现在还缺什么
在真正高效开发前，还差 6 个“开发级文件”：

1. `MVP PRD`：把 MVP 功能收成用户故事和验收标准
2. `API Contract`：前后端接口定义
3. `Pydantic Schema`：核心对象输入输出 schema
4. `Workflow Contract`：Temporal workflow 和 stage task 的输入输出
5. `Prompt Contract`：每类 agent 的标准输入/输出结构
6. `Infra Local Setup`：本地开发环境和运行方式

所以正确的节奏不是继续空谈，而是：

`先把开发级文件补齐 -> 再搭骨架 -> 再做主链路 -> 再补媒体链路 -> 再补 QA 和重跑`

## 2. MVP 要做到什么程度

### 2.1 MVP 的唯一目标
让一个创作者或小团队，能把一段女频网文 / 短剧脚本素材，转成一个**可发布的单集包**。

### 2.2 MVP 的交付单位
MVP 不以“项目”作为最小成功单位，而以：

`一个可发布的单集包`

作为成功单位。

这个单集包至少包含：
1. 项目 Brief
2. 角色卡
3. 单集剧本
4. 分镜表
5. 关键帧图
6. 字幕文件
7. 配音音频
8. 预览成片
9. 封面和标题素材

### 2.3 MVP 不做什么
第一版不要做：
1. 多人实时协作编辑
2. 多平台自动发布
3. 爆款推荐和智能投放
4. 全自动长篇多集内容工厂
5. 完整商业化结算系统

## 3. MVP 功能拆解

### 3.1 必做功能

#### A. 项目创建
1. 新建项目
2. 选择“从素材改编”
3. 上传或粘贴小说/脚本素材
4. 填写平台和时长目标

#### B. 内容主链路
1. 生成项目 Brief
2. 生成人物与世界观
3. 生成单集大纲
4. 生成单集剧本
5. 生成分镜
6. 生成视觉规范

#### C. 媒体主链路
1. 生成关键帧
2. 生成字幕
3. 生成配音
4. 生成预览成片

#### D. 可控能力
1. 编辑关键内容
2. 锁定角色字段
3. 锁定镜头
4. 局部重跑
5. 人工审核通过/打回

#### E. 导出
1. 导出预览视频
2. 导出封面
3. 导出标题和发布素材

### 3.2 延后功能
1. 角色关系图可视化高级编辑器
2. 模板市场
3. 团队权限系统精细化
4. 数据复盘自动优化闭环
5. 高级剪辑模板市场

## 4. 现在最适合的开发路线

### 4.1 开发顺序总览
推荐按 8 步走：

1. 锁开发级文档
2. 初始化仓库结构
3. 跑通基础设施
4. 做后端领域模型和 schema
5. 做工作流骨架
6. 做前端工作台骨架
7. 做内容主链路
8. 做媒体导出与 QA

### 4.2 每一步的具体产出

#### 第一步：锁开发级文档
目标：
让研发、前端、agent、工作流说的是同一种语言。

要产出：
1. `docs/prd/MVP-PRD.md`
2. `docs/engineering/API-CONTRACT.md`
3. `docs/engineering/WORKFLOW-CONTRACT.md`
4. `docs/engineering/AGENT-CONTRACT.md`
5. `docs/engineering/LOCAL-SETUP.md`

#### 第二步：初始化仓库结构
目标：
把项目组织得清楚、克制、好看，不让根目录长成垃圾堆。

#### 第三步：跑通基础设施
目标：
本地一键拉起：
1. PostgreSQL
2. Redis
3. MinIO
4. Temporal
5. API
6. Web

#### 第四步：做后端领域模型和 schema
目标：
先定义核心对象，再写接口。

#### 第五步：做 workflow 骨架
目标：
先让单集 workflow 跑起来，即使内部先用 mock。

#### 第六步：做前端工作台骨架
目标：
先把项目工作台骨架和阶段导航做出来。

#### 第七步：做内容主链路
目标：
先跑通 `素材 -> brief -> 角色卡 -> 剧本 -> 分镜`

#### 第八步：做媒体导出与 QA
目标：
做出第一个“可播放、可审核、可导出”的单集包。

## 5. 开发前的关键判断

### 5.1 你现在应该先写什么，不应该先写什么

#### 先写
1. Schema
2. 数据库 migration
3. Workflow contract
4. Agent task contract
5. 前端 workspace DTO

#### 不要先写
1. 大量 prompt 细节
2. 复杂权限系统
3. 复杂优化策略
4. 花里胡哨的前端动效
5. 过早拆微服务

### 5.2 第一版模型接入策略
不要一开始就追求“最佳模型矩阵”。

推荐：
1. 先只接一个主 LLM 供应商
2. 先只接一个图像供应商
3. 先只接一个 TTS 供应商
4. 模型路由层接口先抽象，但实现可以先简单

这样做的原因：
1. 更快落地
2. 更少调试变量
3. 更容易定位失败原因

## 6. 项目文件结构怎么设计才有审美

### 6.1 根目录原则
好看的项目结构有三个特征：
1. 分层清楚
2. 命名稳定
3. 根目录干净

不好的结构通常是：
1. 所有文件都堆在根目录
2. `utils`、`common`、`misc` 到处飞
3. 前后端和脚本混在一起

### 6.2 推荐目录结构
这是我最推荐的结构：

```text
thinking/
├─ apps/
│  ├─ web/
│  │  ├─ app/
│  │  ├─ components/
│  │  ├─ features/
│  │  ├─ lib/
│  │  ├─ styles/
│  │  └─ public/
│  └─ api/
│     ├─ app/
│     │  ├─ api/
│     │  ├─ core/
│     │  ├─ domain/
│     │  ├─ services/
│     │  ├─ repositories/
│     │  ├─ schemas/
│     │  └─ workers/
│     └─ tests/
├─ workers/
│  ├─ agent-runtime/
│  ├─ media-runtime/
│  └─ qa-runtime/
├─ packages/
│  ├─ contracts/
│  ├─ design-tokens/
│  ├─ ui/
│  └─ config/
├─ infra/
│  ├─ docker/
│  ├─ migrations/
│  └─ temporal/
├─ scripts/
├─ docs/
│  ├─ product/
│  │  ├─ AI漫剧产品设计.md
│  │  ├─ MVP开发执行方案.md
│  │  └─ MVP-PRD.md
│  ├─ design/
│  │  ├─ DESIGN.md
│  │  └─ design-preview.html
│  ├─ engineering/
│  └─ decisions/
├─ README.md
├─ package.json
└─ .env.example
```

### 6.3 为什么这个结构有审美
1. `apps / workers / packages / infra / docs` 五层非常清楚
2. 名称都很直，不耍聪明
3. 根目录保留最重要的少数文件
4. 前端、后端、worker、设计系统都能找到稳定归属

### 6.4 前端目录建议

```text
apps/web/
├─ app/
├─ components/
│  ├─ primitives/
│  ├─ workspace/
│  ├─ storyboard/
│  ├─ preview/
│  └─ review/
├─ features/
│  ├─ projects/
│  ├─ episodes/
│  ├─ characters/
│  ├─ storyboard/
│  ├─ qa/
│  └─ publish/
├─ lib/
├─ styles/
└─ tests/
```

注意：
1. `components` 放可复用 UI
2. `features` 放业务模块
3. 不要把业务逻辑塞进 `components`

### 6.5 后端目录建议

```text
apps/api/app/
├─ api/
├─ core/
├─ domain/
│  ├─ project/
│  ├─ episode/
│  ├─ workflow/
│  ├─ document/
│  ├─ asset/
│  └─ qa/
├─ services/
├─ repositories/
├─ schemas/
├─ integrations/
└─ workers/
```

注意：
1. `domain` 是业务模型
2. `schemas` 是输入输出 contract
3. `repositories` 是数据库访问
4. `integrations` 是外部模型、存储、TTS、图像等接入

### 6.6 文档目录建议

```text
docs/
├─ product/
│  ├─ MVP-PRD.md
│  └─ USER-FLOWS.md
├─ design/
│  ├─ DESIGN-EXTENSIONS.md
│  └─ WIREFRAMES.md
├─ engineering/
│  ├─ API-CONTRACT.md
│  ├─ WORKFLOW-CONTRACT.md
│  ├─ AGENT-CONTRACT.md
│  ├─ DATA-MODEL.md
│  └─ LOCAL-SETUP.md
└─ decisions/
   ├─ ADR-001-monorepo.md
   ├─ ADR-002-temporal.md
   └─ ADR-003-media-pipeline.md
```

## 7. 具体怎么执行开发

### 7.1 Phase 0：开工前 2 到 3 天
目标：
把“能不能开发”变成“可以直接开发”。

任务：
1. 确认技术栈最终版本
2. 确认目录结构
3. 确认数据库表和 schema
4. 确认 MVP 页面清单
5. 确认 workflow 输入输出

交付物：
1. `MVP-PRD.md`
2. `API-CONTRACT.md`
3. `WORKFLOW-CONTRACT.md`
4. `AGENT-CONTRACT.md`

### 7.2 Phase 1：项目初始化
目标：
把开发环境和基础骨架跑起来。

任务：
1. 初始化 monorepo
2. 建 web 项目
3. 建 api 项目
4. 建 worker 项目
5. 建 docker compose
6. 接 PostgreSQL / Redis / MinIO / Temporal

验收：
1. 本地一条命令启动
2. Web 能打开
3. API 健康检查通过
4. Temporal worker 连得上

### 7.3 Phase 2：核心数据与 contract
目标：
让前后端、workflow、worker 用同一套数据语言。

任务：
1. 写 Pydantic schema
2. 写数据库 migration
3. 写 TypeScript DTO
4. 写 shared contract

验收：
1. 核心对象都有 schema
2. API 能创建 project / episode
3. 数据能正确写库

### 7.4 Phase 3：工作台前端骨架
目标：
先做出能看的工作台，不先追求生成能力。

页面：
1. 首页
2. 项目工作台
3. 角色页
4. 分镜页
5. Preview & QA 页

验收：
1. 符合 `docs/design/DESIGN.md`
2. 有三栏骨架
3. 有阶段条
4. 有空状态和 loading 状态

### 7.5 Phase 4：单集内容主链路
目标：
跑通：

`素材 -> brief -> 角色卡 -> 剧本 -> 分镜`

任务：
1. 建 Episode workflow
2. 接 brief agent
3. 接 character/story bible agent
4. 接 script agent
5. 接 storyboard agent

验收：
1. 能创建 stage tasks
2. 每一步结果可写入 documents
3. 工作台能读到结果

### 7.6 Phase 5：媒体主链路
目标：
跑通：

`分镜 -> 关键帧 -> 字幕 -> 配音 -> 预览视频`

任务：
1. 建 VisualSpec 到资产链路
2. 接图像生成
3. 接 TTS
4. 用 FFmpeg 拼预览

验收：
1. 至少能导出一个预览视频
2. 资产表记录完整
3. 工作台可播放预览

### 7.7 Phase 6：QA 与重跑
目标：
让系统从“能生成”升级到“可控可修”。

任务：
1. QA report
2. Human review gate
3. Rerun stage
4. 版本对比

验收：
1. 能打回
2. 能局部重跑
3. 能保留旧版本

## 8. 开发时最容易犯的错误

### 错误一：先做花里胡哨的 AI 交互
应该先做工作台骨架和结构化结果流。

### 错误二：先做复杂 agent，再做 schema
应该先定义 contract，再接 agent。

### 错误三：API 里直接做长任务
应该由 workflow 和 worker 承担。

### 错误四：过早做“全自动”
应该先做“可控、可审、可修”。

### 错误五：目录结构太随意
项目一旦长起来，结构难看会明显拖慢认知速度。

## 9. 你现在最应该执行的具体动作

如果你准备真正开始做，这就是最好的顺序：

1. 在仓库里建立推荐目录结构
2. 创建 `docs/product/MVP-PRD.md`
3. 创建 `docs/engineering/API-CONTRACT.md`
4. 创建 `docs/engineering/WORKFLOW-CONTRACT.md`
5. 创建 `apps/web`
6. 创建 `apps/api`
7. 创建 `workers/agent-runtime`
8. 创建 `workers/media-runtime`
9. 创建 `workers/qa-runtime`
10. 创建 `infra/docker/docker-compose.yml`

## 10. 最后一句话

现在的信息已经足够你开始做一个高质量 MVP，但还不够直接“无脑开写全部功能”。

正确做法不是继续补概念，而是马上进入：

`补开发级 contract -> 搭骨架 -> 跑通单集主链路 -> 再补 QA 和重跑`

如果你愿意，下一步我可以直接继续帮你做真正能落地的第一批工程文件：

1. `docs/product/MVP-PRD.md`
2. `docs/engineering/API-CONTRACT.md`
3. `docs/engineering/WORKFLOW-CONTRACT.md`
4. 推荐的项目目录骨架


