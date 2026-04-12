"""
Export schemas for API requests and responses.

This module defines data classes for export configuration, watermark settings,
and export manifest generation.

Implements Requirements:
- 3.1, 3.2, 3.3, 3.4, 3.5: Export configuration and templates
- 4.2, 4.3, 4.4, 4.5: Export manifest and asset packaging
- 10.1, 10.2, 10.3: Watermark configuration
"""

import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID


@dataclass
class WatermarkConfig:
    """
    水印配置数据类。
    
    实现需求: 10.1, 10.2, 10.3
    
    Attributes:
        enabled: 是否启用水印
        type: 水印类型 ("text" 或 "image")
        content: 文字内容或图片路径
        position: 水印位置 ("top_left", "top_right", "bottom_left", "bottom_right", "center")
        opacity: 透明度 (0.0 - 1.0)
        size: 字体大小或图片缩放百分比（可选）
    """
    enabled: bool
    type: str
    content: str
    position: str
    opacity: float
    size: Optional[int] = None
    
    def __post_init__(self):
        """验证水印配置参数"""
        if self.type not in ["text", "image"]:
            raise ValueError(f"Invalid watermark type: {self.type}")
        
        valid_positions = ["top_left", "top_right", "bottom_left", "bottom_right", "center"]
        if self.position not in valid_positions:
            raise ValueError(f"Invalid watermark position: {self.position}")
        
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError(f"Opacity must be between 0.0 and 1.0, got: {self.opacity}")


@dataclass
class ExportConfig:
    """
    导出配置数据类。
    
    实现需求: 3.1, 3.2, 3.3, 3.4, 3.5
    
    Attributes:
        resolution: 分辨率 (width, height)
        aspect_ratio: 宽高比 ("16:9", "9:16", "4:3")
        video_codec: 视频编码器 ("libx264", "libx265", "vp9")
        audio_codec: 音频编码器 ("aac", "mp3", "opus")
        bitrate: 比特率 ("4M", "6M", "8M")
        frame_rate: 帧率 (24, 30, 60)
        pixel_format: 像素格式 ("yuv420p", "yuv444p")
        watermark: 水印配置（可选）
    """
    resolution: Tuple[int, int]
    aspect_ratio: str
    video_codec: str
    audio_codec: str
    bitrate: str
    frame_rate: int
    pixel_format: str
    watermark: Optional[WatermarkConfig] = None
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        验证配置有效性。
        
        实现需求: 3.5
        
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 验证分辨率
        if self.resolution[0] <= 0 or self.resolution[1] <= 0:
            return False, "Invalid resolution: width and height must be positive"
        
        # 验证编码器
        valid_video_codecs = ["libx264", "libx265", "vp9"]
        if self.video_codec not in valid_video_codecs:
            return False, f"Invalid video codec: {self.video_codec}. Must be one of {valid_video_codecs}"
        
        valid_audio_codecs = ["aac", "mp3", "opus"]
        if self.audio_codec not in valid_audio_codecs:
            return False, f"Invalid audio codec: {self.audio_codec}. Must be one of {valid_audio_codecs}"
        
        # 验证帧率
        valid_frame_rates = [24, 30, 60]
        if self.frame_rate not in valid_frame_rates:
            return False, f"Invalid frame rate: {self.frame_rate}. Must be one of {valid_frame_rates}"
        
        # 验证宽高比格式
        valid_aspect_ratios = ["16:9", "9:16", "4:3", "1:1", "21:9"]
        if self.aspect_ratio not in valid_aspect_ratios:
            return False, f"Invalid aspect ratio: {self.aspect_ratio}. Must be one of {valid_aspect_ratios}"
        
        # 验证像素格式
        valid_pixel_formats = ["yuv420p", "yuv444p"]
        if self.pixel_format not in valid_pixel_formats:
            return False, f"Invalid pixel format: {self.pixel_format}. Must be one of {valid_pixel_formats}"
        
        # 验证比特率格式（简单检查是否以 M 或 K 结尾）
        if not (self.bitrate.endswith('M') or self.bitrate.endswith('K')):
            return False, f"Invalid bitrate format: {self.bitrate}. Must end with 'M' or 'K'"
        
        return True, None


