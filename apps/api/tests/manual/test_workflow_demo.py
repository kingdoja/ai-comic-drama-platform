"""
简化的工作流演示 - 执行前三个阶段（Brief, Story Bible, Character）
"""

import sys
import os
from pathlib import Path
from uuid import uuid4

# 加载环境变量
from dotenv import load_dotenv
project_root = Path(__file__).parent.parent.parent
agent_runtime_path = project_root / "workers" / "agent-runtime"
load_dotenv(agent_runtime_path / ".env")

# 添加路径
sys.path.insert(0, str(agent_runtime_path.absolute()))
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# 设置环境变量
os.environ["DATABASE_URL"] = "postgresql+psycopg://postgres:postgres@localhost:5432/thinking"
os.environ["QWEN_API_KEY"] = "sk-b6cff92b308c47bbaa7ce83d77574fe8"
os.environ["LLM_PROVIDER"] = "qwen"
os.environ["LLM_MODEL"] = "qwen-plus"

from app.db.session import get_db
from app.services.text_workflow_service import TextWorkflowService
from app.repositories.project_repository import ProjectRepository
from app.repositories.episode_repository import EpisodeRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.stage_task_repository import StageTaskRepository
from app.repositories.shot_repository import ShotRepository
from app.repositories.review_repository import ReviewRepository

# 导入 Agent Runtime
from services.llm_service import LLMServiceFactory
from agents.brief_agent import BriefAgent
from agents.story_bible_agent import StoryBibleAgent
from agents.character_agent import CharacterAgent


