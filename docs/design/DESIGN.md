# Design System — AI 漫剧创作者工作台

## Product Context
- **What this is:** 一个面向“女频网文 / 短剧脚本改编为竖屏漫剧”的创作者工作台，帮助创作者把素材转成可发布的单集包。
- **Who it's for:** 网文改编团队、短剧内容工作室、女性向内容创作者、需要稳定周更/日更的创作团队。
- **Space/industry:** AI 创作工具、视频/漫剧制作、内容工作流软件。
- **Project type:** 桌面端优先的 web app / creative workspace。

## Research Synthesis

### References
- Runway Product: https://runwayml.com/product/
- Canva Visual Suite: https://www.canva.com/visual-suite/
- CapCut Creative Suite: https://www.capcut.com/creative-suite
- Figma for Designers: https://www.figma.com/designers/
- Frame.io Capture, Review, Deliver: https://frame.io/capture-review-deliver
- Adobe Express Video Editor: https://www.adobe.com/express/feature/video/editor

### What The Landscape Converges On
1. 所有优秀创作工具都在强调“一个工作区里完成完整流程”。
2. 主界面通常采用左导航 + 中央主画布 + 右辅助面板的结构。
3. 多数工具把 AI 放在可触达的位置，但真正高频的是素材、版本、预览、审核。
4. 最成熟的产品都非常重视 review / approval / feedback，而不只是生成。

### Category Patterns To Keep
1. 清楚的三栏或双栏工作台骨架。
2. 明确的阶段状态和项目导航。
3. 媒体预览区必须成为主视觉重心之一。
4. 版本、评论、审批必须近距离贴着成果物出现。

### Where The Category Feels Weak
1. 很多 AI 创作产品过度“模型中心”，用户在调模型，不是在完成作品。
2. 很多创作工具虽然功能多，但视觉太像工具箱，缺少作品感与戏剧感。
3. 很多社媒编辑器太轻快，适合快剪，不适合长链路的可控改编生产。

### Eureka
**EUREKA:** 大多数 AI 创作产品做成“prompt-first、dark-lab、模型实验室”，因为它们假设用户是在探索生成可能性。  
但这个产品的用户是在把已有故事素材稳定改编成可发布内容，他们需要的是 **编辑控制感、阶段推进感、审片把关感**。  
所以这个产品应该是 **artifact-first**，不是 **prompt-first**。

## Aesthetic Direction
- **Direction:** Editorial Control Room
- **Decoration level:** Intentional
- **Mood:** 像“女性向内容编辑部 + 审片工作台”。整体专业、克制、清晰，但带一点戏剧张力和情绪密度，不冷，不花，不像中台，也不像 AI 实验室。

### Why This Direction
1. 它保留了工作台需要的秩序和效率。
2. 它允许产品带出“剧情、人物、情绪、镜头”的内容气质。
3. 它适合女频改编场景，不会过硬核，也不会过甜腻。

## Safe Choices And Risks

### Safe Choices
1. 三栏工作台骨架，符合 Figma / Frame.io 一类产品的使用预期。
2. 中央内容区优先，右侧 AI 辅助区次之，避免聊天工具化。
3. 清楚的状态进度、版本管理、审核入口，降低学习成本。

### Risks
1. **风险一：在工作台里引入“编辑部感”的高级排版语言。**
   - Gain: 产品不再像普通后台，更有内容品牌感。
   - Cost: 排版需要更克制，不能做花。
2. **风险二：使用酒红 + 铜金作为情绪强调，而不是行业常见蓝紫 AI 色。**
   - Gain: 更贴合女性向剧情改编和“戏剧张力”。
   - Cost: 必须严控使用频率，否则会显得过重。
3. **风险三：默认浅色工作台，局部深色预览舞台，而不是全局深色。**
   - Gain: 文本编辑、分镜阅读、长时间工作更舒服。
   - Cost: 需要精心处理明暗切换和预览区层级。

## Design Principles
1. **Artifact-first:** 先看产物，再看模型和参数。
2. **Stage-aware:** 用户始终知道自己在哪一步、下一步是什么。
3. **Editable, Lockable, Re-runnable:** 关键内容必须可编辑、可锁定、可重跑。
4. **Preview matters:** 9:16 预览是核心舞台，不是附件。
5. **Calm but dramatic:** 界面整体平静，但关键决策点有戏剧张力。

