# Iteration 6: Final Export 与 Pilot Ready 强化 - 需求文档

## 简介

本迭代是项目的最后一个迭代，目标是实现正式的导出功能、完善可观测性，并确保系统可以进入 Pilot 测试阶段。通过实现 Final Export Stage、ExportBundle 记录、导出历史查询和 Trace/Lineage 追踪，将系统从"能生成预览"升级为"能交付成品"。

本迭代是系统从"开发阶段"向"生产就绪"转型的关键里程碑，将首次实现完整的交付流程和端到端的可观测性。

## 术语表

- **Final Export**: 最终导出，生成正式的交付包，包括高分辨率视频、所有资产和元数据
- **Export Bundle**: 导出包，包含视频文件、资产清单、元数据和交付说明的完整包
- **Export Record**: 导出记录，记录每次导出的历史、状态和元数据
- **Delivery Package**: 交付包，最终交付给客户或平台的完整内容包
- **Trace**: 追踪，记录数据流转和处理过程的完整路径
- **Lineage**: 血缘关系，记录数据的来源、依赖和派生关系
- **Observability**: 可观测性，通过日志、指标和追踪了解系统运行状态的能力
- **Manifest**: 清单文件，描述导出包内容和结构的元数据文件
- **Checksum**: 校验和，用于验证文件完整性的哈希值
- **Export Template**: 导出模板，定义不同平台或场景的导出配置
- **Watermark**: 水印，添加到视频中的标识信息
- **Pilot Test**: 试点测试，小规模用户测试以验证系统可用性

## 需求

### 需求 1: Final Export Stage 实现

**用户故事**: 作为内容创作者，我想要导出正式的交付包，以便将内容发布到平台或交付给客户。

#### 验收标准

1. WHEN Final Export Stage 执行 THEN System SHALL 生成高分辨率的最终视频（1080p 或更高）
2. WHEN 导出视频 THEN System SHALL 使用所有 Shot 的主资产（is_selected=true）
3. WHEN 导出完成 THEN System SHALL 生成包含视频、资产清单和元数据的完整导出包
4. WHEN 导出失败 THEN System SHALL 记录详细的失败原因并保留中间产物
5. WHEN 导出成功 THEN System SHALL 更新 Episode 状态为 "exported" 并记录导出时间

### 需求 2: ExportBundle 数据模型

**用户故事**: 作为系统开发者，我想要记录每次导出的完整信息，以便追踪导出历史和管理交付包。

#### 验收标准

1. WHEN 创建导出 THEN System SHALL 创建 ExportBundle 记录并分配唯一 ID
2. WHEN 记录导出 THEN System SHALL 保存导出配置、资产列表和元数据
3. WHEN 导出完成 THEN System SHALL 记录导出包的存储位置和访问 URL
4. WHEN 导出失败 THEN System SHALL 记录失败状态和错误信息
5. WHEN 查询导出 THEN System SHALL 支持按 Episode、Project 和时间范围查询

### 需求 3: 导出配置和模板

**用户故事**: 作为内容创作者，我想要使用不同的导出配置，以便适配不同的平台和场景。

#### 验收标准

1. WHEN 用户选择导出模板 THEN System SHALL 应用对应的分辨率、编码和格式配置
2. WHEN 导出到抖音 THEN System SHALL 使用 9:16 竖屏、1080x1920 分辨率
3. WHEN 导出到 B 站 THEN System SHALL 使用 16:9 横屏、1920x1080 分辨率
4. WHEN 自定义导出 THEN System SHALL 允许用户指定分辨率、码率和编码参数
5. WHEN 导出配置无效 THEN System SHALL 验证参数并返回清晰的错误信息

### 需求 4: 资产打包和清单

**用户故事**: 作为内容创作者，我想要导出包包含所有相关资产，以便完整交付内容。

#### 验收标准

