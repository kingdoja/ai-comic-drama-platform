# Iteration 6: Final Export 与 Pilot Ready 强化 - 任务列表

## 概述

本任务列表将 Final Export 与 Pilot Ready 强化的需求和设计转化为可执行的实现任务。任务按照依赖关系和优先级组织，确保系统能够从"能生成预览"升级为"能交付成品"。

## 任务组织

- **阶段 1**: 数据库迁移和基础模型
- **阶段 2**: Export Service 核心功能
- **阶段 3**: Final Export Stage 实现
- **阶段 4**: Export API 端点
- **阶段 5**: Trace Service 实现
- **阶段 6**: Notification Service 实现
- **阶段 7**: 水印功能
- **阶段 8**: 错误恢复和健壮性
- **阶段 9**: 样板项目验证
- **阶段 10**: Pilot 就绪检查
- **阶段 11**: Observability Service（低优先级）
- **阶段 12**: 性能优化（低优先级）

---

- [x] 阶段 1: 数据库迁移和基础模型
  - [x] 任务 1.1: 创建数据库迁移文件
    **描述**: 创建 Migration 007，包含 export_bundles 和 trace_records 表
  
    **验收标准**:
    - 创建 `infra/migrations/007_final_export_pilot_ready.sql`
    - 包含 export_bundles 表定义
    - 包含 trace_records 表定义
    - 包含所有必要的索引
    - 包含 episodes 表的新字段（last_export_at, export_count）
    - SQL 语法正确，可以成功执行
  
    **实现需求**: 需求 2.1, 7.1
  
    **文件**:
    - `infra/migrations/007_final_export_pilot_ready.sql` (新建)
  
    ---
  
  
  - [x] 任务 1.2: 创建 ExportBundle 数据模型
    **描述**: 在 `app/db/models.py` 中创建 ExportBundleModel
  
    **验收标准**:
    - 定义 ExportBundleModel 类，继承 Base
    - 包含所有字段：id, project_id, episode_id, stage_task_id, export_version, template_name, config_jsonb, status, video_storage_key, manifest_storage_key, bundle_size_bytes, video_duration_ms, asset_ids_jsonb, qa_report_id, quality_score, error_code, error_message, metadata_jsonb, created_at, completed_at
    - 使用正确的类型注解和 mapped_column
    - 定义外键关系
    - 添加表注释
  
    **实现需求**: 需求 2.1, 2.2, 2.3, 2.4
  
    **文件**:
    - `apps/api/app/db/models.py` (修改)
  
    ---
  
  
  - [x] 任务 1.3: 创建 TraceRecord 数据模型
    **描述**: 在 `app/db/models.py` 中创建 TraceRecordModel
  
    **验收标准**:
    - 定义 TraceRecordModel 类，继承 Base
    - 包含所有字段：id, project_id, episode_id, event_type, event_timestamp, source_type, source_id, target_type, target_id, metadata_jsonb, created_at
    - 使用正确的类型注解和 mapped_column
    - 定义外键关系
    - 添加表注释
  
    **实现需求**: 需求 7.1, 7.2, 7.3
  
    **文件**:
    - `apps/api/app/db/models.py` (修改)
  
    ---
  
  
  - [x] 任务 1.4: 创建 ExportBundle Repository
    **描述**: 创建 ExportBundleRepository 用于数据库操作
  
    **验收标准**:
    - 创建 `apps/api/app/repositories/export_bundle_repository.py`
    - 实现 create() 方法
    - 实现 get_by_id() 方法
    - 实现 get_by_episode() 方法
    - 实现 get_by_project() 方法
    - 实现 get_history() 方法（支持分页和过滤）
    - 实现 update_status() 方法
    - 实现 delete() 方法
    - 所有方法包含类型注解和文档字符串
  
    **实现需求**: 需求 2.1, 2.2, 2.4, 2.5, 6.1, 6.2, 6.5
  
    **文件**:
    - `apps/api/app/repositories/export_bundle_repository.py` (新建)
  
    ---
  
  
  - [x] 任务 1.5: 创建 TraceRecord Repository
    **描述**: 创建 TraceRecordRepository 用于追踪记录操作
  
    **验收标准**:
    - 创建 `apps/api/app/repositories/trace_record_repository.py`
    - 实现 create() 方法
    - 实现 get_by_episode() 方法
    - 实现 get_by_source() 方法
    - 实现 get_by_target() 方法
    - 实现 get_lineage() 方法（支持上游、下游、双向查询）
    - 所有方法包含类型注解和文档字符串
  
    **实现需求**: 需求 7.1, 7.2, 7.3, 7.4
  
    **文件**:
    - `apps/api/app/repositories/trace_record_repository.py` (新建)
  
    ---
  
  
  - [x] 任务 1.6: 创建导出配置数据类
    **描述**: 创建 ExportConfig, WatermarkConfig, ExportManifest 等数据类
  
    **验收标准**:
    - 创建 `apps/api/app/schemas/export.py`
    - 定义 ExportConfig 数据类，包含 resolution, aspect_ratio, video_codec, audio_codec, bitrate, frame_rate, pixel_format, watermark
    - 实现 ExportConfig.validate() 方法
    - 定义 WatermarkConfig 数据类
    - 定义 ExportManifest 数据类
    - 定义 VideoInfo, AssetInfo, QASummary 数据类
    - 实现 ExportManifest.to_json() 方法
    - 实现 ExportManifest.verify_checksums() 方法
    - 所有类包含类型注解和文档字符串
  
    **实现需求**: 需求 3.1, 3.2, 3.3, 3.4, 3.5, 4.2, 4.3, 4.4, 4.5, 10.1, 10.2, 10.3
  
    **文件**:
    - `apps/api/app/schemas/export.py` (新建)
  
    ---
  
  

