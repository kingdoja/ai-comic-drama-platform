"""
Character Agent - Generates character profiles with visual anchors.

Implements Requirements: 4.1, 4.2, 4.3, 4.4
"""

from typing import Any, Dict, List, Tuple
from uuid import UUID

from base_agent import BaseAgent, DocumentRef, LockedRef, StageTaskInput, Warning


class CharacterAgent(BaseAgent):
    """
    Character Agent generates character profiles for the story.
    
    Implements Requirements:
    - 4.1: Identify main characters and generate structured cards
    - 4.2: Include character structure (name, role, goal, motivation, speaking_style, visual_anchor)
    - 4.3: Mark visual_anchors as lockable
    - 4.4: Warn about missing visual anchors
    """
    
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
        
        return self.llm_service.generate(
            prompt=plan["prompt"],
            schema=plan["schema"],
            temperature=plan["temperature"]
        )
    
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
                "token_usage": getattr(self.llm_service, "call_count", 1) * 500 if self.llm_service else 500
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
            "token_usage": self.llm_service.get_token_usage() if self.llm_service else 500
        }
    
    def _build_prompt(self, normalized: Dict[str, Any]) -> str:
        """Build prompt for LLM."""
        return f"""Based on the brief and story bible, create character profiles for the main characters.

Brief Information:
- Genre: {normalized['genre']}
- Main Conflict: {normalized['main_conflict']}

Story Bible:
- World Rules: {', '.join(normalized['world_rules'])}
- Relationship Baseline: {normalized['relationship_baseline']}

Generate character profiles that include:
- Name
- Role (protagonist, antagonist, supporting)
- Goal
- Motivation
- Speaking style
- Visual anchor (detailed description for image generation)
- Personality traits
- Relationships to other characters

Return as JSON matching the schema."""
    
    def _generate_summary(self, content: Dict[str, Any]) -> str:
        """Generate summary text for character profile."""
        char_count = len(content.get("characters", []))
        char_names = [c.get("name", "Unknown") for c in content.get("characters", [])]
        return f"Character profiles for {char_count} characters: {', '.join(char_names)}"