1. WHEN 生成导出包 THEN System SHALL 包含最终视频、所有关键帧图像和音频文件
2. WHEN 生成清单 THEN System SHALL 创建 JSON 格式的 manifest.json 文件
3. WHEN 清单文件 THEN System SHALL 包含每个资产的文件名、类型、大小和校验和
4. WHEN 打包资产 THEN System SHALL 按照清单文件组织目录结构
5. WHEN 验证导出包 THEN System SHALL 计算并验证所有文件的校验和

### 需求 5: 导出质量控制

**用户故事**: 作为内容创作者，我想要确保导出的内容符合质量标准，以便避免交付低质量内容。

#### 验收标准

1. WHEN 开始导出 THEN System SHALL 验证最新 QA 报告的状态
2. WHEN QA 有 critical 问题 THEN System SHALL 阻止导出并提示修复问题
3. WHEN QA 通过 THEN System SHALL 允许导出并在导出包中包含 QA 报告
4. WHEN 强制导出 THEN System SHALL 要求审批权限并记录跳过 QA 的原因
5. WHEN 导出完成 THEN System SHALL 对导出的视频进行基础质量检查（可播放性、时长）

### 需求 6: 导出历史和版本管理

**用户故事**: 作为内容创作者，我想要查看导出历史，以便管理不同版本的交付包。

#### 验收标准

1. WHEN 查询导出历史 THEN System SHALL 返回按时间倒序的所有 ExportBundle 记录
2. WHEN 展示导出记录 THEN System SHALL 显示导出时间、配置、状态和下载链接
3. WHEN 导出新版本 THEN System SHALL 自动递增 export_version 并保留旧版本
4. WHEN 比较版本 THEN System SHALL 支持查看不同导出版本的差异
5. WHEN 删除旧版本 THEN System SHALL 支持删除指定的导出包并释放存储空间

### 需求 7: Trace 和 Lineage 追踪

**用户故事**: 作为系统开发者，我想要追踪数据的完整流转路径，以便调试问题和优化流程。

#### 验收标准

1. WHEN 查询 Trace THEN System SHALL 返回从 Brief 到 Final Export 的完整数据流转路径
2. WHEN 展示 Lineage THEN System SHALL 显示每个产物的输入依赖和派生关系
3. WHEN 追踪 Asset THEN System SHALL 显示该 Asset 的生成来源（StageTask、Shot、输入参数）
4. WHEN 追踪 Document THEN System SHALL 显示该 Document 的版本历史和修改记录
5. WHEN 追踪失败 THEN System SHALL 显示失败的 Stage、错误信息和重试历史

### 需求 8: 可观测性仪表板

**用户故事**: 作为系统管理员，我想要查看系统运行状态，以便监控性能和发现问题。

#### 验收标准

1. WHEN 查询系统状态 THEN System SHALL 返回当前运行的 Workflow 数量和状态分布
2. WHEN 查询性能指标 THEN System SHALL 返回各 Stage 的平均耗时和成功率
3. WHEN 查询成本指标 THEN System SHALL 返回 Provider 调用次数和估算成本
4. WHEN 查询错误统计 THEN System SHALL 返回错误类型分布和失败率趋势
5. WHEN 查询资源使用 THEN System SHALL 返回存储空间使用和数据库连接数

### 需求 9: 导出通知和回调

**用户故事**: 作为内容创作者，我想要在导出完成时收到通知，以便及时下载交付包。

#### 验收标准

1. WHEN 导出完成 THEN System SHALL 发送通知到用户的通知中心
2. WHEN 导出失败 THEN System SHALL 发送失败通知并包含错误摘要
3. WHEN 配置 Webhook THEN System SHALL 在导出完成时调用指定的 Webhook URL
4. WHEN 调用 Webhook THEN System SHALL 发送包含导出状态和下载链接的 JSON 数据
5. WHEN Webhook 失败 THEN System SHALL 重试最多 3 次并记录失败日志

### 需求 10: 水印和品牌标识

