"""
Base agent framework implementing the common pipeline for all text agents.

Implements Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID


@dataclass
class DocumentRef:
    """Reference to a document."""
    ref_type: str  # "document"
    ref_id: str  # UUID as string
    document_type: Optional[str] = None
    version: Optional[int] = None


@dataclass
class AssetRef:
    """Reference to an asset."""
    ref_type: str  # "asset" or "shot"
    ref_id: str  # UUID as string


@dataclass
class LockedRef:
    """Reference to a locked field that cannot be modified."""
    document_id: UUID
    document_type: str
    locked_fields: List[str]  # JSON paths like "characters[0].visual_anchor"


@dataclass
class Warning:
    """Non-fatal issue detected during agent execution."""
    warning_type: str  # "consistency", "quality", "constraint"
    severity: str  # "low", "medium", "high"
    message: str
    field_path: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class StageTaskInput:
    """Input for a stage task execution."""
    workflow_run_id: UUID
    project_id: UUID
    episode_id: UUID
    stage_type: str  # "brief", "story_bible", "character", "script", "storyboard"
    input_refs: List[DocumentRef]  # References to input documents
    locked_refs: List[LockedRef]  # References to locked fields
    constraints: Dict[str, Any]  # Stage-specific constraints
    target_ref_ids: List[UUID]  # For targeted rerun (empty for full run)
    raw_material: Optional[str] = None  # For brief stage


@dataclass
class StageTaskOutput:
    """Output from a stage task execution."""
    status: str  # "succeeded", "failed", "partial"
    document_refs: List[DocumentRef]  # Created/updated documents
    asset_refs: List[AssetRef]  # Created assets (for storyboard stage)
    warnings: List[Warning]  # Non-fatal issues
    quality_notes: List[str]  # Quality observations
    metrics: Dict[str, Any]  # duration_ms, token_usage, etc.
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class BaseAgent(ABC):
    """
    Base class for all text generation agents.
    
    Implements the common pipeline: Loader → Normalizer → Planner → Generator → Critic → Validator → Committer
    """
    
    def __init__(self, db_session=None, llm_service=None, validator=None):
        """
        Initialize the base agent.
        
        Args:
            db_session: Database session for loading/committing data
            llm_service: LLM service for content generation
            validator: Validator component for schema validation
        """
        self.db = db_session
        self.llm_service = llm_service
        self.validator = validator
    
    def execute(self, task_input: StageTaskInput) -> StageTaskOutput:
        """
        Execute the agent pipeline.
        
        Implements Requirement 10.1: Agent执行遵循Pipeline顺序
        
        Args:
            task_input: Input for the stage task
            
        Returns:
            StageTaskOutput with results and metrics
        """
        start_time = datetime.now(timezone.utc)
        warnings = []
        
        try:
            # 1. Loader: Load input documents and refs
            context = self.loader(task_input.input_refs, task_input.locked_refs)
            
            # 2. Normalizer: Clean and structure context
            normalized = self.normalizer(context, task_input.constraints)
            
            # 3. Planner: Create execution plan
            plan = self.planner(normalized, task_input)
            
            # 4. Generator: Call LLM to generate content
            draft = self.generator(plan)
            
            # 5. Critic: Self-review for consistency
            reviewed, critic_warnings = self.critic(draft, normalized)
            warnings.extend(critic_warnings)
            
            # 6. Validator: Validate schema and constraints
            validation_result = self.validator_stage(reviewed, task_input.locked_refs)
            
            if not validation_result["is_valid"]:
                # Validation failed - return error
                end_time = datetime.now(timezone.utc)
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                return StageTaskOutput(
                    status="failed",
                    document_refs=[],
                    asset_refs=[],
                    warnings=warnings,
                    quality_notes=[],
                    metrics={"duration_ms": duration_ms},
                    error_code="VALIDATION_FAILED",
                    error_message="; ".join([e["message"] for e in validation_result["errors"]])
                )
            
            # 7. Committer: Persist to database
            refs = self.committer(reviewed, task_input)
            
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return StageTaskOutput(
                status="succeeded",
                document_refs=refs["documents"],
                asset_refs=refs.get("assets", []),
                warnings=warnings,
                quality_notes=refs.get("quality_notes", []),
                metrics={
                    "duration_ms": duration_ms,
                    "token_usage": refs.get("token_usage", 0)
                }
            )
            
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return StageTaskOutput(
                status="failed",
                document_refs=[],
                asset_refs=[],
                warnings=warnings,
                quality_notes=[],
                metrics={"duration_ms": duration_ms},
                error_code="EXECUTION_ERROR",
                error_message=str(e)
            )
    
    @abstractmethod
    def loader(self, input_refs: List[DocumentRef], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Load input documents and refs from database.
        
        Implements Requirement 10.2: Loader加载Refs
        
        Args:
            input_refs: References to input documents
            locked_refs: References to locked fields
            
        Returns:
            Context dictionary with loaded documents
        """
        pass
    
    @abstractmethod
    def normalizer(self, context: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and structure context for generation.
        
        Args:
            context: Raw context from loader
            constraints: Stage-specific constraints
            
        Returns:
            Normalized context
        """
        pass
    
    @abstractmethod
    def planner(self, normalized: Dict[str, Any], task_input: StageTaskInput) -> Dict[str, Any]:
        """
        Create execution plan for generation.
        
        Args:
            normalized: Normalized context
            task_input: Original task input
            
        Returns:
            Execution plan
        """
        pass
    
    @abstractmethod
    def generator(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call LLM to generate content.
        
        Implements Requirement 10.3: Generator调用LLM
        
        Args:
            plan: Execution plan
            
        Returns:
            Generated draft content
        """
        pass
    
    @abstractmethod
    def critic(self, draft: Dict[str, Any], normalized: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Warning]]:
        """
        Self-review for consistency and quality.
        
        Args:
            draft: Generated draft
            normalized: Normalized context for comparison
            
        Returns:
            Tuple of (reviewed content, warnings)
        """
        pass
    
    @abstractmethod
    def validator_stage(self, reviewed: Dict[str, Any], locked_refs: List[LockedRef]) -> Dict[str, Any]:
        """
        Validate schema and constraints.
        
        Implements Requirement 10.4: Validator校验Schema
        
        Args:
            reviewed: Reviewed content from critic
            locked_refs: Locked field references
            
        Returns:
            Validation result with is_valid and errors
        """
        pass
    
    @abstractmethod
    def committer(self, valid: Dict[str, Any], task_input: StageTaskInput) -> Dict[str, Any]:
        """
        Persist to database and return refs.
        
        Implements Requirement 10.5: Committer持久化并返回Refs
        
        Args:
            valid: Validated content
            task_input: Original task input
            
        Returns:
            Dictionary with document_refs, asset_refs, quality_notes, token_usage
        """
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for this agent's output.
        
        Returns:
            JSON schema dictionary
        """
        pass
