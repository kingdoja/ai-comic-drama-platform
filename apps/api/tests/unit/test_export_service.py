"""
Unit tests for ExportService.

Tests export template management functionality.

Requirements:
- 3.1: Export template retrieval
- 3.2: Douyin template configuration
- 3.3: Bilibili template configuration
- 3.4: YouTube template configuration
- 3.5: Custom config validation
"""

import pytest
from unittest.mock import Mock, MagicMock

from app.services.export_service import ExportService
from app.schemas.export import ExportConfig, WatermarkConfig


@pytest.fixture
def mock_db():
    """Mock database session."""
    return Mock()


@pytest.fixture
def mock_storage_service():
    """Mock object storage service."""
    return Mock()


@pytest.fixture
def export_service(mock_db, mock_storage_service):
    """Create ExportService instance with mocked dependencies."""
    return ExportService(db=mock_db, storage_service=mock_storage_service)


class TestGetExportTemplate:
    """Tests for get_export_template method."""
    
    def test_get_douyin_template(self, export_service):
        """
        Test retrieving Douyin template.
        
        Validates: Requirements 3.1, 3.2
        """
        # Act
        config = export_service.get_export_template("douyin")
        
        # Assert
        assert config is not None
        assert config.resolution == (1080, 1920)
        assert config.aspect_ratio == "9:16"
        assert config.video_codec == "libx264"
        assert config.audio_codec == "aac"
        assert config.bitrate == "4M"
        assert config.frame_rate == 30
        assert config.pixel_format == "yuv420p"
    
    def test_get_bilibili_template(self, export_service):
        """
        Test retrieving Bilibili template.
        
        Validates: Requirements 3.1, 3.3
        """
        # Act
        config = export_service.get_export_template("bilibili")
        
        # Assert
        assert config is not None
        assert config.resolution == (1920, 1080)
        assert config.aspect_ratio == "16:9"
        assert config.video_codec == "libx264"
        assert config.audio_codec == "aac"
        assert config.bitrate == "6M"
        assert config.frame_rate == 30
        assert config.pixel_format == "yuv420p"
    
    def test_get_youtube_template(self, export_service):
        """
        Test retrieving YouTube template.
        
        Validates: Requirements 3.1, 3.4
        """
        # Act
        config = export_service.get_export_template("youtube")
        
        # Assert
        assert config is not None
        assert config.resolution == (1920, 1080)
        assert config.aspect_ratio == "16:9"
        assert config.video_codec == "libx264"
        assert config.audio_codec == "aac"
        assert config.bitrate == "8M"
        assert config.frame_rate == 30
        assert config.pixel_format == "yuv420p"
    
    def test_get_nonexistent_template(self, export_service):
        """
        Test retrieving non-existent template returns None.
        
        Validates: Requirements 3.1
        """
        # Act
        config = export_service.get_export_template("nonexistent")
        
        # Assert
        assert config is None
    
    def test_template_names_case_sensitive(self, export_service):
        """
        Test that template names are case-sensitive.
        
        Validates: Requirements 3.1
        """
        # Act
        config_upper = export_service.get_export_template("DOUYIN")
        config_mixed = export_service.get_export_template("Douyin")
        
        # Assert
        assert config_upper is None
        assert config_mixed is None


class TestGetAllTemplates:
    """Tests for get_all_templates method."""
    
    def test_get_all_templates(self, export_service):
        """
        Test retrieving all templates.
        
        Validates: Requirements 3.1
        """
        # Act
        templates = export_service.get_all_templates()
        
        # Assert
        assert len(templates) == 3
        assert "douyin" in templates
        assert "bilibili" in templates
        assert "youtube" in templates
        
        # Verify each template is valid
        assert templates["douyin"].resolution == (1080, 1920)
        assert templates["bilibili"].resolution == (1920, 1080)
        assert templates["youtube"].resolution == (1920, 1080)
    
    def test_all_templates_have_required_fields(self, export_service):
        """
        Test that all templates have required configuration fields.
        
        Validates: Requirements 3.1
        """
        # Act
        templates = export_service.get_all_templates()
        
        # Assert
        for name, config in templates.items():
            assert config.resolution is not None
            assert config.aspect_ratio is not None
            assert config.video_codec is not None
            assert config.audio_codec is not None
            assert config.bitrate is not None
            assert config.frame_rate is not None
            assert config.pixel_format is not None


