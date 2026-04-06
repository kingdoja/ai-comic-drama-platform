"""
Script Agent - Generates script draft from character profiles and story bible.

Implements Requirements: 5.1, 5.2, 5.3, 5.4
"""

from typing import Any, Dict, List, Tuple
from uuid import UUID

from base_agent import BaseAgent, DocumentRef, LockedRef, StageTaskInput, Warning


class ScriptAgent(BaseAgent):
    """
    Script Agent generates script draft with scenes and dialogue.
    
    Implements Requirements:
    - 5.1: Generate script with scene structure and dialogue
    - 5.2: Include scene structure (scene_no, location, characters, dialogue, emotion_beats)
    - 5.3: Update episode script_version
    - 5.4: Check character behaviors against character_profile
    """
    
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
        
        return self.llm_service.generate(
            prompt=plan["prompt"],
            schema=plan["schema"],
            temperature=plan["temperature"]
        )
    
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
                "token_usage": getattr(self.llm_service, "call_count", 1) * 500 if self.llm_service else 500
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
            "token_usage": self.llm_service.get_token_usage() if self.llm_service else 500
        }
    
    def _build_prompt(self, normalized: Dict[str, Any]) -> str:
        """Build prompt for LLM."""
        char_names = [c.get("name", "") for c in normalized.get("characters", [])]
        
        return f"""Based on the brief, story bible, and character profiles, create a script draft.

Main Conflict: {normalized['main_conflict']}
Target Duration: {normalized['target_duration_sec']} seconds

Characters:
{chr(10).join([f"- {c.get('name', '')}: {c.get('role', '')} - {c.get('speaking_style', '')}" for c in normalized.get('characters', [])])}

World Rules:
{chr(10).join([f"- {rule}" for rule in normalized.get('world_rules', [])])}

Forbidden Conflicts:
{chr(10).join([f"- {fc}" for fc in normalized.get('forbidden_conflicts', [])])}

Generate a script draft that includes:
- Scene number, location, and characters present
- Scene goal
- Dialogue with character name, line, and emotion
- Emotion beats for the scene
- Duration estimate in seconds

Ensure character dialogue matches their speaking styles and the script respects forbidden conflicts.

Return as JSON matching the schema."""
    
    def _generate_summary(self, content: Dict[str, Any]) -> str:
        """Generate summary text for script draft."""
        scene_count = len(content.get("scenes", []))
        total_duration = sum(s.get("duration_estimate_sec", 0) for s in content.get("scenes", []))
        return f"Script draft with {scene_count} scenes, estimated {total_duration}s duration"
