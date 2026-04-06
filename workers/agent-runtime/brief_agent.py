"""
Brief Agent - Analyzes raw material and generates adaptation direction document.

Implements Requirements: 2.1, 2.2, 2.3, 2.4
"""

from typing import Any, Dict, List, Tuple
from uuid import UUID

from base_agent import BaseAgent, DocumentRef, LockedRef, StageTaskInput, Warning


class BriefAgent(BaseAgent):
    """
    Brief Agent generates the adaptation direction document from raw material.
    
    Implements Requirements:
    - 2.1: Extract story main line, character relationships, and core conflicts
    - 2.2: Include structured fields (genre, target_audience, core_selling_points, etc.)
    - 2.3: Persist document to database with correct associations
    - 2.4: Validate required fields
    """
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for brief output."""
        return {
            "type": "object",
            "required": [
                "genre",
                "target_audience",
                "core_selling_points",
                "main_conflict",
                "target_style"
            ],
            "properties": {
                "genre": {"type": "string"},
                "target_audience": {"type": "string"},
                "core_selling_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "main_conflict": {"type": "string"},
                "adaptation_risks": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "target_style": {"type": "string"},
                "tone": {"type": "string"}
            }
        }
    
    def loader(self, input_refs: List[DocumentRef], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Load input documents (none for brief stage).
        
        Brief is the first stage, so no input documents to load.
        """
        return {
            "input_documents": [],
            "locked_fields": []
        }
    
    def normalizer(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize context for brief generation.
        
        Args:
            context: Raw context from loader
            constraints: Contains raw_material, platform, target_duration_sec, target_audience
        """
        return {
            "raw_material": constraints.get("raw_material", ""),
            "platform": constraints.get("platform", "douyin"),
            "target_duration_sec": constraints.get("target_duration_sec", 60),
            "target_audience": constraints.get("target_audience", "")
        }
    
    def planner(self, normalized: Dict[str, Any], task_input: StageTaskInput) -> Dict[str, Any]:
        """
        Create execution plan for brief generation.
        """
        return {
            "prompt": self._build_prompt(normalized),
            "schema": self.get_output_schema(),
            "temperature": 0.7
        }
    
    def generator(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call LLM to generate brief content.
        
        Implements Requirement 2.1: Extract story elements
        Implements Requirement 2.2: Generate structured fields
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
        Review brief for quality and completeness.
        
        Brief is the first stage, so no consistency checks against upstream documents.
        """
        warnings = []
        
        # Check if core_selling_points has sufficient items
        selling_points = draft.get("core_selling_points", [])
        if len(selling_points) < 3:
            warnings.append(Warning(
                warning_type="quality",
                severity="medium",
                message="Brief has fewer than 3 core selling points, which may limit creative direction",
                field_path="core_selling_points",
                suggestion="Consider adding more selling points to provide richer creative direction"
            ))
        
        # Check if adaptation_risks are identified
        if not draft.get("adaptation_risks"):
            warnings.append(Warning(
                warning_type="quality",
                severity="low",
                message="No adaptation risks identified",
                field_path="adaptation_risks",
                suggestion="Consider identifying potential challenges in adapting this material"
            ))
        
        return draft, warnings
    
    def validator_stage(self, reviewed: Dict[str, Any], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Validate brief against schema.
        
        Implements Requirement 2.4: Validate required fields
        """
        if not self.validator:
            # Fallback validation if validator not configured
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
        
        # Use validator component
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
        Persist brief document to database.
        
        Implements Requirement 2.3: Persist with correct associations
        """
        if not self.db:
            # Return mock refs if no database configured
            return {
                "documents": [
                    DocumentRef(
                        ref_type="document",
                        ref_id=str(UUID(int=1)),
                        document_type="brief",
                        version=1
                    )
                ],
                "assets": [],
                "quality_notes": ["Brief generated successfully"],
                "token_usage": getattr(self.llm_service, "call_count", 1) * 500 if self.llm_service else 500
            }
        
        # Import here to avoid circular dependency
        from app.repositories.document_repository import DocumentRepository
        
        doc_repo = DocumentRepository(self.db)
        
        # Get next version
        version = doc_repo.latest_version_for_episode_and_type(
            task_input.episode_id,
            "brief"
        ) + 1
        
        # Create document
        document = doc_repo.create(
            commit=False,
            project_id=task_input.project_id,
            episode_id=task_input.episode_id,
            stage_task_id=None,  # Will be set by workflow service
            document_type="brief",
            version=version,
            status="draft",
            title=f"Brief v{version}",
            content_jsonb=valid,
            summary_text=self._generate_summary(valid),
            created_by=None  # AI-generated
        )
        
        self.db.flush()
        
        return {
            "documents": [
                DocumentRef(
                    ref_type="document",
                    ref_id=str(document.id),
                    document_type="brief",
                    version=version
                )
            ],
            "assets": [],
            "quality_notes": ["Brief generated successfully"],
            "token_usage": self.llm_service.get_token_usage() if self.llm_service else 500
        }
    
    def _build_prompt(self, normalized: Dict[str, Any]) -> str:
        """Build prompt for LLM."""
        return f"""Analyze the following raw material and create a brief for adaptation to {normalized['platform']} platform.

Raw Material:
{normalized['raw_material']}

Target Duration: {normalized['target_duration_sec']} seconds
Target Audience: {normalized['target_audience'] or 'General audience'}

Generate a brief that includes:
- Genre classification
- Target audience description
- 3-5 core selling points
- Main conflict
- Adaptation risks
- Target visual style
- Tone

Return as JSON matching the schema."""
    
    def _generate_summary(self, content: Dict[str, Any]) -> str:
        """Generate summary text for brief."""
        genre = content.get("genre", "unknown")
        conflict = content.get("main_conflict", "")
        return f"Brief for {genre} adaptation. Main conflict: {conflict}"
