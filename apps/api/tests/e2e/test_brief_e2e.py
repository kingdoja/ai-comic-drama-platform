"""
端到端测试：Brief 生成完整流程

测试流程：
1. 启动数据库
2. 创建项目和剧集
3. 调用 Brief 生成 API
4. 验证结果
5. 查询生成的 Brief
"""

import requests
import json
from uuid import uuid4

# API 基础 URL
BASE_URL = "http://localhost:8000"


def test_brief_generation():
    """测试 Brief 生成完整流程"""
    
    print("="*60)
    print("Brief 生成端到端测试")
    print("="*60)
    
    # 1. 检查 API 健康状态
    print("\n[1] 检查 API 健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ API 服务正常运行")
        else:
            print(f"✗ API 健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到 API 服务")
        print("  请确保 API 服务已启动:")
        print("  cd apps/api")
        print("  uvicorn app.main:app --reload --port 8000")
        return False
    
    # 2. 创建测试项目
    print("\n[2] 创建测试项目...")
    project_data = {
        "title": "时间循环测试项目",
        "description": "端到端测试项目",
        "status": "active"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
        if response.status_code == 200:
            project = response.json()
            project_id = project["id"]
            print(f"✓ 项目创建成功: {project_id}")
        else:
            print(f"✗ 项目创建失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 项目创建失败: {e}")
        return False
    
    # 3. 创建测试剧集
    print("\n[3] 创建测试剧集...")
    episode_data = {
        "project_id": project_id,
        "episode_number": 1,
        "title": "第一集：循环开始",
        "status": "draft"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/projects/{project_id}/episodes", json=episode_data)
        if response.status_code == 200:
            episode = response.json()
            episode_id = episode["id"]
            print(f"✓ 剧集创建成功: {episode_id}")
        else:
            print(f"✗ 剧集创建失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
    except Exception as e:
        print(f"✗ 剧集创建失败: {e}")
        return False
    
    # 4. 生成 Brief
    print("\n[4] 生成 Brief...")
    print("  (这可能需要 10-15 秒，请耐心等待...)")
    
    raw_material = """
一个年轻的程序员发现自己被困在了一个时间循环中。每天早上7点，他都会在同一个地铁站醒来，
然后经历完全相同的一天。他尝试了各种方法想要打破循环，但都失败了。

直到有一天，他注意到地铁站的一个神秘女孩，她似乎也意识到了时间循环的存在。
两人开始合作，试图找出循环的原因和打破循环的方法。

在调查过程中，他们发现这个循环与一个即将发生的重大事故有关。
如果他们不能在循环中找到真相并阻止事故，整个城市都将陷入危险。
"""
    
    brief_request = {
        "project_id": project_id,
        "episode_id": episode_id,
        "raw_material": raw_material,
        "platform": "douyin",
        "target_duration_sec": 60,
        "target_audience": "18-35岁年轻观众"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brief/generate",
            json=brief_request,
            timeout=60  # 60秒超时
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result["success"]:
                print("✓ Brief 生成成功！")
                print(f"  文档 ID: {result['document_id']}")
                print(f"  Token 使用: {result.get('token_usage', 0)}")
                print(f"  耗时: {result.get('duration_ms', 0)} ms")
                
                document_id = result["document_id"]
                brief_content = result["brief"]
                
            else:
                print(f"✗ Brief 生成失败: {result.get('error')}")
                return False
        else:
            print(f"✗ API 调用失败: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ 请求超时（超过60秒）")
        return False
    except Exception as e:
        print(f"✗ Brief 生成失败: {e}")
        return False
    
    # 5. 显示生成的 Brief
    print("\n[5] 生成的 Brief 内容:")
    print("="*60)
    print(json.dumps(brief_content, ensure_ascii=False, indent=2))
    
    # 6. 查询 Brief
    print("\n[6] 查询生成的 Brief...")
    try:
        response = requests.get(f"{BASE_URL}/api/brief/{document_id}")
        if response.status_code == 200:
            brief = response.json()
            print("✓ Brief 查询成功")
            print(f"  版本: {brief['version']}")
            print(f"  状态: {brief['status']}")
        else:
            print(f"✗ Brief 查询失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Brief 查询失败: {e}")
        return False
    
    # 7. 显示关键信息
    print("\n[7] Brief 关键信息:")
    print("="*60)
    print(f"【故事类型】{brief_content.get('genre', 'N/A')}")
    print(f"【目标受众】{brief_content.get('target_audience', 'N/A')}")
    print(f"【主要冲突】{brief_content.get('main_conflict', 'N/A')}")
    print(f"【视觉风格】{brief_content.get('target_style', 'N/A')}")
    print(f"【叙事基调】{brief_content.get('tone', 'N/A')}")
    
    print(f"\n【核心卖点】")
    for i, point in enumerate(brief_content.get('core_selling_points', []), 1):
        print(f"  {i}. {point}")
    
    print(f"\n【改编风险】")
    for i, risk in enumerate(brief_content.get('adaptation_risks', []), 1):
        print(f"  {i}. {risk}")
    
    return True


def main():
    """主函数"""
    print("\n" + "="*60)
    print("准备运行端到端测试")
    print("="*60)
    print("\n请确保:")
    print("  1. PostgreSQL 数据库已启动")
    print("  2. API 服务已启动 (uvicorn app.main:app --reload --port 8000)")
    print("  3. LLM 服务已配置 (workers/agent-runtime/.env)")
    
    input("\n按 Enter 继续...")
    
    try:
        success = test_brief_generation()
        
        if success:
            print("\n" + "="*60)
            print("✓ 端到端测试通过！")
            print("="*60)
            print("\n恭喜！你已经有了一个完整可用的 AI Brief 生成系统！")
            print("\n下一步:")
            print("  1. 添加更多 Agent（Story Bible, Character, Script, Storyboard）")
            print("  2. 创建前端界面")
            print("  3. 添加图像生成功能")
        else:
            print("\n" + "="*60)
            print("✗ 测试失败")
            print("="*60)
            
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
    except Exception as e:
        print(f"\n✗ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