- [ ] 阶段 2: Export Service 核心功能
  - [x] 任务 2.1: 创建 Export Service 基础结构
    **描述**: 创建 ExportService 类和基础方法
  
    **验收标准**:
    - 创建 `apps/api/app/services/export_service.py`
    - 定义 ExportService 类
    - 实现 __init__() 方法，接收 db 和 storage_service
    - 定义导出模板常量（douyin, bilibili, youtube）
    - 添加类文档字符串
  
    **实现需求**: 需求 2.1, 3.1
  
    **文件**:
    - `apps/api/app/services/export_service.py` (新建)
  
    ---
  
  
  - [ ] 任务 2.2: 实现导出模板管理
    **描述**: 实现 get_export_template() 和相关方法
  
    **验收标准**:
    - 实现 get_export_template(template_name) 方法
    - 支持 "douyin" 模板（1080x1920, 9:16, 4M bitrate）
    - 支持 "bilibili" 模板（1920x1080, 16:9, 6M bitrate）
    - 支持 "youtube" 模板（1920x1080, 16:9, 8M bitrate）
    - 实现 get_all_templates() 方法
    - 实现 validate_custom_config() 方法
    - 模板不存在时返回 None
    - 包含单元测试
  
    **实现需求**: 需求 3.1, 3.2, 3.3, 3.4, 3.5
  
    **文件**:
    - `apps/api/app/services/export_service.py` (修改)
    - `apps/api/tests/unit/test_export_service.py` (新建)
  
    ---
  
  
  - [ ] 任务 2.3: 实现 ExportBundle 创建
    **描述**: 实现 create_export_bundle() 方法
  
    **验收标准**:
    - 实现 create_export_bundle() 方法
    - 接收 episode_id, project_id, export_config, video_asset, manifest 参数
    - 自动计算 export_version（查询该 Episode 的最大版本号 + 1）
    - 创建 ExportBundle 记录
    - 保存导出配置到 config_jsonb
    - 保存资产 ID 列表到 asset_ids_jsonb
    - 返回创建的 ExportBundleModel
    - 包含单元测试
  
    **实现需求**: 需求 2.1, 2.2, 2.3, 6.3
  
    **文件**:
    - `apps/api/app/services/export_service.py` (修改)
    - `apps/api/tests/unit/test_export_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 2.4: 实现清单文件生成
    **描述**: 实现 generate_manifest() 方法
  
    **验收标准**:
    - 实现 generate_manifest() 方法
    - 接收 episode_id, video_asset, all_assets, qa_report 参数
    - 生成 ExportManifest 对象
    - 包含视频信息（文件名、大小、时长、分辨率、编码、校验和）
    - 包含所有资产信息（asset_id, type, filename, size, mime_type, checksum）
    - 包含 QA 报告摘要（如果有）
    - 计算所有文件的 SHA256 校验和
    - 返回 ExportManifest 对象
    - 包含单元测试
  
    **实现需求**: 需求 4.2, 4.3, 4.4, 4.5
  
    **文件**:
    - `apps/api/app/services/export_service.py` (修改)
    - `apps/api/tests/unit/test_export_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 2.5: 实现导出历史查询
    **描述**: 实现 get_export_history() 方法
  
    **验收标准**:
    - 实现 get_export_history() 方法
    - 支持按 episode_id 过滤
    - 支持按 project_id 过滤
    - 支持分页（limit, offset）
    - 按 created_at 倒序排序
    - 返回 ExportBundle 列表
    - 包含单元测试
  
    **实现需求**: 需求 6.1, 6.2
  
    **文件**:
    - `apps/api/app/services/export_service.py` (修改)
    - `apps/api/tests/unit/test_export_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 2.6: 实现导出包删除
    **描述**: 实现 delete_export_bundle() 方法
  
    **验收标准**:
    - 实现 delete_export_bundle() 方法
    - 接收 export_bundle_id 参数
    - 从对象存储删除视频文件
    - 从对象存储删除清单文件
    - 从数据库删除 ExportBundle 记录
    - 使用事务确保一致性
    - 返回是否成功
    - 包含单元测试
  
    **实现需求**: 需求 6.5
  
    **文件**:
    - `apps/api/app/services/export_service.py` (修改)
    - `apps/api/tests/unit/test_export_service.py` (修改)
  
    ---
  
  

- [ ] 阶段 3: Final Export Stage 实现
  - [ ] 任务 3.1: 创建 Final Export Stage 基础结构
    **描述**: 创建 FinalExportStage 类和基础方法
  
    **验收标准**:
    - 创建 `apps/api/app/services/final_export_stage.py`
    - 定义 FinalExportStage 类
    - 实现 __init__() 方法，接收 db, storage_service, export_service, qa_repo, notification_service
    - 定义 execute() 方法签名
    - 添加类文档字符串
  
    **实现需求**: 需求 1.1
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (新建)
  
    ---
  
  
  - [ ] 任务 3.2: 实现 QA 状态验证
    **描述**: 实现 _verify_qa_status() 方法
  
    **验收标准**:
    - 实现 _verify_qa_status() 方法
    - 查询 Episode 的最新 QA 报告
    - 检查是否有 result="failed" 且 severity="critical" 的报告
    - 如果有 critical 问题，返回 (False, error_message)
    - 如果没有问题或只有 warning，返回 (True, None)
    - 包含单元测试
  
    **实现需求**: 需求 5.1, 5.2, 5.3
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (新建)
  
    ---
  
  
  - [ ] 任务 3.3: 实现主资产收集
    **描述**: 实现 _collect_primary_assets() 方法
  
    **验收标准**:
    - 实现 _collect_primary_assets() 方法
    - 查询 Episode 的所有 Shot
    - 对每个 Shot，查询 is_selected=true 的关键帧资产
    - 对每个 Shot，查询 is_selected=true 的音频资产
    - 查询 Episode 的字幕资产（如果有）
    - 按 Shot 顺序组织资产
    - 返回 List[ShotAssets] 和 subtitle_asset
    - 包含单元测试
  
    **实现需求**: 需求 1.2, 4.1
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 3.4: 实现高分辨率视频合成
    **描述**: 实现 _compose_high_resolution_video() 方法
  
    **验收标准**:
    - 实现 _compose_high_resolution_video() 方法
    - 接收 shot_assets_list, subtitle_asset, temp_dir, output_path, export_config 参数
    - 从对象存储下载所有资产到临时目录
    - 使用 FFmpeg 合成视频
    - 支持配置的分辨率（1080p, 1080x1920, 2K, 4K）
    - 支持配置的编码器（libx264, libx265, vp9）
    - 支持配置的码率和帧率
    - 如果有字幕，嵌入字幕
    - 返回视频时长（毫秒）
    - 包含单元测试（使用 Mock FFmpeg）
  
    **实现需求**: 需求 1.1, 3.1, 3.2, 3.3, 3.4
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 3.5: 实现质量检查
    **描述**: 实现 _quality_check() 方法
  
    **验收标准**:
    - 实现 _quality_check() 方法
    - 接收 video_path, expected_duration_ms 参数
    - 检查文件是否存在且可读
    - 使用 FFprobe 检查视频可播放性
    - 检查视频时长是否与预期匹配（允许 ±5% 误差）
    - 检查编码格式是否正确
    - 如果检查通过，返回 (True, None)
    - 如果检查失败，返回 (False, error_message)
    - 包含单元测试
  
    **实现需求**: 需求 5.5
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 3.6: 实现 Final Export Stage 主流程
    **描述**: 实现 execute() 方法的完整流程
  
    **验收标准**:
    - 实现 execute() 方法
    - 步骤 1: 验证 QA 状态（除非 force_export=true）
    - 步骤 2: 收集主资产
    - 步骤 3: 创建临时目录
    - 步骤 4: 合成高分辨率视频
    - 步骤 5: 应用水印（如果配置了）
    - 步骤 6: 质量检查
    - 步骤 7: 上传视频到对象存储
    - 步骤 8: 生成清单文件
    - 步骤 9: 上传清单文件到对象存储
    - 步骤 10: 创建 ExportBundle 记录
    - 步骤 11: 发送通知
    - 步骤 12: 更新 Episode 状态（last_export_at, export_count）
    - 步骤 13: 清理临时文件
    - 使用 try-finally 确保临时文件被清理
    - 失败时记录详细错误信息
    - 返回 FinalExportResult
    - 包含集成测试
  
    **实现需求**: 需求 1.1, 1.2, 1.3, 1.4, 1.5
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  

- [ ] 阶段 4: Export API 端点
  - [ ] 任务 4.1: 创建 Export API 路由文件
    **描述**: 创建 export.py 路由文件和基础结构
  
    **验收标准**:
    - 创建 `apps/api/app/api/routes/export.py`
    - 定义 APIRouter
    - 导入必要的依赖
    - 添加路由文档字符串
  
    **实现需求**: 需求 13.1
  
    **文件**:
    - `apps/api/app/api/routes/export.py` (新建)
  
    ---
  
  
  - [ ] 任务 4.2: 实现创建导出端点
    **描述**: 实现 POST /api/v1/episodes/{episode_id}/export
  
    **验收标准**:
    - 实现 create_export() 端点
    - 接收 CreateExportRequest（template_name, custom_config, watermark, force_export, webhook_url）
    - 验证 Episode 存在
    - 验证用户权限
    - 加载或验证导出配置
    - 创建 ExportBundle 记录（状态为 "pending"）
    - 异步触发 Final Export Stage 执行
    - 返回 CreateExportResponse（export_id, status, message）
    - 包含 API 测试
  
    **实现需求**: 需求 13.1
  
    **文件**:
    - `apps/api/app/api/routes/export.py` (修改)
    - `apps/api/app/schemas/export.py` (修改，添加 Request/Response 类)
    - `apps/api/tests/unit/test_export_api.py` (新建)
  
    ---
  
  
  - [ ] 任务 4.3: 实现获取导出状态端点
    **描述**: 实现 GET /api/v1/export/{export_id}
  
    **验收标准**:
    - 实现 get_export_status() 端点
    - 查询 ExportBundle 记录
    - 验证用户权限
    - 计算进度百分比（基于状态）
    - 返回 ExportStatusResponse（export_id, episode_id, status, progress, created_at, completed_at, download_url, error_message）
    - 如果导出不存在，返回 404
    - 包含 API 测试
  
    **实现需求**: 需求 13.2
  
    **文件**:
    - `apps/api/app/api/routes/export.py` (修改)
    - `apps/api/app/schemas/export.py` (修改)
    - `apps/api/tests/unit/test_export_api.py` (修改)
  
    ---
  
  
  - [ ] 任务 4.4: 实现获取导出历史端点
    **描述**: 实现 GET /api/v1/export/history
  
    **验收标准**:
    - 实现 get_export_history() 端点
    - 支持 episode_id 查询参数（可选）
    - 支持 project_id 查询参数（可选）
    - 支持 limit 和 offset 分页参数
    - 验证用户权限
    - 调用 ExportService.get_export_history()
    - 返回 ExportHistoryResponse（total, items）
    - 包含 API 测试
  
    **实现需求**: 需求 13.3
  
    **文件**:
    - `apps/api/app/api/routes/export.py` (修改)
    - `apps/api/app/schemas/export.py` (修改)
    - `apps/api/tests/unit/test_export_api.py` (修改)
  
    ---
  
  
  - [ ] 任务 4.5: 实现获取下载链接端点
    **描述**: 实现 GET /api/v1/export/{export_id}/download
  
    **验收标准**:
    - 实现 get_export_download_url() 端点
    - 查询 ExportBundle 记录
    - 验证用户权限
    - 验证导出状态为 "completed"
    - 生成视频文件的签名 URL（默认 1 小时有效期）
    - 生成清单文件的签名 URL
    - 返回 ExportDownloadResponse（export_id, video_url, manifest_url, expires_at）
    - 如果导出未完成，返回 400
    - 包含 API 测试
  
    **实现需求**: 需求 13.4
  
    **文件**:
    - `apps/api/app/api/routes/export.py` (修改)
    - `apps/api/app/schemas/export.py` (修改)
    - `apps/api/tests/unit/test_export_api.py` (修改)
  
    ---
  
  
  - [ ] 任务 4.6: 实现删除导出端点
    **描述**: 实现 DELETE /api/v1/export/{export_id}
  
    **验收标准**:
    - 实现 delete_export() 端点
    - 查询 ExportBundle 记录
    - 验证用户权限
    - 调用 ExportService.delete_export_bundle()
    - 返回 DeleteExportResponse（export_id, deleted, message）
    - 如果导出不存在，返回 404
    - 包含 API 测试
  
    **实现需求**: 需求 13.5
  
    **文件**:
    - `apps/api/app/api/routes/export.py` (修改)
    - `apps/api/app/schemas/export.py` (修改)
    - `apps/api/tests/unit/test_export_api.py` (修改)
  
    ---
  
  
  - [ ] 任务 4.7: 注册 Export 路由
    **描述**: 将 Export 路由注册到主应用
  
    **验收标准**:
    - 在 `apps/api/app/api/routes/__init__.py` 中导入 export router
    - 在主应用中注册 export router，前缀为 "/api/v1/export"
    - 验证所有端点可访问
  
    **实现需求**: 需求 13.1-13.5
  
    **文件**:
    - `apps/api/app/api/routes/__init__.py` (修改)
    - `apps/api/app/main.py` (修改)
  
    ---
  
  

- [ ] 阶段 5: Trace Service 实现
  - [ ] 任务 5.1: 创建 Trace Service 基础结构
    **描述**: 创建 TraceService 类和基础方法
  
    **验收标准**:
    - 创建 `apps/api/app/services/trace_service.py`
    - 定义 TraceService 类
    - 实现 __init__() 方法，接收 db
    - 添加类文档字符串
  
    **实现需求**: 需求 7.1
  
    **文件**:
    - `apps/api/app/services/trace_service.py` (新建)
  
    ---
  
  
  - [ ] 任务 5.2: 实现追踪事件记录
    **描述**: 实现 record_trace_event() 方法
  
    **验收标准**:
    - 实现 record_trace_event() 方法
    - 接收 event_type, source_type, source_id, target_type, target_id, metadata 参数
    - 创建 TraceRecord 记录
    - 自动设置 event_timestamp
    - 返回创建的 TraceRecordModel
    - 包含单元测试
  
    **实现需求**: 需求 7.1
  
    **文件**:
    - `apps/api/app/services/trace_service.py` (修改)
    - `apps/api/tests/unit/test_trace_service.py` (新建)
  
    ---
  
  
  - [ ] 任务 5.3: 实现 Lineage 查询
    **描述**: 实现 get_lineage() 方法
  
    **验收标准**:
    - 实现 get_lineage() 方法
    - 接收 target_type, target_id, direction 参数
    - 支持 direction="backward"（查询上游依赖）
    - 支持 direction="forward"（查询下游产物）
    - 支持 direction="both"（查询双向关系）
    - 递归查询，最多 10 层深度
    - 返回 LineageGraph 对象
    - 包含单元测试
  
    **实现需求**: 需求 7.2, 7.3, 7.4
  
    **文件**:
    - `apps/api/app/services/trace_service.py` (修改)
    - `apps/api/app/schemas/trace.py` (新建，定义 LineageGraph 等数据类)
    - `apps/api/tests/unit/test_trace_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 5.4: 实现完整追踪路径查询
    **描述**: 实现 get_full_trace() 方法
  
    **验收标准**:
    - 实现 get_full_trace() 方法
    - 接收 episode_id 参数
    - 查询该 Episode 的所有 TraceRecord
    - 构建完整的追踪图（nodes 和 edges）
    - 按时间顺序组织
    - 返回 TraceGraph 对象
    - 包含单元测试
  
    **实现需求**: 需求 7.1, 7.5
  
    **文件**:
    - `apps/api/app/services/trace_service.py` (修改)
    - `apps/api/app/schemas/trace.py` (修改)
    - `apps/api/tests/unit/test_trace_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 5.5: 创建 Trace API 路由文件
    **描述**: 创建 trace.py 路由文件
  
    **验收标准**:
    - 创建 `apps/api/app/api/routes/trace.py`
    - 定义 APIRouter
    - 导入必要的依赖
    - 添加路由文档字符串
  
    **实现需求**: 需求 7.1
  
    **文件**:
    - `apps/api/app/api/routes/trace.py` (新建)
  
    ---
  
  
  - [ ] 任务 5.6: 实现获取 Episode 追踪端点
    **描述**: 实现 GET /api/v1/trace/episode/{episode_id}
  
    **验收标准**:
    - 实现 get_episode_trace() 端点
    - 验证 Episode 存在
    - 验证用户权限
    - 调用 TraceService.get_full_trace()
    - 返回 TraceGraphResponse（episode_id, nodes, edges）
    - 包含 API 测试
  
    **实现需求**: 需求 7.1
  
    **文件**:
    - `apps/api/app/api/routes/trace.py` (修改)
    - `apps/api/app/schemas/trace.py` (修改)
    - `apps/api/tests/unit/test_trace_api.py` (新建)
  
    ---
  
  
  - [ ] 任务 5.7: 实现获取 Lineage 端点
    **描述**: 实现 GET /api/v1/trace/lineage/{target_type}/{target_id}
  
    **验收标准**:
    - 实现 get_lineage() 端点
    - 支持 direction 查询参数（默认 "backward"）
    - 验证 target 存在
    - 验证用户权限
    - 调用 TraceService.get_lineage()
    - 返回 LineageGraphResponse（target, upstream, downstream）
    - 包含 API 测试
  
    **实现需求**: 需求 7.2, 7.3, 7.4
  
    **文件**:
    - `apps/api/app/api/routes/trace.py` (修改)
    - `apps/api/app/schemas/trace.py` (修改)
    - `apps/api/tests/unit/test_trace_api.py` (修改)
  
    ---
  
  
  - [ ] 任务 5.8: 注册 Trace 路由
    **描述**: 将 Trace 路由注册到主应用
  
    **验收标准**:
    - 在主应用中注册 trace router，前缀为 "/api/v1/trace"
    - 验证所有端点可访问
  
    **实现需求**: 需求 7.1-7.4
  
    **文件**:
    - `apps/api/app/main.py` (修改)
  
    ---
  
  
  - [ ] 任务 5.9: 集成 Trace 到现有 Stage
    **描述**: 在现有 Stage 中添加追踪事件记录
  
    **验收标准**:
    - 在 ImageRenderStage 中记录追踪事件
    - 在 TTSStage 中记录追踪事件
    - 在 SubtitleGenerationStage 中记录追踪事件
    - 在 PreviewExportStage 中记录追踪事件
    - 在 QAStage 中记录追踪事件
    - 在 FinalExportStage 中记录追踪事件
    - 记录 source（输入）和 target（输出）关系
    - 记录关键元数据（duration_ms, input_params 等）
  
    **实现需求**: 需求 7.1
  
    **文件**:
    - `apps/api/app/services/image_render_stage.py` (修改)
    - `apps/api/app/services/tts_stage.py` (修改)
    - `apps/api/app/services/subtitle_generation_stage.py` (修改)
    - `apps/api/app/services/preview_export_stage.py` (修改)
    - `apps/api/app/services/qa_stage.py` (修改)
    - `apps/api/app/services/final_export_stage.py` (修改)
  
    ---
  
  

- [ ] 阶段 6: Notification Service 实现
  - [ ] 任务 6.1: 创建 Notification Service 基础结构
    **描述**: 创建 NotificationService 类和基础方法
  
    **验收标准**:
    - 创建 `apps/api/app/services/notification_service.py`
    - 定义 NotificationService 类
    - 实现 __init__() 方法，接收 db
    - 添加类文档字符串
  
    **实现需求**: 需求 9.1
  
    **文件**:
    - `apps/api/app/services/notification_service.py` (新建)
  
    ---
  
  
  - [ ] 任务 6.2: 实现导出通知发送
    **描述**: 实现 send_export_notification() 方法
  
    **验收标准**:
    - 实现 send_export_notification() 方法
    - 接收 user_id, export_bundle, status 参数
    - 支持 status="completed" 和 status="failed"
    - 构建通知消息（包含导出 ID、Episode 名称、状态）
    - 创建通知记录（存储到数据库或发送到通知服务）
    - 如果是 completed，包含下载链接
    - 如果是 failed，包含错误摘要
    - 包含单元测试
  
    **实现需求**: 需求 9.1, 9.2
  
    **文件**:
    - `apps/api/app/services/notification_service.py` (修改)
    - `apps/api/tests/unit/test_notification_service.py` (新建)
  
    ---
  
  
  - [ ] 任务 6.3: 实现 Webhook 调用
    **描述**: 实现 call_webhook() 方法
  
    **验收标准**:
    - 实现 call_webhook() 方法
    - 接收 webhook_url, export_bundle, max_retries 参数
    - 构建 Webhook payload（JSON 格式）
    - 包含 export_id, episode_id, status, download_url, created_at, completed_at
    - 使用 HTTP POST 发送到 webhook_url
    - 设置 Content-Type: application/json
    - 设置超时（10 秒）
    - 实现重试逻辑（最多 3 次，指数退避）
    - 记录每次调用的结果
    - 返回是否成功
    - 包含单元测试（使用 Mock HTTP 客户端）
  
    **实现需求**: 需求 9.3, 9.4, 9.5
  
    **文件**:
    - `apps/api/app/services/notification_service.py` (修改)
    - `apps/api/tests/unit/test_notification_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 6.4: 集成通知到 Final Export Stage
    **描述**: 在 Final Export Stage 中集成通知发送
  
    **验收标准**:
    - 在 FinalExportStage.execute() 中，导出成功时调用 send_export_notification()
    - 在 FinalExportStage.execute() 中，导出失败时调用 send_export_notification()
    - 如果配置了 webhook_url，调用 call_webhook()
    - Webhook 失败不影响导出任务的状态
    - 记录通知发送结果
  
    **实现需求**: 需求 9.1, 9.2, 9.3, 9.4
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
  
    ---
  
  