@dataclass
class VideoInfo:
    """
    视频文件信息数据类。
    
    实现需求: 4.3
    
    Attributes:
        filename: 文件名
        storage_key: 存储键
        size_bytes: 文件大小（字节）
        duration_ms: 视频时长（毫秒）
        resolution: 分辨率 (width, height)
        codec: 编码器
        bitrate: 比特率
        frame_rate: 帧率
        checksum_sha256: SHA256 校验和
    """
    filename: str
    storage_key: str
    size_bytes: int
    duration_ms: int
    resolution: Tuple[int, int]
    codec: str
    bitrate: str
    frame_rate: int
    checksum_sha256: str


@dataclass
class AssetInfo:
    """
    资产文件信息数据类。
    
    实现需求: 4.3
    
    Attributes:
        asset_id: 资产 ID
        asset_type: 资产类型 (keyframe, audio, subtitle)
        filename: 文件名
        storage_key: 存储键
        size_bytes: 文件大小（字节）
        mime_type: MIME 类型
        checksum_sha256: SHA256 校验和
        shot_id: 关联的 Shot ID（可选）
    """
    asset_id: UUID
    asset_type: str
    filename: str
    storage_key: str
    size_bytes: int
    mime_type: str
    checksum_sha256: str
    shot_id: Optional[UUID] = None


@dataclass
class QASummary:
    """
    QA 报告摘要数据类。
    
    实现需求: 4.3
    
    Attributes:
        qa_report_id: QA 报告 ID
        result: QA 结果 (passed, failed, warning)
        score: 质量分数
        issue_count: 问题数量
        critical_issues: 严重问题列表
    """
    qa_report_id: UUID
    result: str
    score: float
    issue_count: int
    critical_issues: List[str] = field(default_factory=list)


@dataclass
class ExportManifest:
    """
    导出清单文件数据类。
    
    实现需求: 4.2, 4.3, 4.4, 4.5
    
    Attributes:
        version: 清单格式版本
        export_id: 导出 ID
        episode_id: Episode ID
        project_id: Project ID
        export_timestamp: 导出时间戳
        video: 视频信息
        assets: 资产列表
        qa_summary: QA 报告摘要（可选）
        metadata: 元数据
    """
    version: str
    export_id: UUID
    episode_id: UUID
    project_id: UUID
    export_timestamp: datetime
    video: VideoInfo
    assets: List[AssetInfo]
    qa_summary: Optional[QASummary]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """
        序列化为 JSON 字符串。
        
        实现需求: 4.2
        
        Returns:
            str: JSON 格式的清单内容
        """
        def serialize_value(obj):
            """自定义序列化函数"""
            if isinstance(obj, UUID):
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, tuple):
                return list(obj)
            elif hasattr(obj, '__dict__'):
                return {k: serialize_value(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [serialize_value(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: serialize_value(v) for k, v in obj.items()}
            return obj
        
        manifest_dict = asdict(self)
        serialized = serialize_value(manifest_dict)
        return json.dumps(serialized, indent=2, ensure_ascii=False)
    
    def verify_checksums(self, base_dir: str) -> Tuple[bool, List[str]]:
        """
        验证所有文件的校验和。
        
        实现需求: 4.5
        
        Args:
            base_dir: 文件所在的基础目录
            
        Returns:
            Tuple[bool, List[str]]: (是否全部验证通过, 验证失败的文件列表)
        """
        failed_files = []
        
        # 验证视频文件
        video_path = os.path.join(base_dir, self.video.filename)
        if os.path.exists(video_path):
            calculated_checksum = self._calculate_sha256(video_path)
            if calculated_checksum != self.video.checksum_sha256:
                failed_files.append(f"{self.video.filename} (expected: {self.video.checksum_sha256}, got: {calculated_checksum})")
        else:
            failed_files.append(f"{self.video.filename} (file not found)")
        
        # 验证资产文件
        for asset in self.assets:
            asset_path = os.path.join(base_dir, asset.filename)
            if os.path.exists(asset_path):
                calculated_checksum = self._calculate_sha256(asset_path)
                if calculated_checksum != asset.checksum_sha256:
                    failed_files.append(f"{asset.filename} (expected: {asset.checksum_sha256}, got: {calculated_checksum})")
            else:
                failed_files.append(f"{asset.filename} (file not found)")
        
        return len(failed_files) == 0, failed_files
    
    @staticmethod
    def _calculate_sha256(file_path: str) -> str:
        """
        计算文件的 SHA256 校验和。
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: SHA256 校验和（十六进制字符串）
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # 分块读取以处理大文件
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