def main():
    """演示前三个阶段的工作流"""
    
    print("\n" + "="*70)
    print("AI 漫剧生成系统 - 工作流演示")
    print("="*70)
    
    # 连接数据库
    print("\n[1] 连接数据库...")
    db = next(get_db())
    print("✓ 数据库连接成功")
    
    # 创建 LLM 服务
    print("\n[2] 创建 LLM 服务...")
    llm = LLMServiceFactory.create_from_env()
    print(f"✓ LLM 服务: {llm.model}")
    
    # 创建项目
    print("\n[3] 创建测试项目...")
    from app.schemas.project import CreateProjectRequest
    project_repo = ProjectRepository(db)
    project = project_repo.create(CreateProjectRequest(
        name="时间循环悬疑剧",
        source_mode="adaptation",
        genre="科幻悬疑",
        target_platform="douyin",
        target_audience="18-35岁年轻观众"
    ))
    print(f"✓ 项目: {project.name}")
    
    # 创建剧集
    print("\n[4] 创建剧集...")
    from app.schemas.project import CreateEpisodeRequest
    episode_repo = EpisodeRepository(db)
    episode = episode_repo.create(project.id, CreateEpisodeRequest(
        project_id=project.id,
        episode_no=1,
        title="第一集：循环开始",
        target_duration_sec=60
    ))
    print(f"✓ 剧集: {episode.title}")
    
    # 创建 Agents
    print("\n[5] 创建 AI Agents...")
    agents = {
        "brief": BriefAgent(db_session=db, llm_service=llm, validator=None),
        "story_bible": StoryBibleAgent(db_session=db, llm_service=llm, validator=None),
        "character": CharacterAgent(db_session=db, llm_service=llm, validator=None),
    }
    print("✓ Agents 就绪")
    
    # 创建工作流服务
    print("\n[6] 初始化工作流服务...")
    stage_task_repo = StageTaskRepository(db)
    doc_repo = DocumentRepository(db)
    shot_repo = ShotRepository(db)
    workflow_repo = WorkflowRepository(db)
    review_repo = ReviewRepository(db)
    
    workflow_service = TextWorkflowService(
        db=db,
        stage_tasks=stage_task_repo,
        documents=doc_repo,
        shots=shot_repo,
        episodes=episode_repo,
        workflows=workflow_repo
    )
    workflow_service.llm_service = llm
    workflow_service.agents = agents
    print("✓ 工作流服务就绪")
    
    # 创建工作流记录
    print("\n[7] 创建工作流...")
    from app.schemas.workflow import StartEpisodeWorkflowRequest
    workflow = workflow_repo.create(
        project_id=project.id,
        episode_id=episode.id,
        payload=StartEpisodeWorkflowRequest(start_stage="brief"),
        workflow_kind="episode",
        commit=True
    )
    print(f"✓ 工作流ID: {workflow.id}")
    
    # 执行工作流（前三个阶段）
    print("\n[8] 执行工作流...")
    print("  → Brief Agent: 提取核心创意")
    print("  → Story Bible Agent: 建立世界规则")
    print("  → Character Agent: 创建角色档案")
    print("\n  预计耗时: 1-2 分钟...\n")
    
    stages = ["brief", "story_bible", "character_profile"]
    current_stage = "brief"
    
    for i, stage in enumerate(stages, 1):
        # 执行阶段
        result = workflow_service.execute_text_chain(
            project=project,
            episode=episode,
            workflow=workflow,
            start_stage=current_stage
        )
        
        if result["workflow_status"] == "waiting_review":
            paused_stage = result.get("paused_at_stage")
            print(f"  ✓ 阶段 {i}/{len(stages)}: {paused_stage} 完成")
            
            # 自动批准审核
            stage_task = stage_task_repo.latest_by_stage(
                episode_id=episode.id,
                stage_type=paused_stage
            )
            
            if stage_task and stage_task.review_status == "pending":
                review_repo.create(
                    stage_task_id=stage_task.id,
                    project_id=stage_task.project_id,
                    episode_id=stage_task.episode_id,
                    decision="approved",
                    comment_text="自动批准",
                    payload_jsonb={},
                    commit=False
                )
                stage_task.review_status = "approved"
                stage_task.task_status = "succeeded"
                workflow.status = "running"
                db.commit()
            
            # 设置下一阶段
            if i < len(stages):
                current_stage = stages[i]
        elif result["workflow_status"] == "failed":
            print(f"\n✗ 阶段失败: {result.get('error')}")
            return False
    
    print("\n✓ 所有阶段执行完成！")
    
    # 查询生成的文档
    print("\n" + "="*70)
    print("生成的文档")
    print("="*70)
    
    documents = doc_repo.list_for_episode(episode.id)
    
    # Brief
    brief_doc = next((d for d in documents if d.document_type == "brief"), None)
    if brief_doc:
        print("\n【Brief - 核心创意】")
        content = brief_doc.content_jsonb
        print(f"  故事类型: {content.get('genre', 'N/A')}")
        print(f"  目标受众: {content.get('target_audience', 'N/A')}")
        print(f"  主要冲突: {content.get('main_conflict', 'N/A')}")
        print(f"  核心卖点: {len(content.get('core_selling_points', []))} 个")
    
    # Story Bible
    bible_doc = next((d for d in documents if d.document_type == "story_bible"), None)
    if bible_doc:
        print("\n【Story Bible - 世界规则】")
        content = bible_doc.content_jsonb
        print(f"  世界观: {content.get('world_setting', {}).get('description', 'N/A')[:80]}...")
        print(f"  核心规则: {len(content.get('core_rules', []))} 条")
        print(f"  叙事风格: {content.get('narrative_style', {}).get('tone', 'N/A')}")
    
    # Character
    char_doc = next((d for d in documents if d.document_type == "character_profile"), None)
    if char_doc:
        print("\n【Character - 角色档案】")
        content = char_doc.content_jsonb
        characters = content.get('characters', [])
        print(f"  角色数量: {len(characters)} 个")
        for char in characters:
            print(f"    - {char.get('name', 'Unknown')}: {char.get('role', 'N/A')}")
    
    print("\n" + "="*70)
    print("✓ 演示完成！")
    print("="*70)
    print("\n系统已成功生成:")
    print("  ✓ Brief 文档 - 核心创意提取")
    print("  ✓ Story Bible - 世界观和规则")
    print("  ✓ Character Profile - 角色档案")
    print("\n下一步可以:")
    print("  1. 修复 Script Agent 的输出格式")
    print("  2. 完成 Storyboard Agent 的执行")
    print("  3. 添加图像生成功能")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
