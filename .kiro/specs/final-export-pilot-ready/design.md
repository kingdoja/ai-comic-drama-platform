# Iteration 6: Final Export 与 Pilot Ready 强化 - 设计文档

## 概述

本迭代是项目的最后一个迭代，实现从"能生成预览"到"能交付成品"的关键升级。通过实现 Final Export Stage、ExportBundle 记录管理、导出配置模板、Trace/Lineage 追踪和可观测性仪表板，将系统从开发阶段推向生产就绪状态。

关键设计原则：
- **交付质量**: 生成高分辨率、符合平台标准的最终视频
- **可追溯性**: 完整记录从 Brief 到 Final Export 的数据流转路径
- **可配置性**: 支持多平台导出模板和自定义配置
- **可观测性**: 提供系统运行状态的全面可见性
- **生产就绪**: 确保系统稳定性、性能和安全性

## 架构

### Final Export 数据流

```
QA Report (passed)
    ↓
Final Export Stage Trigger
    ↓
Load Export Configuration
    ↓
Collect Primary Assets
    ↓
Download Assets to Temp Directory
    ↓
FFmpeg Composition (High Resolution)
    ↓
Apply Watermark (Optional)
    ↓
Quality Check (Playability, Duration)
    ↓
Upload to Object Storage
    ↓
Create ExportBundle Record
    ↓
Generate Manifest File
    ↓
Package Assets (Video + Manifest + QA Report)
    ↓
Send Notification / Webhook
    ↓
Update Episode Status to "exported"
```

### 组件关系

```
┌─────────────────────────────────────────────────────────┐
│                  Workflow Orchestrator                  │
│  控制 Final Export Stage 执行和状态管理                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─────────────────┬────────────────────┬────────────────┐
                   ↓                 ↓                    ↓                ↓
         ┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐ ┌──────────────┐
         │ Final Export     │ │ Export       │ │ Trace Service   │ │ Observability│
         │ Stage            │ │ Service      │ │                 │ │ Service      │
         └────────┬─────────┘ └──────┬───────┘ └────────┬────────┘ └──────┬───────┘
                  │                  │                   │                 │
                  ↓                  ↓                   ↓                 ↓
         ┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐ ┌──────────────┐
         │ FFmpeg Composer  │ │ Export       │ │ Lineage         │ │ Metrics      │
         │ Watermark        │ │ Config       │ │ Tracker         │ │ Collector    │
         │ Quality Checker  │ │ Repository   │ │                 │ │              │
         └────────┬─────────┘ └──────┬───────┘ └────────┬────────┘ └──────┬───────┘
                  │                  │                   │                 │
                  └──────────────────┴───────────────────┴─────────────────┘
                                     ↓
                   ┌──────────────────────────────────────┐
                   │      Object Storage Service          │
                   │  存储导出包和所有资产                │
                   └──────────────────┬───────────────────┘
                                      ↓
                   ┌──────────────────────────────────────┐
                   │      ExportBundle Repository         │
                   │  管理导出记录和历史                  │
                   └──────────────────────────────────────┘
```


## 组件和接口

### Final Export Stage

```python
class FinalExportStage:
    """
    Final Export Stage，负责生成正式的交付包。
    
    职责：
    1. 验证 QA 状态
    2. 加载导出配置
    3. 收集主资产
    4. 合成高分辨率视频
    5. 应用水印（可选）
    6. 质量检查
    7. 打包和上传
    8. 创建 ExportBundle 记录
    9. 发送通知
    
    实现需求: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    
    def __init__(
        self,
        db: Session,
        storage_service: ObjectStorageService,
        export_service: ExportService,
        qa_repo: QARepository,
        notification_service: NotificationService
    ):
        self.db = db
        self.storage_service = storage_service
        self.export_service = export_service
        self.qa_repo = qa_repo
        self.notification_service = notification_service
    
    def execute(
        self,
        episode_id: UUID,
        project_id: UUID,
        stage_task_id: UUID,
        export_config: ExportConfig
    ) -> FinalExportResult:
        """
        执行 Final Export Stage。
        
        Args:
            episode_id: Episode ID
            project_id: Project ID
            stage_task_id: StageTask ID
            export_config: 导出配置
            
        Returns:
            FinalExportResult: 执行结果
            
        流程：
        1. 验证 QA 状态（需求 5.1, 5.2）
        2. 收集主资产（需求 1.2）
        3. 下载资产到临时目录
        4. 合成高分辨率视频（需求 1.1）
        5. 应用水印（需求 10.1-10.4）
        6. 质量检查（需求 5.5）
        7. 上传导出包（需求 1.3）
        8. 创建 ExportBundle 记录（需求 2.1-2.4）
        9. 生成清单文件（需求 4.2, 4.3）
        10. 发送通知（需求 9.1-9.4）
        11. 更新 Episode 状态（需求 1.5）
        """
        pass
    
    def _verify_qa_status(
        self,
        episode_id: UUID
    ) -> Tuple[bool, Optional[str]]:
        """
        验证 QA 状态。
        
        实现需求: 5.1, 5.2, 5.3
        
        Returns:
            (is_passed, error_message)
        """
        # 获取最新的 QA 报告
        qa_reports = self.qa_repo.get_latest_for_episode(episode_id)
        
        # 检查是否有 critical 问题
        for report in qa_reports:
            if report.result == "failed" and report.severity == "critical":
                return False, f"QA failed with critical issues: {report.issues_jsonb}"
        
        return True, None
    
    def _compose_high_resolution_video(
        self,
        shot_assets_list: List[ShotAssets],
        subtitle_asset: Optional[AssetModel],
        temp_dir: str,
        output_path: str,
        export_config: ExportConfig
    ) -> int:
        """
        合成高分辨率视频。
        
        实现需求: 1.1, 3.1, 3.2, 3.3, 3.4
        
        支持的分辨率：
        - 1080p (1920x1080) - B站、YouTube 横屏
        - 1080x1920 - 抖音、快手竖屏
        - 2K (2560x1440)
        - 4K (3840x2160)
        
        Returns:
            视频时长（毫秒）
        """
        pass
    
    def _apply_watermark(
        self,
        input_path: str,
        output_path: str,
        watermark_config: WatermarkConfig
    ) -> None:
        """
        应用水印。
        
        实现需求: 10.1, 10.2, 10.3, 10.4
        
        支持：
        - 文字水印
        - 图片水印
        - 位置：左上、右上、左下、右下、居中
        - 透明度和大小
        """
        pass
    
    def _quality_check(
        self,
        video_path: str,
        expected_duration_ms: int
    ) -> Tuple[bool, Optional[str]]:
        """
        质量检查。
        
        实现需求: 5.5
        
        检查项：
        - 文件可读性
        - 视频可播放性
        - 时长匹配
        - 编码格式正确
        """
        pass
```

### Export Service

