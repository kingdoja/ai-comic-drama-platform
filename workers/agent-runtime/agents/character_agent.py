"""
Character Agent - Generates character profiles with visual anchors.

Implements Requirements: 4.1, 4.2, 4.3, 4.4
"""

import json
from typing import Any, Dict, List, Tuple
from uuid import UUID

from agents.base_agent import BaseAgent, DocumentRef, LockedRef, StageTaskInput, Warning
from services.llm_service import LLMServiceFactory, LLMMessage


class CharacterAgent(BaseAgent):
    """
    Character Agent generates character profiles for the story.
    
    Implements Requirements:
    - 4.1: Identify main characters and generate structured cards
    - 4.2: Include character structure (name, role, goal, motivation, speaking_style, visual_anchor)
    - 4.3: Mark visual_anchors as lockable
    - 4.4: Warn about missing visual anchors
    """
    
    def __init__(self, db_session=None, llm_service=None, validator=None):
        """
        Initialize Character Agent.
        
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
        """Get the JSON schema for character profile output."""
        return {
            "type": "object",
            "required": ["characters"],
            "properties": {
                "characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": [
                            "name",
                            "role",
                            "goal",
                            "motivation",
                            "speaking_style",
                            "visual_anchor"
                        ],
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "goal": {"type": "string"},
                            "motivation": {"type": "string"},
                            "speaking_style": {"type": "string"},
                            "visual_anchor": {"type": "string"},
                            "personality_traits": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "relationships": {"type": "object"}
                        }
                    },
                    "minItems": 1
                }
            }
        }
    
    def loader(self, input_refs: List[DocumentRef], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Load brief and story bible as input.
        
        Implements Requirement 4.1: Load brief and story_bible as input references
        """
        if not self.db or not hasattr(self.db, 'query'):
            return {
                "input_documents": {
                    "brief": {
                        "genre": "urban_drama",
                        "core_selling_points": ["Identity reversal"],
                        "main_conflict": "Protagonist proves identity"
                    },
                    "story_bible": {
                        "world_rules": ["Family status by tokens"],
                        "relationship_baseline": {}
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
        Normalize context for character generation.
        """
        brief = context.get("input_documents", {}).get("brief", {})
        story_bible = context.get("input_documents", {}).get("story_bible", {})
        
        return {
            "brief": brief,
            "story_bible": story_bible,
            "genre": brief.get("genre", ""),
            "main_conflict": brief.get("main_conflict", ""),
            "world_rules": story_bible.get("world_rules", []),
            "relationship_baseline": story_bible.get("relationship_baseline", {})
        }
    
    def planner(self, normalized: Dict[str, Any], task_input: StageTaskInput) -> Dict[str, Any]:
        """
        Create execution plan for character generation.
        """
        return {
            "prompt": self._build_prompt(normalized),
            "schema": self.get_output_schema(),
            "temperature": 0.7
        }
    
    def generator(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call LLM to generate character profiles.
        
        Implements Requirement 4.1: Identify main characters and generate cards
        Implements Requirement 4.2: Include all required character fields
        """
        if not self.llm_service:
            raise RuntimeError("LLM service not configured")
        
        # Build system and user prompts
        system_prompt = """你是一个专业的角色设计师和编剧。你的任务是为影视作品创建详细的角色档案，包含视觉锚点。

你需要：
1. 识别故事中的主要角色（2-4个）
2. 为每个角色创建完整的档案（姓名、角色定位、目标、动机、说话风格、视觉锚点）
3. 确保视觉锚点具体、独特、易于识别
4. 角色之间要有清晰的关系和冲突

请以 JSON 格式返回结果，确保所有字段都完整且有价值。"""
        
        user_prompt = plan["prompt"]
        
        # Call LLM
        response = self.llm_service.generate_from_prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=plan["temperature"],
            max_tokens=3000
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
        Review character profiles for completeness and consistency.
        
        Implements Requirement 4.4: Warn about missing visual anchors
        """
        warnings = []
        
        characters = draft.get("characters", [])
        
        # Check for missing or empty visual anchors
        for idx, character in enumerate(characters):
            visual_anchor = character.get("visual_anchor", "")
            if not visual_anchor or not visual_anchor.strip():
                warnings.append(Warning(
                    warning_type="quality",
                    severity="high",
                    message=f"Character '{character.get('name', 'Unknown')}' is missing visual anchor",
                    field_path=f"characters[{idx}].visual_anchor",
                    suggestion="Add visual anchor description for consistent character rendering"
                ))
        
        # Check if characters have defined relationships
        for idx, character in enumerate(characters):
            relationships = character.get("relationships", {})
            if not relationships:
                warnings.append(Warning(
                    warning_type="quality",
                    severity="low",
                    message=f"Character '{character.get('name', 'Unknown')}' has no defined relationships",
                    field_path=f"characters[{idx}].relationships",
                    suggestion="Define relationships to other characters for better story coherence"
                ))
        
        # Check if we have protagonist
        has_protagonist = any(c.get("role", "").lower() in ["protagonist", "main", "lead"] for c in characters)
        if not has_protagonist:
            warnings.append(Warning(
                warning_type="quality",
                severity="medium",
                message="No protagonist identified in character profiles",
                field_path="characters",
                suggestion="Ensure at least one character is marked as protagonist"
            ))
        
        return draft, warnings
    
    def validator_stage(self, reviewed: Dict[str, Any], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Validate character profiles against schema.
        
        Implements Requirement 4.2: Validate character structure
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
            
            # Validate character structure
            characters = reviewed.get("characters", [])
            if characters:
                char_required = schema["properties"]["characters"]["items"]["required"]
                for idx, char in enumerate(characters):
                    for field in char_required:
                        if field not in char or not char[field]:
                            errors.append({
                                "field_path": f"characters[{idx}].{field}",
                                "error_type": "missing_required",
                                "message": f"Required character field '{field}' is missing"
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
        Persist character profile to database.
        
        Implements Requirement 4.3: Mark visual_anchors as lockable
        """
        if not self.db:
            return {
                "documents": [
                    DocumentRef(
                        ref_type="document",
                        ref_id=str(UUID(int=3)),
                        document_type="character_profile",
                        version=1
                    )
                ],
                "assets": [],
                "quality_notes": ["Character profiles generated with lockable visual anchors"],
                "token_usage": self._token_usage
            }
        
        from app.repositories.document_repository import DocumentRepository
        
        doc_repo = DocumentRepository(self.db)
        
        version = doc_repo.latest_version_for_episode_and_type(
            task_input.episode_id,
            "character_profile"
        ) + 1
        
        # Mark visual anchors as lockable in metadata
        lockable_fields = []
        characters = valid.get("characters", [])
        for idx, char in enumerate(characters):
            lockable_fields.append(f"characters[{idx}].name")
            lockable_fields.append(f"characters[{idx}].visual_anchor")
        
        # Add lockable fields to content
        valid["_lockable_fields"] = lockable_fields
        
        document = doc_repo.create(
            commit=False,
            project_id=task_input.project_id,
            episode_id=task_input.episode_id,
            stage_task_id=None,
            document_type="character_profile",
            version=version,
            status="draft",
            title=f"Character Profile v{version}",
            content_jsonb=valid,
            summary_text=self._generate_summary(valid),
            created_by=None
        )
        
        self.db.flush()
        
        return {
            "documents": [
                DocumentRef(
                    ref_type="document",
                    ref_id=str(document.id),
                    document_type="character_profile",
                    version=version
                )
            ],
            "assets": [],
            "quality_notes": [
                f"Generated {len(characters)} character profiles",
                f"Lockable fields: {', '.join(lockable_fields)}"
            ],
            "token_usage": self._token_usage
        }
    
    def _build_prompt(self, normalized: Dict[str, Any]) -> str:
        """Build prompt for LLM."""
        schema = self.get_output_schema()
        
        world_rules_str = '\n'.join([f"  - {rule}" for rule in normalized.get('world_rules', [])])
        if not world_rules_str:
            world_rules_str = "  （无）"
        
        relationship_baseline = normalized.get('relationship_baseline', {})
        if relationship_baseline:
            rel_str = '\n'.join([f"  - {k}: {v}" for k, v in relationship_baseline.items()])
        else:
            rel_str = "  （无）"
        
        return f"""基于 Brief 和 Story Bible，创建主要角色的详细档案。

【Brief 信息】
- 故事类型：{normalized.get('genre', '未指定')}
- 主要冲突：{normalized.get('main_conflict', '未指定')}

【Story Bible】
- 世界规则：
{world_rules_str}

- 角色关系基线：
{rel_str}

【输出要求】
请以 JSON 格式返回，包含以下结构：

{{
  "characters": [
    {{
      "name": "角色姓名",
      "role": "角色定位（主角/配角/反派等）",
      "goal": "角色目标（想要达成什么）",
      "motivation": "内在动机（为什么要这么做）",
      "speaking_style": "说话风格（语气、用词特点、口头禅等）",
      "visual_anchor": "视觉锚点（具体、独特、易识别的外貌特征，用于图像生成）",
      "personality_traits": ["性格特征1", "性格特征2", "性格特征3"],
      "relationships": {{
        "与其他角色的关系": "关系描述"
      }}
    }}
  ]
}}

【关键要求】
1. 识别 2-4 个主要角色
2. visual_anchor 必须具体详细（如："左眼角有一道细长疤痕，总是戴着父亲留下的银色怀表，黑色短发略显凌乱"）
3. speaking_style 要有特色（如："语速快，喜欢用技术术语，紧张时会重复'等等'这个词"）
4. 角色之间要有清晰的关系和冲突
5. 至少有一个主角（protagonist）

【示例输出】
```json
{{
  "characters": [
    {{
      "name": "陈屿",
      "role": "主角（程序员）",
      "goal": "打破时间循环，阻止城市灾难",
      "motivation": "证明自己的身份，找回失去的记忆和家人",
      "speaking_style": "理性冷静，喜欢用逻辑分析问题，紧张时会下意识摸左手腕（原本戴表的位置）",
      "visual_anchor": "左眼角有一道细长疤痕（童年事故留下），总是穿着深蓝色连帽衫，右手食指有轻微颤抖（长期编程导致），黑色短发略显凌乱",
      "personality_traits": ["理性", "执着", "内向", "善于观察"],
      "relationships": {{
        "神秘女孩": "合作关系，但对她的真实身份充满疑惑",
        "父亲": "复杂的情感纠葛，既怨恨又渴望理解"
      }}
    }},
    {{
      "name": "神秘女孩",
      "role": "关键配角（回响体）",
      "goal": "帮助主角找到真相",
      "motivation": "完成未完成的使命，弥补过去的遗憾",
      "speaking_style": "简洁克制，很少用第一人称，说话时眼神飘忽，像在回忆什么",
      "visual_anchor": "半透明的身影（在特定光线下），穿着白色连衣裙（边缘有数字化像素闪烁），长发遮住右半边脸，左手腕有发光的数字编码",
      "personality_traits": ["神秘", "冷静", "善良", "孤独"],
      "relationships": {{
        "陈屿": "引导者和协助者，但从不透露自己的秘密",
        "事故": "与即将发生的事故有深刻联系"
      }}
    }}
  ]
}}
```

请根据 Brief 和 Story Bible 生成角色档案："""
    
    def _generate_summary(self, content: Dict[str, Any]) -> str:
        """Generate summary text for character profile."""
        char_count = len(content.get("characters", []))
        char_names = [c.get("name", "Unknown") for c in content.get("characters", [])]
        return f"Character profiles for {char_count} characters: {', '.join(char_names)}"
