"""
测试并修复代理问题

这个脚本会：
1. 检测系统代理设置
2. 临时禁用代理
3. 测试 LLM 连接
"""

import os
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

print("="*60)
print("代理问题诊断和修复")
print("="*60)

# 检查环境变量中的代理设置
print("\n[1] 检查系统代理设置:")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']
found_proxy = False

for var in proxy_vars:
    value = os.environ.get(var)
    if value:
        print(f"  发现代理: {var} = {value}")
        found_proxy = True

if not found_proxy:
    print("  未发现环境变量代理设置")

# 临时禁用代理
print("\n[2] 临时禁用代理...")
for var in proxy_vars:
    if var in os.environ:
        del os.environ[var]
        print(f"  已移除: {var}")

# 显式设置为空
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'
print("  已设置 NO_PROXY=*")

# 加载 .env
print("\n[3] 加载配置文件...")
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / ".env"
    load_dotenv(env_file)
    print(f"  ✓ 已加载: {env_file}")
except ImportError:
    print("  ⚠ python-dotenv 未安装")

# 检查 API Key
api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    print("\n✗ 错误: 未找到 QWEN_API_KEY")
    sys.exit(1)

print(f"  ✓ API Key: {api_key[:10]}...{api_key[-4:]}")

# 测试连接
print("\n[4] 测试通义千问连接...")
print("="*60)

try:
    from services.llm_service import QwenLLMService
    
    llm = QwenLLMService()
    print(f"✓ 服务创建成功，模型: {llm.model}")
    
    print("\n正在调用 API（无代理）...")
    response = llm.generate_from_prompt(
        system_prompt="你是一个测试助手，请简短回复。",
        user_prompt="请回复：通义千问连接成功",
        temperature=0.1,
        max_tokens=50
    )
    
    print("\n" + "="*60)
    print("✓ 测试成功！")
    print("="*60)
    print(f"\n响应内容: {response.content}")
    print(f"Token 使用: {response.token_usage}")
    print(f"使用模型: {response.model}")
    
    print("\n" + "="*60)
    print("解决方案")
    print("="*60)
    print("\n问题原因: 系统配置了代理，但代理不可用")
    print("\n永久解决方法（选择一种）:")
    print("\n方法 1: 在 .env 文件中禁用代理")
    print("  在 .env 文件末尾添加:")
    print("  NO_PROXY=*")
    print("  HTTP_PROXY=")
    print("  HTTPS_PROXY=")
    
    print("\n方法 2: 在代码中禁用代理")
    print("  已为你创建修复版本的测试脚本")
    
    print("\n方法 3: 配置正确的代理")
    print("  如果你需要使用代理，请配置可用的代理地址")
    
except Exception as e:
    print(f"\n✗ 仍然失败: {e}")
    print("\n可能的原因:")
    print("1. 网络连接问题")
    print("2. 防火墙阻止")
    print("3. API Key 无效")
    print("\n请尝试:")
    print("- 检查网络连接")
    print("- 暂时关闭防火墙/杀毒软件")
    print("- 验证 API Key 是否正确")
    sys.exit(1)