- [ ] 阶段 7: 水印功能
  - [ ] 任务 7.1: 实现文字水印
    **描述**: 实现 _apply_watermark() 方法的文字水印功能
  
    **验收标准**:
    - 实现 _apply_watermark() 方法
    - 接收 input_path, output_path, watermark_config 参数
    - 支持 watermark_config.type="text"
    - 使用 FFmpeg drawtext 滤镜
    - 支持位置：top_left, top_right, bottom_left, bottom_right, center
    - 支持透明度（alpha）
    - 支持字体大小
    - 生成带水印的视频到 output_path
    - 包含单元测试（使用 Mock FFmpeg）
  
    **实现需求**: 需求 10.1, 10.2, 10.3
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 7.2: 实现图片水印
    **描述**: 扩展 _apply_watermark() 方法支持图片水印
  
    **验收标准**:
    - 支持 watermark_config.type="image"
    - watermark_config.content 为图片路径或 URL
    - 如果是 URL，先下载图片
    - 使用 FFmpeg overlay 滤镜
    - 支持位置：top_left, top_right, bottom_left, bottom_right, center
    - 支持透明度（alpha）
    - 支持大小缩放（size 参数为百分比）
    - 包含单元测试
  
    **实现需求**: 需求 10.1, 10.2, 10.3, 10.4
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 7.3: 集成水印到导出流程
    **描述**: 在 Final Export Stage 中集成水印应用
  
    **验收标准**:
    - 在 FinalExportStage.execute() 中，视频合成后检查是否配置了水印
    - 如果 watermark.enabled=true，调用 _apply_watermark()
    - 如果 watermark.enabled=false 或未配置，跳过水印步骤
    - 水印应用失败时记录错误并继续（不阻止导出）
    - 包含集成测试
  
    **实现需求**: 需求 10.1, 10.4
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  