**用户故事**: 作为内容创作者，我想要在导出视频中添加水印，以便保护版权和品牌标识。

#### 验收标准

1. WHEN 配置水印 THEN System SHALL 支持添加文字水印或图片水印
2. WHEN 添加水印 THEN System SHALL 允许指定水印位置（左上、右上、左下、右下、居中）
3. WHEN 添加水印 THEN System SHALL 允许指定水印透明度和大小
4. WHEN 导出视频 THEN System SHALL 在视频合成时嵌入水印
5. WHEN 禁用水印 THEN System SHALL 支持导出无水印版本（需要权限）

### 需求 11: 导出性能优化

**用户故事**: 作为系统开发者，我想要优化导出性能，以便缩短导出时间。

#### 验收标准

1. WHEN 导出视频 THEN System SHALL 使用硬件加速（如 GPU 编码）
2. WHEN 处理大量 Shot THEN System SHALL 支持并行处理和批量合成
3. WHEN 导出多个 Episode THEN System SHALL 支持队列管理和优先级调度
4. WHEN 导出完成 THEN System SHALL 在 5 分钟内完成 10 个 Shot 的视频导出
5. WHEN 系统负载高 THEN System SHALL 限制并发导出数量以保护系统稳定性

### 需求 12: 样板项目验证

**用户故事**: 作为系统开发者，我想要创建样板项目，以便验证端到端流程和演示系统能力。

#### 验收标准

1. WHEN 创建样板项目 THEN System SHALL 使用预定义的 Brief 和配置
2. WHEN 执行样板项目 THEN System SHALL 完整运行从 Brief 到 Final Export 的所有 Stage
3. WHEN 样板项目完成 THEN System SHALL 生成可播放的最终视频
4. WHEN 验证样板项目 THEN System SHALL 检查所有产物的完整性和正确性
5. WHEN 样板项目失败 THEN System SHALL 记录详细的失败信息并生成诊断报告

### 需求 13: 导出 API 端点

**用户故事**: 作为前端开发者，我想要调用导出 API，以便在界面中触发和管理导出。

#### 验收标准

1. WHEN 调用 POST /api/export THEN System SHALL 创建导出任务并返回任务 ID
2. WHEN 调用 GET /api/export/{id} THEN System SHALL 返回导出任务的状态和进度
3. WHEN 调用 GET /api/export/history THEN System SHALL 返回导出历史列表
4. WHEN 调用 GET /api/export/{id}/download THEN System SHALL 返回导出包的下载 URL
5. WHEN 调用 DELETE /api/export/{id} THEN System SHALL 删除指定的导出包

### 需求 14: 导出错误恢复

**用户故事**: 作为系统开发者，我想要实现健壮的错误恢复机制，以便处理导出过程中的异常。

#### 验收标准

1. WHEN 导出过程中断 THEN System SHALL 保存中间状态并支持从断点恢复
2. WHEN FFmpeg 失败 THEN System SHALL 记录详细的错误日志并保留临时文件
3. WHEN 存储上传失败 THEN System SHALL 重试最多 3 次并使用指数退避
4. WHEN 导出超时 THEN System SHALL 终止任务并记录超时原因
5. WHEN 系统异常 THEN System SHALL 回滚未完成的导出并保持数据一致性

### 需求 15: Pilot 就绪检查

**用户故事**: 作为项目经理，我想要验证系统是否准备好进入 Pilot 测试，以便确保系统质量。

#### 验收标准

1. WHEN 执行就绪检查 THEN System SHALL 验证所有核心功能是否正常工作
2. WHEN 检查数据库 THEN System SHALL 验证所有必需的表和索引是否存在
3. WHEN 检查 Provider THEN System SHALL 验证 LLM、Image 和 TTS Provider 是否可用
4. WHEN 检查存储 THEN System SHALL 验证对象存储服务是否可访问
5. WHEN 就绪检查通过 THEN System SHALL 生成就绪报告并标记系统为 "pilot_ready"