## Color System

### Core Palette
- **Porcelain:** `#F7F2EC`
- **Paper:** `#FCFAF7`
- **Ink:** `#17151D`
- **Graphite:** `#2A2731`
- **Slate:** `#66606F`
- **Soft Line:** `#D7D0C8`
- **Wine:** `#8E334F`
- **Copper:** `#B86D40`
- **Dusty Rose:** `#D9B8BF`
- **Sage Smoke:** `#A8B09E`

### Semantic Colors
- **Success:** `#2E7D5A`
- **Warning:** `#C07A24`
- **Error:** `#B23A3A`
- **Info:** `#3559B7`

### Usage Rules
1. 默认页面背景使用 `Paper` 或 `Porcelain`。
2. 正文和高对比信息使用 `Ink` / `Graphite`。
3. `Wine` 只用于关键强调：当前阶段、锁定状态、主 CTA、关键剧情标签。
4. `Copper` 用于次级强调：进度、状态提醒、版本变化。
5. 大面积强饱和色禁止使用。

## Typography

### Font Roles
- **Display / Section Headlines:** `Cormorant Garamond`
- **UI / Body / Labels:** `Plus Jakarta Sans`
- **Data / Version / Technical Meta:** `IBM Plex Mono`

### Why These Fonts
1. `Cormorant Garamond` 给出一点“编辑部 / 剧情感 / 戏剧感”，但只用于少量标题，不进入高频 UI。
2. `Plus Jakarta Sans` 足够现代、清晰、友好，适合密集工作台。
3. `IBM Plex Mono` 让版本号、镜头编码、任务状态、时间戳更有系统感。

### Type Scale
- Display XL: 48 / 52
- Display L: 36 / 42
- H1: 28 / 34
- H2: 22 / 28
- H3: 18 / 24
- Body L: 16 / 26
- Body M: 14 / 22
- Body S: 12 / 18
- Mono S: 12 / 18

### Typography Rules
1. Serif 只用于英雄区、章节标题、少量强调。
2. 所有输入框、按钮、表单、表格一律用无衬线。
3. 编码、时长、版本、状态标签使用等宽字体。

## Layout System

### Layout Approach
- **Approach:** Hybrid
- **Why:** 产品本体是高密度工作台，必须守纪律；但英雄区、空状态、项目封面、成片页顶部允许一点 editorial 处理。

### Grid
- Desktop content width: `1440px` max
- Workspace shell: `280px / fluid center / 340px`
- Comfortable shell: `240px / fluid center / 320px`
- Page padding: `24px`
- Section gap: `24px` or `32px`

### Spacing Scale
- Base unit: `8px`
- Tight: `4 / 8 / 12`
- Standard: `16 / 24 / 32`
- Spacious: `40 / 48 / 64`

### Radius
- Cards: `16px`
- Inputs / buttons: `12px`
- Pills / tags: `999px`
- Preview frame: `20px`

### Border And Shadow
- Borders are preferred over heavy shadows.
- Default border: `1px solid #D7D0C8`
- Elevated card shadow: `0 12px 30px rgba(23, 21, 29, 0.08)`
- Preview well shadow: `0 24px 48px rgba(23, 21, 29, 0.18)`

## Motion
- **Approach:** Intentional
- **Why:** 这个产品需要给用户“系统正在推进”的反馈，但不应该显得浮夸。

### Motion Rules
1. 阶段推进用轻微滑移和淡入。
2. 生成中状态用低频脉冲或扫描线，不用过度 loader。
3. 版本切换和对比要有明显但短促的过渡。
4. 大面积弹跳、果冻感动效禁用。

## Core Surface Model

### Surface Hierarchy
1. **Background Surface:** `Paper`
2. **Panel Surface:** `#F4EEE7`
3. **Card Surface:** `#FFFDFC`
4. **Dark Preview Surface:** `#17151D`
5. **Overlay Surface:** `rgba(23, 21, 29, 0.58)`

