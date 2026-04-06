# LLM 服务集成指南

## 概述

本项目支持多个 LLM 提供商，默认使用**通义千问（Qwen）**。

## 快速开始

### 1. 安装依赖

```bash
# 通义千问（必需）
pip install dashscope

# OpenAI（可选）
pip install openai

# Claude（可选）
pip install anthropic
```

### 2. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
```

### 3. 获取 API Key

#### 通义千问（推荐）
1. 访问 [DashScope 控制台](https://dashscope.console.aliyun.com/apiKey)
2. 登录阿里云账号
3. 创建 API Key
4. 复制到 `.env` 文件的 `QWEN_API_KEY`

**价格**（2024年）：
- qwen-turbo: ¥0.0008/1K tokens
- qwen-plus: ¥0.004/1K tokens
- qwen-max: ¥0.04/1K tokens

#### OpenAI
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 创建 API Key
3. 复制到 `.env` 文件的 `OPENAI_API_KEY`

**价格**（2024年）：
- gpt-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
- gpt-4o: $2.50/1M input tokens, $10.00/1M output tokens

#### Anthropic Claude
1. 访问 [Anthropic Console](https://console.anthropic.com/settings/keys)
2. 创建 API Key
3. 复制到 `.env` 文件的 `ANTHROPIC_API_KEY`

**价格**（2024年）：
- claude-3-5-sonnet: $3.00/1M input tokens, $15.00/1M output tokens
- claude-3-opus: $15.00/1M input tokens, $75.00/1M output tokens

## 使用方法

### 方式 1：使用工厂方法（推荐）

```python
from llm_service import LLMServiceFactory, LLMProvider

# 从环境变量自动创建（读取 LLM_PROVIDER）
llm = LLMServiceFactory.create_from_env()

# 或手动指定提供商
llm = LLMServiceFactory.create(LLMProvider.QWEN)
llm = LLMServiceFactory.create(LLMProvider.OPENAI)
llm = LLMServiceFactory.create(LLMProvider.CLAUDE)

# 生成文本
response = llm.generate_from_prompt(
    system_prompt="你是一个专业的编剧助手",
    user_prompt="请为一部科幻漫剧写一个简短的故事梗概",
    temperature=0.7
)

print(response.content)
print(f"Token 使用: {response.token_usage}")
```

### 方式 2：直接使用服务类

```python
from llm_service import QwenLLMService, LLMMessage

# 创建服务实例
llm = QwenLLMService(
    api_key="your_api_key",  # 或从环境变量读取
    model="qwen-plus"
)

# 使用消息列表
messages = [
    LLMMessage(role="system", content="你是一个专业的编剧助手"),
    LLMMessage(role="user", content="请为一部科幻漫剧写一个简短的故事梗概")
]

response = llm.generate(messages, temperature=0.7)
print(response.content)
```

### 方式 3：在 Agent 中使用

```python
from llm_service import LLMServiceFactory
from brief_agent import BriefAgent

# 创建 LLM 服务
llm = LLMServiceFactory.create_from_env()

# 创建 Agent（传入 LLM 服务）
agent = BriefAgent(
    db_session=db,
    llm_service=llm,
    validator=validator
)

# 执行 Agent
result = agent.execute(task_input)
```

## 切换 LLM 提供商

### 方法 1：修改环境变量

```bash
# .env 文件
LLM_PROVIDER=qwen    # 使用通义千问
# LLM_PROVIDER=openai  # 使用 OpenAI
# LLM_PROVIDER=claude  # 使用 Claude
```

### 方法 2：代码中指定

```python
from llm_service import LLMServiceFactory, LLMProvider

# 使用通义千问
llm = LLMServiceFactory.create(LLMProvider.QWEN)

# 使用 OpenAI
llm = LLMServiceFactory.create(LLMProvider.OPENAI, model="gpt-4o")

# 使用 Claude
llm = LLMServiceFactory.create(LLMProvider.CLAUDE, model="claude-3-5-sonnet-20241022")
```

## 模型选择建议

### 通义千问（推荐用于中文内容）
- **qwen-turbo**: 快速响应，适合简单任务
- **qwen-plus**: 平衡性能和成本，推荐日常使用
- **qwen-max**: 最强性能，适合复杂创作任务

### OpenAI（推荐用于英文内容）
- **gpt-4o-mini**: 快速且便宜，适合简单任务
- **gpt-4o**: 最新模型，综合性能最佳
- **gpt-4-turbo**: 强大的推理能力

### Claude（推荐用于长文本）
- **claude-3-haiku**: 快速响应
- **claude-3-5-sonnet**: 最新模型，性价比高
- **claude-3-opus**: 最强性能，适合复杂任务

## 成本估算

以生成一个完整剧集（5个文档）为例：

### 通义千问 qwen-plus
- Brief: ~500 tokens × ¥0.004/1K = ¥0.002
- Story Bible: ~2000 tokens × ¥0.004/1K = ¥0.008
- Character: ~1500 tokens × ¥0.004/1K = ¥0.006
- Script: ~5000 tokens × ¥0.004/1K = ¥0.020
- Storyboard: ~3000 tokens × ¥0.004/1K = ¥0.012

**总计**: ~¥0.048/剧集 (~$0.007)

### OpenAI gpt-4o-mini
- 总计: ~$0.10/剧集

### Claude claude-3-5-sonnet
- 总计: ~$0.20/剧集

## 错误处理

```python
from llm_service import LLMServiceFactory

try:
    llm = LLMServiceFactory.create_from_env()
    response = llm.generate_from_prompt(
        system_prompt="你是助手",
        user_prompt="你好"
    )
except ValueError as e:
    print(f"配置错误: {e}")
except ImportError as e:
    print(f"依赖缺失: {e}")
except Exception as e:
    print(f"API 调用失败: {e}")
```

## 常见问题

### Q: 如何测试 LLM 是否配置正确？

```python
from llm_service import LLMServiceFactory

llm = LLMServiceFactory.create_from_env()
response = llm.generate_from_prompt(
    system_prompt="你是一个测试助手",
    user_prompt="请回复：配置成功",
    temperature=0.1
)
print(response.content)
```

### Q: 如何控制生成长度？

```python
response = llm.generate_from_prompt(
    system_prompt="你是助手",
    user_prompt="写一个故事",
    max_tokens=1000  # 限制最大 token 数
)
```

### Q: 如何降低成本？

1. 使用更便宜的模型（qwen-turbo, gpt-4o-mini）
2. 减少 max_tokens 限制
3. 优化 prompt，减少不必要的输入
4. 使用缓存机制避免重复调用

### Q: 通义千问 API 报错怎么办？

常见错误：
- `InvalidApiKey`: API Key 无效或过期
- `InsufficientBalance`: 账户余额不足
- `RateLimitExceeded`: 超过调用频率限制

解决方案：
1. 检查 API Key 是否正确
2. 登录控制台充值
3. 降低调用频率或升级套餐

## 下一步

- 查看 `brief_agent.py` 了解如何在 Agent 中使用 LLM
- 查看 `test_llm_service.py` 了解测试用例
- 阅读各提供商的官方文档了解更多高级功能

---

**最后更新**: 2026-04-06
