"""
Export Service

Provides business logic for managing export configurations and ExportBundle records.

Requirements:
- 2.1: Create and manage ExportBundle records
- 3.1: Manage export configuration templates
"""

from typing import Optional, Dict, Tuple
from uuid import UUID
import logging

from sqlalchemy.orm import Session

from app.repositories.export_bundle_repository import ExportBundleRepository
from app.services.object_storage_service import ObjectStorageService
from app.schemas.export import ExportConfig

logger = logging.getLogger(__name__)


class ExportService:
    """
    Service for managing export configurations and ExportBundle records.
    
    Responsibilities:
    1. Manage export configuration templates
    2. Create and query ExportBundle records
    3. Coordinate with storage service for export packages
    
    Requirements: 2.1, 3.1
    """
    
    # Export template constants (Requirement 3.1)
    TEMPLATE_DOUYIN = "douyin"
    TEMPLATE_BILIBILI = "bilibili"
    TEMPLATE_YOUTUBE = "youtube"
    TEMPLATE_CUSTOM = "custom"
    
    def __init__(
        self,
        db: Session,
        storage_service: ObjectStorageService
    ):
        """
        Initialize the ExportService.
        
        Args:
            db: SQLAlchemy database session
            storage_service: Object storage service for managing export files
        """
        self.db = db
        self.storage_service = storage_service
        self.export_repo = ExportBundleRepository(db)
        
        logger.info("ExportService initialized")
    
    def get_export_template(self, template_name: str) -> Optional[ExportConfig]:
        """
        获取导出模板配置。
        
        实现需求: 3.1, 3.2, 3.3, 3.4
        
        Args:
            template_name: 模板名称 (douyin, bilibili, youtube)
            
        Returns:
            ExportConfig: 导出配置，如果模板不存在则返回 None
        """
        templates = {
            self.TEMPLATE_DOUYIN: ExportConfig(
                resolution=(1080, 1920),
                aspect_ratio="9:16",
                video_codec="libx264",
                audio_codec="aac",
                bitrate="4M",
                frame_rate=30,
                pixel_format="yuv420p"
            ),
            self.TEMPLATE_BILIBILI: ExportConfig(
                resolution=(1920, 1080),
                aspect_ratio="16:9",
                video_codec="libx264",
                audio_codec="aac",
                bitrate="6M",
                frame_rate=30,
                pixel_format="yuv420p"
            ),
            self.TEMPLATE_YOUTUBE: ExportConfig(
                resolution=(1920, 1080),
                aspect_ratio="16:9",
                video_codec="libx264",
                audio_codec="aac",
                bitrate="8M",
                frame_rate=30,
                pixel_format="yuv420p"
            )
        }
        
        config = templates.get(template_name)
        if config:
            logger.info(f"Retrieved export template: {template_name}")
        else:
            logger.warning(f"Export template not found: {template_name}")
        
        return config
    
    def get_all_templates(self) -> Dict[str, ExportConfig]:
        """
        获取所有预定义的导出模板。
        
        实现需求: 3.1
        
        Returns:
            Dict[str, ExportConfig]: 模板名称到配置的映射
        """
        templates = {
            self.TEMPLATE_DOUYIN: self.get_export_template(self.TEMPLATE_DOUYIN),
            self.TEMPLATE_BILIBILI: self.get_export_template(self.TEMPLATE_BILIBILI),
            self.TEMPLATE_YOUTUBE: self.get_export_template(self.TEMPLATE_YOUTUBE)
        }
        
        logger.info(f"Retrieved {len(templates)} export templates")
        return templates
    
    def validate_custom_config(self, config: ExportConfig) -> Tuple[bool, Optional[str]]:
        """
        验证自定义导出配置的有效性。
        
        实现需求: 3.5
        
        Args:
            config: 要验证的导出配置
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        is_valid, error_message = config.validate()
        
        if is_valid:
            logger.info("Custom export config validation passed")
        else:
            logger.warning(f"Custom export config validation failed: {error_message}")
        
        return is_valid, error_message
