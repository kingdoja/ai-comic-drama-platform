"""
简化版端到端测试：Brief 生成（无需数据库）

这个测试直接调用 Brief Agent，不需要：
- Docker
- PostgreSQL
- 数据库迁移

只需要：
- LLM 服务配置（workers/agent-runtime/.env）
"""

import sys
from pathlib import Path
from uuid import uuid4

# 添加 agent runtime 到路径
# 当前文件: apps/api/test_brief_simple.py
# 目标路径: workers/agent-runtime
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # 回到项目根目录
agent_runtime_path = project_root / "workers" / "agent-runtime"

sys.path.insert(0, str(agent_runtime_path))

print(f"当前文件: {current_file}")
print(f"项目根目录: {project_root}")
print(f"Agent runtime 路径: {agent_runtime_path}")
print(f"路径是否存在: {agent_runtime_path.exists()}")

# 加载 .env
try:
    from dotenv import load_dotenv
    env_file = agent_runtime_path / ".env"
    load_dotenv(env_file)
    print(f"✓ 已加载 LLM 配置: {env_file}")
except ImportError:
    print("⚠ python-dotenv 未安装")

from brief_agent import BriefAgent
from base_agent import StageTaskInput
from llm_service import LLMServiceFactory


def test_brief_generation_simple():
    """简化版 Brief 生成测试"""
    
    print("\n" + "="*60)
    print("Brief 生成简化测试（无需数据库）")
    print("="*60)
    
    # 1. 创建 LLM 服务
    print("\n[1] 创建 LLM 服务...")
    try:
        llm = LLMServiceFactory.create_from_env()
        print(f"✓ LLM 服务创建成功: {llm.model}")
    except Exception as e:
        print(f"✗ LLM 服务创建失败: {e}")
        print("\n请确保:")
        print("  1. workers/agent-runtime/.env 文件存在")
        print("  2. QWEN_API_KEY 已配置")
        return False
    
    # 2. 创建 Brief Agent（不使用数据库）
    print("\n[2] 创建 Brief Agent...")
    agent = BriefAgent(
        db_session=None,  # 不使用数据库
        llm_service=llm,
        validator=None
    )
    print("✓ Brief Agent 创建成功")
    
    # 3. 准备测试输入
    print("\n[3] 准备测试输入...")
    
    raw_material = """
一个年轻的程序员发现自己被困在了一个时间循环中。每天早上7点，他都会在同一个地铁站醒来，
然后经历完全相同的一天。他尝试了各种方法想要打破循环，但都失败了。

直到有一天，他注意到地铁站的一个神秘女孩，她似乎也意识到了时间循环的存在。
两人开始合作，试图找出循环的原因和打破循环的方法。

在调查过程中，他们发现这个循环与一个即将发生的重大事故有关。
如果他们不能在循环中找到真相并阻止事故，整个城市都将陷入危险。
"""
    
    task_input = StageTaskInput(
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
    
    print("✓ 测试输入准备完成")
    
    # 4. 执行 Agent
    print("\n[4] 执行 Brief Agent...")
    print("  (这可能需要 10-15 秒，请耐心等待...)")
    
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
    
    print("✓ 结果验证通过")
    
    # 6. 获取生成的内容
    print("\n[6] 获取生成的 Brief 内容...")
    
    # 由于没有数据库，我们重新生成来显示内容
    context = agent.loader([], [])
    normalized = agent.normalizer(context, task_input.constraints)
    plan = agent.planner(normalized, task_input)
    
    try:
        draft = agent.generator(plan)
        
        print("\n" + "="*60)
        print("生成的 Brief")
        print("="*60)
        
        import json
        print("\n" + json.dumps(draft, ensure_ascii=False, indent=2))
        
        # 7. 显示关键信息
        print("\n" + "="*60)
        print("Brief 关键信息")
        print("="*60)
        
        print(f"\n【故事类型】{draft.get('genre', 'N/A')}")
        print(f"【目标受众】{draft.get('target_audience', 'N/A')}")
        print(f"【主要冲突】{draft.get('main_conflict', 'N/A')}")
        print(f"【视觉风格】{draft.get('target_style', 'N/A')}")
        print(f"【叙事基调】{draft.get('tone', 'N/A')}")
        
        print(f"\n【核心卖点】")
        for i, point in enumerate(draft.get('core_selling_points', []), 1):
            print(f"  {i}. {point}")
        
        print(f"\n【改编风险】")
        for i, risk in enumerate(draft.get('adaptation_risks', []), 1):
            print(f"  {i}. {risk}")
        
        return True
        
    except Exception as e:
        print(f"✗ 内容生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("Brief 生成简化测试（无需数据库）")
    print("="*60)
    
    try:
        success = test_brief_generation_simple()
        
        if success:
            print("\n" + "="*60)
            print("✓ 测试通过！")
            print("="*60)
            print("\n恭喜！Brief Agent 工作正常！")
            print("\n下一步:")
            print("  1. 安装 Docker Desktop 以使用完整功能")
            print("  2. 或者继续开发其他 Agent")
            print("  3. 或者添加图像生成功能")
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
