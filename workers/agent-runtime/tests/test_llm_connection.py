"""
测试 LLM 连接和配置

运行方式:
    python test_llm_connection.py
"""

import os
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_service import LLMServiceFactory, LLMProvider


def test_qwen():
    """测试通义千问连接"""
    print("\n" + "="*50)
    print("测试通义千问 (Qwen)")
    print("="*50)
    
    try:
        llm = LLMServiceFactory.create(LLMProvider.QWEN)
        print(f"✓ 服务创建成功")
        print(f"  模型: {llm.model}")
        
        response = llm.generate_from_prompt(
            system_prompt="你是一个测试助手，请简短回复。",
            user_prompt="请回复：通义千问连接成功",
            temperature=0.1,
            max_tokens=50
        )
        
        print(f"✓ API 调用成功")
        print(f"  响应: {response.content}")
        print(f"  Token 使用: {response.token_usage}")
        print(f"  模型: {response.model}")
        
        return True
        
    except ValueError as e:
        print(f"✗ 配置错误: {e}")
        print(f"  提示: 请在 .env 文件中设置 QWEN_API_KEY")
        return False
    except ImportError as e:
        print(f"✗ 依赖缺失: {e}")
        print(f"  提示: 运行 pip install dashscope")
        return False
    except Exception as e:
        print(f"✗ API 调用失败: {e}")
        return False


def test_openai():
    """测试 OpenAI 连接"""
    print("\n" + "="*50)
    print("测试 OpenAI")
    print("="*50)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⊘ 跳过: 未配置 OPENAI_API_KEY")
        return None
    
    try:
        llm = LLMServiceFactory.create(LLMProvider.OPENAI)
        print(f"✓ 服务创建成功")
        print(f"  模型: {llm.model}")
        
        response = llm.generate_from_prompt(
            system_prompt="You are a test assistant. Reply briefly.",
            user_prompt="Reply: OpenAI connection successful",
            temperature=0.1,
            max_tokens=50
        )
        
        print(f"✓ API 调用成功")
        print(f"  响应: {response.content}")
        print(f"  Token 使用: {response.token_usage}")
        print(f"  模型: {response.model}")
        
        return True
        
    except ImportError as e:
        print(f"✗ 依赖缺失: {e}")
        print(f"  提示: 运行 pip install openai")
        return False
    except Exception as e:
        print(f"✗ API 调用失败: {e}")
        return False


def test_claude():
    """测试 Claude 连接"""
    print("\n" + "="*50)
    print("测试 Anthropic Claude")
    print("="*50)
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⊘ 跳过: 未配置 ANTHROPIC_API_KEY")
        return None
    
    try:
        llm = LLMServiceFactory.create(LLMProvider.CLAUDE)
        print(f"✓ 服务创建成功")
        print(f"  模型: {llm.model}")
        
        response = llm.generate_from_prompt(
            system_prompt="You are a test assistant. Reply briefly.",
            user_prompt="Reply: Claude connection successful",
            temperature=0.1,
            max_tokens=50
        )
        
        print(f"✓ API 调用成功")
        print(f"  响应: {response.content}")
        print(f"  Token 使用: {response.token_usage}")
        print(f"  模型: {response.model}")
        
        return True
        
    except ImportError as e:
        print(f"✗ 依赖缺失: {e}")
        print(f"  提示: 运行 pip install anthropic")
        return False
    except Exception as e:
        print(f"✗ API 调用失败: {e}")
        return False


def test_from_env():
    """测试从环境变量创建服务"""
    print("\n" + "="*50)
    print("测试从环境变量创建服务")
    print("="*50)
    
    provider = os.getenv("LLM_PROVIDER", "qwen")
    print(f"  LLM_PROVIDER: {provider}")
    
    try:
        llm = LLMServiceFactory.create_from_env()
        print(f"✓ 服务创建成功")
        print(f"  模型: {llm.model}")
        
        response = llm.generate_from_prompt(
            system_prompt="你是一个测试助手，请简短回复。",
            user_prompt="请回复：环境变量配置成功",
            temperature=0.1,
            max_tokens=50
        )
        
        print(f"✓ API 调用成功")
        print(f"  响应: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("LLM 连接测试")
    print("="*60)
    
    # 检查 .env 文件
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("\n⚠ 警告: .env 文件不存在")
        print("  请复制 .env.example 到 .env 并配置 API Key")
        print(f"  cp {Path(__file__).parent}/.env.example {env_file}")
    else:
        # 加载 .env 文件
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✓ 已加载 .env 文件")
        except ImportError:
            print("⚠ python-dotenv 未安装，无法自动加载 .env")
            print("  运行: pip install python-dotenv")
    
    # 运行测试
    results = {
        "通义千问": test_qwen(),
        "OpenAI": test_openai(),
        "Claude": test_claude(),
        "环境变量": test_from_env()
    }
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, result in results.items():
        if result is True:
            status = "✓ 通过"
        elif result is False:
            status = "✗ 失败"
        else:
            status = "⊘ 跳过"
        print(f"  {name}: {status}")
    
    # 返回状态码
    if any(r is False for r in results.values()):
        print("\n⚠ 部分测试失败，请检查配置")
        sys.exit(1)
    elif all(r is None or r is True for r in results.values()):
        print("\n✓ 所有测试通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()