- [ ] 阶段 8: 错误恢复和健壮性
  - [ ] 任务 8.1: 实现导出错误处理
    **描述**: 在 Final Export Stage 中实现健壮的错误处理
  
    **验收标准**:
    - 在 execute() 方法中使用 try-except 捕获所有异常
    - 失败时更新 ExportBundle 状态为 "failed"
    - 记录 error_code 和 error_message
    - 保留中间产物（临时文件）用于调试
    - 发送失败通知
    - 包含单元测试
  
    **实现需求**: 需求 1.4, 14.2, 14.5
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 8.2: 实现存储上传重试
    **描述**: 实现对象存储上传的重试机制
  
    **验收标准**:
    - 在 ObjectStorageService 中实现 upload_with_retry() 方法
    - 最多重试 3 次
    - 使用指数退避（1s, 2s, 4s）
    - 记录每次重试的结果
    - 全部失败后抛出异常
    - 包含单元测试
  
    **实现需求**: 需求 14.3
  
    **文件**:
    - `apps/api/app/services/object_storage_service.py` (修改)
    - `apps/api/tests/unit/test_object_storage_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 8.3: 实现导出超时控制
    **描述**: 为导出过程添加超时控制
  
    **验收标准**:
    - 在 FinalExportStage.execute() 中设置超时（默认 30 分钟）
    - 使用 signal.alarm() 或 threading.Timer 实现超时
    - 超时后终止 FFmpeg 进程
    - 记录超时原因
    - 更新 ExportBundle 状态为 "failed"
    - 包含单元测试
  
    **实现需求**: 需求 14.4
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 8.4: 实现断点续传支持
    **描述**: 实现导出过程的断点续传
  
    **验收标准**:
    - 在 ExportBundle 中添加 checkpoint_jsonb 字段（通过迁移）
    - 在每个关键步骤后保存检查点
    - 实现 resume_export() 方法
    - 从检查点恢复时跳过已完成的步骤
    - 验证中间产物的完整性
    - 包含单元测试
  
    **实现需求**: 需求 14.1
  
    **文件**:
    - `infra/migrations/007_final_export_pilot_ready.sql` (修改)
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 8.5: 实现数据一致性保护
    **描述**: 使用事务保护数据一致性
  
    **验收标准**:
    - 在 ExportService 的关键操作中使用数据库事务
    - 失败时回滚所有更改
    - 不创建不完整的 ExportBundle 记录
    - 清理失败的临时文件
    - 包含单元测试
  
    **实现需求**: 需求 14.5
  
    **文件**:
    - `apps/api/app/services/export_service.py` (修改)
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/tests/unit/test_export_service.py` (修改)
  
    ---
  
  

