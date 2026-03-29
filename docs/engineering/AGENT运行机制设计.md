# Agent 运行机制设计

## 1. 这份文档回答什么问题

这份文档专门回答四个问题：

1. 这个产品的每个 agent 具体是怎么设计的
2. 哪些环节会调用 LLM，哪些不会
3. 整个系统从开始到结束的流程是怎么运转的
4. 工程上如何把这些 agent 真正实现出来

这不是产品概念文档，而是运行机制文档。

---

## 2. 先说结论

这个系统不是“多个 AI 自由聊天”，而是一个：

`Workflow Orchestrator + Specialized Agents + Shared Memory + Media Workers + QA Gate`

其中：

1. 负责编排的是 workflow，不是 agent 自己
2. 负责生成文本内容的是 LLM 型 agent
3. 负责生成图片、语音、视频的是 media worker
4. 负责做质量门禁的是 QA agent / QA worker
5. 所有阶段都围绕结构化文档和资产运转，而不是围绕聊天记录运转

---

## 3. 到底有没有调用 LLM

有，而且是核心能力之一，但不是所有环节都直接调用通用 LLM。

可以分成三类：

### 3.1 直接调用 LLM 的 Agent

这些 agent 的核心工作是理解内容、规划内容、生成结构化文本。

1. Brief Agent
2. Story Bible Agent
3. Character Agent
4. Script Agent
5. Storyboard Agent
6. Visual Spec Agent
7. Subtitle Agent
8. QA Agent 的一部分语义检查能力

### 3.2 不一定调用通用 LLM 的 Worker

这些环节更偏执行层，主要调用媒体模型或工具：

1. Image Render Worker
2. TTS Worker
3. Edit Export Worker

它们可能会搭配轻量 LLM 做 prompt 优化、错误归因或命名整理，但核心执行不依赖通用 LLM。

### 3.3 混合调用的 QA / Evaluation 层

QA 不能只靠 LLM，也不能只靠规则。

通常会采用混合模式：

1. 规则检查：字幕长度、时长错位、空字段、引用缺失
2. LLM / VLM 检查：角色一致性、剧情逻辑、画面与台词是否匹配
3. 聚合器：汇总成 `qa_report` 和 rerun 建议

一句话说清楚：

`文本规划类 agent 大多调用 LLM，媒体执行类 worker 大多调用专用模型或工具，QA 用规则 + LLM / VLM 的混合机制。`

---

## 4. 系统的总体运转架构

## 4.1 组件分层

### A. Web / API 层

负责：

1. 接收用户操作
2. 创建项目、剧集、workflow run
3. 提供工作台读取接口
4. 提供重跑、锁定、审核接口

在当前项目结构里，对应：

1. `apps/web`
2. `apps/api`

### B. Workflow Orchestrator 层

负责：

1. 决定当前跑哪个 stage
2. 构造每个 stage 的输入
3. 决定调用哪类 runtime
4. 控制重试、失败恢复、人工审核停顿
5. 管理 workflow 状态机

建议实现位置：

1. `infra/temporal`
2. `workers/*-runtime` 中对应 worker 的 activity 实现

### C. Agent Runtime 层

负责执行文本型阶段。

主要处理：

1. 读取输入文档
2. 组装 prompt
3. 调用 LLM
4. 输出结构化结果
5. 校验并提交新文档版本

当前目录对应：

1. `workers/agent-runtime`

### D. Media Runtime 层

负责执行媒体类阶段。

主要处理：

1. 图像生成
2. 语音生成
3. 素材合成
4. 预览视频导出

当前目录对应：

1. `workers/media-runtime`

### E. QA Runtime 层

负责执行评估和质量门禁。

主要处理：

1. 规则检查
2. 模型检查
3. 生成 qa_report
4. 给出 rerun 建议

当前目录对应：

1. `workers/qa-runtime`

### F. Shared Memory / Persistence 层

负责保存“系统真相”。

包括：

1. projects
2. episodes
3. workflow_runs
4. documents
5. assets
6. qa_reports

当前项目里已经有对应 repository 和 schema：

