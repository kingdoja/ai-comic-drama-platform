"""
Unit tests for export schemas.

Tests the ExportConfig, WatermarkConfig, ExportManifest, and related data classes.
"""

import json
import os
import tempfile
from datetime import datetime
from uuid import uuid4

import pytest

from app.schemas.export import (
    AssetInfo,
    ExportConfig,
    ExportManifest,
    QASummary,
    VideoInfo,
    WatermarkConfig,
)


class TestWatermarkConfig:
    """Test WatermarkConfig data class"""
    
    def test_valid_text_watermark(self):
        """Test creating a valid text watermark"""
        watermark = WatermarkConfig(
            enabled=True,
            type="text",
            content="© 2024",
            position="bottom_right",
            opacity=0.7,
            size=24
        )
        assert watermark.enabled is True
        assert watermark.type == "text"
        assert watermark.content == "© 2024"
        assert watermark.position == "bottom_right"
        assert watermark.opacity == 0.7
        assert watermark.size == 24
    
    def test_valid_image_watermark(self):
        """Test creating a valid image watermark"""
        watermark = WatermarkConfig(
            enabled=True,
            type="image",
            content="/path/to/logo.png",
            position="top_left",
            opacity=0.5
        )
        assert watermark.type == "image"
        assert watermark.content == "/path/to/logo.png"
    
    def test_invalid_watermark_type(self):
        """Test that invalid watermark type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid watermark type"):
            WatermarkConfig(
                enabled=True,
                type="invalid",
                content="test",
                position="center",
                opacity=0.5
            )
    
    def test_invalid_position(self):
        """Test that invalid position raises ValueError"""
        with pytest.raises(ValueError, match="Invalid watermark position"):
            WatermarkConfig(
                enabled=True,
                type="text",
                content="test",
                position="invalid_position",
                opacity=0.5
            )
    
    def test_invalid_opacity_too_high(self):
        """Test that opacity > 1.0 raises ValueError"""
        with pytest.raises(ValueError, match="Opacity must be between"):
            WatermarkConfig(
                enabled=True,
                type="text",
                content="test",
                position="center",
                opacity=1.5
            )
    
    def test_invalid_opacity_negative(self):
        """Test that negative opacity raises ValueError"""
        with pytest.raises(ValueError, match="Opacity must be between"):
            WatermarkConfig(
                enabled=True,
                type="text",
                content="test",
                position="center",
                opacity=-0.1
            )


class TestExportConfig:
    """Test ExportConfig data class"""
    
    def test_valid_config_bilibili(self):
        """Test creating a valid Bilibili export config"""
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="6M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is True
        assert error is None
    
    def test_valid_config_douyin(self):
        """Test creating a valid Douyin export config"""
        config = ExportConfig(
            resolution=(1080, 1920),
            aspect_ratio="9:16",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="4M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is True
        assert error is None
    
    def test_config_with_watermark(self):
        """Test config with watermark"""
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
            frame_rate=60,
            pixel_format="yuv420p",
            watermark=watermark
        )
        is_valid, error = config.validate()
        assert is_valid is True
        assert config.watermark is not None
        assert config.watermark.content == "© 2024"
    
    def test_invalid_resolution_zero_width(self):
        """Test that zero width resolution fails validation"""
        config = ExportConfig(
            resolution=(0, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="6M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "Invalid resolution" in error
    
    def test_invalid_resolution_negative_height(self):
        """Test that negative height resolution fails validation"""
        config = ExportConfig(
            resolution=(1920, -1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="6M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "Invalid resolution" in error
    
    def test_invalid_video_codec(self):
        """Test that invalid video codec fails validation"""
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="invalid_codec",
            audio_codec="aac",
            bitrate="6M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "Invalid video codec" in error
    
    def test_invalid_audio_codec(self):
        """Test that invalid audio codec fails validation"""
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="invalid_codec",
            bitrate="6M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "Invalid audio codec" in error
    
    def test_invalid_frame_rate(self):
        """Test that invalid frame rate fails validation"""
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="6M",
            frame_rate=45,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "Invalid frame rate" in error
    
    def test_invalid_aspect_ratio(self):
        """Test that invalid aspect ratio fails validation"""
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="invalid",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="6M",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "Invalid aspect ratio" in error
    
    def test_invalid_pixel_format(self):
        """Test that invalid pixel format fails validation"""
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="6M",
            frame_rate=30,
            pixel_format="invalid"
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "Invalid pixel format" in error
    
    def test_invalid_bitrate_format(self):
        """Test that invalid bitrate format fails validation"""
        config = ExportConfig(
            resolution=(1920, 1080),
            aspect_ratio="16:9",
            video_codec="libx264",
            audio_codec="aac",
            bitrate="6000",
            frame_rate=30,
            pixel_format="yuv420p"
        )
        is_valid, error = config.validate()
        assert is_valid is False
        assert "Invalid bitrate format" in error


class TestVideoInfo:
    """Test VideoInfo data class"""
    
    def test_create_video_info(self):
        """Test creating VideoInfo"""
        video = VideoInfo(
            filename="final_video.mp4",
            storage_key="exports/episode123/final_video.mp4",
            size_bytes=10485760,
            duration_ms=60000,
            resolution=(1920, 1080),
            codec="libx264",
            bitrate="6M",
            frame_rate=30,
            checksum_sha256="abc123def456"
        )
        assert video.filename == "final_video.mp4"
        assert video.size_bytes == 10485760
        assert video.duration_ms == 60000
        assert video.resolution == (1920, 1080)


class TestAssetInfo:
    """Test AssetInfo data class"""
    
    def test_create_asset_info_with_shot(self):
        """Test creating AssetInfo with shot_id"""
        asset_id = uuid4()
        shot_id = uuid4()
        asset = AssetInfo(
            asset_id=asset_id,
            asset_type="keyframe",
            filename="shot_001_keyframe.png",
            storage_key="assets/shot_001_keyframe.png",
            size_bytes=2048576,
            mime_type="image/png",
            checksum_sha256="def789ghi012",
            shot_id=shot_id
        )
        assert asset.asset_id == asset_id
        assert asset.asset_type == "keyframe"
        assert asset.shot_id == shot_id
    
    def test_create_asset_info_without_shot(self):
        """Test creating AssetInfo without shot_id"""
        asset_id = uuid4()
        asset = AssetInfo(
            asset_id=asset_id,
            asset_type="audio",
            filename="background_music.mp3",
            storage_key="assets/background_music.mp3",
            size_bytes=5242880,
            mime_type="audio/mpeg",
            checksum_sha256="ghi345jkl678"
        )
        assert asset.shot_id is None


class TestQASummary:
    """Test QASummary data class"""
    
    def test_create_qa_summary_passed(self):
        """Test creating QASummary for passed QA"""
        qa_id = uuid4()
        summary = QASummary(
            qa_report_id=qa_id,
            result="passed",
            score=95.5,
            issue_count=0,
            critical_issues=[]
        )
        assert summary.qa_report_id == qa_id
        assert summary.result == "passed"
        assert summary.score == 95.5
        assert len(summary.critical_issues) == 0
    
    def test_create_qa_summary_failed(self):
        """Test creating QASummary for failed QA"""
        qa_id = uuid4()
        summary = QASummary(
            qa_report_id=qa_id,
            result="failed",
            score=65.0,
            issue_count=3,
            critical_issues=["Missing dialogue in shot 3", "Invalid character reference"]
        )
        assert summary.result == "failed"
        assert summary.issue_count == 3
        assert len(summary.critical_issues) == 2


class TestExportManifest:
    """Test ExportManifest data class"""
    
    def test_create_manifest(self):
        """Test creating ExportManifest"""
        export_id = uuid4()
        episode_id = uuid4()
        project_id = uuid4()
        qa_id = uuid4()
        asset_id = uuid4()
        
        video = VideoInfo(
            filename="final_video.mp4",
            storage_key="exports/final_video.mp4",
            size_bytes=10485760,
            duration_ms=60000,
            resolution=(1920, 1080),
            codec="libx264",
            bitrate="6M",
            frame_rate=30,
            checksum_sha256="abc123"
        )
        
        assets = [
            AssetInfo(
                asset_id=asset_id,
                asset_type="keyframe",
                filename="shot_001.png",
                storage_key="assets/shot_001.png",
                size_bytes=2048576,
                mime_type="image/png",
                checksum_sha256="def456"
            )
        ]
        
        qa_summary = QASummary(
            qa_report_id=qa_id,
            result="passed",
            score=95.0,
            issue_count=0
        )
        
        manifest = ExportManifest(
            version="1.0",
            export_id=export_id,
            episode_id=episode_id,
            project_id=project_id,
            export_timestamp=datetime.now(),
            video=video,
            assets=assets,
            qa_summary=qa_summary,
            metadata={"shots_count": 10}
        )
        
        assert manifest.version == "1.0"
        assert manifest.export_id == export_id
        assert manifest.video.filename == "final_video.mp4"
        assert len(manifest.assets) == 1
        assert manifest.qa_summary.result == "passed"
    
    def test_manifest_to_json(self):
        """Test serializing manifest to JSON"""
        export_id = uuid4()
        episode_id = uuid4()
        project_id = uuid4()
        
        video = VideoInfo(
            filename="test.mp4",
            storage_key="exports/test.mp4",
            size_bytes=1024,
            duration_ms=30000,
            resolution=(1920, 1080),
            codec="libx264",
            bitrate="6M",
            frame_rate=30,
            checksum_sha256="abc123"
        )
        
        manifest = ExportManifest(
            version="1.0",
            export_id=export_id,
            episode_id=episode_id,
            project_id=project_id,
            export_timestamp=datetime(2024, 1, 1, 12, 0, 0),
            video=video,
            assets=[],
            qa_summary=None,
            metadata={}
        )
        
        json_str = manifest.to_json()
        assert isinstance(json_str, str)
        
        # Parse JSON to verify it's valid
        parsed = json.loads(json_str)
        assert parsed["version"] == "1.0"
        assert parsed["video"]["filename"] == "test.mp4"
        assert parsed["video"]["resolution"] == [1920, 1080]
    
    def test_verify_checksums_success(self):
        """Test verifying checksums when all files match"""
        export_id = uuid4()
        episode_id = uuid4()
        project_id = uuid4()
        
        # Create temporary files with known content
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create video file
            video_path = os.path.join(temp_dir, "video.mp4")
            video_content = b"fake video content"
            with open(video_path, "wb") as f:
                f.write(video_content)
            
            # Calculate actual checksum
            import hashlib
            video_checksum = hashlib.sha256(video_content).hexdigest()
            
            video = VideoInfo(
                filename="video.mp4",
                storage_key="exports/video.mp4",
                size_bytes=len(video_content),
                duration_ms=30000,
                resolution=(1920, 1080),
                codec="libx264",
                bitrate="6M",
                frame_rate=30,
                checksum_sha256=video_checksum
            )
            
            manifest = ExportManifest(
                version="1.0",
                export_id=export_id,
                episode_id=episode_id,
                project_id=project_id,
                export_timestamp=datetime.now(),
                video=video,
                assets=[],
                qa_summary=None
            )
            
            is_valid, failed_files = manifest.verify_checksums(temp_dir)
            assert is_valid is True
            assert len(failed_files) == 0
    
    def test_verify_checksums_mismatch(self):
        """Test verifying checksums when file content doesn't match"""
        export_id = uuid4()
        episode_id = uuid4()
        project_id = uuid4()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create video file
            video_path = os.path.join(temp_dir, "video.mp4")
            with open(video_path, "wb") as f:
                f.write(b"fake video content")
            
            # Use wrong checksum
            video = VideoInfo(
                filename="video.mp4",
                storage_key="exports/video.mp4",
                size_bytes=100,
                duration_ms=30000,
                resolution=(1920, 1080),
                codec="libx264",
                bitrate="6M",
                frame_rate=30,
                checksum_sha256="wrong_checksum"
            )
            
            manifest = ExportManifest(
                version="1.0",
                export_id=export_id,
                episode_id=episode_id,
                project_id=project_id,
                export_timestamp=datetime.now(),
                video=video,
                assets=[],
                qa_summary=None
            )
            
            is_valid, failed_files = manifest.verify_checksums(temp_dir)
            assert is_valid is False
            assert len(failed_files) == 1
            assert "video.mp4" in failed_files[0]
    
    def test_verify_checksums_missing_file(self):
        """Test verifying checksums when file is missing"""
        export_id = uuid4()
        episode_id = uuid4()
        project_id = uuid4()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            video = VideoInfo(
                filename="missing.mp4",
                storage_key="exports/missing.mp4",
                size_bytes=100,
                duration_ms=30000,
                resolution=(1920, 1080),
                codec="libx264",
                bitrate="6M",
                frame_rate=30,
                checksum_sha256="abc123"
            )
            
            manifest = ExportManifest(
                version="1.0",
                export_id=export_id,
                episode_id=episode_id,
                project_id=project_id,
                export_timestamp=datetime.now(),
                video=video,
                assets=[],
                qa_summary=None
            )
            
            is_valid, failed_files = manifest.verify_checksums(temp_dir)
            assert is_valid is False
            assert len(failed_files) == 1
            assert "file not found" in failed_files[0]