- [ ] 阶段 9: 样板项目验证
  - [ ] 任务 9.1: 创建样板项目数据
    **描述**: 创建用于验证的样板项目
  
    **验收标准**:
    - 创建 `apps/api/scripts/create_sample_project.py`
    - 创建 Project 和 Episode
    - 创建预定义的 Brief（10-15 个 Shot）
    - 创建 Shot 数据（包含对白和旁白）
    - 创建 Mock 资产（关键帧、音频）
    - 所有数据符合系统规范
    - 脚本可重复执行
  
    **实现需求**: 需求 12.1
  
    **文件**:
    - `apps/api/scripts/create_sample_project.py` (新建)
  
    ---
  
  
  - [ ] 任务 9.2: 执行端到端验证
    **描述**: 执行样板项目的完整流程
  
    **验收标准**:
    - 创建 `apps/api/scripts/run_sample_workflow.py`
    - 执行从 Brief 到 Final Export 的所有 Stage
    - 验证每个 Stage 成功完成
    - 验证 QA 检查通过
    - 验证导出包生成
    - 记录执行时间和结果
    - 脚本可重复执行
  
    **实现需求**: 需求 12.2
  
    **文件**:
    - `apps/api/scripts/run_sample_workflow.py` (新建)
  
    ---
  
  
  - [ ] 任务 9.3: 验证产物质量
    **描述**: 验证样板项目的产物质量
  
    **验收标准**:
    - 创建 `apps/api/scripts/validate_sample_output.py`
    - 检查视频文件存在且可播放
    - 检查视频时长正确
    - 检查音频清晰度
    - 检查字幕同步
    - 检查清单文件完整性
    - 验证校验和
    - 生成验证报告
  
    **实现需求**: 需求 12.3, 12.4
  
    **文件**:
    - `apps/api/scripts/validate_sample_output.py` (新建)
  
    ---
  
  
  - [ ] 任务 9.4: 验证可追溯性
    **描述**: 验证样板项目的可追溯性
  
    **验收标准**:
    - 查询完整追踪路径
    - 验证所有 Stage 都有追踪记录
    - 验证 Lineage 关系正确
    - 验证所有产物可追溯到源头
    - 生成追踪图可视化
    - 包含验证脚本
  
    **实现需求**: 需求 12.4
  
    **文件**:
    - `apps/api/scripts/validate_sample_trace.py` (新建)
  
    ---
  
  
  - [ ] 任务 9.5: 创建样板项目文档
    **描述**: 编写样板项目的使用文档
  
    **验收标准**:
    - 创建 `apps/api/docs/SAMPLE_PROJECT_GUIDE.md`
    - 说明样板项目的目的
    - 提供创建和运行步骤
    - 提供验证步骤
    - 提供故障排除指南
    - 包含预期输出示例
  
    **实现需求**: 需求 12.1-12.5
  
    **文件**:
    - `apps/api/docs/SAMPLE_PROJECT_GUIDE.md` (新建)
  
    ---
  
  