1. `apps/api/app/repositories/*`
2. `apps/api/app/schemas/*`
3. `apps/api/app/db/models.py`

---

## 5. 一次完整运行是怎么发生的

下面用“用户点击生成一集漫剧”举例。

## 5.1 启动阶段

1. 用户在工作台点击“开始生成”
2. Web 调用 API，请求启动 `episode_workflow`
3. API 创建 `workflow_run` 记录
4. Orchestrator 接管执行

此时系统会记录：

1. `project_id`
2. `episode_id`
3. `start_stage`
4. `triggered_by`
5. 当前 workflow 状态

## 5.2 编排阶段

Orchestrator 读取 `WORKFLOW-CONTRACT`，按顺序推进：

1. `brief`
2. `story_bible`
3. `character`
4. `script`
5. `storyboard`
6. `visual_spec`
7. `image_render`
8. `subtitle`
9. `tts`
10. `edit_export_preview`
11. `qa`
12. `human_review_gate`
13. `export_final`

每到一个阶段，编排器都会构造一份 `StageTaskInput`。

## 5.3 StageTaskInput 是什么

每个 agent / worker 不会自己去猜上下文，而是接收明确输入：

```json
{
  "workflow_run_id": "uuid",
  "project_id": "uuid",
  "episode_id": "uuid",
  "stage_type": "script",
  "input_refs": [],
  "locked_refs": [],
  "constraints": {},
  "target_ref_ids": []
}
```

它的作用是：

1. 告诉本阶段该读什么
2. 告诉本阶段哪些内容不能改
3. 告诉本阶段要满足什么约束
4. 告诉本阶段是否是局部重跑

## 5.4 Runtime 执行阶段

拿到 `StageTaskInput` 后，对应 runtime 开始执行：

1. Agent Runtime 处理文本阶段
2. Media Runtime 处理图像、语音、导出阶段
3. QA Runtime 处理质量检查阶段

## 5.5 结果提交阶段

每个阶段完成后，返回统一的 `StageTaskOutput`：

```json
{
  "status": "succeeded",
  "document_refs": [],
  "asset_refs": [],
  "qa_refs": [],
  "warnings": [],
  "metrics": {
    "duration_ms": 0
  }
}
```

编排器根据结果决定：

1. 进入下一阶段
2. 重试当前阶段
3. 停在人工审核节点
4. 标记 workflow 失败
5. 触发局部 rerun

---

## 6. 每个 Agent 的标准内部流水线

所有文本类 agent 都使用统一内部管线：

1. Loader
2. Normalizer
3. Planner
4. Generator
5. Critic
6. Validator
7. Committer

这是为了避免每个 agent 都变成黑盒。

## 6.1 Loader

负责从共享存储加载输入。

会读取：

1. documents
2. assets metadata
3. locked refs
4. constraints
5. 历史版本

## 6.2 Normalizer

负责把输入整理成可用上下文。

典型动作：

1. 摘要原始素材
2. 统一角色名、场景名
3. 去掉重复信息
4. 识别必须继承的锁定字段

## 6.3 Planner

负责先产出“执行计划”，不是直接让模型开写。

例如：

1. Script Agent 先规划剧情节拍
2. Storyboard Agent 先规划镜头预算
3. Subtitle Agent 先规划字幕切分

## 6.4 Generator

真正调用模型生成候选结果。

这一步通常会：

1. 传入系统 prompt
2. 传入 stage-specific prompt
3. 传入输出 schema
4. 要求返回 JSON 结构

## 6.5 Critic

对草稿做一轮自检。

检查项通常包括：

1. 是否偏离 brief
2. 是否和角色设定冲突
3. 是否节奏异常
4. 是否输出过度发散

## 6.6 Validator

做工程化校验。

检查：

1. JSON 是否可解析
2. schema 是否合法
3. 必填字段是否齐全
4. 引用关系是否正确
5. 是否修改了 locked 字段

## 6.7 Committer

把通过校验的结果正式写回数据库和对象存储。

会写入：

1. 新的 document 版本
2. 关联 refs
3. warnings
4. quality notes
5. metrics