```python
class ExportService:
    """
    导出服务，管理导出配置和 ExportBundle 记录。
    
    职责：
    1. 管理导出配置模板
    2. 创建和查询 ExportBundle
    3. 生成清单文件
    4. 管理导出历史
    
    实现需求: 2.1-2.5, 3.1-3.5, 4.1-4.5, 6.1-6.5
    """
    
    def __init__(
        self,
        db: Session,
        storage_service: ObjectStorageService
    ):
        self.db = db
        self.storage_service = storage_service
    
    def create_export_bundle(
        self,
        episode_id: UUID,
        project_id: UUID,
        export_config: ExportConfig,
        video_asset: AssetModel,
        manifest: ExportManifest
    ) -> ExportBundleModel:
        """
        创建导出包记录。
        
        实现需求: 2.1, 2.2, 2.3
        
        Args:
            episode_id: Episode ID
            project_id: Project ID
            export_config: 导出配置
            video_asset: 视频资产
            manifest: 清单文件
            
        Returns:
            ExportBundleModel: 导出包记录
        """
        pass
    
    def get_export_template(
        self,
        template_name: str
    ) -> ExportConfig:
        """
        获取导出模板。
        
        实现需求: 3.1, 3.2, 3.3
        
        预定义模板：
        - douyin: 抖音竖屏 (1080x1920, 9:16)
        - bilibili: B站横屏 (1920x1080, 16:9)
        - youtube: YouTube 横屏 (1920x1080, 16:9)
        - custom: 自定义配置
        """
        templates = {
            "douyin": ExportConfig(
                resolution=(1080, 1920),
                aspect_ratio="9:16",
                video_codec="libx264",
                audio_codec="aac",
                bitrate="4M",
                frame_rate=30,
                pixel_format="yuv420p"
            ),
            "bilibili": ExportConfig(
                resolution=(1920, 1080),
                aspect_ratio="16:9",
                video_codec="libx264",
                audio_codec="aac",
                bitrate="6M",
                frame_rate=30,
                pixel_format="yuv420p"
            ),
            "youtube": ExportConfig(
                resolution=(1920, 1080),
                aspect_ratio="16:9",
                video_codec="libx264",
                audio_codec="aac",
                bitrate="8M",
                frame_rate=30,
                pixel_format="yuv420p"
            )
        }
        return templates.get(template_name)
    
    def generate_manifest(
        self,
        episode_id: UUID,
        video_asset: AssetModel,
        all_assets: List[AssetModel],
        qa_report: Optional[QAReportModel]
    ) -> ExportManifest:
        """
        生成清单文件。
        
        实现需求: 4.2, 4.3, 4.4
        
        清单内容：
        - 导出元数据
        - 视频文件信息
        - 所有资产列表
        - 校验和
        - QA 报告摘要
        """
        pass
    
    def get_export_history(
        self,
        episode_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        limit: int = 50
    ) -> List[ExportBundleModel]:
        """
        获取导出历史。
        
        实现需求: 6.1, 6.2
        
        Returns:
            按时间倒序的导出记录列表
        """
        pass
    
    def delete_export_bundle(
        self,
        export_bundle_id: UUID
    ) -> bool:
        """
        删除导出包。
        
        实现需求: 6.5
        
        删除：
        - 视频文件
        - 清单文件
        - ExportBundle 记录
        """
        pass
```


### Trace Service

```python
class TraceService:
    """
    追踪服务，记录和查询数据流转路径。
    
    职责：
    1. 记录数据流转事件
    2. 构建 Lineage 关系
    3. 查询追踪路径
    4. 可视化数据流
    
    实现需求: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_trace_event(
        self,
        event_type: str,
        source_type: str,
        source_id: UUID,
        target_type: str,
        target_id: UUID,
        metadata: dict = None
    ) -> TraceRecordModel:
        """
        记录追踪事件。
        
        实现需求: 7.1
        
        事件类型：
        - stage_execution: Stage 执行
        - asset_generation: 资产生成
        - document_creation: 文档创建
        - transformation: 数据转换
        """
        pass
    
    def get_lineage(
        self,
        target_type: str,
        target_id: UUID,
        direction: str = "backward"
    ) -> LineageGraph:
        """
        获取血缘关系。
        
        实现需求: 7.2, 7.3, 7.4
        
        Args:
            target_type: 目标类型 (asset, document, shot)
            target_id: 目标 ID
            direction: 方向 (backward=上游, forward=下游, both=双向)
            
        Returns:
            LineageGraph: 血缘关系图
        """
        pass
    
    def get_full_trace(
        self,
        episode_id: UUID
    ) -> TraceGraph:
        """
        获取完整追踪路径。
        
        实现需求: 7.1, 7.5
        
        Returns:
            从 Brief 到 Final Export 的完整数据流转路径
        """
        pass
```

### Observability Service

```python
class ObservabilityService:
    """
    可观测性服务，提供系统运行状态的可见性。
    
    职责：
    1. 收集系统指标
    2. 聚合性能数据
    3. 生成统计报告
    4. 提供仪表板数据
    
    实现需求: 8.1, 8.2, 8.3, 8.4, 8.5
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_status(self) -> SystemStatus:
        """
        获取系统状态。
        
        实现需求: 8.1
        
        Returns:
            SystemStatus: 包含运行中的 Workflow 数量和状态分布
        """
        pass
    
    def get_performance_metrics(
        self,
        time_range: str = "24h"
    ) -> PerformanceMetrics:
        """
        获取性能指标。
        
        实现需求: 8.2
        
        Returns:
            PerformanceMetrics: 各 Stage 的平均耗时和成功率
        """
        pass
    
    def get_cost_metrics(
        self,
        time_range: str = "24h"
    ) -> CostMetrics:
        """
        获取成本指标。
        
        实现需求: 8.3
        
        Returns:
            CostMetrics: Provider 调用次数和估算成本
        """
        pass
    
    def get_error_statistics(
        self,
        time_range: str = "24h"
    ) -> ErrorStatistics:
        """
        获取错误统计。
        
        实现需求: 8.4
        
        Returns:
            ErrorStatistics: 错误类型分布和失败率趋势
        """
        pass
    
    def get_resource_usage(self) -> ResourceUsage:
        """
        获取资源使用情况。
        
        实现需求: 8.5
        
        Returns:
            ResourceUsage: 存储空间使用和数据库连接数
        """
        pass
```

### Notification Service

```python
class NotificationService:
    """
    通知服务，发送导出完成通知和 Webhook 回调。
    
    职责：
    1. 发送用户通知
    2. 调用 Webhook
    3. 重试失败的通知
    4. 记录通知历史
    
    实现需求: 9.1, 9.2, 9.3, 9.4, 9.5
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_export_notification(
        self,
        user_id: UUID,
        export_bundle: ExportBundleModel,
        status: str
    ) -> None:
        """
        发送导出通知。
        
        实现需求: 9.1, 9.2
        
        Args:
            user_id: 用户 ID
            export_bundle: 导出包
            status: 状态 (completed, failed)
        """
        pass
    
    def call_webhook(
        self,
        webhook_url: str,
        export_bundle: ExportBundleModel,
        max_retries: int = 3
    ) -> bool:
        """
        调用 Webhook。
        
        实现需求: 9.3, 9.4, 9.5
        
        Args:
            webhook_url: Webhook URL
            export_bundle: 导出包
            max_retries: 最大重试次数
            
        Returns:
            是否成功
        """
        pass
```

## 数据模型

### ExportBundle 表结构