- [ ] 阶段 10: Pilot 就绪检查
  - [ ] 任务 10.1: 创建 Pilot 就绪检查器
    **描述**: 实现 PilotReadinessChecker 类
  
    **验收标准**:
    - 创建 `apps/api/app/services/pilot_readiness_checker.py`
    - 定义 PilotReadinessChecker 类
    - 实现 run_readiness_check() 方法
    - 定义 ReadinessReport 和 CheckResult 数据类
    - 添加类文档字符串
  
    **实现需求**: 需求 15.1
  
    **文件**:
    - `apps/api/app/services/pilot_readiness_checker.py` (新建)
  
    ---
  
  
  - [ ] 任务 10.2: 实现核心功能检查
    **描述**: 实现 _check_core_features() 方法
  
    **验收标准**:
    - 检查所有 Stage 类型是否可用
    - 检查导出模板是否存在
    - 检查关键服务是否可实例化
    - 返回 CheckResult
    - 包含单元测试
  
    **实现需求**: 需求 15.1
  
    **文件**:
    - `apps/api/app/services/pilot_readiness_checker.py` (修改)
    - `apps/api/tests/unit/test_pilot_readiness_checker.py` (新建)
  
    ---
  
  
  - [ ] 任务 10.3: 实现数据库检查
    **描述**: 实现 _check_database() 方法
  
    **验收标准**:
    - 检查所有必需的表是否存在
    - 检查所有必需的索引是否存在
    - 检查数据库连接是否正常
    - 返回 CheckResult
    - 包含单元测试
  
    **实现需求**: 需求 15.2
  
    **文件**:
    - `apps/api/app/services/pilot_readiness_checker.py` (修改)
    - `apps/api/tests/unit/test_pilot_readiness_checker.py` (修改)
  
    ---
  
  
  - [ ] 任务 10.4: 实现 Provider 检查
    **描述**: 实现 _check_providers() 方法
  
    **验收标准**:
    - 检查 LLM Provider 连接
    - 检查 Image Provider 连接
    - 检查 TTS Provider 连接
    - 测试每个 Provider 的基本功能
    - 返回 CheckResult
    - 包含单元测试
  
    **实现需求**: 需求 15.3
  
    **文件**:
    - `apps/api/app/services/pilot_readiness_checker.py` (修改)
    - `apps/api/tests/unit/test_pilot_readiness_checker.py` (修改)
  
    ---
  
  
  - [ ] 任务 10.5: 实现存储检查
    **描述**: 实现 _check_storage() 方法
  
    **验收标准**:
    - 检查对象存储连接
    - 检查存储空间是否充足（至少 10GB）
    - 测试上传和下载功能
    - 返回 CheckResult
    - 包含单元测试
  
    **实现需求**: 需求 15.4
  
    **文件**:
    - `apps/api/app/services/pilot_readiness_checker.py` (修改)
    - `apps/api/tests/unit/test_pilot_readiness_checker.py` (修改)
  
    ---
  
  
  - [ ] 任务 10.6: 实现性能检查
    **描述**: 实现 _check_performance() 方法
  
    **验收标准**:
    - 检查数据库响应时间（< 100ms）
    - 检查 FFmpeg 可用性
    - 检查系统资源（CPU、内存）
    - 返回 CheckResult
    - 包含单元测试
  
    **实现需求**: 需求 15.1
  
    **文件**:
    - `apps/api/app/services/pilot_readiness_checker.py` (修改)
    - `apps/api/tests/unit/test_pilot_readiness_checker.py` (修改)
  
    ---
  
  
  - [ ] 任务 10.7: 实现安全检查
    **描述**: 实现 _check_security() 方法
  
    **验收标准**:
    - 检查必需的环境变量是否设置
    - 检查存储端点是否使用 HTTPS
    - 检查敏感信息是否加密
    - 返回 CheckResult
    - 包含单元测试
  
    **实现需求**: 需求 15.1
  
    **文件**:
    - `apps/api/app/services/pilot_readiness_checker.py` (修改)
    - `apps/api/tests/unit/test_pilot_readiness_checker.py` (修改)
  
    ---
  
  
  - [ ] 任务 10.8: 创建就绪检查 API 端点
    **描述**: 创建 GET /api/v1/pilot/readiness 端点
  
    **验收标准**:
    - 创建 `apps/api/app/api/routes/pilot.py`
    - 实现 get_readiness() 端点
    - 调用 PilotReadinessChecker.run_readiness_check()
    - 返回 ReadinessReport
    - 验证管理员权限
    - 包含 API 测试
  
    **实现需求**: 需求 15.5
  
    **文件**:
    - `apps/api/app/api/routes/pilot.py` (新建)
    - `apps/api/tests/unit/test_pilot_api.py` (新建)
  
    ---
  
  
  - [ ] 任务 10.9: 创建就绪检查脚本
    **描述**: 创建命令行就绪检查脚本
  
    **验收标准**:
    - 创建 `apps/api/scripts/check_pilot_readiness.py`
    - 执行完整的就绪检查
    - 输出彩色的检查结果
    - 生成 HTML 格式的报告
    - 如果检查失败，返回非零退出码
    - 脚本可独立运行
  
    **实现需求**: 需求 15.1-15.5
  
    **文件**:
    - `apps/api/scripts/check_pilot_readiness.py` (新建)
  
    ---
  
  
  - [ ] 任务 10.10: 创建就绪检查文档
    **描述**: 编写 Pilot 就绪检查文档
  
    **验收标准**:
    - 创建 `apps/api/docs/PILOT_READINESS.md`
    - 说明就绪检查的目的
    - 列出所有检查项
    - 提供运行步骤
    - 提供故障排除指南
    - 包含示例报告
  
    **实现需求**: 需求 15.1-15.5
  
    **文件**:
    - `apps/api/docs/PILOT_READINESS.md` (新建)
  
    ---
  
  

- [ ] 阶段 11: Observability Service（低优先级）
  - [ ] 任务 11.1: 创建 Observability Service 基础结构
    **描述**: 创建 ObservabilityService 类
  
    **验收标准**:
    - 创建 `apps/api/app/services/observability_service.py`
    - 定义 ObservabilityService 类
    - 实现 __init__() 方法
    - 添加类文档字符串
  
    **实现需求**: 需求 8.1
  
    **文件**:
    - `apps/api/app/services/observability_service.py` (新建)
  
    ---
  
  
  - [ ] 任务 11.2: 实现系统状态查询
    **描述**: 实现 get_system_status() 方法
  
    **验收标准**:
    - 查询当前运行的 Workflow 数量
    - 统计各状态的 Workflow 数量
    - 统计各 Stage 的运行和排队数量
    - 返回 SystemStatus 对象
    - 包含单元测试
  
    **实现需求**: 需求 8.1
  
    **文件**:
    - `apps/api/app/services/observability_service.py` (修改)
    - `apps/api/app/schemas/observability.py` (新建)
    - `apps/api/tests/unit/test_observability_service.py` (新建)
  
    ---
  
  
  - [ ] 任务 11.3: 实现性能指标查询
    **描述**: 实现 get_performance_metrics() 方法
  
    **验收标准**:
    - 查询指定时间范围内的 StageTask 记录
    - 计算各 Stage 的平均耗时
    - 计算各 Stage 的成功率
    - 统计总执行次数
    - 返回 PerformanceMetrics 对象
    - 包含单元测试
  
    **实现需求**: 需求 8.2
  
    **文件**:
    - `apps/api/app/services/observability_service.py` (修改)
    - `apps/api/app/schemas/observability.py` (修改)
    - `apps/api/tests/unit/test_observability_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 11.4: 实现成本指标查询
    **描述**: 实现 get_cost_metrics() 方法
  
    **验收标准**:
    - 查询 Provider 调用记录
    - 统计各 Provider 的调用次数
    - 估算成本（基于预定义的单价）
    - 返回 CostMetrics 对象
    - 包含单元测试
  
    **实现需求**: 需求 8.3
  
    **文件**:
    - `apps/api/app/services/observability_service.py` (修改)
    - `apps/api/app/schemas/observability.py` (修改)
    - `apps/api/tests/unit/test_observability_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 11.5: 实现错误统计查询
    **描述**: 实现 get_error_statistics() 方法
  
    **验收标准**:
    - 查询失败的 StageTask 记录
    - 统计错误类型分布
    - 计算失败率趋势
    - 返回 ErrorStatistics 对象
    - 包含单元测试
  
    **实现需求**: 需求 8.4
  
    **文件**:
    - `apps/api/app/services/observability_service.py` (修改)
    - `apps/api/app/schemas/observability.py` (修改)
    - `apps/api/tests/unit/test_observability_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 11.6: 实现资源使用查询
    **描述**: 实现 get_resource_usage() 方法
  
    **验收标准**:
    - 查询对象存储使用情况
    - 查询数据库连接数
    - 查询系统资源（CPU、内存）
    - 返回 ResourceUsage 对象
    - 包含单元测试
  
    **实现需求**: 需求 8.5
  
    **文件**:
    - `apps/api/app/services/observability_service.py` (修改)
    - `apps/api/app/schemas/observability.py` (修改)
    - `apps/api/tests/unit/test_observability_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 11.7: 创建 Observability API 路由
    **描述**: 创建 observability.py 路由文件
  
    **验收标准**:
    - 创建 `apps/api/app/api/routes/observability.py`
    - 实现 GET /api/v1/observability/system-status
    - 实现 GET /api/v1/observability/performance
    - 实现 GET /api/v1/observability/costs
    - 实现 GET /api/v1/observability/errors
    - 实现 GET /api/v1/observability/resources
    - 所有端点验证管理员权限
    - 包含 API 测试
  
    **实现需求**: 需求 8.1-8.5
  
    **文件**:
    - `apps/api/app/api/routes/observability.py` (新建)
    - `apps/api/tests/unit/test_observability_api.py` (新建)
  
    ---
  
  
  - [ ] 任务 11.8: 注册 Observability 路由
    **描述**: 将 Observability 路由注册到主应用
  
    **验收标准**:
    - 在主应用中注册 observability router
    - 前缀为 "/api/v1/observability"
    - 验证所有端点可访问
  
    **实现需求**: 需求 8.1-8.5
  
    **文件**:
    - `apps/api/app/main.py` (修改)
  
    ---
  
  

