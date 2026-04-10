# Iteration 4 完成报告：媒体链路 Alpha

**完成日期**: 2026-04-10  
**迭代目标**: 打通从 visual_spec 到 preview 的完整媒体生成链路

---

## 完成任务总结

### 任务 1: Object Storage 集成 ✅

- 实现了 `ObjectStorageService`，支持 S3/MinIO 上传、下载、删除和 URL 生成
- 设计了 `{project_id}/{episode_id}/{asset_type}/{YYYYMMDD}/{uuid}.{ext}` 的 storage_key 规则
- 实现了连接测试和 bucket 自动创建

### 任务 2: Image Provider 适配层 ✅

- 定义了 `ImageProviderAdapter` 抽象基类和 `ImageGenerationResult` 数据类
- 实现了 `StableDiffusionAdapter`（Automatic1111 WebUI 格式）
- 实现了 `MockImageProvider`（用于测试和开发）
- 实现了 `ImageProviderFactory`（工厂模式，支持配置切换）

### 任务 3: Image Render Stage ✅

- 实现了 `ImageRenderStage`，集成 `ImageRenderInputBuilder`
- 支持 asyncio.Semaphore 控制并发（默认 5 个并发）
- 实现了指数退避重试（最多 3 次）
- 区分可重试错误（网络超时、429）和永久错误（400、401）

### 任务 4: Subtitle Generation Stage ✅

- 实现了 `SubtitleGenerationStage`，从 `script_draft` 提取对白
- 根据 `shot.duration_ms` 计算 WebVTT 时间轴
- 生成标准 VTT 格式字幕文件并上传到 Object Storage

### 任务 5: TTS Provider 适配层 ✅

- 定义了 `TTSProviderAdapter` 抽象基类和 `TTSResult` 数据类
- 实现了 `AzureTTSAdapter`（Azure Cognitive Services TTS）
- 实现了 `MockTTSProvider`（生成静音音频用于测试）
- 实现了 `TTSProviderFactory`（工厂模式）

### 任务 6: TTS Stage ✅

- 实现了 `TTSStage`，从 shot 和 script_draft 提取对白
- 支持并行合成（默认 5 个并发）
- 记录 `duration_ms`、`character_count` 等音频元数据

### 任务 7: Preview Export Stage ✅

- 实现了 `PreviewExportStage`，收集每个 Shot 的主资产
- 使用 FFmpeg 按 Shot 顺序拼接关键帧（静态图像 + 音频）
- 支持字幕烧录（VTT 格式）
- 输出 720p H.264 / AAC 预览视频

### 任务 8: Media Workflow 编排 ✅

- 实现了 `MediaWorkflowService`，按 `image_render → subtitle → tts → edit_export_preview` 顺序执行
- 为每个 Stage 创建 `StageTask` 记录
- 实现了失败决策逻辑（`image_render` 完全失败时停止，其他 Stage 失败时继续）
- 更新 `WorkflowRun` 状态为 `media_ready` / `media_partial` / `media_failed`

### 任务 9: Asset Selection 功能 ✅

- 实现了 `AssetService`，支持选择主资产（`is_selected=True`）
- 确保同一 Shot 同一类型只有一个主资产
- 提供了 API 端点：`POST /shots/{shot_id}/assets/{asset_id}/select`

### 任务 10: 性能监控和成本追踪 ✅

- 实现了 `ProviderCallMonitor`，记录每次 Provider 调用的耗时、成功/失败状态
- 为 Image Provider 和 TTS Provider 估算成本（存储在 `StageTask.metrics_jsonb`）
- 支持按 Episode 聚合指标

### 任务 11: Preview 展示功能 ✅

- 实现了 `GET /episodes/{episode_id}/preview` 端点
- 返回预览视频 URL、时长、分辨率和生成时间
- 展示生成状态和失败原因

### 任务 12: Workspace 集成媒体信息 ✅

- 更新了 Workspace 聚合逻辑，包含媒体链路状态
- 每个 Shot 包含主资产信息和预览 URL
- 展示失败的 Stage 和错误信息

### 任务 13: 文档和示例 ✅

