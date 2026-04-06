"""
测试 Script Agent 使用真实 LLM

这个脚本会：
1. 创建 Script Agent 实例
2. 使用真实 LLM 生成剧本
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

from agents.script_agent import ScriptAgent
from agents.base_agent import StageTaskInput
from services.llm_service import LLMServiceFactory
from services.mock_llm_service import MockLLMService


# ── Pytest end-to-end tests (use MockLLMService, no real API calls) ──────────

def _make_script_task_input() -> StageTaskInput:
    """Build a minimal StageTaskInput for Script stage."""
    return StageTaskInput(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        episode_id=uuid4(),
        stage_type="script",
        input_refs=[],
        locked_refs=[],
        constraints={
            "brief": {
                "genre": "科幻悬疑",
                "main_conflict": "主角必须在时间循环中找出真相并阻止灾难",
            },
            "story_bible": {
                "world_rules": ["时间循环每24小时重置一次"],
                "forbidden_conflicts": ["不能让主角轻易打破循环"],
            },
            "character_profile": {
                "characters": [
                    {
                        "name": "陈屿",
                        "role": "protagonist",
                        "speaking_style": "理性冷静，喜欢用逻辑分析问题",
                    }
                ]
            },
            "target_duration_sec": 60,
        },
        target_ref_ids=[],
        raw_material="",
    )


def test_script_agent_pipeline_succeeds():
    """Script Agent end-to-end: full pipeline returns succeeded status."""
    agent = ScriptAgent(db_session=None, llm_service=MockLLMService(), validator=None)
    result = agent.execute(_make_script_task_input())
    assert result.status == "succeeded", f"Expected succeeded, got {result.status}: {result.error_message}"


def test_script_agent_returns_document_refs():
    """Script Agent end-to-end: result contains at least one document ref."""
    agent = ScriptAgent(db_session=None, llm_service=MockLLMService(), validator=None)
    result = agent.execute(_make_script_task_input())
    assert result.document_refs, "Expected at least one document ref in result"
    assert result.document_refs[0].document_type == "script_draft"


def test_script_agent_output_has_scenes():
    """Script Agent end-to-end: generator produces a non-empty scenes list."""
    agent = ScriptAgent(db_session=None, llm_service=MockLLMService(), validator=None)
    task_input = _make_script_task_input()
    context = agent.loader(task_input.input_refs, task_input.locked_refs)
    normalized = agent.normalizer(context, task_input.constraints)
    plan = agent.planner(normalized, task_input)
    draft = agent.generator(plan)

    assert "scenes" in draft, "Output missing 'scenes' key"
    assert len(draft["scenes"]) > 0, "Expected at least one scene in output"

    required_scene_fields = ["scene_no", "location", "characters", "dialogue", "emotion_beats"]
    for scene in draft["scenes"]:
        for field in required_scene_fields:
            assert field in scene, f"Scene missing required field '{field}'"


def test_script_agent_metrics_present():
    """Script Agent end-to-end: result metrics include duration_ms."""
    agent = ScriptAgent(db_session=None, llm_service=MockLLMService(), validator=None)
    result = agent.execute(_make_script_task_input())
    assert "duration_ms" in result.metrics
    assert result.metrics["duration_ms"] >= 0


def test_script_agent():
    """测试 Script Agent"""
    
    print("="*60)
    print("Script Agent 真实 LLM 测试")
    print("="*60)
    
    # 1. 创建 LLM 服务
    print("\n[1] 创建 LLM 服务...")
    try:
        llm = LLMServiceFactory.create_from_env()
        print(f"✓ LLM 服务创建成功: {llm.model}")
    except Exception as e:
        print(f"✗ LLM 服务创建失败: {e}")
        return False
    
    # 2. 创建 Script Agent
    print("\n[2] 创建 Script Agent...")
    agent = ScriptAgent(
        db_session=None,
        llm_service=llm,
        validator=None
    )
    print("✓ Script Agent 创建成功")
    
    # 3. 准备测试输入
    print("\n[3] 准备测试输入...")
    
    # 模拟上游文档
    brief_content = {
        "genre": "科幻悬疑",
        "main_conflict": "主角必须在有限的时间循环中找出真相，打破循环并阻止城市灾难"
    }
    
    story_bible_content = {
        "world_rules": [
            "时间循环每24小时重置一次，只有主角保留记忆",
            "循环中的事件可以被改变，但核心事故必然发生",
            "只有找到事故的真正原因才能打破循环"
        ],
        "forbidden_conflicts": [
            "不能让主角轻易打破循环，必须经过充分的探索",
            "不能让循环的原因过于简单或随意"
        ]
    }
    
    character_profile_content = {
        "characters": [
            {
                "name": "陈屿",
                "role": "主角（程序员）",
                "goal": "打破时间循环，阻止城市灾难",
                "motivation": "证明自己的身份，找回失去的记忆",
                "speaking_style": "理性冷静，喜欢用逻辑分析问题，紧张时会下意识摸左手腕"
            },
            {
                "name": "神秘女孩",
                "role": "关键配角（回响体）",
                "goal": "帮助主角找到真相",
                "motivation": "完成未完成的使命",
                "speaking_style": "简洁克制，很少用第一人称，说话时眼神飘忽"
            }
        ]
    }
    
    task_input = StageTaskInput(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        episode_id=uuid4(),
        stage_type="script",
        input_refs=[],
        locked_refs=[],
        constraints={
            "brief": brief_content,
            "story_bible": story_bible_content,
            "character_profile": character_profile_content,
            "target_duration_sec": 60
        },
        target_ref_ids=[],
        raw_material=""
    )
    
    print("✓ 测试输入准备完成")
    print(f"  目标时长: {60} 秒")
    print(f"  角色数量: {len(character_profile_content['characters'])}")
    
    # 4. 执行 Agent
    print("\n[4] 执行 Script Agent...")
    print("  (这可能需要 20-30 秒，请耐心等待...)")
    
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
    print("\n[6] 生成的剧本:")
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
        print("✓ 剧本生成成功！")
        print("="*60)
        
        # 显示场景摘要
        scenes = draft.get('scenes', [])
        total_duration = sum(s.get('duration_estimate_sec', 0) for s in scenes)
        
        print(f"\n共生成 {len(scenes)} 个场景，预计总时长 {total_duration} 秒\n")
        
        for scene in scenes:
            print(f"【场景 {scene.get('scene_no', 'N/A')}：{scene.get('location', 'N/A')}】")
            print(f"  目标：{scene.get('goal', 'N/A')}")
            print(f"  角色：{', '.join(scene.get('characters', []))}")
            print(f"  对话数：{len(scene.get('dialogue', []))} 条")
            print(f"  预计时长：{scene.get('duration_estimate_sec', 0)} 秒")
            
            # 显示前2条对话
            dialogues = scene.get('dialogue', [])
            if dialogues:
                print(f"  对话预览：")
                for i, d in enumerate(dialogues[:2], 1):
                    print(f"    {i}. {d.get('character', 'N/A')}: {d.get('line', 'N/A')[:30]}...")
            
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
        success = test_script_agent()
        
        if success:
            print("\n" + "="*60)
            print("✓ 所有测试通过！")
            print("="*60)
            print("\n下一步:")
            print("  1. Script Agent 已成功集成真实 LLM")
            print("  2. 最后更新 Storyboard Agent")
            print("  3. 然后进行代码重构，整理项目结构")
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