- [ ] 阶段 12: 性能优化（低优先级）
  - [ ] 任务 12.1: 实现硬件加速支持
    **描述**: 在视频合成中启用硬件加速
  
    **验收标准**:
    - 检测可用的硬件加速器（NVENC, VideoToolbox, QSV）
    - 在 FFmpeg 命令中使用硬件编码器
    - 如果硬件加速不可用，回退到软件编码
    - 记录使用的编码器类型
    - 测试性能提升
  
    **实现需求**: 需求 11.1
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
    - `apps/api/docs/HARDWARE_ACCELERATION.md` (新建)
  
    ---
  
  
  - [ ] 任务 12.2: 实现并行资产下载
    **描述**: 并行下载导出所需的资产
  
    **验收标准**:
    - 使用 ThreadPoolExecutor 并行下载
    - 最多 5 个并发下载
    - 显示下载进度
    - 处理下载失败
    - 测试性能提升
  
    **实现需求**: 需求 11.2
  
    **文件**:
    - `apps/api/app/services/final_export_stage.py` (修改)
  
    ---
  
  
  - [ ] 任务 12.3: 实现导出队列管理
    **描述**: 实现导出任务的队列管理
  
    **验收标准**:
    - 创建 `apps/api/app/services/export_queue.py`
    - 实现队列管理器
    - 限制并发导出数量（默认 3 个）
    - 支持优先级调度
    - 监控系统负载
    - 动态调整并发数
  
    **实现需求**: 需求 11.3, 11.5
  
    **文件**:
    - `apps/api/app/services/export_queue.py` (新建)
    - `apps/api/tests/unit/test_export_queue.py` (新建)
  
    ---
  
  
  - [ ] 任务 12.4: 实现导出配置缓存
    **描述**: 缓存常用的导出配置
  
    **验收标准**:
    - 使用内存缓存（如 functools.lru_cache）
    - 缓存导出模板
    - 缓存 FFmpeg 参数
    - 设置合理的缓存大小
    - 测试性能提升
  
    **实现需求**: 需求 11.2
  
    **文件**:
    - `apps/api/app/services/export_service.py` (修改)
  
    ---
  
  
  - [ ] 任务 12.5: 性能测试和基准
    **描述**: 创建性能测试套件
  
    **验收标准**:
    - 创建 `apps/api/tests/performance/test_export_performance.py`
    - 测试不同 Shot 数量的导出时间
    - 测试不同分辨率的导出时间
    - 测试并发导出性能
    - 生成性能报告
    - 验证 10 个 Shot 在 5 分钟内完成
  
    **实现需求**: 需求 11.4
  
    **文件**:
    - `apps/api/tests/performance/test_export_performance.py` (新建)
    - `apps/api/docs/PERFORMANCE_BENCHMARKS.md` (新建)
  
    ---
  
  

## 正确性属性测试

- [ ] 任务 13.1: 属性 1 测试 - QA 阻止导出
  **描述**: 测试 QA critical 问题阻止导出

  **验收标准**:
  - 创建 `apps/api/tests/properties/test_qa_blocks_export.py`
  - 使用 Hypothesis 生成测试数据
  - 测试有 critical 问题时导出被阻止
  - 测试 force_export=true 时可以导出
  - 测试只有 warning 时可以导出

  **实现需求**: 需求 5.1, 5.2, 5.4

  **文件**:
  - `apps/api/tests/properties/test_qa_blocks_export.py` (新建)

  ---


- [ ] 任务 13.2: 属性 2 测试 - 导出配置有效性
  **描述**: 测试导出配置验证

  **验收标准**:
  - 创建 `apps/api/tests/properties/test_export_config_validation.py`
  - 使用 Hypothesis 生成随机配置
  - 测试无效配置被拒绝
  - 测试有效配置被接受
  - 测试边界条件

  **实现需求**: 需求 3.4, 3.5

  **文件**:
  - `apps/api/tests/properties/test_export_config_validation.py` (新建)

  ---


- [ ] 任务 13.3: 属性 3 测试 - 主资产完整性
  **描述**: 测试导出包包含所有主资产

  **验收标准**:
  - 创建 `apps/api/tests/properties/test_primary_assets_completeness.py`
  - 测试所有 is_selected=true 的资产都被包含
  - 测试资产顺序正确
  - 测试缺失资产时导出失败

  **实现需求**: 需求 1.2, 4.1

  **文件**:
  - `apps/api/tests/properties/test_primary_assets_completeness.py` (新建)

  ---


- [ ] 任务 13.4: 属性 4 测试 - 清单文件一致性
  **描述**: 测试清单文件与实际资产一致

  **验收标准**:
  - 创建 `apps/api/tests/properties/test_manifest_consistency.py`
  - 测试清单中列出的资产都存在
  - 测试实际资产都在清单中
  - 测试资产元数据正确

  **实现需求**: 需求 4.2, 4.3, 4.4

  **文件**:
  - `apps/api/tests/properties/test_manifest_consistency.py` (新建)

  ---


- [ ] 任务 13.5: 属性 5 测试 - 校验和验证
  **描述**: 测试文件校验和正确性

  **验收标准**:
  - 创建 `apps/api/tests/properties/test_checksum_verification.py`
  - 测试所有文件的校验和与清单一致
  - 测试文件修改后校验和不匹配
  - 测试校验和算法正确

  **实现需求**: 需求 4.5

  **文件**:
  - `apps/api/tests/properties/test_checksum_verification.py` (新建)

  ---


- [ ] 任务 13.6: 属性 6 测试 - 导出版本递增
  **描述**: 测试导出版本号递增

  **验收标准**:
  - 创建 `apps/api/tests/properties/test_export_version_increment.py`
  - 测试新导出的版本号大于之前的版本
  - 测试并发导出时版本号不冲突
  - 测试版本号从 1 开始

  **实现需求**: 需求 6.3

  **文件**:
  - `apps/api/tests/properties/test_export_version_increment.py` (新建)

  ---


## 文档和部署

- [ ] 任务 14.1: 创建 Final Export 用户指南
  **描述**: 编写 Final Export 功能的用户指南

  **验收标准**:
  - 创建 `apps/api/docs/FINAL_EXPORT_GUIDE.md`
  - 说明导出功能的用途
  - 提供导出步骤说明
  - 说明导出模板的使用
  - 说明水印配置
  - 提供故障排除指南
  - 包含 API 使用示例

  **实现需求**: 需求 1.1-1.5, 3.1-3.5, 10.1-10.4

  **文件**:
  - `apps/api/docs/FINAL_EXPORT_GUIDE.md` (新建)

  ---


- [ ] 任务 14.2: 创建 Trace 和 Lineage 指南
  **描述**: 编写追踪和血缘关系的使用指南

  **验收标准**:
  - 创建 `apps/api/docs/TRACE_LINEAGE_GUIDE.md`
  - 说明追踪功能的用途
  - 说明如何查询追踪路径
  - 说明如何查询血缘关系
  - 提供可视化示例
  - 提供 API 使用示例

  **实现需求**: 需求 7.1-7.5

  **文件**:
  - `apps/api/docs/TRACE_LINEAGE_GUIDE.md` (新建)

  ---