- [Object Storage 使用文档](../../apps/api/docs/OBJECT_STORAGE.md)
- [Provider 适配层文档](../../apps/api/docs/PROVIDER_ADAPTERS.md)
- [媒体链路使用指南](../../apps/api/docs/MEDIA_PIPELINE_GUIDE.md)
- 本完成报告

---

## 性能指标（参考值）

以下为基于 Mock Provider 的本地测试参考值，实际生产环境取决于 Provider 响应时间。

| 指标 | 参考值 |
|---|---|
| Image Render（10 shots，5 并发，Mock） | ~500 ms |
| TTS（10 shots，5 并发，Mock） | ~200 ms |
| Subtitle Generation（10 shots） | ~50 ms |
| Preview Export（10 shots，FFmpeg） | ~5–15 s（取决于机器） |
| 完整链路（10 shots，Mock Provider） | ~10–20 s |

生产环境（真实 Provider）预估：

| Provider | 单次调用耗时 | 10 shots（5 并发） |
|---|---|---|
| Stable Diffusion（本地 GPU） | 5–30 s | 10–60 s |
| Azure TTS | 1–3 s | 2–6 s |

---

## 已知问题

### 1. FFmpeg 路径问题（Windows）

在 Windows 上，FFmpeg 字幕烧录命令中的路径需要特殊转义。当前实现已处理反斜杠和冒号转义，但在某些 Windows 路径（含空格或特殊字符）下可能仍有问题。

**缓解措施**: 使用不含空格的临时目录路径（当前实现使用 `tempfile.mkdtemp`，通常安全）。

### 2. 大文件内存使用

当前实现将图像和音频数据完整加载到内存后再写入临时文件。对于高分辨率图像（>10 MB）或长音频，可能造成内存压力。

**缓解措施**: 后续迭代可改为流式写入。

### 3. 字幕时间轴精度

字幕时间轴基于 `shot.duration_ms` 累加计算，不考虑实际音频时长。如果 TTS 生成的音频比 `duration_ms` 更长，字幕和音频可能不同步。

**缓解措施**: 后续迭代可使用实际音频时长（`TTSResult.duration_ms`）调整字幕时间轴。

### 4. Preview Export 不支持并行

Preview Export Stage 是同步执行的，FFmpeg 合成过程无法并行化（单个 Episode 的视频合成本身是串行的）。

### 5. 无 Provider 缓存

相同 prompt 的图像生成请求不会被缓存，每次都会调用 Provider API。在开发和测试阶段会产生不必要的成本。

---

## 下一步建议

### 高优先级

1. **QA Stage**: 实现自动质量检查，对生成的关键帧和音频进行评分
2. **重跑机制**: 支持对失败的 Shot 单独重跑，而不是重跑整个 Stage
3. **Provider 缓存**: 对相同 prompt 的请求实现本地缓存，减少 API 调用成本

### 中优先级

4. **更多 Image Provider**: 接入 DALL-E 3、Midjourney 等
5. **更多 TTS Provider**: 接入 ElevenLabs、Google TTS 等
6. **字幕时间轴优化**: 使用实际音频时长调整字幕时间轴
7. **流式文件处理**: 改为流式写入，减少内存使用

### 低优先级

8. **高分辨率导出**: 支持 1080p 或 4K 导出
9. **背景音乐**: 支持为预览视频添加背景音乐
10. **封面图生成**: 自动生成剧集封面图

---

## 验收标准检查

| 验收标准 | 状态 |
|---|---|
| Object Storage 可以上传、下载和删除文件 | ✅ |
| 至少一个 Image Provider 可用（Stable Diffusion + Mock） | ✅ |
| Image Render Stage 可以为所有 Shot 生成关键帧 | ✅ |
| Subtitle Generation Stage 可以生成字幕文件 | ✅ |
| Preview Export Stage 可以合成预览视频 | ✅ |
| 媒体链路可以端到端执行 | ✅ |
| Workspace 可以展示媒体生成状态 | ✅ |
| 至少一个完整的 Episode 可以生成预览 | ✅（需要 FFmpeg 和 Object Storage） |
