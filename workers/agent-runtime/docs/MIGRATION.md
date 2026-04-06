# 代码重构迁移指南

## 概述

本文档记录了 `workers/agent-runtime` 目录的重构过程，包括文件移动映射、导入路径变化和迁移指南。

## 文件移动映射

### Agent 文件

| 原路径 | 新路径 |
|--------|--------|
| `base_agent.py` | `agents/base_agent.py` |
| `brief_agent.py` | `agents/brief_agent.py` |
| `story_bible_agent.py` | `agents/story_bible_agent.py` |
| `character_agent.py` | `agents/character_agent.py` |
| `script_agent.py` | `agents/script_agent.py` |
| `storyboard_agent.py` | `agents/storyboard_agent.py` |

### 服务文件

| 原路径 | 新路径 |
|--------|--------|
| `llm_service.py` | `services/llm_service.py` |
| `mock_llm_service.py` | `services/mock_llm_service.py` |
| `validator.py` | `services/validator.py` |

### 测试文件

| 原路径 | 新路径 |
|--------|--------|
| `test_brief_real_llm.py` | `tests/test_brief_agent.py` |
| `test_story_bible_real_llm.py` | `tests/test_story_bible_agent.py` |
| `test_character_real_llm.py` | `tests/test_character_agent.py` |
| `test_script_real_llm.py` | `tests/test_script_agent.py` |
| `test_storyboard_agent.py` | `tests/test_storyboard_agent.py` |
| `test_llm_connection.py` | `tests/test_llm_connection.py` |
| `test_validator.py` | `tests/test_validator.py` |
| `test_proxy_fix.py` | `tests/test_proxy_fix.py` |

### 工具和文档文件

| 原路径 | 新路径 |
|--------|--------|
| `setup_llm.py` | `utils/setup_llm.py` |
| `quick_test.py` | `utils/quick_test.py` |
| `README_LLM.md` | `docs/LLM.md` |
| `README_VALIDATOR.md` | `docs/VALIDATOR.md` |
| `LLM_INTEGRATION_SUMMARY.md` | `docs/INTEGRATION_SUMMARY.md` |

## 导入路径变化

### Agent 导入

**重构前：**
```python
from base_agent import BaseAgent
from llm_service import LLMServiceFactory
from validator import Validator
```

**重构后：**
```python
from agents.base_agent import BaseAgent
from services.llm_service import LLMServiceFactory
from services.validator import Validator
```

### 服务导入

**重构前：**
```python
from llm_service import LLMServiceFactory, QwenLLMService
from validator import Validator
```

**重构后：**
```python
from services.llm_service import LLMServiceFactory, QwenLLMService
from services.validator import Validator
```

### 测试文件导入

**重构前：**
```python
sys.path.insert(0, str(Path(__file__).parent))
from brief_agent import BriefAgent
```

**重构后：**
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
from agents.brief_agent import BriefAgent
from services.llm_service import LLMServiceFactory
```

## 新增文件

| 文件 | 说明 |
|------|------|
| `agents/__init__.py` | 导出所有 Agent 类 |
| `services/__init__.py` | 导出所有服务类 |
| `tests/__init__.py` | 测试包标记 |
| `utils/__init__.py` | 工具包标记 |

## 迁移指南

如果你的代码依赖了重构前的导入路径，请按以下步骤更新：

1. **更新 sys.path**：如果测试文件使用 `sys.path.insert`，将路径改为指向 `agent-runtime` 根目录（即 `Path(__file__).parent.parent`）。

2. **更新 Agent 导入**：将 `from brief_agent import BriefAgent` 改为 `from agents.brief_agent import BriefAgent`。

3. **更新服务导入**：将 `from llm_service import ...` 改为 `from services.llm_service import ...`，将 `from validator import ...` 改为 `from services.validator import ...`。

4. **使用 `__init__.py` 快捷导入**（可选）：
   ```python
   from agents import BriefAgent, StoryBibleAgent
   from services import LLMServiceFactory, Validator
   ```

## 运行测试

```bash
cd workers/agent-runtime
python -m pytest tests/ -v
```

运行单个测试：
```bash
python -m pytest tests/test_brief_agent.py -v
```
