"""
快速测试 LLM 连接

使用方法:
1. 在 .env 文件中填入你的 QWEN_API_KEY
2. 运行: python quick_test.py
"""

import os
import sys
from pathlib import Path

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    load_dotenv(env_file)
    print(f"✓ 已加载配置文件: {env_file}\n")
except ImportError:
    print("⚠ python-dotenv 未安装")
    print("  运行: pip install python-dotenv\n")

# 检查 API Key
api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    print("✗ 错误: 未找到 QWEN_API_KEY")
    print("\n请按以下步骤配置:")
    print("1. 访问 https://dashscope.console.aliyun.com/apiKey")
    print("2. 登录阿里云账号并创建 API Key")
    print("3. 编辑 .env 文件，将 API Key 填入 QWEN_API_KEY=")
    print("\n示例:")
    print("  QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx")
    sys.exit(1)

print(f"✓ 找到 API Key: {api_key[:10]}...{api_key[-4:]}\n")

# 测试连接
print("="*50)
print("测试通义千问连接")
print("="*50)

try:
    from llm_service import QwenLLMService
    
    print("创建服务...")
    llm = QwenLLMService()
    print(f"✓ 服务创建成功，模型: {llm.model}\n")
    
    print("调用 API...")
    response = llm.generate_from_prompt(
        system_prompt="你是一个测试助手，请简短回复。",
        user_prompt="请回复：通义千问连接成功",
        temperature=0.1,
        max_tokens=50
    )
    
    print("✓ API 调用成功！\n")
    print(f"响应内容: {response.content}")
    print(f"Token 使用: {response.token_usage}")
    print(f"使用模型: {response.model}")
    
    print("\n" + "="*50)
    print("✓ 测试通过！LLM 服务配置正确")
    print("="*50)
    
except ImportError as e:
    print(f"✗ 依赖缺失: {e}")
    print("\n请运行: pip install dashscope")
    sys.exit(1)
    
except Exception as e:
    print(f"✗ API 调用失败: {e}")
    print("\n可能的原因:")
    print("1. API Key 无效或过期")
    print("2. 账户余额不足")
    print("3. 网络连接问题")
    print("\n请检查:")
    print("- API Key 是否正确")
    print("- 登录控制台查看余额: https://dashscope.console.aliyun.com/")
    sys.exit(1)
