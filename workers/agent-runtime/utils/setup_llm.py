"""
LLM 配置向导

交互式配置 LLM 服务
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(text)
    print("="*60)


def print_step(number, text):
    """打印步骤"""
    print(f"\n[步骤 {number}] {text}")


def get_input(prompt, default=None):
    """获取用户输入"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(prompt).strip()
    return value if value else default


def setup_env_file():
    """设置 .env 文件"""
    print_header("LLM 配置向导")
    
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    # 检查是否已存在 .env
    if env_file.exists():
        print(f"\n✓ 发现现有 .env 文件: {env_file}")
        overwrite = get_input("是否覆盖? (y/N)", "n").lower()
        if overwrite != "y":
            print("保留现有配置")
            return str(env_file)
    
    # 选择 LLM 提供商
    print_step(1, "选择 LLM 提供商")
    print("  1. 通义千问 (Qwen) - 推荐，中文效果好")
    print("  2. OpenAI (GPT-4/GPT-3.5)")
    print("  3. Anthropic Claude")
    
    choice = get_input("请选择 (1-3)", "1")
    
    provider_map = {
        "1": ("qwen", "QWEN_API_KEY", "qwen-plus"),
        "2": ("openai", "OPENAI_API_KEY", "gpt-4o-mini"),
        "3": ("claude", "ANTHROPIC_API_KEY", "claude-3-5-sonnet-20241022")
    }
    
    if choice not in provider_map:
        print("✗ 无效选择，使用默认: 通义千问")
        choice = "1"
    
    provider, api_key_name, default_model = provider_map[choice]
    
    # 获取 API Key
    print_step(2, f"配置 {provider.upper()} API Key")
    
    if provider == "qwen":
        print("  获取方式: https://dashscope.console.aliyun.com/apiKey")
    elif provider == "openai":
        print("  获取方式: https://platform.openai.com/api-keys")
    elif provider == "claude":
        print("  获取方式: https://console.anthropic.com/settings/keys")
    
    api_key = get_input(f"请输入 {api_key_name}")
    
    if not api_key:
        print("✗ API Key 不能为空")
        sys.exit(1)
    
    # 选择模型
    print_step(3, "选择模型（可选）")
    
    if provider == "qwen":
        print("  可选模型:")
        print("    - qwen-turbo (快速，便宜)")
        print("    - qwen-plus (平衡，推荐)")
        print("    - qwen-max (最强，贵)")
    elif provider == "openai":
        print("  可选模型:")
        print("    - gpt-4o-mini (快速，便宜)")
        print("    - gpt-4o (最新，推荐)")
        print("    - gpt-4-turbo (强大)")
    elif provider == "claude":
        print("  可选模型:")
        print("    - claude-3-haiku-20240307 (快速)")
        print("    - claude-3-5-sonnet-20241022 (推荐)")
        print("    - claude-3-opus-20240229 (最强)")
    
    model = get_input("请输入模型名称", default_model)
    
    # 生成 .env 文件
    print_step(4, "生成配置文件")
    
    env_content = f"""# LLM 配置
LLM_PROVIDER={provider}
LLM_MODEL={model}

# {provider.upper()} API Key
{api_key_name}={api_key}
"""
    
    # 如果有示例文件，添加其他配置
    if env_example.exists():
        with open(env_example, 'r', encoding='utf-8') as f:
            example_content = f.read()
        
        # 添加其他提供商的配置（注释掉）
        env_content += "\n# 其他 LLM 提供商配置（可选）\n"
        for line in example_content.split('\n'):
            if line.startswith('#') or not line.strip():
                continue
            if api_key_name not in line and 'LLM_PROVIDER' not in line and 'LLM_MODEL' not in line:
                env_content += f"# {line}\n"
    
    # 写入文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✓ 配置文件已生成: {env_file}")
    
    return str(env_file)


def test_connection():
    """测试连接"""
    print_step(5, "测试连接")
    
    test_script = Path(__file__).parent / "test_llm_connection.py"
    
    if not test_script.exists():
        print("✗ 测试脚本不存在")
        return False
    
    print("运行测试...")
    os.system(f"python {test_script}")
    
    return True


def install_dependencies():
    """安装依赖"""
    print_header("安装依赖")
    
    requirements = Path(__file__).parent / "requirements.txt"
    
    if not requirements.exists():
        print("✗ requirements.txt 不存在")
        return False
    
    print("安装 Python 包...")
    os.system(f"pip install -r {requirements}")
    
    return True


def main():
    """主函数"""
    print_header("欢迎使用 LLM 配置向导")
    print("\n本向导将帮助你配置 LLM 服务")
    
    # 询问是否安装依赖
    install = get_input("\n是否安装依赖? (Y/n)", "y").lower()
    if install != "n":
        install_dependencies()
    
    # 配置 .env
    env_file = setup_env_file()
    
    # 测试连接
    test = get_input("\n是否测试连接? (Y/n)", "y").lower()
    if test != "n":
        test_connection()
    
    # 完成
    print_header("配置完成")
    print("\n✓ LLM 服务已配置完成！")
    print(f"\n配置文件: {env_file}")
    print("\n下一步:")
    print("  1. 查看 README_LLM.md 了解使用方法")
    print("  2. 运行 python test_llm_connection.py 测试连接")
    print("  3. 在 Agent 中使用 LLM 服务")
    print("\n祝你使用愉快！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ 用户取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        sys.exit(1)
