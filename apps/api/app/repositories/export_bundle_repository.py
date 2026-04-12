from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models import ExportBundleModel


class ExportBundleRepository:
    """
    Repository for ExportBundle database operations.
    
    Provides CRUD operations for ExportBundleModel with proper error handling
    and type annotations.
    
    Requirements: 2.1, 2.2, 2.4, 2.5, 6.1, 6.2, 6.5
    """
    
    def __init__(self, db: Session) -> None:
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(
        self,
        project_id: UUID,
        episode_id: UUID,
        template_name: str,
        config_jsonb: dict,
        stage_task_id: Optional[UUID] = None,
        export_version: int = 1,
        status: str = "pending",
        metadata_jsonb: Optional[dict] = None,
    ) -> ExportBundleModel:
        """
        Create a new export bundle record.
        
        Requirements: 2.1, 2.2
        
        Args:
            project_id: Project UUID
            episode_id: Episode UUID
            template_name: Export template name (douyin, bilibili, youtube, custom)
            config_jsonb: Export configuration dictionary
            stage_task_id: Optional StageTask UUID
            export_version: Version number for this export
            status: Export status (pending, processing, completed, failed)
            metadata_jsonb: Optional metadata dictionary
            
        Returns:
            Created ExportBundleModel instance
        """
        export_bundle = ExportBundleModel(
            project_id=project_id,
            episode_id=episode_id,
            stage_task_id=stage_task_id,
            export_version=export_version,
            template_name=template_name,
            config_jsonb=config_jsonb,
            status=status,
            metadata_jsonb=metadata_jsonb or {},
        )
        
        self.db.add(export_bundle)
        self.db.flush()
        self.db.refresh(export_bundle)
        
        return export_bundle
    
    def get_by_id(self, export_bundle_id: UUID) -> Optional[ExportBundleModel]:
        """
        Get export bundle by ID.
        
        Requirements: 2.4
        
        Args:
            export_bundle_id: Export bundle UUID
            
        Returns:
            ExportBundleModel instance if found, None otherwise
        """
        return self.db.get(ExportBundleModel, export_bundle_id)
    
    def get_by_episode(
        self,
        episode_id: UUID,
        limit: int = 50
    ) -> List[ExportBundleModel]:
        """
        Get all export bundles for a specific episode.
        
        Requirements: 2.5, 6.1
        
        Args:
            episode_id: Episode UUID
            limit: Maximum number of records to return
            
        Returns:
            List of ExportBundleModel instances ordered by created_at descending
        """
        stmt = (
            select(ExportBundleModel)
            .where(ExportBundleModel.episode_id == episode_id)
            .order_by(ExportBundleModel.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
    
    def get_by_project(
        self,
        project_id: UUID,
        limit: int = 50
    ) -> List[ExportBundleModel]:
        """
        Get all export bundles for a specific project.
        
        Requirements: 2.5, 6.1
        
        Args:
            project_id: Project UUID
            limit: Maximum number of records to return
            
        Returns:
            List of ExportBundleModel instances ordered by created_at descending
        """
        stmt = (
            select(ExportBundleModel)
            .where(ExportBundleModel.project_id == project_id)
            .order_by(ExportBundleModel.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
    
    def get_history(
        self,
        episode_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ExportBundleModel]:
        """
        Get export history with pagination and filtering.
        
        Requirements: 6.1, 6.2
        
        Args:
            episode_id: Optional filter by episode UUID
            project_id: Optional filter by project UUID
            status: Optional filter by status (pending, processing, completed, failed)
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of ExportBundleModel instances ordered by created_at descending
        """
        stmt = select(ExportBundleModel)
        
        # Apply filters
        if episode_id:
            stmt = stmt.where(ExportBundleModel.episode_id == episode_id)
        if project_id:
            stmt = stmt.where(ExportBundleModel.project_id == project_id)
        if status:
            stmt = stmt.where(ExportBundleModel.status == status)
        
        # Apply ordering and pagination
        stmt = (
            stmt
            .order_by(ExportBundleModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        return list(self.db.scalars(stmt).all())
    
    def update_status(
        self,
        export_bundle_id: UUID,
        status: str,
        video_storage_key: Optional[str] = None,
        manifest_storage_key: Optional[str] = None,
        bundle_size_bytes: Optional[int] = None,
        video_duration_ms: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        completed_at: Optional[datetime] = None,
    ) -> Optional[ExportBundleModel]:
        """
        Update export bundle status and related fields.
        
        Requirements: 2.4
        
        Args:
            export_bundle_id: Export bundle UUID
            status: New status (pending, processing, completed, failed)
            video_storage_key: Optional video storage key
            manifest_storage_key: Optional manifest storage key
            bundle_size_bytes: Optional bundle size in bytes
            video_duration_ms: Optional video duration in milliseconds
            error_code: Optional error code for failed exports
            error_message: Optional error message for failed exports
            completed_at: Optional completion timestamp
            
        Returns:
            Updated ExportBundleModel instance if found, None otherwise
        """
        export_bundle = self.db.get(ExportBundleModel, export_bundle_id)
        if not export_bundle:
            return None
        
        # Update status
        export_bundle.status = status
        
        # Update optional fields if provided
        if video_storage_key is not None:
            export_bundle.video_storage_key = video_storage_key
        if manifest_storage_key is not None:
            export_bundle.manifest_storage_key = manifest_storage_key
        if bundle_size_bytes is not None:
            export_bundle.bundle_size_bytes = bundle_size_bytes
        if video_duration_ms is not None:
            export_bundle.video_duration_ms = video_duration_ms
        if error_code is not None:
            export_bundle.error_code = error_code
        if error_message is not None:
            export_bundle.error_message = error_message
        if completed_at is not None:
            export_bundle.completed_at = completed_at
        
        self.db.flush()
        self.db.refresh(export_bundle)
        
        return export_bundle
    
    def delete(self, export_bundle_id: UUID) -> bool:
        """
        Delete an export bundle record.
        
        Requirements: 6.5
        
        Args:
            export_bundle_id: Export bundle UUID
            
        Returns:
            True if deleted successfully, False if not found
        """
        export_bundle = self.db.get(ExportBundleModel, export_bundle_id)
        if not export_bundle:
            return False
        
        self.db.delete(export_bundle)
        self.db.flush()
        
        return True
