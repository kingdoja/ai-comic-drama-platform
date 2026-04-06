# Agent Runtime

AI 漫剧生成系统的 Agent 运行时模块，负责生成剧集的各类文档（Brief、Story Bible、Character、Script、Storyboard）。

## 目录结构

```
workers/agent-runtime/
├── agents/                    # Agent 实现模块
│   ├── __init__.py           # 导出所有 Agent
│   ├── base_agent.py         # Agent 基类
│   ├── brief_agent.py        # Brief 生成 Agent
│   ├── story_bible_agent.py  # Story Bible 生成 Agent
│   ├── character_agent.py    # Character 生成 Agent
│   ├── script_agent.py       # Script 生成 Agent
│   └── storyboard_agent.py   # Storyboard 生成 Agent
├── services/                  # 服务层模块
│   ├── __init__.py           # 导出所有服务
│   ├── llm_service.py        # LLM 服务（Qwen、OpenAI、Claude）
│   ├── mock_llm_service.py   # Mock LLM 服务（用于测试）
│   └── validator.py          # 验证器服务
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
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── setup_llm.py          # LLM 配置向导
│   └── quick_test.py         # LLM 快速连接测试
├── docs/                      # 文档
│   ├── LLM.md                # LLM 服务文档
│   ├── VALIDATOR.md          # 验证器文档
│   ├── INTEGRATION_SUMMARY.md # 集成总结
│   └── AGENTS_COMPLETE.md    # Agent 完整文档
├── .env                       # 环境变量（不提交到 Git）
├── .env.example              # 环境变量示例
├── requirements.txt          # Python 依赖
├── main.py                   # 主入口文件
└── README.md                 # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
cd workers/agent-runtime
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# 至少需要配置一个 LLM 提供商的 API Key
```

### 3. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定 Agent 的测试
pytest tests/test_brief_agent.py

# 运行 LLM 连接测试
pytest tests/test_llm_connection.py
```

## 使用示例

### 导入 Agent

```python
# 方式 1：从 agents 模块导入
from agents import BriefAgent, StoryBibleAgent, CharacterAgent

# 方式 2：直接导入特定 Agent
from agents.brief_agent import BriefAgent
from agents.story_bible_agent import StoryBibleAgent
```

### 导入服务

```python
# 方式 1：从 services 模块导入
from services import LLMServiceFactory, Validator

# 方式 2：直接导入特定服务
from services.llm_service import LLMServiceFactory, LLMProvider
from services.validator import Validator
```

### 创建和使用 Agent

```python
from agents import BriefAgent
from services import LLMServiceFactory, Validator

# 创建 LLM 服务（从环境变量自动配置）
llm = LLMServiceFactory.create_from_env()

# 创建验证器
validator = Validator()

# 创建 Brief Agent
agent = BriefAgent(
    db_session=db,
    llm_service=llm,
    validator=validator
)

# 执行 Agent
result = agent.execute(task_input)
```

### 切换 LLM 提供商

```python
from services import LLMServiceFactory, LLMProvider

# 使用通义千问（推荐用于中文内容）
llm = LLMServiceFactory.create(LLMProvider.QWEN)

# 使用 OpenAI
llm = LLMServiceFactory.create(LLMProvider.OPENAI, model="gpt-4o")

# 使用 Claude
llm = LLMServiceFactory.create(LLMProvider.CLAUDE, model="claude-3-5-sonnet-20241022")
```

## Agent 说明

### BriefAgent
生成剧集的 Brief 文档，包含故事梗概、主题、目标受众等信息。

**输入**: 项目信息、剧集信息  
**输出**: Brief 文档（JSON 格式）

### StoryBibleAgent
生成 Story Bible 文档，包含世界观设定、故事背景、核心冲突等。

**输入**: Brief 文档  
**输出**: Story Bible 文档（JSON 格式）

### CharacterAgent
生成角色设定文档，包含角色性格、背景、关系等。

**输入**: Brief、Story Bible  
**输出**: Character 文档（JSON 格式）

### ScriptAgent
生成剧本文档，包含对话、场景描述、镜头说明等。

**输入**: Brief、Story Bible、Character  
**输出**: Script 文档（JSON 格式）

### StoryboardAgent
生成分镜脚本文档，包含镜头描述、画面构图等。

**输入**: Script  
**输出**: Storyboard 文档（JSON 格式）

## 服务说明

### LLMService
LLM 服务抽象层，支持多个 LLM 提供商：
- **Qwen (通义千问)**: 推荐用于中文内容，性价比高
- **OpenAI**: 推荐用于英文内容，性能强大
- **Claude**: 推荐用于长文本，上下文窗口大

详细使用方法请参考 [docs/LLM.md](docs/LLM.md)

### Validator
验证器服务，用于验证生成的文档是否符合格式要求。

详细使用方法请参考 [docs/VALIDATOR.md](docs/VALIDATOR.md)

## 测试

### 运行所有测试

```bash
pytest tests/
```

### 运行特定测试

```bash
# 测试 Brief Agent
pytest tests/test_brief_agent.py

# 测试 LLM 连接
pytest tests/test_llm_connection.py

# 测试验证器
pytest tests/test_validator.py
```

### 测试覆盖率

```bash
pytest --cov=agents --cov=services tests/
```

## 开发指南

### 添加新的 Agent

1. 在 `agents/` 目录创建新的 Agent 文件
2. 继承 `BaseAgent` 类
3. 实现 `execute()` 方法
4. 在 `agents/__init__.py` 中导出新 Agent
5. 在 `tests/` 目录添加测试文件

示例：

```python
# agents/new_agent.py
from agents.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def execute(self, task_input):
        # 实现生成逻辑
        pass
```

```python
# agents/__init__.py
from .new_agent import NewAgent

__all__ = [
    # ... 其他 Agent
    'NewAgent',
]
```

### 添加新的服务

1. 在 `services/` 目录创建新的服务文件
2. 实现服务接口
3. 在 `services/__init__.py` 中导出新服务
4. 在 `tests/` 目录添加测试文件

## 常见问题

### Q: 如何配置 LLM API Key？

编辑 `.env` 文件，添加对应提供商的 API Key：

```bash
# 通义千问（推荐）
QWEN_API_KEY=your_qwen_api_key

# OpenAI（可选）
OPENAI_API_KEY=your_openai_api_key

# Claude（可选）
ANTHROPIC_API_KEY=your_claude_api_key

# 选择默认提供商
LLM_PROVIDER=qwen
```

### Q: 如何测试 LLM 是否配置正确？

```bash
pytest tests/test_llm_connection.py
```

或运行快速测试脚本：

```bash
python utils/quick_test.py
```

### Q: 导入模块时出错怎么办？

确保你在正确的目录运行代码，并且已经安装所有依赖：

```bash
cd workers/agent-runtime
pip install -r requirements.txt
```

如果仍有问题，检查 Python 路径：

```python
import sys
print(sys.path)
```

### Q: 如何降低 LLM 调用成本？

1. 使用更便宜的模型（qwen-turbo, gpt-4o-mini）
2. 减少 max_tokens 限制
3. 优化 prompt，减少不必要的输入
4. 使用缓存机制避免重复调用

详细信息请参考 [docs/LLM.md](docs/LLM.md)

## 相关文档

- [LLM 服务集成指南](docs/LLM.md)
- [验证器使用指南](docs/VALIDATOR.md)
- [集成总结](docs/INTEGRATION_SUMMARY.md)
- [Agent 完整文档](docs/AGENTS_COMPLETE.md)

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。

---

**最后更新**: 2026-04-06