- [ ] 任务 14.3: 更新 API 文档
  **描述**: 更新 OpenAPI/Swagger 文档

  **验收标准**:
  - 添加 Export API 端点文档
  - 添加 Trace API 端点文档
  - 添加 Observability API 端点文档
  - 添加 Pilot API 端点文档
  - 添加请求/响应示例
  - 添加错误码说明

  **实现需求**: 需求 13.1-13.5, 7.1-7.4, 8.1-8.5, 15.1-15.5

  **文件**:
  - `apps/api/app/main.py` (修改，更新 OpenAPI 配置)

  ---


- [ ] 任务 14.4: 创建迁移指南
  **描述**: 编写数据库迁移指南

  **验收标准**:
  - 创建 `infra/migrations/MIGRATION_007_GUIDE.md`
  - 说明迁移的内容
  - 提供迁移步骤
  - 提供回滚步骤
  - 说明注意事项
  - 提供验证步骤

  **实现需求**: 需求 2.1, 7.1

  **文件**:
  - `infra/migrations/MIGRATION_007_GUIDE.md` (新建)

  ---


- [ ] 任务 14.5: 创建部署检查清单
  **描述**: 编写 Pilot 部署检查清单

  **验收标准**:
  - 创建 `docs/deployment/PILOT_DEPLOYMENT_CHECKLIST.md`
  - 列出部署前检查项
  - 列出部署步骤
  - 列出部署后验证项
  - 提供回滚计划
  - 提供监控指标

  **实现需求**: 需求 15.1-15.5

  **文件**:
  - `docs/deployment/PILOT_DEPLOYMENT_CHECKLIST.md` (新建)

  ---


- [ ] 任务 14.6: 更新项目 README
  **描述**: 更新项目 README 文档

  **验收标准**:
  - 在 README.md 中添加 Final Export 功能说明
  - 添加 Trace 和 Lineage 功能说明
  - 更新功能列表
  - 更新架构图
  - 添加 Pilot 就绪状态

  **实现需求**: 需求 1.1-1.5, 7.1-7.5, 15.1-15.5

  **文件**:
  - `README.md` (修改)

  ---


## 任务执行顺序建议

### 第 1 周: 核心导出功能

**优先级**: 高

**任务**:
- 阶段 1: 数据库迁移和基础模型（任务 1.1-1.6）
- 阶段 2: Export Service 核心功能（任务 2.1-2.6）
- 阶段 3: Final Export Stage 实现（任务 3.1-3.6）

**目标**: 实现基础的导出功能，能够生成高分辨率视频

---

### 第 2 周: API 和集成

**优先级**: 高

**任务**:
- 阶段 4: Export API 端点（任务 4.1-4.7）
- 阶段 8: 错误恢复和健壮性（任务 8.1-8.5）

**目标**: 实现完整的 Export API，确保系统健壮性

---

### 第 3 周: Trace 和通知

**优先级**: 中

**任务**:
- 阶段 5: Trace Service 实现（任务 5.1-5.9）
- 阶段 6: Notification Service 实现（任务 6.1-6.4）
- 阶段 7: 水印功能（任务 7.1-7.3）

**目标**: 实现追踪、通知和水印功能

---

### 第 4 周: 验证和就绪

**优先级**: 高

**任务**:
- 阶段 9: 样板项目验证（任务 9.1-9.5）
- 阶段 10: Pilot 就绪检查（任务 10.1-10.10）
- 正确性属性测试（任务 13.1-13.6）
- 文档和部署（任务 14.1-14.6）

**目标**: 验证系统完整性，确保 Pilot 就绪

---

### 后续迭代: 可观测性和优化

**优先级**: 低

**任务**:
- 阶段 11: Observability Service（任务 11.1-11.8）
- 阶段 12: 性能优化（任务 12.1-12.5）

**目标**: 提升系统可观测性和性能

---

## 任务统计

### 按阶段统计

- **阶段 1**: 数据库迁移和基础模型 - 6 个任务
- **阶段 2**: Export Service 核心功能 - 6 个任务
- **阶段 3**: Final Export Stage 实现 - 6 个任务
- **阶段 4**: Export API 端点 - 7 个任务
- **阶段 5**: Trace Service 实现 - 9 个任务
- **阶段 6**: Notification Service 实现 - 4 个任务
- **阶段 7**: 水印功能 - 3 个任务
- **阶段 8**: 错误恢复和健壮性 - 5 个任务
- **阶段 9**: 样板项目验证 - 5 个任务
- **阶段 10**: Pilot 就绪检查 - 10 个任务
- **阶段 11**: Observability Service - 8 个任务（低优先级）
- **阶段 12**: 性能优化 - 5 个任务（低优先级）
- **正确性属性测试**: 6 个任务
- **文档和部署**: 6 个任务

**总计**: 86 个任务

### 按优先级统计

- **高优先级**: 61 个任务（必须在本迭代完成）
- **中优先级**: 12 个任务（本迭代尽量完成）
- **低优先级**: 13 个任务（可推迟到后续迭代）

---

## 成功标准

### 功能完整性

- ✓ 所有高优先级任务完成
- ✓ Final Export Stage 正常工作
- ✓ Export API 端点可用
- ✓ Trace Service 正常工作
- ✓ 样板项目验证通过

### 质量标准

- ✓ 单元测试覆盖率 > 80%
- ✓ 所有 API 端点有测试
- ✓ 正确性属性测试通过
- ✓ 集成测试通过
- ✓ 代码审查通过

### 性能标准

- ✓ 10 个 Shot 的视频在 5 分钟内完成导出
- ✓ API 响应时间 < 500ms
- ✓ 导出成功率 > 95%

### Pilot 就绪

- ✓ Pilot 就绪检查全部通过
- ✓ 样板项目可以完整运行
- ✓ 文档完整
- ✓ 部署检查清单完成

---

## 注意事项

### 依赖关系

1. **阶段 1 必须最先完成**，因为其他阶段依赖数据模型和 Repository
2. **阶段 2 和 3 可以并行开发**，但 3 依赖 2 的部分功能
3. **阶段 4 依赖阶段 2 和 3**
4. **阶段 5-7 可以并行开发**
5. **阶段 9 依赖阶段 1-8 的完成**
6. **阶段 10 依赖所有其他阶段**

### 技术债务

- 性能优化（阶段 12）可以推迟，但需要在后续迭代中完成
- Observability Service（阶段 11）可以推迟，但对生产环境很重要
- 水印功能（阶段 7）是增强功能，可以根据优先级调整

### 风险管理

- **FFmpeg 性能**: 如果性能不足，考虑使用硬件加速或云端处理
- **存储成本**: 实现自动清理机制，避免成本失控
- **Trace 数据量**: 实现数据归档和清理策略
- **并发导出**: 实现队列管理，避免系统过载

---

## 下一步行动

1. **执行数据库迁移**（任务 1.1）
2. **创建基础数据模型**（任务 1.2-1.3）
3. **实现 Repository 层**（任务 1.4-1.5）
4. **开始 Export Service 开发**（任务 2.1-2.6）
5. **并行开发 Final Export Stage**（任务 3.1-3.6）

---

## 总结

本任务列表将 Final Export 与 Pilot Ready 强化的需求和设计转化为 86 个可执行的任务，按照 12 个阶段组织。通过完成这些任务，系统将从"能生成预览"升级为"能交付成品"，并具备完整的可追溯性和可观测性，为进入 Pilot 测试阶段做好准备。

建议按照 4 周的时间表执行，优先完成高优先级任务，确保核心功能在第 4 周结束时可以进入 Pilot 测试。