class TestValidateCustomConfig:
    """Tests for validate_custom_config method."""
    
    def test_validate_valid_config(self, export_service):
        """
        Test validating a valid custom configuration.
        
        Validates: Requirements 3.5
        """
        # Arrange
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="8M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is True
        assert error_message is None
    
    def test_validate_invalid_resolution(self, export_service):
        """
        Test validating config with invalid resolution.
        
        Validates: Requirements 3.5
        """
        # Arrange
        config = ExportConfig(
            resolution=(0, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="8M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is False
        assert "resolution" in error_message.lower()
    
    def test_validate_invalid_video_codec(self, export_service):
        """
        Test validating config with invalid video codec.
        
        Validates: Requirements 3.5
        """
        # Arrange
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="invalid_codec",
            audio_codec="aac",
            bitrate="8M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is False
        assert "video codec" in error_message.lower()
    
    def test_validate_invalid_audio_codec(self, export_service):
        """
        Test validating config with invalid audio codec.
        
        Validates: Requirements 3.5
        """
        # Arrange
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="invalid_codec",
            bitrate="8M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is False
        assert "audio codec" in error_message.lower()
    
    def test_validate_invalid_frame_rate(self, export_service):
        """
        Test validating config with invalid frame rate.
        
        Validates: Requirements 3.5
        """
        # Arrange
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="8M",
            frame_rate=120,  # Invalid frame rate
            pixel_format="yuv420p"
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is False
        assert "frame rate" in error_message.lower()
    
    def test_validate_invalid_aspect_ratio(self, export_service):
        """
        Test validating config with invalid aspect ratio.
        
        Validates: Requirements 3.5
        """
        # Arrange
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="invalid:ratio",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="8M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is False
        assert "aspect ratio" in error_message.lower()
    
    def test_validate_invalid_pixel_format(self, export_service):
        """
        Test validating config with invalid pixel format.
        
        Validates: Requirements 3.5
        """
        # Arrange
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="8M",
            frame_rate=30,
            pixel_format="invalid_format"
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is False
        assert "pixel format" in error_message.lower()
    
    def test_validate_invalid_bitrate_format(self, export_service):
        """
        Test validating config with invalid bitrate format.
        
        Validates: Requirements 3.5
        """
        # Arrange
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="8000",  # Missing M or K suffix
            frame_rate=30,
            pixel_format="yuv420p"
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is False
        assert "bitrate" in error_message.lower()
    
    def test_validate_config_with_watermark(self, export_service):
        """
        Test validating config with watermark configuration.
        
        Validates: Requirements 3.5
        """
        # Arrange
        watermark = WatermarkConfig(
            enabled=True,
            type="text",
            content="© 2024",
            position="bottom_right",
            opacity=0.7
        )
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="8M",
            frame_rate=30,
            pixel_format="yuv420p",
            watermark=watermark
        )
        
        # Act
        is_valid, error_message = export_service.validate_custom_config(config)
        
        # Assert
        assert is_valid is True
        assert error_message is None


class TestTemplateConstants:
    """Tests for template constant values."""
    
    def test_template_constants_defined(self):
        """
        Test that template constants are properly defined.
        
        Validates: Requirements 3.1
        """
        # Assert
        assert ExportService.TEMPLATE_DOUYIN == "douyin"
        assert ExportService.TEMPLATE_BILIBILI == "bilibili"
        assert ExportService.TEMPLATE_YOUTUBE == "youtube"
        assert ExportService.TEMPLATE_CUSTOM == "custom"
