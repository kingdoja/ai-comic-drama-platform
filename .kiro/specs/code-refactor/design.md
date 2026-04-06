# 代码重构设计文档

## 概述

本设计文档描述如何重构 `workers/agent-runtime` 目录，将混乱的文件组织改造为清晰、专业的目录结构。

## 架构

### 当前结构问题

```
workers/agent-runtime/
├── base_agent.py
├── brief_agent.py
├── story_bible_agent.py
├── character_agent.py
├── script_agent.py
├── storyboard_agent.py
├── llm_service.py
├── mock_llm_service.py
├── validator.py
├── test_brief_real_llm.py
├── test_story_bible_real_llm.py
├── test_character_real_llm.py
├── test_script_real_llm.py
├── test_storyboard_agent.py
├── test_llm_connection.py
├── test_validator.py
├── test_proxy_fix.py
├── setup_llm.py
├── README_LLM.md
├── README_VALIDATOR.md
├── LLM_INTEGRATION_SUMMARY.md
├── .env
├── .env.example
└── requirements.txt
```

**问题：**
- 所有文件堆积在一个目录
- Agent、Service、Test 混在一起
- 难以快速定位文件
- 不符合 Python 项目最佳实践

### 目标结构

```
workers/agent-runtime/
├── agents/                    # Agent 实现模块
│   ├── __init__.py           # 导出所有 Agent
│   ├── base_agent.py
│   ├── brief_agent.py
│   ├── story_bible_agent.py
│   ├── character_agent.py
│   ├── script_agent.py
│   └── storyboard_agent.py
├── services/                  # 服务层模块
│   ├── __init__.py           # 导出所有服务
│   ├── llm_service.py
│   ├── mock_llm_service.py
│   └── validator.py
├── tests/                     # 测试模块
│   ├── __init__.py
│   ├── test_brief_agent.py
│   ├── test_story_bible_agent.py
│   ├── test_character_agent.py
│   ├── test_script_agent.py
│   ├── test_storyboard_agent.py
│   ├── test_llm_connection.py
│   ├── test_validator.py
│   └── test_proxy_fix.py
├── utils/                     # 工具模块（可选）
│   ├── __init__.py
│   └── setup_llm.py
├── docs/                      # 文档
│   ├── LLM.md
│   ├── VALIDATOR.md
│   └── INTEGRATION_SUMMARY.md
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## 组件和接口

### 1. agents/ 模块

**职责：** 包含所有 Agent 实现

**文件：**
- `base_agent.py` - Agent 基类
- `brief_agent.py` - Brief 生成 Agent
- `story_bible_agent.py` - Story Bible 生成 Agent
- `character_agent.py` - Character 生成 Agent
- `script_agent.py` - Script 生成 Agent
- `storyboard_agent.py` - Storyboard 生成 Agent

**__init__.py 导出：**
```python
from .base_agent import BaseAgent, DocumentRef, LockedRef, StageTaskInput, Warning
from .brief_agent import BriefAgent
from .story_bible_agent import StoryBibleAgent
from .character_agent import CharacterAgent
from .script_agent import ScriptAgent
from .storyboard_agent import StoryBoardAgent

__all__ = [
    'BaseAgent',
    'DocumentRef',
    'LockedRef',
    'StageTaskInput',
    'Warning',
    'BriefAgent',
    'StoryBibleAgent',
    'CharacterAgent',
    'ScriptAgent',
    'StoryBoardAgent',
]
```

### 2. services/ 模块

**职责：** 包含所有服务层实现

**文件：**
- `llm_service.py` - LLM 服务（Qwen、OpenAI、Claude）
- `mock_llm_service.py` - Mock LLM 服务（用于测试）
- `validator.py` - 验证器服务

**__init__.py 导出：**
```python
from .llm_service import (
    LLMService,
    LLMServiceFactory,
    LLMMessage,
    LLMResponse,
    QwenLLMService,
    OpenAILLMService,
    ClaudeLLMService,
)
from .mock_llm_service import MockLLMService
from .validator import Validator, ValidationResult, ValidationError