### Workspace Hierarchy
1. 左栏是结构。
2. 中栏是主舞台。
3. 右栏是建议和检查。
4. 顶部是阶段和动作。

## Navigation Model

### Primary Navigation
1. Home
2. Projects
3. Templates
4. Assets
5. Analytics

### Project Navigation
1. Overview
2. Story Bible
3. Characters
4. Episode Plan
5. Storyboard
6. Preview & QA
7. Publish

### Persistent Status Bar
必须常驻显示：
1. 当前阶段
2. 上一步
3. 下一步
4. 最近一次运行结果
5. 当前审核状态

## Key Page Patterns

### 1. Dashboard / Home
- Recent projects first
- “从素材改编”作为主入口
- 空状态不要像管理后台，要像创作入口

### 2. Project Workspace
- 左侧项目树固定
- 中间显示当前阶段主编辑器
- 右侧显示 AI 建议、版本、QA、风险
- 顶部固定推进栏和当前状态

### 3. Character Library
- 角色卡应像 casting board
- 每张卡重点展示：
  - 名称
  - 功能位
  - 视觉锚点
  - 当前锁定状态
  - 被引用次数

### 4. Storyboard
- 必须是视觉流，不是字段表
- 每张镜头卡必须出现：
  - 缩略图
  - 镜头编号
  - 时长
  - 出场角色
  - 当前状态
  - 锁定/重跑操作

### 5. Preview & QA
- 9:16 预览居中
- 旁边紧贴 QA 列表
- 风险信息优先于导出按钮

## Components

### Buttons
- Primary: Wine fill + light text
- Secondary: light surface + ink border
- Ghost: transparent + ink text
- Destructive: error tone outline first, solid only for final confirmation

### Tags
- Stage tags: wine / copper family
- Status tags: semantic colors
- Locked tag: graphite background + light text

### Inputs
- 背景接近 `Card Surface`
- Focus 使用 `Wine` 细边框，不用外发光
- 错误状态用 `Error` 边框 + 说明文本

### Cards
- 用边框和轻阴影建立层级
- 重要卡片允许顶部有一条 `Wine` 或 `Copper` 标识线

## Content Tone
1. 说“当前阶段”“生成结果”“重跑这个镜头”，不说内部工程术语。
2. 不对用户展示 `workflow`、`schema`、`stage task` 这类内部词。
3. AI 文案要像制作助理，不像聊天机器人。

## Do / Don't

### Do
1. 让内容产物成为界面主角。
2. 用排版和留白建立专业感。
3. 用小范围强调色制造记忆点。
4. 让每一步都看起来可控。

### Don't
1. 不要做成全屏聊天工具。
2. 不要做成紫色 AI 实验室。
3. 不要做成企业中台风的冷后台。
4. 不要在同一个页面塞四五个主任务。

## Accessibility
1. 正文对比度至少达到 AA。
2. 所有关键状态不能只靠颜色区分。
3. Storyboard 卡片必须支持键盘聚焦顺序。
4. 9:16 预览旁的说明区要支持高密度信息阅读。

## Responsive Rules
1. Desktop first.
2. Tablet 允许压缩为双栏。
3. Mobile 只做查看、审批、评论、轻操作，不做复杂编辑。

## Implementation Tokens

### CSS Custom Properties
```css
:root {
  --bg: #fcfaf7;
  --bg-soft: #f7f2ec;
  --panel: #f4eee7;
  --card: #fffdfc;
  --ink: #17151d;
  --graphite: #2a2731;
  --slate: #66606f;
  --line: #d7d0c8;
  --accent: #8e334f;
  --accent-2: #b86d40;
  --rose: #d9b8bf;
  --sage: #a8b09e;
  --success: #2e7d5a;
  --warning: #c07a24;
  --error: #b23a3a;
  --info: #3559b7;
  --radius-card: 16px;
  --radius-control: 12px;
  --radius-pill: 999px;
  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
}
```

## Final Design Decision
这个产品的最佳气质不是“AI 工具感”，而是：

**一个能让创作者稳定推进作品的编辑部控制台。**

它应该让用户感到：
1. 我在掌控流程
2. 我在审阅作品
3. 我可以修改、锁定、回滚
4. 我不是在和一个黑箱对赌