---

## 7. 每个核心 Agent 是怎么设计的

## 7.1 Brief Agent

### 是否调用 LLM

是，核心依赖 LLM。

### 作用

把原始素材和用户目标整理成可执行的改编 brief。

### 输入

1. 原始小说片段 / 剧本素材
2. 平台约束
3. 时长目标
4. 用户意图

### 输出

1. `brief` document
2. 核心卖点
3. 主线冲突
4. 改编风险
5. 目标风格

### 内部实现建议

1. Loader 读取原始素材和项目配置
2. Normalizer 提炼故事主线与角色关系
3. Planner 规划保留线、压缩线、强化线
4. Generator 调用 LLM 生成 brief JSON
5. Validator 校验字段完整性
6. Committer 落库为 `brief`

### 工程注意点

1. 不要让 Brief Agent 直接输出太长文学文本
2. 输出应服务于后续 agent 消费
3. 风险字段要结构化，方便人工 review

---

## 7.2 Story Bible Agent

### 是否调用 LLM

是。

### 作用

建立项目级世界规则和故事约束，是全局一致性的基础。

### 输入

1. `brief`
2. 原始素材摘要

### 输出

1. `story_bible` document
2. 世界规则
3. 时间线
4. 关系基线
5. 禁止冲突项

### 内部实现建议

1. 将原始设定改写成结构化规则
2. 明确哪些规则是硬约束
3. 为 Character / Script 阶段提供引用底座

### 工程注意点

1. 这里的输出应该“少而稳”，不要过度世界观发散
2. 可拆成 project-level 文档，不必每集重复生成

---

## 7.3 Character Agent

### 是否调用 LLM

是。

### 作用

生成角色卡，并把角色定义稳定下来。

### 输入

1. `brief`
2. `story_bible`

### 输出

1. `character_profile` document
2. 角色目标
3. 角色动机
4. 说话风格
5. 视觉锚点
6. 关系表

### 内部实现建议

1. 按主角 / 配角 / 功能角色拆层生成
2. 每个角色都输出文本锚点 + 视觉锚点 + 语言锚点
3. 对关键字段加锁，后续阶段默认只读

### 工程注意点

1. 角色视觉锚点必须能被下游 image prompt 消费
2. 说话风格必须能被 TTS 和字幕阶段复用

---

## 7.4 Script Agent

### 是否调用 LLM

是，而且是文本链路的核心 agent。

### 作用

把素材改编成单集可执行剧本。

### 输入

1. `brief`
2. `story_bible`
3. `character_profile`

### 输出

1. `script_draft` document
2. 场次结构
3. 每场目标
4. 台词
5. 情绪节拍
6. cliffhanger

### 内部实现建议

推荐做成两段式：

1. 先生成 beat sheet
2. 再生成 dialogue + scene draft

而不是一次性生成整集全文。

### 工程注意点

1. 限制每集镜头预算和时长预算
2. 强约束输出结构，方便下游 storyboard 拆镜头
3. script 失败时不要覆盖已确认旧版本

---

## 7.5 Storyboard Agent

### 是否调用 LLM

是。

### 作用

把剧本拆成镜头级执行计划。

### 输入

1. `script_draft`
2. 平台节奏模板
3. 镜头预算约束

### 输出

1. `shots` document
2. shot list
3. 景别
4. 时长
5. 转场
6. 情绪标签
7. 对应台词片段

### 内部实现建议

1. 先做 shot planning
2. 再做 shot expansion
3. 输出镜头 id，供后续单镜头重跑使用

### 工程注意点

1. shot 必须有稳定 id
2. shot 结构必须能对齐字幕和图像生成
3. 这是后续局部 rerun 的关键节点

---

## 7.6 Visual Spec Agent

### 是否调用 LLM

是。

### 作用

把分镜转成可渲染的视觉规格，而不是直接出图。

### 输入

1. `shots`
2. `character_profile` 中的视觉锚点
3. 风格模板
4. 已锁定视觉约束

### 输出