__all__ = [
    'LLMService',
    'LLMServiceFactory',
    'LLMMessage',
    'LLMResponse',
    'QwenLLMService',
    'OpenAILLMService',
    'ClaudeLLMService',
    'MockLLMService',
    'Validator',
    'ValidationResult',
    'ValidationError',
]
```

### 3. tests/ 模块

**职责：** 包含所有测试文件

**文件：**
- `test_brief_agent.py` - Brief Agent 测试
- `test_story_bible_agent.py` - Story Bible Agent 测试
- `test_character_agent.py` - Character Agent 测试
- `test_script_agent.py` - Script Agent 测试
- `test_storyboard_agent.py` - Storyboard Agent 测试
- `test_llm_connection.py` - LLM 连接测试
- `test_validator.py` - 验证器测试
- `test_proxy_fix.py` - 代理修复测试

### 4. utils/ 模块（可选）

**职责：** 包含工具脚本

**文件：**
- `setup_llm.py` - LLM 配置向导

### 5. docs/ 模块

**职责：** 包含文档文件

**文件：**
- `LLM.md` - LLM 服务文档
- `VALIDATOR.md` - 验证器文档
- `INTEGRATION_SUMMARY.md` - 集成总结

## 数据模型

无需修改数据模型，只是文件移动和导入路径更新。

## 正确性属性

*A property is a characteristic or behavior that should hold true across all valid executions of a system.*

### Property 1: 导入路径正确性
*For any* 移动后的文件，所有导入语句应该能正确解析到目标模块
**Validates: Requirements 3.1, 3.2**

### Property 2: 测试可执行性
*For any* 测试文件，移动后应该能正常执行并通过
**Validates: Requirements 3.2, 3.3**

### Property 3: Agent 功能完整性
*For any* Agent，移动后应该保持原有功能不变
**Validates: Requirements 3.3**

### Property 4: 文档完整性
*For any* 文档文件，移动后应该保持内容完整且路径引用正确
**Validates: Requirements 4.1, 4.2**

## 错误处理

### 导入错误
- **场景：** 移动文件后导入路径错误
- **处理：** 更新所有 import 语句，使用相对导入或包导入
- **验证：** 运行所有测试确保导入正确

### 路径错误
- **场景：** 文件引用路径错误（如 .env 文件）
- **处理：** 更新所有文件路径引用
- **验证：** 测试配置加载功能

## 测试策略

### 单元测试
- 移动文件后运行所有现有测试
- 确保所有测试通过
- 验证导入路径正确

### 集成测试
- 测试 Agent 端到端执行
- 验证 LLM 服务正常工作
- 确认配置文件正确加载

### 手动测试
- 检查目录结构是否清晰
- 验证文档路径引用正确
- 确认新开发者能快速理解结构

## 迁移步骤

1. **创建新目录结构**
   - 创建 agents/、services/、tests/、utils/、docs/ 目录
   - 添加 __init__.py 文件

2. **移动 Agent 文件**
   - 移动所有 *_agent.py 到 agents/
   - 更新 agents/__init__.py

3. **移动服务文件**
   - 移动 llm_service.py、validator.py 等到 services/
   - 更新 services/__init__.py

4. **移动测试文件**
   - 移动所有 test_*.py 到 tests/
   - 更新测试中的导入路径

5. **移动工具和文档**
   - 移动 setup_llm.py 到 utils/
   - 移动文档到 docs/

6. **更新导入路径**
   - 更新所有文件中的 import 语句
   - 使用 `from agents.brief_agent import BriefAgent` 格式

7. **测试验证**
   - 运行所有测试
   - 修复任何导入错误
   - 验证功能完整性

8. **更新文档**
   - 更新 README.md
   - 添加目录结构说明
   - 创建迁移指南
