"""
Script Agent - Generates script draft from character profiles and story bible.

Implements Requirements: 5.1, 5.2, 5.3, 5.4
"""

import json
from typing import Any, Dict, List, Tuple
from uuid import UUID

from agents.base_agent import BaseAgent, DocumentRef, LockedRef, StageTaskInput, Warning
from services.llm_service import LLMServiceFactory, LLMMessage


class ScriptAgent(BaseAgent):
    """
    Script Agent generates script draft with scenes and dialogue.
    
    Implements Requirements:
    - 5.1: Generate script with scene structure and dialogue
    - 5.2: Include scene structure (scene_no, location, characters, dialogue, emotion_beats)
    - 5.3: Update episode script_version
    - 5.4: Check character behaviors against character_profile
    """
    
    def __init__(self, db_session=None, llm_service=None, validator=None):
        """
        Initialize Script Agent.
        
        Args:
            db_session: Database session
            llm_service: LLM service (if None, creates from environment)
            validator: Validator component
        """
        # Create LLM service if not provided
        if llm_service is None:
            llm_service = LLMServiceFactory.create_from_env()
        
        super().__init__(db_session, llm_service, validator)
        self._token_usage = 0
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for script draft output."""
        return {
            "type": "object",
            "required": ["scenes"],
            "properties": {
                "scenes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": [
                            "scene_no",
                            "location",
                            "characters",
                            "dialogue",
                            "emotion_beats"
                        ],
                        "properties": {
                            "scene_no": {"type": "integer"},
                            "location": {"type": "string"},
                            "characters": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "goal": {"type": "string"},
                            "dialogue": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "character": {"type": "string"},
                                        "line": {"type": "string"},
                                        "emotion": {"type": "string"}
                                    }
                                }
                            },
                            "emotion_beats": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "duration_estimate_sec": {"type": "integer"}
                        }
                    },
                    "minItems": 1
                }
            }
        }
    
    def loader(self, input_refs: List[DocumentRef], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Load brief, story bible, and character profile as input.
        
        Implements Requirement 5.1: Load all upstream documents
        """
        if not self.db or not hasattr(self.db, 'query'):
            return {
                "input_documents": {
                    "brief": {
                        "genre": "urban_drama",
                        "main_conflict": "Identity proof",
                        "core_selling_points": ["Identity reversal"]
                    },
                    "story_bible": {
                        "world_rules": ["Family status by tokens"],
                        "forbidden_conflicts": []
                    },
                    "character_profile": {
                        "characters": [
                            {
                                "name": "Lin Qingwan",
                                "role": "protagonist",
                                "speaking_style": "calm and determined"
                            }
                        ]
                    }
                },
                "locked_fields": []
            }
        
        from app.db.models import DocumentModel
        
        input_documents = {}
        
        for ref in input_refs:
            if ref.ref_type == "document":
                doc = self.db.query(DocumentModel).filter_by(id=UUID(ref.ref_id)).first()
                if doc:
                    input_documents[doc.document_type] = doc.content_jsonb
        
        return {
            "input_documents": input_documents,
            "locked_fields": [lf.locked_fields for lf in locked_refs]
        }
    
    def normalizer(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize context for script generation.
        """
        brief = context.get("input_documents", {}).get("brief", {})
        story_bible = context.get("input_documents", {}).get("story_bible", {})
        character_profile = context.get("input_documents", {}).get("character_profile", {})
        
        return {
            "brief": brief,
            "story_bible": story_bible,
            "character_profile": character_profile,
            "main_conflict": brief.get("main_conflict", ""),
            "world_rules": story_bible.get("world_rules", []),
            "forbidden_conflicts": story_bible.get("forbidden_conflicts", []),
            "characters": character_profile.get("characters", []),
            "target_duration_sec": constraints.get("target_duration_sec", 60)
        }
    
    def planner(self, normalized: Dict[str, Any], task_input: StageTaskInput) -> Dict[str, Any]:
        """
        Create execution plan for script generation.
        """
        return {
            "prompt": self._build_prompt(normalized),
            "schema": self.get_output_schema(),
            "temperature": 0.8
        }
    
    def generator(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call LLM to generate script draft.
        
        Implements Requirement 5.1: Generate script with scenes and dialogue
        Implements Requirement 5.2: Include all required scene fields
        """
        if not self.llm_service:
            raise RuntimeError("LLM service not configured")
        
        # Build system and user prompts
        system_prompt = """你是一个专业的编剧和对话设计师。你的任务是为短视频创作详细的剧本，包含场景、对话和情感节奏。

你需要：
1. 根据角色档案和故事圣经创作剧本
2. 每个场景包含场景号、地点、角色、对话、情感节奏
3. 对话要符合角色的说话风格
4. 控制总时长在目标范围内
5. 确保情感节奏起伏有致

请以 JSON 格式返回结果，确保所有字段都完整且有价值。"""
        
        user_prompt = plan["prompt"]
        
        # Call LLM with higher max_tokens for script generation
        response = self.llm_service.generate_from_prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=plan["temperature"],
            max_tokens=4000
        )
        
        # Track token usage
        self._token_usage = response.token_usage.get("total_tokens", 0)
        
        # Parse JSON response
        try:
            content = json.loads(response.content)
            return content
        except json.JSONDecodeError:
            # If LLM didn't return valid JSON, try to extract it
            content_str = response.content.strip()
            
            # Try to find JSON in markdown code blocks
            if "```json" in content_str:
                start = content_str.find("```json") + 7
                end = content_str.find("```", start)
                content_str = content_str[start:end].strip()
            elif "```" in content_str:
                start = content_str.find("```") + 3
                end = content_str.find("```", start)
                content_str = content_str[start:end].strip()
            
            try:
                content = json.loads(content_str)
                return content
            except json.JSONDecodeError as e:
                raise RuntimeError(f"LLM returned invalid JSON: {e}\nResponse: {response.content}")
    
    def critic(self, draft: Dict[str, Any], normalized: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Warning]]:
        """
        Review script for consistency with character profiles and story bible.
        
        Implements Requirement 5.4: Check character behaviors against character_profile
        """
        warnings = []
        
        scenes = draft.get("scenes", [])
        characters = {c["name"]: c for c in normalized.get("characters", [])}
        forbidden_conflicts = normalized.get("forbidden_conflicts", [])
        
        # Check character behavior consistency
        for scene_idx, scene in enumerate(scenes):
            for dialogue_idx, dialogue in enumerate(scene.get("dialogue", [])):
                char_name = dialogue.get("character", "")
                line = dialogue.get("line", "")
                emotion = dialogue.get("emotion", "")
                
                if char_name in characters:
                    char_profile = characters[char_name]
                    speaking_style = char_profile.get("speaking_style", "").lower()
                    
                    # Simple consistency check based on speaking style keywords
                    if "calm" in speaking_style and any(word in emotion.lower() for word in ["aggressive", "angry", "shouting"]):
                        warnings.append(Warning(
                            warning_type="consistency",
                            severity="medium",
                            message=f"Character '{char_name}' dialogue emotion '{emotion}' may conflict with speaking style '{speaking_style}'",
                            field_path=f"scenes[{scene_idx}].dialogue[{dialogue_idx}]",
                            suggestion=f"Review dialogue to match character's speaking style: {speaking_style}"
                        ))
        
        # Check for forbidden conflicts
        for scene_idx, scene in enumerate(scenes):
            scene_text = str(scene).lower()
            for forbidden in forbidden_conflicts:
                forbidden_lower = forbidden.lower()
                # Simple keyword matching
                if any(word in scene_text for word in forbidden_lower.split()):
                    warnings.append(Warning(
                        warning_type="consistency",
                        severity="high",
                        message=f"Scene may violate forbidden conflict: '{forbidden}'",
                        field_path=f"scenes[{scene_idx}]",
                        suggestion=f"Review scene to ensure it doesn't violate: {forbidden}"
                    ))
        
        # Check total duration
        total_duration = sum(scene.get("duration_estimate_sec", 0) for scene in scenes)
        target_duration = normalized.get("target_duration_sec", 60)
        if total_duration > target_duration * 1.2:
            warnings.append(Warning(
                warning_type="constraint",
                severity="high",
                message=f"Script duration ({total_duration}s) exceeds target ({target_duration}s) by more than 20%",
                field_path="scenes",
                suggestion="Consider condensing scenes or removing less critical content"
            ))
        
        return draft, warnings
    
    def validator_stage(self, reviewed: Dict[str, Any], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Validate script draft against schema.
        
        Implements Requirement 5.2: Validate scene structure
        """
        if not self.validator:
            schema = self.get_output_schema()
            required = schema.get("required", [])
            errors = []
            
            for field in required:
                if field not in reviewed or not reviewed[field]:
                    errors.append({
                        "field_path": field,
                        "error_type": "missing_required",
                        "message": f"Required field '{field}' is missing or empty"
                    })
            
            # Validate scene structure
            scenes = reviewed.get("scenes", [])
            if scenes:
                scene_required = schema["properties"]["scenes"]["items"]["required"]
                for idx, scene in enumerate(scenes):
                    for field in scene_required:
                        if field not in scene or not scene[field]:
                            errors.append({
                                "field_path": f"scenes[{idx}].{field}",
                                "error_type": "missing_required",
                                "message": f"Required scene field '{field}' is missing"
                            })
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors
            }
        
        validation_result = self.validator.validate(
            content=reviewed,
            schema=self.get_output_schema(),
            locked_refs=locked_refs
        )
        
        return {
            "is_valid": validation_result.is_valid,
            "errors": [
                {
                    "field_path": e.field_path,
                    "error_type": e.error_type,
                    "message": e.message
                }
                for e in validation_result.errors
            ]
        }
    
    def committer(self, valid: Dict[str, Any], task_input: StageTaskInput) -> Dict[str, Any]:
        """
        Persist script draft to database.
        
        Implements Requirement 5.3: Update episode script_version
        """
        if not self.db or not hasattr(self.db, 'query'):
            return {
                "documents": [
                    DocumentRef(
                        ref_type="document",
                        ref_id=str(UUID(int=4)),
                        document_type="script_draft",
                        version=1
                    )
                ],
                "assets": [],
                "quality_notes": ["Script draft generated"],
                "token_usage": self._token_usage
            }
        
        from app.repositories.document_repository import DocumentRepository
        from app.repositories.episode_repository import EpisodeRepository
        
        doc_repo = DocumentRepository(self.db)
        episode_repo = EpisodeRepository(self.db)
        
        version = doc_repo.latest_version_for_episode_and_type(
            task_input.episode_id,
            "script_draft"
        ) + 1
        
        document = doc_repo.create(
            commit=False,
            project_id=task_input.project_id,
            episode_id=task_input.episode_id,
            stage_task_id=None,
            document_type="script_draft",
            version=version,
            status="draft",
            title=f"Script Draft v{version}",
            content_jsonb=valid,
            summary_text=self._generate_summary(valid),
            created_by=None
        )
        
        # Update episode script_version
        episode_repo.update_progress(
            task_input.episode_id,
            commit=False,
            script_version=version
        )
        
        self.db.flush()
        
        scene_count = len(valid.get("scenes", []))
        total_duration = sum(s.get("duration_estimate_sec", 0) for s in valid.get("scenes", []))
        
        return {
            "documents": [
                DocumentRef(
                    ref_type="document",
                    ref_id=str(document.id),
                    document_type="script_draft",
                    version=version
                )
            ],
            "assets": [],
            "quality_notes": [
                f"Generated script with {scene_count} scenes",
                f"Total estimated duration: {total_duration}s"
            ],
            "token_usage": self._token_usage
        }
    
    def _build_prompt(self, normalized: Dict[str, Any]) -> str:
        """Build prompt for LLM."""
        schema = self.get_output_schema()
        
        # Format characters
        char_list = []
        for c in normalized.get('characters', []):
            char_list.append(f"  - {c.get('name', '')}: {c.get('role', '')} - 说话风格：{c.get('speaking_style', '')}")
        char_str = '\n'.join(char_list) if char_list else "  （无）"
        
        # Format world rules
        world_rules_str = '\n'.join([f"  - {rule}" for rule in normalized.get('world_rules', [])])
        if not world_rules_str:
            world_rules_str = "  （无）"
        
        # Format forbidden conflicts
        forbidden_str = '\n'.join([f"  - {fc}" for fc in normalized.get('forbidden_conflicts', [])])
        if not forbidden_str:
            forbidden_str = "  （无）"
        
        return f"""基于 Brief、Story Bible 和角色档案，创作一个完整的剧本草稿。

【基本信息】
- 主要冲突：{normalized.get('main_conflict', '未指定')}
- 目标时长：{normalized.get('target_duration_sec', 60)} 秒

【角色信息】
{char_str}

【世界规则】
{world_rules_str}

【禁止冲突】
{forbidden_str}

【输出要求】
请以 JSON 格式返回，包含以下结构：

{{
  "scenes": [
    {{
      "scene_no": 1,
      "location": "场景地点",
      "characters": ["角色1", "角色2"],
      "goal": "本场景的目标（推动什么情节）",
      "dialogue": [
        {{
          "character": "角色名",
          "line": "台词内容",
          "emotion": "情绪（如：紧张、愤怒、悲伤、喜悦等）"
        }}
      ],
      "emotion_beats": ["情感节奏1", "情感节奏2"],
      "duration_estimate_sec": 20
    }}
  ]
}}

【关键要求】
1. 创建 3-5 个场景，总时长控制在目标范围内
2. 每个场景要有明确的目标和情感节奏
3. 对话必须符合角色的说话风格
4. 不能出现禁止冲突中列出的情节
5. 场景之间要有逻辑连贯性
6. duration_estimate_sec 要合理估算（一般对话 1 行约 3-5 秒）

【示例输出】
```json
{{
  "scenes": [
    {{
      "scene_no": 1,
      "location": "梧桐路地铁站B出口",
      "characters": ["陈屿"],
      "goal": "展现主角意识到时间循环的困惑和恐慌",
      "dialogue": [
        {{
          "character": "陈屿",
          "line": "又是7点...又是这个闸机...这到底是怎么回事？",
          "emotion": "困惑"
        }},
        {{
          "character": "陈屿",
          "line": "等等，我昨天也在这里醒来...不对，是每天都在这里！",
          "emotion": "惊恐"
        }}
      ],
      "emotion_beats": [
        "从困惑到意识到异常",
        "恐慌情绪逐渐升级"
      ],
      "duration_estimate_sec": 15
    }},
    {{
      "scene_no": 2,
      "location": "地铁站台",
      "characters": ["陈屿", "神秘女孩"],
      "goal": "主角首次注意到神秘女孩的异常",
      "dialogue": [
        {{
          "character": "陈屿",
          "line": "你...你也在这里？你是不是也...？",
          "emotion": "试探"
        }},
        {{
          "character": "神秘女孩",
          "line": "循环第12天了。你终于注意到了。",
          "emotion": "平静"
        }},
        {{
          "character": "陈屿",
          "line": "什么？你怎么知道...你到底是谁？",
          "emotion": "震惊"
        }},
        {{
          "character": "神秘女孩",
          "line": "这不重要。重要的是，你父亲留下的东西。",
          "emotion": "神秘"
        }}
      ],
      "emotion_beats": [
        "主角的试探和不确定",
        "女孩的神秘感",
        "主角的震惊和好奇"
      ],
      "duration_estimate_sec": 25
    }}
  ]
}}
```

请根据提供的信息创作剧本："""
    
    def _generate_summary(self, content: Dict[str, Any]) -> str:
        """Generate summary text for script draft."""
        scene_count = len(content.get("scenes", []))
        total_duration = sum(s.get("duration_estimate_sec", 0) for s in content.get("scenes", []))
        return f"Script draft with {scene_count} scenes, estimated {total_duration}s duration"