```python
class ExportBundleModel(Base):
    """
    导出包记录表。
    
    实现需求: 2.1, 2.2, 2.3, 2.4
    """
    __tablename__ = "export_bundles"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    episode_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("episodes.id", ondelete="CASCADE"))
    stage_task_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("stage_tasks.id", ondelete="SET NULL"), nullable=True)
    
    # 导出配置
    export_version: Mapped[int] = mapped_column(Integer, default=1)
    template_name: Mapped[str] = mapped_column(String(64))  # douyin, bilibili, youtube, custom
    config_jsonb: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {
    #   "resolution": [1920, 1080],
    #   "aspect_ratio": "16:9",
    #   "video_codec": "libx264",
    #   "audio_codec": "aac",
    #   "bitrate": "6M",
    #   "frame_rate": 30,
    #   "pixel_format": "yuv420p",
    #   "watermark": {
    #     "enabled": true,
    #     "type": "text",
    #     "content": "© 2024",
    #     "position": "bottom_right",
    #     "opacity": 0.7
    #   }
    # }
    
    # 导出结果
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, processing, completed, failed
    video_storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manifest_storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bundle_size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    video_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 资产清单
    asset_ids_jsonb: Mapped[list] = mapped_column(JSONB, default=list)  # 包含的所有资产 ID
    
    # 质量信息
    qa_report_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("qa_reports.id", ondelete="SET NULL"), nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # 错误信息
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 元数据
    metadata_jsonb: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {
    #   "export_duration_ms": 45000,
    #   "shots_count": 10,
    #   "assets_count": 25,
    #   "download_url": "https://...",
    #   "expires_at": "2024-12-31T23:59:59Z"
    # }
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
```

### TraceRecord 表结构

