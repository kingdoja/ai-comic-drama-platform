# 代码重构需求文档

## 简介

当前项目文件组织较为混乱，测试文件、配置文件、Agent 实现文件都堆积在同一目录下。需要重新组织代码结构，提升代码可读性和可维护性。

## 术语表

- **Agent**: AI 代理，负责生成特定类型的文档（Brief、Story Bible、Character、Script、Storyboard）
- **Test**: 测试文件，用于验证 Agent 功能
- **Service**: 服务层，如 LLM 服务、验证器服务
- **Config**: 配置文件，如 .env、requirements.txt

## 需求

### 需求 1：重组 workers/agent-runtime 目录结构

**用户故事：** 作为开发者，我希望 agent-runtime 目录结构清晰，以便快速找到相关文件。

#### 验收标准

1. WHEN 查看 workers/agent-runtime 目录 THEN 系统应该按功能分类组织文件
2. WHEN 查找 Agent 实现 THEN 系统应该将所有 Agent 放在 agents/ 子目录
3. WHEN 查找测试文件 THEN 系统应该将所有测试放在 tests/ 子目录
4. WHEN 查找服务文件 THEN 系统应该将服务类放在 services/ 子目录
5. WHEN 查找配置文件 THEN 系统应该将配置保留在根目录或 config/ 子目录

### 需求 2：创建清晰的目录结构

**用户故事：** 作为新加入的开发者，我希望目录结构一目了然，以便快速理解项目组织。

#### 验收标准

1. WHEN 查看项目结构 THEN 系统应该有 agents/、tests/、services/ 等清晰的子目录
2. WHEN 查看 agents/ 目录 THEN 系统应该包含所有 5 个 Agent 实现文件
3. WHEN 查看 tests/ 目录 THEN 系统应该包含所有测试文件，按 Agent 分组
4. WHEN 查看 services/ 目录 THEN 系统应该包含 llm_service.py、validator.py 等服务文件
5. WHEN 查看根目录 THEN 系统应该只保留必要的配置文件和 README

### 需求 3：更新导入路径

**用户故事：** 作为开发者，我希望重构后代码仍能正常运行，所有导入路径正确更新。

#### 验收标准

1. WHEN 移动文件后 THEN 系统应该更新所有相关的 import 语句
2. WHEN 运行测试 THEN 系统应该能正确找到所有模块
3. WHEN Agent 执行 THEN 系统应该能正确导入依赖的服务
4. WHEN 查看导入语句 THEN 系统应该使用相对导入或包导入
5. WHEN 添加 __init__.py THEN 系统应该将目录标记为 Python 包

### 需求 4：创建文档说明

**用户故事：** 作为开发者，我希望有清晰的文档说明新的目录结构，以便理解项目组织。

#### 验收标准

1. WHEN 查看 README THEN 系统应该说明新的目录结构
2. WHEN 查看各子目录 THEN 系统应该有对应的 README 说明该目录的用途
3. WHEN 查看文档 THEN 系统应该包含文件移动的映射表
4. WHEN 新开发者加入 THEN 系统应该提供快速上手指南
5. WHEN 查看测试文档 THEN 系统应该说明如何运行各类测试

## 建议的目录结构

```
workers/agent-runtime/
├── agents/                    # Agent 实现
│   ├── __init__.py
│   ├── base_agent.py         # 基类
│   ├── brief_agent.py
│   ├── story_bible_agent.py
│   ├── character_agent.py
│   ├── script_agent.py
│   └── storyboard_agent.py
├── services/                  # 服务层
│   ├── __init__.py
│   ├── llm_service.py
│   ├── mock_llm_service.py
│   └── validator.py
├── tests/                     # 测试文件
│   ├── __init__.py
│   ├── test_brief_agent.py
│   ├── test_story_bible_agent.py
│   ├── test_character_agent.py
│   ├── test_script_agent.py
│   ├── test_storyboard_agent.py
│   ├── test_llm_connection.py
│   ├── test_validator.py
│   └── test_proxy_fix.py
├── config/                    # 配置（可选）
│   └── setup_llm.py
├── docs/                      # 文档
│   ├── README_LLM.md
│   ├── README_VALIDATOR.md
│   └── LLM_INTEGRATION_SUMMARY.md
├── .env                       # 环境变量
├── .env.example
├── requirements.txt
└── README.md                  # 主文档
```
