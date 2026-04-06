"""
测试导入路径是否正确
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

print("测试导入...")

try:
    from agents.brief_agent import BriefAgent
    print("✓ BriefAgent 导入成功")
except Exception as e:
    print(f"✗ BriefAgent 导入失败: {e}")

try:
    from agents.story_bible_agent import StoryBibleAgent
    print("✓ StoryBibleAgent 导入成功")
except Exception as e:
    print(f"✗ StoryBibleAgent 导入失败: {e}")

try:
    from agents.character_agent import CharacterAgent
    print("✓ CharacterAgent 导入成功")
except Exception as e:
    print(f"✗ CharacterAgent 导入失败: {e}")

try:
    from agents.script_agent import ScriptAgent
    print("✓ ScriptAgent 导入成功")
except Exception as e:
    print(f"✗ ScriptAgent 导入失败: {e}")

try:
    from agents.storyboard_agent import StoryboardAgent
    print("✓ StoryboardAgent 导入成功")
except Exception as e:
    print(f"✗ StoryboardAgent 导入失败: {e}")

try:
    from services.llm_service import LLMServiceFactory
    print("✓ LLMServiceFactory 导入成功")
except Exception as e:
    print(f"✗ LLMServiceFactory 导入失败: {e}")

try:
    from services.validator import Validator
    print("✓ Validator 导入成功")
except Exception as e:
    print(f"✗ Validator 导入失败: {e}")

print("\n所有导入测试完成！")