1. `visual_spec` document
2. 每镜头角色出镜要求
3. 构图要求
4. 服装道具要求
5. 场景要求
6. 风格关键词

### 内部实现建议

1. 先确定每个 shot 的视觉目标
2. 再生成 render-ready spec
3. spec 必须是 image worker 可直接消费的数据结构

### 工程注意点

1. Visual planning 和 image rendering 必须拆开
2. 文本规划错误和生成失败要能分开定位

---

## 7.7 Image Render Worker

### 是否调用通用 LLM

不一定。

核心执行通常是图像模型，不是通用 LLM。

### 作用

根据 `visual_spec` 生成关键帧或镜头图。

### 输入

1. `visual_spec`
2. locked character refs
3. style presets
4. target shot ids

### 输出

1. `shot_image` assets
2. 缩略图
3. 渲染元数据

### 内部实现建议

1. 一个 shot 对应一次独立渲染任务
2. 每个任务记录 prompt、seed、model、参数
3. 失败时支持只重跑目标 shot

### 工程注意点

1. 图片资产必须版本化
2. 记录 prompt lineage，方便追踪为什么画崩
3. 将大图放对象存储，数据库只存 metadata 和 ref

---

## 7.8 Subtitle Agent

### 是否调用 LLM

通常会调用轻量 LLM，但也要结合规则切分。

### 作用

把剧本和镜头对齐成移动端可读字幕。

### 输入

1. `script_draft`
2. `shots`

### 输出

1. `subtitle_script` document
2. 字幕切分
3. 压缩后文案
4. `subtitle_file` asset

### 内部实现建议

1. 先按镜头切句
2. 再按移动端阅读习惯做压缩
3. 最后导出字幕文件

### 工程注意点

1. 不能只是复制对白
2. 单条字幕长度、每秒字数要规则校验
3. 必须给 TTS 留下稳定切片边界

---

## 7.9 TTS Worker

### 是否调用通用 LLM

通常不调用。

核心是调用 TTS 模型或供应商接口。

### 作用

生成角色语音资产。

### 输入

1. `subtitle_script`
2. character voice config
3. 情绪标签

### 输出

1. `audio_voice` assets
2. 时长信息
3. 角色语音版本

### 内部实现建议

1. 按角色和句子切片生成
2. 回写片段时长
3. 为合成阶段提供可拼接音轨

### 工程注意点

1. 音频生成要可缓存
2. 同一句重跑时应支持复用配置
3. 时长变化会影响预览导出和 QA

---

## 7.10 Edit Export Worker

### 是否调用通用 LLM

通常不调用。

### 作用

把图像、字幕、音频合成为预览视频或最终导出包。

### 输入

1. selected shot images
2. subtitle file
3. audio assets
4. BGM / transition presets

### 输出

1. `preview_video`
2. `final_video`
3. `cover_image`
4. `export_bundle`

### 内部实现建议

1. 使用 FFmpeg 或等价渲染管线
2. 生成 preview 和 final 两种导出级别
3. 输出时长、分辨率、版本号

### 工程注意点

1. 这个阶段是纯执行层，不要混入复杂生成逻辑
2. 任何失败都应有明确工具日志

---

## 7.11 QA Agent / QA Worker

### 是否调用 LLM

会，但不是只靠 LLM。

### 作用

做最终质量门禁，判断作品是否可继续进入审核或导出。

### 输入

1. `preview_video`
2. documents
3. assets
4. 历史问题记录

### 输出

1. `qa_report`
2. 问题清单
3. 严重级别
4. rerun 建议
5. 是否允许进入 `human_review_gate`

### 检查内容

1. 角色一致性
2. 台词与字幕一致性
3. 画面与台词一致性
4. 字幕遮挡
5. 时长错配
6. 人物称呼错误
7. 世界规则冲突
8. 图像崩坏
9. 节奏异常

### 内部实现建议

做成三段式：

1. Rule checks
2. LLM / VLM semantic checks
3. Report aggregator

### 工程注意点

1. QA 输出必须可解释，不能只给一个分数
2. 每个问题都要能映射到建议 rerun 的 stage

---

