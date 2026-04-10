# Object Storage Service

## Overview

The `ObjectStorageService` provides a unified interface for uploading, downloading, and managing media files in S3-compatible object storage (AWS S3, MinIO, Alibaba Cloud OSS, etc.).

All generated media assets — keyframes, audio files, subtitles, and preview videos — are stored via this service.

## Configuration

Add the following to your `.env` file:

```env
# Object Storage (S3 / MinIO)
S3_ENDPOINT=http://localhost:9000        # MinIO local; use https://s3.amazonaws.com for AWS
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
S3_BUCKET=thinking-media
S3_REGION=us-east-1
S3_USE_SSL=false                         # Set true for production / AWS
```

### Local Development with MinIO

Start MinIO via Docker Compose:

```bash
docker compose -f infra/docker/docker-compose.yml up -d minio
```

MinIO console is available at `http://localhost:9001` (user: `minio`, password: `minio123`).

### AWS S3

```env
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=<your-access-key-id>
S3_SECRET_KEY=<your-secret-access-key>
S3_BUCKET=your-bucket-name
S3_REGION=ap-east-1
S3_USE_SSL=true
```

## Storage Key Convention

Every file stored in object storage is identified by a **storage key** — a path-like string that encodes context about the asset.

### Format

```
{project_id}/{episode_id}/{asset_type}/{YYYYMMDD}/{uuid}.{ext}
```

### Examples

| Asset Type | Example Key |
|---|---|
| Keyframe image | `proj-123/ep-456/keyframe/20260410/a1b2c3d4.png` |
| Audio file | `proj-123/ep-456/audio/20260410/e5f6a7b8.mp3` |
| Subtitle file | `proj-123/ep-456/subtitle/20260410/c9d0e1f2.vtt` |
| Preview video | `proj-123/ep-456/preview/20260410/f3a4b5c6.mp4` |

### Generating a Key

```python
from app.services.object_storage_service import ObjectStorageService

storage = ObjectStorageService()

key = storage.generate_storage_key(
    project_id=str(project.id),
    episode_id=str(episode.id),
    asset_type="keyframe",
    file_extension="png",
)
# → "proj-uuid/ep-uuid/keyframe/20260410/random-uuid.png"
```

## Usage

### Upload a File

```python
from app.services.object_storage_service import ObjectStorageService

storage = ObjectStorageService()

result = storage.upload_file(
    file_path="/tmp/shot_001.png",
    storage_key=key,
    content_type="image/png",
    metadata={"shot_id": str(shot.id)},   # optional
)

print(result.storage_key)   # path in bucket
print(result.url)           # presigned URL (valid 1 hour)
print(result.size_bytes)    # file size
```

### Download a File

```python
success = storage.download_file(
    storage_key="proj-uuid/ep-uuid/keyframe/20260410/abc.png",
    local_path="/tmp/downloaded.png",
)

if not success:
    print("File not found")
```

### Delete a File

```python
storage.delete_file(storage_key="proj-uuid/ep-uuid/keyframe/20260410/abc.png")
```

### Get a Presigned URL

```python
# Default expiry: 1 hour
url = storage.get_url(storage_key, expires_in=3600)

# Longer-lived URL for sharing
url = storage.get_url(storage_key, expires_in=86400)  # 24 hours
```

### Check File Existence

```python
if storage.file_exists(storage_key):
    print("File exists")
```

### Test Connection

```python
status = storage.test_connection()
# {
#   "status": "connected",
#   "bucket": "thinking-media",
#   "bucket_exists": True,
#   "endpoint": "http://localhost:9000",
#   "region": "us-east-1"
# }
```

You can also run the connection test script:

```bash
cd apps/api
python scripts/test_object_storage.py
```

## Error Handling

| Scenario | Behaviour |
|---|---|
| File not found on upload | Raises `FileNotFoundError` |
| Upload fails (network / auth) | Raises `RuntimeError` with details |
| Download — key not found | Returns `False` |
| Delete fails | Raises `RuntimeError` |
| URL generation fails | Raises `RuntimeError` |

```python
try:
    result = storage.upload_file(file_path, key, "image/png")
except FileNotFoundError:
    logger.error("Local file missing before upload")
except RuntimeError as e:
    logger.error(f"Storage error: {e}")
```

## Requirements Coverage

| Requirement | Description |
|---|---|
| 1.1 | Upload to configured S3/OSS |
| 1.2 | Unique `storage_key` + accessible URL |
| 1.3 | Download via `storage_key` |
| 1.4 | Error logging + retry (handled by callers) |
| 1.5 | Delete file when asset is removed |
