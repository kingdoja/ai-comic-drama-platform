"""
测试 Character Agent 使用真实 LLM

这个脚本会：
1. 创建 Character Agent 实例
2. 使用真实 LLM 生成角色档案
3. 验证输出格式
4. 显示生成的内容
"""

import os
import sys
import json
from pathlib import Path
from uuid import UUID, uuid4

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载 .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
    print("✓ 已加载 LLM 配置")
except ImportError:
    print("⚠ python-dotenv 未安装，使用环境变量")

import pytest

from agents.character_agent import CharacterAgent
from agents.base_agent import StageTaskInput
from services.llm_service import LLMServiceFactory
from services.mock_llm_service import MockLLMService


# ── Pytest end-to-end tests (use MockLLMService, no real API calls) ──────────

def _make_character_task_input() -> StageTaskInput:
    """Build a minimal StageTaskInput for Character stage."""
    return StageTaskInput(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        episode_id=uuid4(),
        stage_type="character",
        input_refs=[],
        locked_refs=[],
        constraints={
            "brief": {
                "genre": "科幻悬疑",
                "core_selling_points": ["时间循环", "双主角合作"],
                "main_conflict": "主角必须在时间循环中找出真相并阻止灾难",
            },
            "story_bible": {
                "world_rules": ["时间循环每24小时重置一次，只有主角保留记忆"],
                "relationship_baseline": {"主角与女孩": "陌生人"},
            },
        },
        target_ref_ids=[],
        raw_material="",
    )


def test_character_agent_pipeline_succeeds():
    """Character Agent end-to-end: full pipeline returns succeeded status."""
    agent = CharacterAgent(db_session=None, llm_service=MockLLMService(), validator=None)
    result = agent.execute(_make_character_task_input())
    assert result.status == "succeeded", f"Expected succeeded, got {result.status}: {result.error_message}"


def test_character_agent_returns_document_refs():
    """Character Agent end-to-end: result contains at least one document ref."""
    agent = CharacterAgent(db_session=None, llm_service=MockLLMService(), validator=None)
    result = agent.execute(_make_character_task_input())
    assert result.document_refs, "Expected at least one document ref in result"
    assert result.document_refs[0].document_type == "character_profile"


def test_character_agent_output_has_characters():
    """Character Agent end-to-end: generator produces a non-empty characters list."""
    agent = CharacterAgent(db_session=None, llm_service=MockLLMService(), validator=None)
    task_input = _make_character_task_input()
    context = agent.loader(task_input.input_refs, task_input.locked_refs)
    normalized = agent.normalizer(context, task_input.constraints)
    plan = agent.planner(normalized, task_input)
    draft = agent.generator(plan)

    assert "characters" in draft, "Output missing 'characters' key"
    assert len(draft["characters"]) > 0, "Expected at least one character in output"

    required_char_fields = ["name", "role", "goal", "motivation", "speaking_style", "visual_anchor"]
    for char in draft["characters"]:
        for field in required_char_fields:
            assert field in char, f"Character missing required field '{field}'"


def test_character_agent_metrics_present():
    """Character Agent end-to-end: result metrics include duration_ms."""
    agent = CharacterAgent(db_session=None, llm_service=MockLLMService(), validator=None)
    result = agent.execute(_make_character_task_input())
    assert "duration_ms" in result.metrics
    assert result.metrics["duration_ms"] >= 0


