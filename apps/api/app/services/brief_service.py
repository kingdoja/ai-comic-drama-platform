"""
Brief Service - Handles brief generation business logic
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

# Add agent runtime to path
agent_runtime_path = Path(__file__).parent.parent.parent.parent.parent / "workers" / "agent-runtime"
sys.path.insert(0, str(agent_runtime_path))

from agents.brief_agent import BriefAgent
from agents.base_agent import StageTaskInput
from services.llm_service import LLMServiceFactory

from app.repositories.document_repository import DocumentRepository


class BriefService:
    """Service for generating and managing briefs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        
        # Create LLM service (shared across requests)
        try:
            self.llm_service = LLMServiceFactory.create_from_env()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM service: {e}")
    
    def generate_brief(
        self,
        project_id: UUID,
        episode_id: UUID,
        raw_material: str,
        platform: str = "douyin",
        target_duration_sec: int = 60,
        target_audience: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a brief using Brief Agent.
        
        Args:
            project_id: Project UUID
            episode_id: Episode UUID
            raw_material: Raw story material
            platform: Target platform
            target_duration_sec: Target duration in seconds
            target_audience: Target audience description
            
        Returns:
            Dictionary with document_id, content, token_usage, duration_ms
        """
        start_time = datetime.now(timezone.utc)
        
        # Create Brief Agent
        agent = BriefAgent(
            db_session=self.db,
            llm_service=self.llm_service,
            validator=None  # TODO: Add validator
        )
        
        # Prepare task input
        task_input = StageTaskInput(
            workflow_run_id=uuid4(),
            project_id=project_id,
            episode_id=episode_id,
            stage_type="brief",
            input_refs=[],
            locked_refs=[],
            constraints={
                "raw_material": raw_material,
                "platform": platform,
                "target_duration_sec": target_duration_sec,
                "target_audience": target_audience or ""
            },
            target_ref_ids=[],
            raw_material=raw_material
        )
        
        # Execute agent
        result = agent.execute(task_input)
        
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Check if execution succeeded
        if result.status != "succeeded":
            raise RuntimeError(
                f"Brief generation failed: {result.error_message or 'Unknown error'}"
            )
        
        # Get document from database
        if not result.document_refs:
            raise RuntimeError("No document was created")
        
        doc_ref = result.document_refs[0]
        document = self.doc_repo.get_by_id(UUID(doc_ref.ref_id))
        
        if not document:
            raise RuntimeError(f"Document {doc_ref.ref_id} not found in database")
        
        return {
            "document_id": document.id,
            "content": document.content_jsonb,
            "token_usage": result.metrics.get("token_usage", 0),
            "duration_ms": duration_ms,
            "warnings": [
                {
                    "type": w.warning_type,
                    "severity": w.severity,
                    "message": w.message
                }
                for w in result.warnings
            ]
        }
    
    def get_brief(self, document_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get a brief by document ID.
        
        Args:
            document_id: Document UUID
            
        Returns:
            Dictionary with brief content or None if not found
        """
        document = self.doc_repo.get_by_id(document_id)
        
        if not document or document.document_type != "brief":
            return None
        
        return {
            "id": str(document.id),
            "project_id": str(document.project_id),
            "episode_id": str(document.episode_id),
            "version": document.version,
            "status": document.status,
            "content": document.content_jsonb,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
