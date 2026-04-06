"""
LLM Service Layer - 支持多个 LLM 提供商

支持的提供商：
- 通义千问（Qwen）- 默认
- OpenAI (GPT-4/GPT-3.5)
- Anthropic Claude
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class LLMProvider(Enum):
    """LLM 提供商枚举"""
    QWEN = "qwen"  # 通义千问
    OPENAI = "openai"
    CLAUDE = "claude"


@dataclass
class LLMMessage:
    """LLM 消息格式"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """LLM 响应格式"""
    content: str
    token_usage: Dict[str, int]  # {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    model: str
    finish_reason: str  # "stop", "length", "content_filter"


class BaseLLMService(ABC):
    """LLM 服务抽象基类"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        初始化 LLM 服务
        
        Args:
            api_key: API 密钥（如果为 None，从环境变量读取）
            model: 模型名称（如果为 None，使用默认模型）
        """
        self.api_key = api_key or self._get_api_key_from_env()
        self.model = model or self._get_default_model()
    
    @abstractmethod
    def _get_api_key_from_env(self) -> str:
        """从环境变量获取 API 密钥"""
        pass
    
    @abstractmethod
    def _get_default_model(self) -> str:
        """获取默认模型名称"""
        pass
    
    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成文本
        
        Args:
            messages: 消息列表
            temperature: 温度参数（0-1）
            max_tokens: 最大生成 token 数
            **kwargs: 其他提供商特定参数
            
        Returns:
            LLMResponse 对象
        """
        pass
    
    def generate_from_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        从简单的 system + user prompt 生成文本
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数
            
        Returns:
            LLMResponse 对象
        """
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]
        return self.generate(messages, temperature, max_tokens, **kwargs)


class QwenLLMService(BaseLLMService):
    """通义千问 LLM 服务"""
    
    def _get_api_key_from_env(self) -> str:
        api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("QWEN_API_KEY or DASHSCOPE_API_KEY environment variable not set")
        return api_key
    
    def _get_default_model(self) -> str:
        return "qwen-plus"  # 或 "qwen-turbo", "qwen-max"
    
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        使用通义千问生成文本
        
        文档: https://help.aliyun.com/zh/dashscope/developer-reference/api-details
        """
        try:
            import dashscope
            from dashscope import Generation
        except ImportError:
            raise ImportError(
                "dashscope package not installed. "
                "Install with: pip install dashscope"
            )
        
        # 禁用代理（避免代理配置问题）
        os.environ['NO_PROXY'] = '*'
        if 'HTTP_PROXY' in os.environ:
            del os.environ['HTTP_PROXY']
        if 'HTTPS_PROXY' in os.environ:
            del os.environ['HTTPS_PROXY']
        if 'http_proxy' in os.environ:
            del os.environ['http_proxy']
        if 'https_proxy' in os.environ:
            del os.environ['https_proxy']
        
        # 设置 API Key
        dashscope.api_key = self.api_key
        
        # 转换消息格式
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # 调用 API
        response = Generation.call(
            model=self.model,
            messages=formatted_messages,
            result_format='message',
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # 检查响应
        if response.status_code != 200:
            raise Exception(f"Qwen API error: {response.code} - {response.message}")
        
        # 解析响应
        output = response.output
        usage = response.usage
        
        return LLMResponse(
            content=output.choices[0].message.content,
            token_usage={
                "prompt_tokens": usage.input_tokens,
                "completion_tokens": usage.output_tokens,
                "total_tokens": usage.total_tokens
            },
            model=self.model,
            finish_reason=output.choices[0].finish_reason
        )


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM 服务"""
    
    def _get_api_key_from_env(self) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return api_key
    
    def _get_default_model(self) -> str:
        return "gpt-4o-mini"  # 或 "gpt-4", "gpt-3.5-turbo"
    
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        使用 OpenAI 生成文本
        
        文档: https://platform.openai.com/docs/api-reference/chat
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package not installed. "
                "Install with: pip install openai"
            )
        
        client = OpenAI(api_key=self.api_key)
        
        # 转换消息格式
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # 调用 API
        response = client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # 解析响应
        choice = response.choices[0]
        usage = response.usage
        
        return LLMResponse(
            content=choice.message.content,
            token_usage={
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            },
            model=response.model,
            finish_reason=choice.finish_reason
        )


class ClaudeLLMService(BaseLLMService):
    """Anthropic Claude LLM 服务"""
    
    def _get_api_key_from_env(self) -> str:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        return api_key
    
    def _get_default_model(self) -> str:
        return "claude-3-5-sonnet-20241022"  # 或 "claude-3-opus-20240229"
    
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        使用 Claude 生成文本
        
        文档: https://docs.anthropic.com/claude/reference/messages_post
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )
        
        client = Anthropic(api_key=self.api_key)
        
        # Claude 需要分离 system 消息
        system_message = None
        formatted_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 调用 API
        response = client.messages.create(
            model=self.model,
            system=system_message,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens or 4096,  # Claude 需要 max_tokens
            **kwargs
        )
        
        # 解析响应
        content = response.content[0].text
        usage = response.usage
        
        return LLMResponse(
            content=content,
            token_usage={
                "prompt_tokens": usage.input_tokens,
                "completion_tokens": usage.output_tokens,
                "total_tokens": usage.input_tokens + usage.output_tokens
            },
            model=response.model,
            finish_reason=response.stop_reason
        )


class LLMServiceFactory:
    """LLM 服务工厂"""
    
    @staticmethod
    def create(
        provider: LLMProvider = LLMProvider.QWEN,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMService:
        """
        创建 LLM 服务实例
        
        Args:
            provider: LLM 提供商
            api_key: API 密钥（可选）
            model: 模型名称（可选）
            
        Returns:
            LLM 服务实例
        """
        if provider == LLMProvider.QWEN:
            return QwenLLMService(api_key, model)
        elif provider == LLMProvider.OPENAI:
            return OpenAILLMService(api_key, model)
        elif provider == LLMProvider.CLAUDE:
            return ClaudeLLMService(api_key, model)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @staticmethod
    def create_from_env() -> BaseLLMService:
        """
        从环境变量创建 LLM 服务
        
        环境变量：
        - LLM_PROVIDER: "qwen", "openai", "claude" (默认: qwen)
        - LLM_MODEL: 模型名称（可选）
        
        Returns:
            LLM 服务实例
        """
        provider_str = os.getenv("LLM_PROVIDER", "qwen").lower()
        model = os.getenv("LLM_MODEL")
        
        try:
            provider = LLMProvider(provider_str)
        except ValueError:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {provider_str}. "
                f"Must be one of: {[p.value for p in LLMProvider]}"
            )
        
        return LLMServiceFactory.create(provider, model=model)