## 8. 这些 Agent 到底怎么协作

不是：

`Agent A 直接跟 Agent B 自由聊天`

而是：

`Agent A -> 结构化产物 -> Shared Memory -> Orchestrator -> Agent B`

也就是说：

1. 上游 agent 只负责生产自己的标准化结果
2. Orchestrator 决定下游是谁
3. 下游只读取自己被授权的 refs
4. 共享记忆才是跨阶段协作媒介

这样设计的好处：

1. 可追踪
2. 可回滚
3. 可重跑
4. 可做版本管理
5. 可做质量分析

---

## 9. Agent 真正怎么落成代码

## 9.1 推荐的代码职责拆分

### API 层

负责：

1. 启动 workflow
2. 查询 workspace
3. 发起 rerun
4. 执行锁定和审核动作

### Workflow 层

负责：

1. 编排 stage
2. 处理重试
3. 控制状态转换
4. 控制 human review gate

### Agent Runtime 层

负责：

1. Stage handler 注册
2. Prompt builder
3. LLM client
4. Schema validator
5. Result committer

### Media Runtime 层

负责：

1. Render adapter
2. TTS adapter
3. Export adapter
4. Asset metadata committer

### QA Runtime 层

负责：

1. Rule engine
2. Semantic evaluator
3. QA report composer

---

## 9.2 推荐的 Agent Runtime 内部模块

一个文本型 agent runtime 可以拆成：

1. `task_router`
2. `context_loader`
3. `prompt_builder`
4. `llm_client`
5. `output_parser`
6. `validator`
7. `committer`

执行顺序：

1. `task_router` 根据 `stage_type` 选中 agent handler
2. `context_loader` 根据 `input_refs` 拉取文档
3. `prompt_builder` 组装系统提示词、约束、schema
4. `llm_client` 发起模型调用
5. `output_parser` 把结果转成结构化对象
6. `validator` 校验对象
7. `committer` 写入 documents / assets / qa_reports

---

## 9.3 一个 stage 的伪代码

```python

def run_stage(task: StageTaskInput) -> StageTaskOutput:
    context = context_loader.load(task.input_refs, task.locked_refs)
    normalized = normalizer.normalize(context, task.constraints)
    plan = planner.build(normalized, task.stage_type)
    draft = generator.generate(plan, schema=stage_schema(task.stage_type))
    reviewed = critic.review(draft, normalized)
    valid = validator.validate(reviewed, locked_refs=task.locked_refs)
    refs = committer.commit(valid, project_id=task.project_id, episode_id=task.episode_id)
    return StageTaskOutput(
        status="succeeded",
        document_refs=refs.documents,
        asset_refs=refs.assets,
        warnings=refs.warnings,
        metrics=refs.metrics,
    )
```

这个伪代码体现的是：

1. agent 是被动执行单元
2. workflow 才是主动调度单元
3. 结果必须结构化返回

---

## 10. 为什么这样设计更适合 AI 漫剧产品

因为这个产品不是一次性文本生成，而是长链路内容生产。

它有几个天然要求：

1. 阶段很多
2. 一致性要求高
3. 局部返工频繁
4. 人工把关必要
5. 媒体成本高

所以必须把系统设计成：

1. workflow-first
2. artifact-first
3. stage-based rerun
4. hybrid human-in-the-loop

而不是把所有希望都压在一个大模型 prompt 上。

---

## 11. 最终一句话总结

如果要用一句话讲这个产品的 agent 运行机制，可以这么说：

`这个系统里，LLM 负责内容理解和结构化生成，媒体模型负责图像和语音执行，workflow 负责调度和恢复，数据库与对象存储负责共享记忆，QA 负责质量门禁，几者共同组成一条可追踪、可重跑、可交付的 AI 漫剧生产流水线。`

---

## 12. 对照阅读

建议配合阅读：

1. `docs/engineering/AGENT-CONTRACT.md`
2. `docs/engineering/WORKFLOW-CONTRACT.md`
3. `docs/product/AI漫剧产品设计.md`
4. `docs/interview/AGENT内部架构与面试回答.md`