```python
class TraceRecordModel(Base):
    """
    追踪记录表。
    
    实现需求: 7.1, 7.2, 7.3
    """
    __tablename__ = "trace_records"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    episode_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("episodes.id", ondelete="CASCADE"))
    
    # 事件信息
    event_type: Mapped[str] = mapped_column(String(64))  # stage_execution, asset_generation, document_creation, transformation
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # 源和目标
    source_type: Mapped[str] = mapped_column(String(32))  # document, shot, asset, stage_task
    source_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    target_type: Mapped[str] = mapped_column(String(32))  # document, shot, asset, stage_task
    target_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    
    # 元数据
    metadata_jsonb: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {
    #   "stage_type": "image_render",
    #   "input_params": {...},
    #   "output_metrics": {...},
    #   "duration_ms": 5000
    # }
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### ExportConfig 数据类

```python
@dataclass
class ExportConfig:
    """
    导出配置。
    
    实现需求: 3.1, 3.2, 3.3, 3.4
    """
    resolution: Tuple[int, int]  # (width, height)
    aspect_ratio: str  # "16:9", "9:16", "4:3"
    video_codec: str  # "libx264", "libx265", "vp9"
    audio_codec: str  # "aac", "mp3", "opus"
    bitrate: str  # "4M", "6M", "8M"
    frame_rate: int  # 24, 30, 60
    pixel_format: str  # "yuv420p", "yuv444p"
    watermark: Optional[WatermarkConfig] = None
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        验证配置有效性。
        
        实现需求: 3.5
        """
        # 验证分辨率
        if self.resolution[0] <= 0 or self.resolution[1] <= 0:
            return False, "Invalid resolution"
        
        # 验证编码器
        valid_codecs = ["libx264", "libx265", "vp9"]
        if self.video_codec not in valid_codecs:
            return False, f"Invalid video codec: {self.video_codec}"
        
        # 验证帧率
        if self.frame_rate not in [24, 30, 60]:
            return False, f"Invalid frame rate: {self.frame_rate}"
        
        return True, None


@dataclass
class WatermarkConfig:
    """
    水印配置。
    
    实现需求: 10.1, 10.2, 10.3
    """
    enabled: bool
    type: str  # "text", "image"
    content: str  # 文字内容或图片路径
    position: str  # "top_left", "top_right", "bottom_left", "bottom_right", "center"
    opacity: float  # 0.0 - 1.0
    size: Optional[int] = None  # 字体大小或图片缩放百分比
```


### ExportManifest 数据类

```python
@dataclass
class ExportManifest:
    """
    导出清单文件。
    
    实现需求: 4.2, 4.3, 4.4
    """
    version: str  # 清单格式版本
    export_id: UUID
    episode_id: UUID
    project_id: UUID
    export_timestamp: datetime
    
    # 视频信息
    video: VideoInfo
    
    # 资产列表
    assets: List[AssetInfo]
    
    # QA 报告摘要
    qa_summary: Optional[QASummary]
    
    # 元数据
    metadata: dict
    
    def to_json(self) -> str:
        """
        序列化为 JSON 字符串。
        
        实现需求: 4.2
        """
        pass
    
    def verify_checksums(self, base_dir: str) -> Tuple[bool, List[str]]:
        """
        验证所有文件的校验和。
        
        实现需求: 4.5
        
        Returns:
            (is_valid, failed_files)
        """
        pass


@dataclass
class VideoInfo:
    """视频文件信息"""
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
    """资产文件信息"""
    asset_id: UUID
    asset_type: str  # keyframe, audio, subtitle
    filename: str
    storage_key: str
    size_bytes: int
    mime_type: str
    checksum_sha256: str
    shot_id: Optional[UUID] = None


@dataclass
class QASummary:
    """QA 报告摘要"""
    qa_report_id: UUID
    result: str  # passed, failed, warning
    score: float
    issue_count: int
    critical_issues: List[str]
```

## API 设计

### Export API 端点

```python
# POST /api/v1/episodes/{episode_id}/export
@router.post("/{episode_id}/export")
async def create_export(
    episode_id: UUID,
    request: CreateExportRequest,
    db: Session = Depends(get_db)
) -> CreateExportResponse:
    """
    创建导出任务。
    
    实现需求: 13.1
    
    Request Body:
    {
      "template_name": "douyin",  // 或 "bilibili", "youtube", "custom"
      "custom_config": {  // 仅当 template_name="custom" 时需要
        "resolution": [1920, 1080],
        "bitrate": "8M",
        ...
      },
      "watermark": {
        "enabled": true,
        "type": "text",
        "content": "© 2024",
        "position": "bottom_right",
        "opacity": 0.7
      },
      "force_export": false,  // 是否跳过 QA 检查
      "webhook_url": "https://example.com/webhook"  // 可选
    }
    
    Response:
    {
      "export_id": "uuid",
      "status": "pending",
      "message": "Export task created successfully"
    }
    """
    pass


# GET /api/v1/export/{export_id}
@router.get("/{export_id}")
async def get_export_status(
    export_id: UUID,
    db: Session = Depends(get_db)
) -> ExportStatusResponse:
    """
    获取导出任务状态。
    
    实现需求: 13.2
    
    Response:
    {
      "export_id": "uuid",
      "episode_id": "uuid",
      "status": "processing",  // pending, processing, completed, failed
      "progress": 65,  // 0-100
      "created_at": "2024-01-01T00:00:00Z",
      "completed_at": null,
      "download_url": null,
      "error_message": null
    }
    """
    pass


# GET /api/v1/export/history
@router.get("/history")
async def get_export_history(
    episode_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> ExportHistoryResponse:
    """
    获取导出历史。
    
    实现需求: 13.3
    
    Response:
    {
      "total": 100,
      "items": [
        {
          "export_id": "uuid",
          "episode_id": "uuid",
          "export_version": 1,
          "template_name": "douyin",
          "status": "completed",
          "bundle_size_bytes": 52428800,
          "video_duration_ms": 60000,
          "created_at": "2024-01-01T00:00:00Z",
          "completed_at": "2024-01-01T00:05:00Z",
          "download_url": "https://..."
        },
        ...
      ]
    }
    """
    pass


# GET /api/v1/export/{export_id}/download
@router.get("/{export_id}/download")
async def get_export_download_url(
    export_id: UUID,
    expires_in: int = 3600,
    db: Session = Depends(get_db)
) -> ExportDownloadResponse:
    """
    获取导出包下载链接。
    
    实现需求: 13.4
    
    Response:
    {
      "export_id": "uuid",
      "video_url": "https://...",
      "manifest_url": "https://...",
      "expires_at": "2024-01-01T01:00:00Z"
    }
    """
    pass


# DELETE /api/v1/export/{export_id}
@router.delete("/{export_id}")
async def delete_export(
    export_id: UUID,
    db: Session = Depends(get_db)
) -> DeleteExportResponse:
    """
    删除导出包。
    
    实现需求: 13.5
    
    Response:
    {
      "export_id": "uuid",
      "deleted": true,
      "message": "Export bundle deleted successfully"
    }
    """
    pass
```

### Trace API 端点

```python
# GET /api/v1/trace/episode/{episode_id}
@router.get("/episode/{episode_id}")
async def get_episode_trace(
    episode_id: UUID,
    db: Session = Depends(get_db)
) -> TraceGraphResponse:
    """
    获取 Episode 的完整追踪路径。
    
    实现需求: 7.1
    
    Response:
    {
      "episode_id": "uuid",
      "nodes": [
        {
          "id": "uuid",
          "type": "document",
          "name": "brief_draft",
          "created_at": "2024-01-01T00:00:00Z"
        },
        ...
      ],
      "edges": [
        {
          "source_id": "uuid",
          "target_id": "uuid",
          "event_type": "stage_execution",
          "timestamp": "2024-01-01T00:01:00Z"
        },
        ...
      ]
    }
    """
    pass


# GET /api/v1/trace/lineage/{target_type}/{target_id}
@router.get("/lineage/{target_type}/{target_id}")
async def get_lineage(
    target_type: str,
    target_id: UUID,
    direction: str = "backward",
    db: Session = Depends(get_db)
) -> LineageGraphResponse:
    """
    获取血缘关系。
    
    实现需求: 7.2, 7.3, 7.4
    
    Query Parameters:
    - direction: backward (上游), forward (下游), both (双向)
    
    Response:
    {
      "target": {
        "id": "uuid",
        "type": "asset",
        "name": "keyframe_shot_001.png"
      },
      "upstream": [
        {
          "id": "uuid",
          "type": "shot",
          "name": "Shot 001",
          "relationship": "generated_from"
        },
        ...
      ],
      "downstream": [
        {
          "id": "uuid",
          "type": "asset",
          "name": "preview.mp4",
          "relationship": "used_in"
        },
        ...
      ]
    }
    """
    pass
```

### Observability API 端点

```python
# GET /api/v1/observability/system-status
@router.get("/system-status")
async def get_system_status(
    db: Session = Depends(get_db)
) -> SystemStatusResponse:
    """
    获取系统状态。
    
    实现需求: 8.1
    
    Response:
    {
      "workflows": {
        "running": 5,
        "pending": 10,
        "completed": 100,
        "failed": 2
      },
      "stages": {
        "image_render": {"running": 3, "queued": 5},
        "tts": {"running": 2, "queued": 3},
        ...
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
    """
    pass


# GET /api/v1/observability/performance
@router.get("/performance")
async def get_performance_metrics(
    time_range: str = "24h",
    db: Session = Depends(get_db)
) -> PerformanceMetricsResponse:
    """
    获取性能指标。
    
    实现需求: 8.2
    
    Response:
    {
      "stages": [
        {
          "stage_type": "image_render",
          "avg_duration_ms": 5000,
          "success_rate": 0.95,
          "total_executions": 100
        },
        ...
      ],
      "time_range": "24h"
    }
    """
    pass


# GET /api/v1/observability/costs
@router.get("/costs")
async def get_cost_metrics(
    time_range: str = "24h",
    db: Session = Depends(get_db)
) -> CostMetricsResponse:
    """
    获取成本指标。
    
    实现需求: 8.3
    
    Response:
    {
      "providers": [
        {
          "provider_name": "stable_diffusion",
          "call_count": 100,
          "estimated_cost": 5.00,
          "currency": "USD"
        },
        ...
      ],
      "total_cost": 15.00,
      "time_range": "24h"
    }
    """
    pass


# GET /api/v1/observability/errors
@router.get("/errors")
async def get_error_statistics(
    time_range: str = "24h",
    db: Session = Depends(get_db)
) -> ErrorStatisticsResponse:
    """
    获取错误统计。
    
    实现需求: 8.4
    
    Response:
    {
      "error_types": [
        {
          "error_code": "PROVIDER_TIMEOUT",
          "count": 10,
          "percentage": 0.5
        },
        ...
      ],
      "failure_rate": 0.02,
      "time_range": "24h"
    }
    """
    pass


# GET /api/v1/observability/resources
@router.get("/resources")
async def get_resource_usage(
    db: Session = Depends(get_db)
) -> ResourceUsageResponse:
    """
    获取资源使用情况。
    
    实现需求: 8.5
    
    Response:
    {
      "storage": {
        "total_bytes": 10737418240,
        "used_bytes": 5368709120,
        "usage_percentage": 0.5
      },
      "database": {
        "active_connections": 10,
        "max_connections": 100
      },
      "timestamp": "2024-01-01T00:00:00Z"
    }
    """
    pass
```


## 正确性属性

*属性是系统在所有有效执行中应该保持的特征或行为，是人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: QA 阻止导出
*对于任何*QA 结果为 "failed" 且 severity 为 "critical" 的 Episode，不应该允许执行 Final Export（除非 force_export=true）
**验证需求**: 需求 5.1, 5.2, 5.4

### 属性 2: 导出配置有效性
*对于任何*导出请求，配置参数应该通过验证才能开始导出
**验证需求**: 需求 3.4, 3.5

### 属性 3: 主资产完整性
*对于任何*导出包，应该包含所有 Shot 的主资产（is_selected=true）
**验证需求**: 需求 1.2, 4.1

### 属性 4: 清单文件一致性
*对于任何*导出包，清单文件中列出的资产应该与实际包含的资产一致
**验证需求**: 需求 4.2, 4.3, 4.4

### 属性 5: 校验和验证
*对于任何*导出包中的文件，其校验和应该与清单文件中记录的一致
**验证需求**: 需求 4.5

### 属性 6: 导出版本递增
*对于任何*Episode 的新导出，export_version 应该大于之前的所有导出版本
**验证需求**: 需求 6.3

### 属性 7: Trace 完整性
*对于任何*完成的 Episode，应该能够追踪从 Brief 到 Final Export 的完整路径
**验证需求**: 需求 7.1, 7.5

### 属性 8: Lineage 双向性
*对于任何*数据产物，如果 A 是 B 的上游，则 B 应该是 A 的下游
**验证需求**: 需求 7.2

### 属性 9: 导出质量检查
*对于任何*成功的导出，视频应该可播放且时长与预期匹配
**验证需求**: 需求 5.5

### 属性 10: 通知可靠性
*对于任何*导出完成或失败，应该发送通知（最多重试 3 次）
**验证需求**: 需求 9.1, 9.2

### 属性 11: Webhook 重试幂等性
*对于任何*Webhook 调用，重试应该发送相同的数据
**验证需求**: 需求 9.4, 9.5

### 属性 12: 水印应用一致性
*对于任何*启用水印的导出，水印应该出现在视频的指定位置
**验证需求**: 需求 10.1, 10.2, 10.3, 10.4

## 错误处理

### QA 检查失败

**场景**: QA 报告显示 critical 问题

**处理**:
1. 阻止导出并返回清晰的错误信息
2. 列出所有 critical 问题
3. 提示用户修复问题或使用 force_export
4. 记录阻止原因

**实现需求**: 5.1, 5.2

### 导出配置无效

**场景**: 用户提供的导出配置参数无效

**处理**:
1. 验证所有配置参数
2. 返回具体的验证错误信息
3. 提供有效值的示例
4. 不创建导出任务

**实现需求**: 3.5

### FFmpeg 合成失败

**场景**: 视频合成过程中 FFmpeg 失败

**处理**:
1. 捕获 FFmpeg 错误输出
2. 保留临时文件用于调试
3. 记录详细的错误日志
4. 更新 ExportBundle 状态为 "failed"
5. 发送失败通知

**实现需求**: 14.2

### 存储上传失败

**场景**: 导出包上传到对象存储失败

**处理**:
1. 重试最多 3 次，使用指数退避
2. 如果全部失败，保留本地文件
3. 记录失败原因和重试历史
4. 更新 ExportBundle 状态为 "failed"
5. 允许用户手动重试

**实现需求**: 14.3

### 导出超时

**场景**: 导出过程超过预期时间

**处理**:
1. 设置合理的超时限制（如 30 分钟）
2. 超时后终止 FFmpeg 进程
3. 保存已完成的中间产物
4. 记录超时原因
5. 更新 ExportBundle 状态为 "failed"

**实现需求**: 14.4

### 质量检查失败

**场景**: 导出的视频无法播放或时长不匹配

**处理**:
1. 记录具体的质量问题
2. 不上传失败的视频
3. 保留临时文件用于调试
4. 更新 ExportBundle 状态为 "failed"
5. 提供详细的错误信息

**实现需求**: 5.5

### Webhook 调用失败

**场景**: Webhook URL 无法访问或返回错误

**处理**:
1. 重试最多 3 次，使用指数退避
2. 记录每次重试的响应
3. 如果全部失败，记录失败日志
4. 不影响导出任务的成功状态
5. 允许用户手动重新发送 Webhook

**实现需求**: 9.5

### 断点续传

**场景**: 导出过程中系统异常中断

**处理**:
1. 保存中间状态到数据库
2. 记录已完成的步骤
3. 支持从断点恢复
4. 不重复已完成的工作
5. 验证中间产物的完整性

**实现需求**: 14.1

### 数据一致性保护

**场景**: 导出过程中数据库操作失败

**处理**:
1. 使用数据库事务保护
2. 失败时回滚所有更改
3. 不创建不完整的 ExportBundle 记录
4. 记录异常堆栈
5. 清理临时文件

**实现需求**: 14.5

## 测试策略

### 单元测试

1. **Final Export Stage 测试**
   - 测试 QA 状态验证
   - 测试资产收集
   - 测试视频合成
   - 测试水印应用
   - 测试质量检查
   - 使用 Mock Provider 和 Storage

2. **Export Service 测试**
   - 测试导出配置验证
   - 测试模板加载
   - 测试 ExportBundle 创建
   - 测试清单文件生成
   - 测试导出历史查询

3. **Trace Service 测试**
   - 测试追踪事件记录
   - 测试 Lineage 查询
   - 测试完整追踪路径
   - 测试双向关系

4. **Observability Service 测试**
   - 测试系统状态查询
   - 测试性能指标聚合
   - 测试成本统计
   - 测试错误统计

5. **Notification Service 测试**
   - 测试通知发送
   - 测试 Webhook 调用
   - 测试重试逻辑
   - 使用 Mock HTTP 客户端

### 集成测试

1. **端到端导出流程测试**
   - 创建完整的测试数据
   - 执行 Final Export Stage
   - 验证导出包生成
   - 验证清单文件正确性
   - 验证视频可播放性
   - 验证通知发送

2. **多平台导出测试**
   - 测试抖音模板导出
   - 测试 B 站模板导出
   - 测试 YouTube 模板导出
   - 测试自定义配置导出
   - 验证输出符合平台规范

3. **Trace 和 Lineage 测试**
   - 创建完整的 Episode 数据
   - 记录所有追踪事件
   - 查询完整追踪路径
   - 验证 Lineage 关系正确性

4. **错误恢复测试**
   - 模拟 FFmpeg 失败
   - 模拟存储上传失败
   - 模拟系统中断
   - 验证断点续传
   - 验证数据一致性

### 性能测试

1. **导出性能测试**
   - 测试不同 Shot 数量的导出时间
   - 测试不同分辨率的导出时间
   - 测试并发导出性能
   - 验证硬件加速效果

2. **查询性能测试**
   - 测试导出历史查询性能
   - 测试 Trace 查询性能
   - 测试 Lineage 查询性能
   - 测试可观测性指标查询性能

3. **大规模测试**
   - 测试 100+ Shot 的导出
   - 测试长视频（60 分钟+）导出
   - 测试大量并发导出
   - 测试存储性能

### 样板项目验证

1. **创建样板项目**
   - 使用预定义的 Brief
   - 包含 10-15 个 Shot
   - 包含对白和旁白
   - 包含多个角色

2. **执行完整流程**
   - 从 Brief 到 Final Export
   - 验证所有 Stage 成功
   - 验证 QA 检查通过
   - 验证导出包生成

3. **验证产物质量**
   - 视频可播放
   - 音频清晰
   - 字幕同步
   - 画面质量符合要求

4. **验证可追溯性**
   - 查询完整追踪路径
   - 验证 Lineage 关系
   - 验证所有产物可追溯

**实现需求**: 12.1, 12.2, 12.3, 12.4, 12.5


## 性能考虑

### 导出性能优化

**目标**: 10 个 Shot 的视频在 5 分钟内完成导出

**优化策略**:
1. **硬件加速**: 使用 GPU 编码（NVENC, VideoToolbox）
2. **并行处理**: 并行下载资产和生成视频片段
3. **缓存优化**: 缓存常用的导出配置和模板
4. **资源池**: 复用 FFmpeg 进程和临时目录
5. **增量导出**: 只重新生成变更的部分

**实现需求**: 11.1, 11.2, 11.4

### 并发控制

**策略**:
- 限制同时进行的导出任务数量（默认 3 个）
- 使用队列管理导出请求
- 支持优先级调度
- 监控系统负载，动态调整并发数

**实现需求**: 11.3, 11.5

### 数据库优化

**索引策略**:
```sql
-- ExportBundle 索引
CREATE INDEX idx_export_bundles_episode ON export_bundles(episode_id, created_at DESC);
CREATE INDEX idx_export_bundles_project ON export_bundles(project_id, created_at DESC);
CREATE INDEX idx_export_bundles_status ON export_bundles(status, created_at DESC);

-- TraceRecord 索引
CREATE INDEX idx_trace_records_episode ON trace_records(episode_id, event_timestamp DESC);
CREATE INDEX idx_trace_records_source ON trace_records(source_type, source_id);
CREATE INDEX idx_trace_records_target ON trace_records(target_type, target_id);
```

### 存储优化

**策略**:
- 使用对象存储的多部分上传
- 压缩清单文件
- 定期清理过期的导出包
- 使用 CDN 加速下载

### 查询性能

**Trace 查询优化**:
- 使用图数据库或缓存 Lineage 关系
- 限制查询深度（默认最多 10 层）
- 使用分页返回大量结果
- 缓存常用的追踪路径

**可观测性查询优化**:
- 使用时间序列数据库存储指标
- 预聚合常用的统计数据
- 使用缓存减少数据库查询
- 异步更新仪表板数据

## 可扩展性

### 支持更多导出格式

**扩展点**:
- 添加新的导出模板
- 支持不同的视频编码器
- 支持不同的容器格式（MP4, WebM, MOV）
- 支持音频单独导出

**示例**:
```python
templates = {
    "tiktok": ExportConfig(
        resolution=(1080, 1920),
        aspect_ratio="9:16",
        video_codec="libx264",
        max_duration_ms=180000  # 3 分钟
    ),
    "instagram_reel": ExportConfig(
        resolution=(1080, 1920),
        aspect_ratio="9:16",
        video_codec="libx264",
        max_duration_ms=90000  # 90 秒
    ),
    "4k_youtube": ExportConfig(
        resolution=(3840, 2160),
        aspect_ratio="16:9",
        video_codec="libx265",
        bitrate="20M"
    )
}
```

### 支持更多水印类型

**扩展点**:
- 动态水印（时间戳、帧号）
- 多个水印
- 水印动画效果
- 条件水印（仅在特定 Shot 显示）

### 支持更多通知渠道

**扩展点**:
- 邮件通知
- 短信通知
- 企业微信/钉钉通知
- Slack 通知
- 自定义通知插件

### 支持批量导出

**扩展点**:
- 批量导出多个 Episode
- 批量应用相同配置
- 批量下载导出包
- 导出进度汇总

## 安全性

### 访问控制

**策略**:
- 验证用户对 Episode 的访问权限
- 限制导出包的下载权限
- 使用签名 URL 限制访问时间
- 记录所有访问日志

**实现**:
```python
def verify_export_access(user_id: UUID, export_id: UUID) -> bool:
    """验证用户是否有权访问导出包"""
    export_bundle = get_export_bundle(export_id)
    episode = get_episode(export_bundle.episode_id)
    project = get_project(episode.project_id)
    
    return user_id == project.owner_id or user_has_permission(user_id, project.id, "export.read")
```

### 数据保护

**策略**:
- 导出包使用加密存储
- 敏感信息（如水印文字）加密存储
- 定期清理过期的导出包
- 支持导出包的软删除和恢复

### 成本控制

**策略**:
- 限制单个用户的导出次数
- 限制导出包的存储时间
- 监控异常高成本的导出
- 实现预算告警

**实现**:
```python
class ExportQuota:
    """导出配额管理"""
    
    def check_quota(self, user_id: UUID) -> Tuple[bool, Optional[str]]:
        """检查用户是否还有导出配额"""
        # 检查今日导出次数
        today_exports = count_exports_today(user_id)
        if today_exports >= MAX_EXPORTS_PER_DAY:
            return False, f"Daily export limit reached: {MAX_EXPORTS_PER_DAY}"
        
        # 检查存储空间
        user_storage = get_user_storage_usage(user_id)
        if user_storage >= MAX_STORAGE_BYTES:
            return False, f"Storage limit reached: {MAX_STORAGE_BYTES} bytes"
        
        return True, None
```

### 输入验证

**策略**:
- 验证所有用户输入
- 防止路径遍历攻击
- 防止 SQL 注入
- 防止 XSS 攻击

**实现**:
```python
def validate_export_config(config: ExportConfig) -> Tuple[bool, Optional[str]]:
    """验证导出配置"""
    # 验证分辨率范围
    if config.resolution[0] > 7680 or config.resolution[1] > 4320:
        return False, "Resolution exceeds maximum (8K)"
    
    # 验证码率范围
    bitrate_value = int(config.bitrate.rstrip("M"))
    if bitrate_value > 50:
        return False, "Bitrate exceeds maximum (50M)"
    
    # 验证水印内容
    if config.watermark and config.watermark.type == "text":
        if len(config.watermark.content) > 100:
            return False, "Watermark text too long (max 100 characters)"
    
    return True, None
```

## Pilot 就绪检查

### 就绪检查清单

**实现需求**: 15.1, 15.2, 15.3, 15.4, 15.5

```python
class PilotReadinessChecker:
    """Pilot 就绪检查器"""
    
    def run_readiness_check(self) -> ReadinessReport:
        """
        执行完整的就绪检查。
        
        Returns:
            ReadinessReport: 就绪检查报告
        """
        report = ReadinessReport()
        
        # 1. 核心功能检查
        report.add_check("core_features", self._check_core_features())
        
        # 2. 数据库检查
        report.add_check("database", self._check_database())
        
        # 3. Provider 检查
        report.add_check("providers", self._check_providers())
        
        # 4. 存储检查
        report.add_check("storage", self._check_storage())
        
        # 5. 性能检查
        report.add_check("performance", self._check_performance())
        
        # 6. 安全检查
        report.add_check("security", self._check_security())
        
        # 生成总体评估
        report.generate_summary()
        
        return report
    
    def _check_core_features(self) -> CheckResult:
        """检查核心功能"""
        checks = []
        
        # 检查所有 Stage 是否可用
        for stage_type in STAGE_TYPES:
            try:
                stage = get_stage_instance(stage_type)
                checks.append((f"Stage: {stage_type}", True, None))
            except Exception as e:
                checks.append((f"Stage: {stage_type}", False, str(e)))
        
        # 检查导出功能
        try:
            export_service = ExportService(db, storage_service)
            templates = export_service.get_all_templates()
            checks.append(("Export templates", len(templates) > 0, None))
        except Exception as e:
            checks.append(("Export templates", False, str(e)))
        
        return CheckResult("Core Features", checks)
    
    def _check_database(self) -> CheckResult:
        """检查数据库"""
        checks = []
        
        # 检查所有必需的表
        required_tables = [
            "projects", "episodes", "workflow_runs", "stage_tasks",
            "documents", "shots", "assets", "qa_reports",
            "review_decisions", "export_bundles", "trace_records"
        ]
        
        for table in required_tables:
            exists = check_table_exists(table)
            checks.append((f"Table: {table}", exists, None if exists else "Table not found"))
        
        # 检查索引
        required_indexes = [
            "idx_export_bundles_episode",
            "idx_trace_records_episode",
            "idx_assets_shot_selected"
        ]
        
        for index in required_indexes:
            exists = check_index_exists(index)
            checks.append((f"Index: {index}", exists, None if exists else "Index not found"))
        
        return CheckResult("Database", checks)
    
    def _check_providers(self) -> CheckResult:
        """检查 Provider"""
        checks = []
        
        # 检查 LLM Provider
        try:
            llm_provider = get_llm_provider()
            response = llm_provider.test_connection()
            checks.append(("LLM Provider", response.success, response.error))
        except Exception as e:
            checks.append(("LLM Provider", False, str(e)))
        
        # 检查 Image Provider
        try:
            image_provider = get_image_provider()
            response = image_provider.test_connection()
            checks.append(("Image Provider", response.success, response.error))
        except Exception as e:
            checks.append(("Image Provider", False, str(e)))
        
        # 检查 TTS Provider
        try:
            tts_provider = get_tts_provider()
            response = tts_provider.test_connection()
            checks.append(("TTS Provider", response.success, response.error))
        except Exception as e:
            checks.append(("TTS Provider", False, str(e)))
        
        return CheckResult("Providers", checks)
    
    def _check_storage(self) -> CheckResult:
        """检查存储"""
        checks = []
        
        # 检查对象存储连接
        try:
            storage_service = get_storage_service()
            test_result = storage_service.test_connection()
            checks.append(("Object Storage", test_result.success, test_result.error))
        except Exception as e:
            checks.append(("Object Storage", False, str(e)))
        
        # 检查存储空间
        try:
            usage = storage_service.get_usage()
            has_space = usage.available_bytes > 10 * 1024 * 1024 * 1024  # 至少 10GB
            checks.append(("Storage Space", has_space, 
                          None if has_space else f"Only {usage.available_bytes} bytes available"))
        except Exception as e:
            checks.append(("Storage Space", False, str(e)))
        
        return CheckResult("Storage", checks)
    
    def _check_performance(self) -> CheckResult:
        """检查性能"""
        checks = []
        
        # 检查数据库响应时间
        start = time.time()
        try:
            db.execute("SELECT 1")
            duration_ms = (time.time() - start) * 1000
            is_fast = duration_ms < 100
            checks.append(("Database Response", is_fast, 
                          None if is_fast else f"Slow response: {duration_ms}ms"))
        except Exception as e:
            checks.append(("Database Response", False, str(e)))
        
        # 检查 FFmpeg 可用性
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                   capture_output=True, timeout=5)
            checks.append(("FFmpeg", result.returncode == 0, None))
        except Exception as e:
            checks.append(("FFmpeg", False, str(e)))
        
        return CheckResult("Performance", checks)
    
    def _check_security(self) -> CheckResult:
        """检查安全性"""
        checks = []
        
        # 检查环境变量
        required_env_vars = [
            "DATABASE_URL",
            "OBJECT_STORAGE_ENDPOINT",
            "OBJECT_STORAGE_ACCESS_KEY",
            "OBJECT_STORAGE_SECRET_KEY"
        ]
        
        for var in required_env_vars:
            exists = os.getenv(var) is not None
            checks.append((f"Env: {var}", exists, 
                          None if exists else "Environment variable not set"))
        
        # 检查 HTTPS
        storage_endpoint = os.getenv("OBJECT_STORAGE_ENDPOINT", "")
        uses_https = storage_endpoint.startswith("https://")
        checks.append(("HTTPS Storage", uses_https, 
                      None if uses_https else "Storage endpoint not using HTTPS"))
        
        return CheckResult("Security", checks)


@dataclass
class ReadinessReport:
    """就绪检查报告"""
    checks: Dict[str, CheckResult] = field(default_factory=dict)
    is_ready: bool = False
    summary: str = ""
    
    def add_check(self, category: str, result: CheckResult):
        """添加检查结果"""
        self.checks[category] = result
    
    def generate_summary(self):
        """生成总体评估"""
        total_checks = sum(len(result.checks) for result in self.checks.values())
        passed_checks = sum(
            sum(1 for check in result.checks if check[1])
            for result in self.checks.values()
        )
        
        self.is_ready = passed_checks == total_checks
        self.summary = f"Passed {passed_checks}/{total_checks} checks"
        
        if self.is_ready:
            self.summary += " - System is PILOT READY ✓"
        else:
            failed_categories = [
                category for category, result in self.checks.items()
                if not all(check[1] for check in result.checks)
            ]
            self.summary += f" - Failed categories: {', '.join(failed_categories)}"


@dataclass
class CheckResult:
    """单个类别的检查结果"""
    category: str
    checks: List[Tuple[str, bool, Optional[str]]]  # (name, passed, error_message)
```


## 数据库迁移

### Migration 007: Export Bundle 和 Trace

```sql
-- Migration 007: Final Export and Pilot Ready
-- 创建 export_bundles 表
CREATE TABLE export_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    stage_task_id UUID REFERENCES stage_tasks(id) ON DELETE SET NULL,
    
    -- 导出配置
    export_version INTEGER NOT NULL DEFAULT 1,
    template_name VARCHAR(64) NOT NULL,
    config_jsonb JSONB NOT NULL DEFAULT '{}',
    
    -- 导出结果
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    video_storage_key TEXT,
    manifest_storage_key TEXT,
    bundle_size_bytes BIGINT NOT NULL DEFAULT 0,
    video_duration_ms INTEGER,
    
    -- 资产清单
    asset_ids_jsonb JSONB NOT NULL DEFAULT '[]',
    
    -- 质量信息
    qa_report_id UUID REFERENCES qa_reports(id) ON DELETE SET NULL,
    quality_score NUMERIC(5, 2),
    
    -- 错误信息
    error_code VARCHAR(64),
    error_message TEXT,
    
    -- 元数据
    metadata_jsonb JSONB NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 创建 trace_records 表
CREATE TABLE trace_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    episode_id UUID NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    
    -- 事件信息
    event_type VARCHAR(64) NOT NULL,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 源和目标
    source_type VARCHAR(32) NOT NULL,
    source_id UUID NOT NULL,
    target_type VARCHAR(32) NOT NULL,
    target_id UUID NOT NULL,
    
    -- 元数据
    metadata_jsonb JSONB NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 创建索引
CREATE INDEX idx_export_bundles_episode ON export_bundles(episode_id, created_at DESC);
CREATE INDEX idx_export_bundles_project ON export_bundles(project_id, created_at DESC);
CREATE INDEX idx_export_bundles_status ON export_bundles(status, created_at DESC);

CREATE INDEX idx_trace_records_episode ON trace_records(episode_id, event_timestamp DESC);
CREATE INDEX idx_trace_records_source ON trace_records(source_type, source_id);
CREATE INDEX idx_trace_records_target ON trace_records(target_type, target_id);
CREATE INDEX idx_trace_records_event_type ON trace_records(event_type, event_timestamp DESC);

-- 添加 Episode 导出状态字段（如果不存在）
ALTER TABLE episodes ADD COLUMN IF NOT EXISTS last_export_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE episodes ADD COLUMN IF NOT EXISTS export_count INTEGER NOT NULL DEFAULT 0;

-- 添加注释
COMMENT ON TABLE export_bundles IS '导出包记录表，存储每次导出的配置和结果';
COMMENT ON TABLE trace_records IS '追踪记录表，记录数据流转和处理过程';
```

## 实现优先级

### 高优先级（本迭代必须完成）

1. **Final Export Stage 实现**
   - QA 状态验证
   - 高分辨率视频合成
   - 质量检查
   - ExportBundle 记录创建
   - 实现需求: 1.1-1.5, 5.1-5.5

2. **Export Service 实现**
   - 导出配置管理
   - 导出模板（抖音、B站、YouTube）
   - 清单文件生成
   - 导出历史查询
   - 实现需求: 2.1-2.5, 3.1-3.5, 4.1-4.5, 6.1-6.5

3. **Export API 端点**
   - POST /api/v1/episodes/{episode_id}/export
   - GET /api/v1/export/{export_id}
   - GET /api/v1/export/history
   - GET /api/v1/export/{export_id}/download
   - DELETE /api/v1/export/{export_id}
   - 实现需求: 13.1-13.5

4. **数据库迁移**
   - 创建 export_bundles 表
   - 创建 trace_records 表
   - 创建必要的索引
   - 实现需求: 2.1, 7.1

5. **样板项目验证**
   - 创建样板项目
   - 执行完整流程
   - 验证产物质量
   - 实现需求: 12.1-12.5

### 中优先级（本迭代尽量完成）

1. **Trace Service 实现**
   - 追踪事件记录
   - Lineage 查询
   - 完整追踪路径
   - 实现需求: 7.1-7.5

2. **Trace API 端点**
   - GET /api/v1/trace/episode/{episode_id}
   - GET /api/v1/trace/lineage/{target_type}/{target_id}
   - 实现需求: 7.1-7.4

3. **Notification Service 实现**
   - 导出完成通知
   - Webhook 回调
   - 重试机制
   - 实现需求: 9.1-9.5

4. **水印功能**
   - 文字水印
   - 图片水印
   - 位置和透明度配置
   - 实现需求: 10.1-10.4

5. **错误恢复机制**
   - 断点续传
   - 重试逻辑
   - 数据一致性保护
   - 实现需求: 14.1-14.5

### 低优先级（可推迟到后续迭代）

1. **Observability Service 实现**
   - 系统状态查询
   - 性能指标聚合
   - 成本统计
   - 错误统计
   - 资源使用监控
   - 实现需求: 8.1-8.5

2. **Observability API 端点**
   - GET /api/v1/observability/system-status
   - GET /api/v1/observability/performance
   - GET /api/v1/observability/costs
   - GET /api/v1/observability/errors
   - GET /api/v1/observability/resources
   - 实现需求: 8.1-8.5

3. **性能优化**
   - 硬件加速
   - 并行处理优化
   - 缓存策略
   - 实现需求: 11.1-11.5

4. **高级水印功能**
   - 动态水印
   - 多个水印
   - 水印动画
   - 实现需求: 10.5（扩展）

5. **批量导出功能**
   - 批量导出多个 Episode
   - 批量配置
   - 批量下载
   - 实现需求: 扩展功能

## 实现路线图

### Week 1: 核心导出功能

**目标**: 实现基础的 Final Export Stage 和 Export Service

**任务**:
1. 创建数据库迁移（export_bundles 表）
2. 实现 ExportBundleModel 和 Repository
3. 实现 Export Service 基础功能
4. 实现导出配置和模板
5. 实现 Final Export Stage 基础流程
6. 单元测试

### Week 2: API 和集成

**目标**: 实现 Export API 端点和端到端集成

**任务**:
1. 实现 Export API 端点
2. 实现清单文件生成
3. 实现质量检查
4. 集成 QA 状态验证
5. 集成测试
6. 修复 Bug

### Week 3: Trace 和通知

**目标**: 实现 Trace Service 和 Notification Service

**任务**:
1. 创建数据库迁移（trace_records 表）
2. 实现 TraceRecordModel 和 Repository
3. 实现 Trace Service
4. 实现 Trace API 端点
5. 实现 Notification Service
6. 实现 Webhook 回调

### Week 4: 样板项目和 Pilot 就绪

**目标**: 验证系统完整性，确保 Pilot 就绪

**任务**:
1. 创建样板项目
2. 执行完整流程验证
3. 实现 Pilot 就绪检查
4. 性能测试和优化
5. 文档完善
6. 准备 Pilot 发布

## 成功标准

### 功能完整性

- ✓ 所有高优先级功能实现并测试通过
- ✓ 样板项目可以完整运行
- ✓ 导出的视频符合质量标准
- ✓ API 端点正常工作
- ✓ 错误处理健壮

### 性能指标

- ✓ 10 个 Shot 的视频在 5 分钟内完成导出
- ✓ 导出历史查询响应时间 < 500ms
- ✓ Trace 查询响应时间 < 1s
- ✓ 系统支持 3 个并发导出任务

### 质量标准

- ✓ 单元测试覆盖率 > 80%
- ✓ 集成测试覆盖核心流程
- ✓ 所有 API 端点有文档
- ✓ 错误信息清晰易懂
- ✓ 日志记录完整

### Pilot 就绪

- ✓ Pilot 就绪检查全部通过
- ✓ 数据库迁移成功
- ✓ Provider 连接正常
- ✓ 存储服务可用
- ✓ 安全检查通过

## 风险和缓解

### 风险 1: FFmpeg 性能不足

**影响**: 导出时间过长，影响用户体验

**缓解措施**:
- 使用硬件加速（GPU 编码）
- 优化 FFmpeg 参数
- 实现并行处理
- 提供进度反馈

### 风险 2: 存储成本过高

**影响**: 运营成本增加

**缓解措施**:
- 实现导出包过期清理
- 压缩清单文件
- 使用对象存储的生命周期策略
- 监控和告警

### 风险 3: Trace 数据量过大

**影响**: 数据库性能下降

**缓解措施**:
- 定期归档旧数据
- 使用分区表
- 优化索引
- 限制查询深度

### 风险 4: 导出失败率高

**影响**: 用户体验差，系统可靠性低

**缓解措施**:
- 实现健壮的错误处理
- 实现断点续传
- 提供详细的错误信息
- 实现自动重试

### 风险 5: Pilot 测试发现重大问题

**影响**: 延迟发布时间

**缓解措施**:
- 充分的单元测试和集成测试
- 样板项目验证
- 提前进行内部测试
- 准备快速修复流程

## 总结

本设计文档详细描述了 Final Export 与 Pilot Ready 强化迭代的完整设计，包括：

1. **架构设计**: 清晰的组件关系和数据流
2. **组件接口**: 详细的类和方法定义
3. **数据模型**: 完整的数据库表结构
4. **API 设计**: RESTful API 端点规范
5. **正确性属性**: 可验证的系统属性
6. **错误处理**: 健壮的错误处理策略
7. **测试策略**: 全面的测试计划
8. **性能考虑**: 性能优化策略
9. **可扩展性**: 未来扩展点
10. **安全性**: 安全措施和访问控制
11. **Pilot 就绪**: 完整的就绪检查
12. **实现优先级**: 清晰的实现路线图

通过本迭代的实现，系统将从"能生成预览"升级为"能交付成品"，并具备完整的可追溯性和可观测性，为进入 Pilot 测试阶段做好准备。