def test_character_agent():
    """测试 Character Agent"""
    
    print("="*60)
    print("Character Agent 真实 LLM 测试")
    print("="*60)
    
    # 1. 创建 LLM 服务
    print("\n[1] 创建 LLM 服务...")
    try:
        llm = LLMServiceFactory.create_from_env()
        print(f"✓ LLM 服务创建成功: {llm.model}")
    except Exception as e:
        print(f"✗ LLM 服务创建失败: {e}")
        return False
    
    # 2. 创建 Character Agent
    print("\n[2] 创建 Character Agent...")
    agent = CharacterAgent(
        db_session=None,  # 不使用数据库
        llm_service=llm,
        validator=None
    )
    print("✓ Character Agent 创建成功")
    
    # 3. 准备测试输入（模拟 Brief 和 Story Bible 的输出）
    print("\n[3] 准备测试输入...")
    
    # 模拟 Brief 文档
    brief_content = {
        "genre": "科幻悬疑",
        "target_audience": "18-35岁，喜欢科幻和烧脑剧情的年轻观众",
        "core_selling_points": [
            "时间循环的创新设定",
            "紧张刺激的悬疑氛围",
            "意想不到的反转结局",
            "双主角合作破解谜题",
            "城市危机的高风险"
        ],
        "main_conflict": "主角必须在有限的时间循环中找出真相，打破循环并阻止城市灾难"
    }
    
    # 模拟 Story Bible 文档
    story_bible_content = {
        "world_rules": [
            "时间循环严格锚定于城市地铁系统——每日清晨7:00整，所有受循环影响者在'梧桐路站'B出口闸机前重置意识",
            "身份可被视觉锚点验证，语言/证件/生物识别在循环中不可靠",
            "神秘女孩并非循环'幸存者'而是'回响体'——她是事故中本应死亡却因数据残留形成的临时人格投影"
        ],
        "relationship_baseline": {
            "主角与神秘女孩": "单向认知关系：主角视其为破局关键线索；女孩视主角为'未完成的校验对象'",
            "主角与父亲": "法律意义上的失踪者，情感上被主角定义为'背叛者'"
        }
    }
    
    task_input = StageTaskInput(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        episode_id=uuid4(),
        stage_type="character",
        input_refs=[],
        locked_refs=[],
        constraints={
            "brief": brief_content,
            "story_bible": story_bible_content
        },
        target_ref_ids=[],
        raw_material=""
    )
    
    print("✓ 测试输入准备完成")
    print(f"  Brief 类型: {brief_content['genre']}")
    print(f"  世界规则数量: {len(story_bible_content['world_rules'])}")
    
    # 4. 执行 Agent
    print("\n[4] 执行 Character Agent...")
    print("  (这可能需要 15-20 秒，请耐心等待...)")
    
    try:
        result = agent.execute(task_input)
        print(f"✓ Agent 执行完成")
        print(f"  状态: {result.status}")
        print(f"  耗时: {result.metrics['duration_ms']} ms")
        print(f"  Token 使用: {result.metrics.get('token_usage', 0)}")
    except Exception as e:
        print(f"✗ Agent 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. 验证结果
    print("\n[5] 验证结果...")
    
    if result.status != "succeeded":
        print(f"✗ Agent 执行失败")
        if result.error_message:
            print(f"  错误: {result.error_message}")
        return False
    
    if not result.document_refs:
        print("✗ 没有生成文档")
        return False
    
    print("✓ 结果验证通过")
    
    # 6. 显示生成的内容
    print("\n[6] 生成的角色档案:")
    print("="*60)
    
    # 重新生成以显示内容
    print("\n重新生成以显示内容...")
    
    context = agent.loader([], [])
    normalized = agent.normalizer(context, task_input.constraints)
    plan = agent.planner(normalized, task_input)
    
    try:
        draft = agent.generator(plan)
        
        print("\n" + json.dumps(draft, ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print("✓ 角色档案生成成功！")
        print("="*60)
        
        # 显示每个角色的详细信息
        characters = draft.get('characters', [])
        print(f"\n共生成 {len(characters)} 个角色：\n")
        
        for i, char in enumerate(characters, 1):
            print(f"【角色 {i}：{char.get('name', 'N/A')}】")
            print(f"  角色定位：{char.get('role', 'N/A')}")
            print(f"  目标：{char.get('goal', 'N/A')}")
            print(f"  动机：{char.get('motivation', 'N/A')}")
            print(f"  说话风格：{char.get('speaking_style', 'N/A')}")
            print(f"  视觉锚点：{char.get('visual_anchor', 'N/A')}")
            
            if char.get('personality_traits'):
                print(f"  性格特征：{', '.join(char['personality_traits'])}")
            
            if char.get('relationships'):
                print(f"  关系：")
                for rel, desc in char['relationships'].items():
                    print(f"    - {rel}: {desc}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ 内容生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    try:
        success = test_character_agent()
        
        if success:
            print("\n" + "="*60)
            print("✓ 所有测试通过！")
            print("="*60)
            print("\n下一步:")
            print("  1. Character Agent 已成功集成真实 LLM")
            print("  2. 继续更新 Script Agent")
            print("  3. 最后更新 Storyboard Agent")
            sys.exit(0)
        else:
            print("\n" + "="*60)
            print("✗ 测试失败")
            print("="*60)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
