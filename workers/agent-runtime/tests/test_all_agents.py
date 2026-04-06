"""
测试所有 5 个 Agent 的真实 LLM 集成

这个脚本会依次测试：
1. Brief Agent
2. Story Bible Agent
3. Character Agent
4. Script Agent
5. Storyboard Agent
"""

import os
import sys
import json
from pathlib import Path
from uuid import uuid4

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 加载 .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    print("⚠ python-dotenv 未安装")

from agents.brief_agent import BriefAgent
from agents.story_bible_agent import StoryBibleAgent
from agents.character_agent import CharacterAgent
from agents.script_agent import ScriptAgent
from agents.storyboard_agent import StoryboardAgent
from agents.base_agent import StageTaskInput, DocumentRef
from services.llm_service import LLMServiceFactory


def test_all_agents():
    """测试所有 5 个 Agent"""
    
    print("="*70)
    print("测试所有 Agent 的真实 LLM 集成")
    print("="*70)
    
    # 准备测试素材
    raw_material = """
一个年轻的程序员发现自己被困在了一个时间循环中。每天早上7点，他都会在同一个地铁站醒来，
然后经历完全相同的一天。他尝试了各种方法想要打破循环，但都失败了。

直到有一天，他注意到地铁站的一个神秘女孩，她似乎也意识到了时间循环的存在。
两人开始合作，试图找出循环的原因和打破循环的方法。

在调查过程中，他们发现这个循环与一个即将发生的重大事故有关。
如果他们不能在循环中找到真相并阻止事故,整个城市都将陷入危险。
"""
    
    # 创建 LLM 服务
    print("\n[0] 创建 LLM 服务...")
    try:
        llm = LLMServiceFactory.create_from_env()
        print(f"✓ LLM 服务创建成功: {llm.model}")
    except Exception as e:
        print(f"✗ LLM 服务创建失败: {e}")
        return False
    
    # 存储生成的文档引用
    document_refs = {}
    
    # ========== 1. Brief Agent ==========
    print("\n" + "="*70)
    print("[1] 测试 Brief Agent")
    print("="*70)
    
    try:
        brief_agent = BriefAgent(db_session=None, llm_service=llm, validator=None)
        
        brief_input = StageTaskInput(
            workflow_run_id=uuid4(),
            project_id=uuid4(),
            episode_id=uuid4(),
            stage_type="brief",
            input_refs=[],
            locked_refs=[],
            constraints={
                "raw_material": raw_material,
                "platform": "douyin",
                "target_duration_sec": 60,
                "target_audience": "18-35岁年轻观众"
            },
            target_ref_ids=[],
            raw_material=raw_material
        )
        
        print("  执行 Brief Agent...")
        result = brief_agent.execute(brief_input)
        
        if result.status == "succeeded":
            print(f"  ✓ Brief Agent 成功")
            print(f"    耗时: {result.metrics['duration_ms']} ms")
            print(f"    Token: {result.metrics.get('token_usage', 0)}")
            
            # 保存 brief 引用
            if result.document_refs:
                document_refs['brief'] = result.document_refs[0]
        else:
            print(f"  ✗ Brief Agent 失败: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"  ✗ Brief Agent 异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== 2. Story Bible Agent ==========
    print("\n" + "="*70)
    print("[2] 测试 Story Bible Agent")
    print("="*70)
    
    try:
        story_bible_agent = StoryBibleAgent(db_session=None, llm_service=llm, validator=None)
        
        story_bible_input = StageTaskInput(
            workflow_run_id=uuid4(),
            project_id=uuid4(),
            episode_id=uuid4(),
            stage_type="story_bible",
            input_refs=[document_refs.get('brief')] if 'brief' in document_refs else [],
            locked_refs=[],
            constraints={
                "raw_material_summary": raw_material[:200]
            },
            target_ref_ids=[],
            raw_material=""
        )
        
        print("  执行 Story Bible Agent...")
        result = story_bible_agent.execute(story_bible_input)
        
        if result.status == "succeeded":
            print(f"  ✓ Story Bible Agent 成功")
            print(f"    耗时: {result.metrics['duration_ms']} ms")
            print(f"    Token: {result.metrics.get('token_usage', 0)}")
            
            if result.document_refs:
                document_refs['story_bible'] = result.document_refs[0]
        else:
            print(f"  ✗ Story Bible Agent 失败: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"  ✗ Story Bible Agent 异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== 3. Character Agent ==========
    print("\n" + "="*70)
    print("[3] 测试 Character Agent")
    print("="*70)
    
    try:
        character_agent = CharacterAgent(db_session=None, llm_service=llm, validator=None)
        
        character_input = StageTaskInput(
            workflow_run_id=uuid4(),
            project_id=uuid4(),
            episode_id=uuid4(),
            stage_type="character",
            input_refs=[
                document_refs.get('brief'),
                document_refs.get('story_bible')
            ] if 'brief' in document_refs and 'story_bible' in document_refs else [],
            locked_refs=[],
            constraints={},
            target_ref_ids=[],
            raw_material=""
        )
        
        print("  执行 Character Agent...")
        result = character_agent.execute(character_input)
        
        if result.status == "succeeded":
            print(f"  ✓ Character Agent 成功")
            print(f"    耗时: {result.metrics['duration_ms']} ms")
            print(f"    Token: {result.metrics.get('token_usage', 0)}")
            
            if result.document_refs:
                document_refs['character_profile'] = result.document_refs[0]
        else:
            print(f"  ✗ Character Agent 失败: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"  ✗ Character Agent 异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== 4. Script Agent ==========
    print("\n" + "="*70)
    print("[4] 测试 Script Agent")
    print("="*70)
    
    try:
        script_agent = ScriptAgent(db_session=None, llm_service=llm, validator=None)
        
        script_input = StageTaskInput(
            workflow_run_id=uuid4(),
            project_id=uuid4(),
            episode_id=uuid4(),
            stage_type="script",
            input_refs=[
                document_refs.get('brief'),
                document_refs.get('story_bible'),
                document_refs.get('character_profile')
            ] if all(k in document_refs for k in ['brief', 'story_bible', 'character_profile']) else [],
            locked_refs=[],
            constraints={
                "target_duration_sec": 60
            },
            target_ref_ids=[],
            raw_material=""
        )
        
        print("  执行 Script Agent...")
        result = script_agent.execute(script_input)
        
        if result.status == "succeeded":
            print(f"  ✓ Script Agent 成功")
            print(f"    耗时: {result.metrics['duration_ms']} ms")
            print(f"    Token: {result.metrics.get('token_usage', 0)}")
            
            if result.document_refs:
                document_refs['script_draft'] = result.document_refs[0]
        else:
            print(f"  ✗ Script Agent 失败: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"  ✗ Script Agent 异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== 5. Storyboard Agent ==========
    print("\n" + "="*70)
    print("[5] 测试 Storyboard Agent")
    print("="*70)
    
    try:
        storyboard_agent = StoryboardAgent(db_session=None, llm_service=llm, validator=None)
        
        storyboard_input = StageTaskInput(
            workflow_run_id=uuid4(),
            project_id=uuid4(),
            episode_id=uuid4(),
            stage_type="storyboard",
            input_refs=[
                document_refs.get('script_draft'),
                document_refs.get('character_profile')
            ] if 'script_draft' in document_refs and 'character_profile' in document_refs else [],
            locked_refs=[],
            constraints={
                "platform": "douyin",
                "aspect_ratio": "9:16",
                "target_duration_sec": 60,
                "max_shots": 20
            },
            target_ref_ids=[],
            raw_material=""
        )
        
        print("  执行 Storyboard Agent...")
        result = storyboard_agent.execute(storyboard_input)
        
        if result.status == "succeeded":
            print(f"  ✓ Storyboard Agent 成功")
            print(f"    耗时: {result.metrics['duration_ms']} ms")
            print(f"    Token: {result.metrics.get('token_usage', 0)}")
            
            if result.document_refs:
                document_refs['visual_spec'] = result.document_refs[0]
        else:
            print(f"  ✗ Storyboard Agent 失败: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"  ✗ Storyboard Agent 异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ========== 总结 ==========
    print("\n" + "="*70)
    print("✓ 所有 5 个 Agent 测试通过！")
    print("="*70)
    
    print("\n生成的文档:")
    for doc_type, ref in document_refs.items():
        print(f"  - {doc_type}: {ref.document_type} v{ref.version}")
    
    print("\n下一步:")
    print("  1. 所有 Agent 已成功集成真实 LLM")
    print("  2. 可以测试完整的文本工作流")
    print("  3. 或者开始集成数据库和 API")
    
    return True


def main():
    """主函数"""
    try:
        success = test_all_agents()
        
        if success:
            sys.exit(0)
        else:
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
