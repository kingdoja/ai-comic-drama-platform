"""
Story Bible Agent - Establishes world rules and story constraints.

Implements Requirements: 3.1, 3.2, 3.3, 3.4
"""

from typing import Any, Dict, List, Tuple
from uuid import UUID

from base_agent import BaseAgent, DocumentRef, LockedRef, StageTaskInput, Warning


class StoryBibleAgent(BaseAgent):
    """
    Story Bible Agent generates world rules and story constraints.
    
    Implements Requirements:
    - 3.1: Extract world rules, timeline, and relationship baseline
    - 3.2: Include structured fields (world_rules, forbidden_conflicts, etc.)
    - 3.3: Mark as constraint source for downstream stages
    - 3.4: Check for conflicts with brief
    """
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for story bible output."""
        return {
            "type": "object",
            "required": [
                "world_rules",
                "forbidden_conflicts"
            ],
            "properties": {
                "world_rules": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "timeline": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "event": {"type": "string"},
                            "time": {"type": "string"}
                        }
                    }
                },
                "relationship_baseline": {
                    "type": "object"
                },
                "forbidden_conflicts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "key_settings": {
                    "type": "object"
                }
            }
        }
    
    def loader(self, input_refs: List[DocumentRef], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Load brief document as input.
        
        Implements Requirement 3.1: Load brief as input reference
        """
        if not self.db or not hasattr(self.db, 'query'):
            # Return mock data if no database or not a real SQLAlchemy session
            return {
                "input_documents": {
                    "brief": {
                        "genre": "urban_drama",
                        "core_selling_points": ["Identity reversal", "Visual anchors", "Family dynamics"],
                        "main_conflict": "Protagonist proves identity"
                    }
                },
                "locked_fields": []
            }
        
        # Import here to avoid circular dependency
        from app.db.models import DocumentModel
        
        input_documents = {}
        
        for ref in input_refs:
            if ref.ref_type == "document":
                # Load document from database
                doc = self.db.query(DocumentModel).filter_by(id=UUID(ref.ref_id)).first()
                if doc:
                    input_documents[doc.document_type] = doc.content_jsonb
        
        return {
            "input_documents": input_documents,
            "locked_fields": [lf.locked_fields for lf in locked_refs]
        }
    
    def normalizer(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize context for story bible generation.
        """
        brief = context.get("input_documents", {}).get("brief", {})
        
        return {
            "brief": brief,
            "raw_material_summary": constraints.get("raw_material_summary", ""),
            "genre": brief.get("genre", ""),
            "core_selling_points": brief.get("core_selling_points", []),
            "main_conflict": brief.get("main_conflict", "")
        }
    
    def planner(self, normalized: Dict[str, Any], task_input: StageTaskInput) -> Dict[str, Any]:
        """
        Create execution plan for story bible generation.
        """
        return {
            "prompt": self._build_prompt(normalized),
            "schema": self.get_output_schema(),
            "temperature": 0.7
        }
    
    def generator(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call LLM to generate story bible content.
        
        Implements Requirement 3.1: Extract world rules, timeline, relationship baseline
        Implements Requirement 3.2: Generate structured fields
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
        Review story bible for consistency with brief.
        
        Implements Requirement 3.4: Check for conflicts with brief
        """
        warnings = []
        
        # Check if world rules conflict with core selling points
        world_rules = draft.get("world_rules", [])
        core_selling_points = normalized.get("core_selling_points", [])
        
        # Simple keyword-based conflict detection
        for rule in world_rules:
            rule_lower = rule.lower()
            for selling_point in core_selling_points:
                sp_lower = selling_point.lower()
                # Check for negation words that might indicate conflict
                if any(neg in rule_lower for neg in ["no", "never", "cannot", "forbidden"]):
                    # Check if rule contradicts selling point
                    if any(word in rule_lower for word in sp_lower.split()):
                        warnings.append(Warning(
                            warning_type="consistency",
                            severity="medium",
                            message=f"World rule may conflict with selling point: '{rule}' vs '{selling_point}'",
                            field_path="world_rules",
                            suggestion="Review world rule to ensure it supports the core selling points"
                        ))
        
        # Check if forbidden_conflicts are too restrictive
        forbidden = draft.get("forbidden_conflicts", [])
        if len(forbidden) > 5:
            warnings.append(Warning(
                warning_type="quality",
                severity="low",
                message="Many forbidden conflicts may overly constrain creative freedom",
                field_path="forbidden_conflicts",
                suggestion="Consider consolidating or prioritizing the most important constraints"
            ))
        
        return draft, warnings
    
    def validator_stage(self, reviewed: Dict[str, Any], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Validate story bible against schema.
        
        Implements Requirement 3.2: Validate required fields
        """
        if not self.validator:
            # Fallback validation
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
        Persist story bible document to database.
        
        Implements Requirement 3.3: Mark as constraint source
        """
        if not self.db:
            return {
                "documents": [
                    DocumentRef(
                        ref_type="document",
                        ref_id=str(UUID(int=2)),
                        document_type="story_bible",
                        version=1
                    )
                ],
                "assets": [],
                "quality_notes": ["Story bible generated as constraint source"],
                "token_usage": getattr(self.llm_service, "call_count", 1) * 500 if self.llm_service else 500
            }
        
        from app.repositories.document_repository import DocumentRepository
        
        doc_repo = DocumentRepository(self.db)
        
        version = doc_repo.latest_version_for_episode_and_type(
            task_input.episode_id,
            "story_bible"
        ) + 1
        
        # Create document with status indicating it's a constraint source
        document = doc_repo.create(
            commit=False,
            project_id=task_input.project_id,
            episode_id=task_input.episode_id,
            stage_task_id=None,
            document_type="story_bible",
            version=version,
            status="locked",  # Mark as constraint source
            title=f"Story Bible v{version}",
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
                    document_type="story_bible",
                    version=version
                )
            ],
            "assets": [],
            "quality_notes": ["Story bible generated as constraint source for downstream stages"],
            "token_usage": self.llm_service.get_token_usage() if self.llm_service else 500
        }
    
    def _build_prompt(self, normalized: Dict[str, Any]) -> str:
        """Build prompt for LLM."""
        return f"""Based on the brief, create a story bible that establishes world rules and constraints.

Brief Information:
- Genre: {normalized['genre']}
- Core Selling Points: {', '.join(normalized['core_selling_points'])}
- Main Conflict: {normalized['main_conflict']}

Raw Material Summary:
{normalized['raw_material_summary']}

Generate a story bible that includes:
- World rules that support the story
- Timeline of key events
- Relationship baseline between characters
- Forbidden conflicts (things that should not happen)
- Key settings descriptions

Return as JSON matching the schema."""
    
    def _generate_summary(self, content: Dict[str, Any]) -> str:
        """Generate summary text for story bible."""
        rule_count = len(content.get("world_rules", []))
        forbidden_count = len(content.get("forbidden_conflicts", []))
        return f"Story bible with {rule_count} world rules and {forbidden_count} forbidden conflicts"
