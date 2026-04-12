# Export Schema Documentation

## Overview

This module provides data classes for export configuration, watermark settings, and export manifest generation for the Final Export feature.

## Data Classes

### ExportConfig

配置导出参数，包括分辨率、编码器、帧率等。

**属性:**
- `resolution`: 分辨率 (width, height)
- `aspect_ratio`: 宽高比 ("16:9", "9:16", "4:3", "1:1", "21:9")
- `video_codec`: 视频编码器 ("libx264", "libx265", "vp9")
- `audio_codec`: 音频编码器 ("aac", "mp3", "opus")
- `bitrate`: 比特率 ("4M", "6M", "8M")
- `frame_rate`: 帧率 (24, 30, 60)
- `pixel_format`: 像素格式 ("yuv420p", "yuv444p")
- `watermark`: 水印配置（可选）

**方法:**
- `validate()`: 验证配置有效性，返回 (is_valid, error_message)

**示例:**
```python
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
```

### WatermarkConfig

配置水印参数。

**属性:**
- `enabled`: 是否启用水印
- `type`: 水印类型 ("text" 或 "image")
- `content`: 文字内容或图片路径
- `position`: 水印位置 ("top_left", "top_right", "bottom_left", "bottom_right", "center")
- `opacity`: 透明度 (0.0 - 1.0)
- `size`: 字体大小或图片缩放百分比（可选）

**示例:**
```python
watermark = WatermarkConfig(
    enabled=True,
    type="text",
    content="© 2024",
    position="bottom_right",
    opacity=0.7,
    size=24
)
```

### VideoInfo

视频文件信息。

**属性:**
- `filename`: 文件名
- `storage_key`: 存储键
- `size_bytes`: 文件大小（字节）
- `duration_ms`: 视频时长（毫秒）
- `resolution`: 分辨率 (width, height)
- `codec`: 编码器
- `bitrate`: 比特率
- `frame_rate`: 帧率
- `checksum_sha256`: SHA256 校验和

### AssetInfo

资产文件信息。

**属性:**
- `asset_id`: 资产 ID
- `asset_type`: 资产类型 (keyframe, audio, subtitle)
- `filename`: 文件名
- `storage_key`: 存储键
- `size_bytes`: 文件大小（字节）
- `mime_type`: MIME 类型
- `checksum_sha256`: SHA256 校验和
- `shot_id`: 关联的 Shot ID（可选）

### QASummary

QA 报告摘要。

**属性:**
- `qa_report_id`: QA 报告 ID
- `result`: QA 结果 (passed, failed, warning)
- `score`: 质量分数
- `issue_count`: 问题数量
- `critical_issues`: 严重问题列表

### ExportManifest

导出清单文件，包含完整的导出包信息。

**属性:**
- `version`: 清单格式版本
- `export_id`: 导出 ID
- `episode_id`: Episode ID
- `project_id`: Project ID
- `export_timestamp`: 导出时间戳
- `video`: 视频信息 (VideoInfo)
- `assets`: 资产列表 (List[AssetInfo])
- `qa_summary`: QA 报告摘要（可选）
- `metadata`: 元数据字典

**方法:**
- `to_json()`: 序列化为 JSON 字符串
- `verify_checksums(base_dir)`: 验证所有文件的校验和，返回 (is_valid, failed_files)

**示例:**
```python
manifest = ExportManifest(
    version="1.0",
    export_id=uuid4(),
    episode_id=uuid4(),
    project_id=uuid4(),
    export_timestamp=datetime.now(),
    video=video_info,
    assets=[asset1, asset2],
    qa_summary=qa_summary,
    metadata={"shots_count": 10}
)

# 序列化为 JSON
json_str = manifest.to_json()

# 验证校验和
is_valid, failed_files = manifest.verify_checksums("/path/to/export")
```

## Requirements Mapping

- **需求 3.1, 3.2, 3.3, 3.4, 3.5**: ExportConfig 数据类和验证
- **需求 4.2, 4.3, 4.4, 4.5**: ExportManifest 数据类和方法
- **需求 10.1, 10.2, 10.3**: WatermarkConfig 数据类

## Testing

单元测试位于 `tests/unit/test_export_schema.py`，包含：
- WatermarkConfig 验证测试
- ExportConfig 验证测试
- ExportManifest JSON 序列化测试
- 校验和验证测试
