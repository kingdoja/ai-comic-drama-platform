# Rerun Usage Guide

## Overview

The Rerun system enables iterative content improvement by allowing workflows to be re-executed from specific stages. Implemented as part of Iteration 5, it provides both full workflow reruns and targeted shot-level reruns, ensuring efficient iteration without wasting resources.

## Key Concepts

### Workflow Rerun

A **Workflow Rerun** re-executes a workflow starting from a specified stage, running all subsequent stages with new inputs or parameters. Previous stages' outputs are preserved.

### Shot-Level Rerun

A **Shot-Level Rerun** re-executes a specific stage for selected shots only, leaving other shots unchanged. This enables targeted improvements without regenerating all content.

### Rerun Lineage

Each rerun creates a new `WorkflowRun` that references its parent, maintaining a complete history of iterations and allowing version comparison.

## Rerun Types

### 1. Full Workflow Rerun

Re-execute from a specific stage through the end of the workflow.

**Use cases:**
- Major content changes affecting all shots
- Regenerating all media after script updates
- Applying new provider settings globally

**Example:**
```python
POST /api/episodes/{episode_id}/rerun
{
    "from_stage": "image_render",
    "reason": "Updated character designs, regenerate all images"
}
```

### 2. Partial Workflow Rerun

Re-execute specific stages without going through the entire workflow.

**Use cases:**
- Regenerating only audio after voice actor change
- Updating subtitles without touching images
- Re-exporting preview with new settings

**Example:**
```python
POST /api/episodes/{episode_id}/rerun
{
    "from_stage": "tts",
    "to_stage": "edit_export_preview",  # Optional: stop at this stage
    "reason": "New voice actor for main character"
}
```

### 3. Shot-Level Rerun

Re-execute a stage for specific shots only.

**Use cases:**
- Fixing specific problematic shots
- Adjusting individual shot compositions
- Regenerating audio for specific dialogue

**Example:**
```python
POST /api/episodes/{episode_id}/rerun-shots
{
    "shot_ids": ["shot-uuid-1", "shot-uuid-2"],
    "stage_type": "image_render",
    "reason": "Adjust lighting for shots 3 and 7"
}
```

## Architecture

### Rerun Data Flow

```
User Initiates Rerun
    ↓
Rerun Service Validates Request
    ↓
Create New WorkflowRun
  - Set rerun_from_stage
  - Set parent_workflow_run_id
  - Set rerun_reason
  - Set rerun_shot_ids (if shot-level)
    ↓
Load Context from Previous Run
  - Preserve earlier stage outputs
  - Load latest document versions
    ↓
Execute Stages
  - Start from rerun_from_stage
  - Execute all subsequent stages
  - Generate new versions
    ↓
Update Database
  - Create new Documents/Assets
  - Increment version numbers
  - Preserve old versions
    ↓
Complete Rerun
  - Update WorkflowRun status
  - Notify user
```

### Data Protection

The rerun system protects existing data:

1. **No Deletion**: Old versions are never deleted
2. **Version Increment**: New outputs get higher version numbers
3. **Transactional**: Failures rollback without affecting existing data
4. **Isolation**: Rerun outputs don't overwrite non-target content

## API Reference

### Workflow Rerun

**Endpoint:** `POST /api/episodes/{episode_id}/rerun`

**Request Body:**
```json
{
    "from_stage": "image_render",
    "to_stage": "edit_export_preview",  // Optional
    "reason": "Reason for rerun",
    "config_overrides": {  // Optional
        "image_provider": "stable_diffusion_v2"
    }
}
```

**Response:**
```json
{
    "workflow_run_id": "new-workflow-uuid",
    "episode_id": "episode-uuid",
    "rerun_from_stage": "image_render",
    "parent_workflow_run_id": "parent-workflow-uuid",
    "status": "running",
    "created_at": "2026-04-11T10:30:00Z"
}
```

### Shot-Level Rerun

**Endpoint:** `POST /api/episodes/{episode_id}/rerun-shots`

**Request Body:**
```json
{
    "shot_ids": ["shot-uuid-1", "shot-uuid-2"],
    "stage_type": "image_render",
    "reason": "Adjust specific shots",
    "config_overrides": {  // Optional
        "prompt_adjustments": {
            "shot-uuid-1": "Add more dramatic lighting"
        }
    }
}
```

**Response:**
```json
{
    "workflow_run_id": "new-workflow-uuid",
    "episode_id": "episode-uuid",
    "rerun_shot_ids": ["shot-uuid-1", "shot-uuid-2"],
    "stage_type": "image_render",
    "status": "running",
    "created_at": "2026-04-11T10:30:00Z"
}
```

### Get Rerun History

**Endpoint:** `GET /api/episodes/{episode_id}/rerun-history`

**Response:**
```json
{
    "reruns": [
        {
            "workflow_run_id": "workflow-uuid",
            "rerun_from_stage": "image_render",
            "parent_workflow_run_id": "parent-uuid",
            "rerun_reason": "Updated character designs",
            "rerun_shot_ids": null,
            "status": "completed",
            "created_at": "2026-04-11T10:30:00Z",
            "completed_at": "2026-04-11T10:45:00Z"
        }
    ]
}
```

### Get Rerun Status

**Endpoint:** `GET /api/workflow-runs/{workflow_run_id}`

**Response:**
```json
{
    "id": "workflow-uuid",
    "episode_id": "episode-uuid",
    "workflow_kind": "media",
    "status": "running",
    "rerun_from_stage": "image_render",
    "parent_workflow_run_id": "parent-uuid",
    "current_stage": "tts",
    "progress": {
        "completed_stages": 2,
        "total_stages": 5,
        "percentage": 40
    }
}
```

## Usage Examples

### Example 1: Full Workflow Rerun After Script Update

```python
# Scenario: Script was updated, need to regenerate all media

# 1. Update script document
update_script(episode_id, new_script_content)

# 2. Trigger rerun from image_render
response = requests.post(
    f"/api/episodes/{episode_id}/rerun",
    json={
        "from_stage": "image_render",
        "reason": "Script updated with new dialogue and scene descriptions"
    }
)

workflow_run_id = response.json()["workflow_run_id"]

# 3. Monitor progress
while True:
    status = requests.get(f"/api/workflow-runs/{workflow_run_id}")
    if status.json()["status"] in ["completed", "failed"]:
        break
    time.sleep(5)
```

### Example 2: Shot-Level Rerun for Specific Issues

```python
# Scenario: QA identified issues with shots 3 and 7

# 1. Get problematic shot IDs
qa_report = requests.get(f"/api/episodes/{episode_id}/qa-reports/latest")
problematic_shots = extract_shot_ids_from_issues(qa_report.json())

# 2. Trigger shot-level rerun
response = requests.post(
    f"/api/episodes/{episode_id}/rerun-shots",
    json={
        "shot_ids": problematic_shots,
        "stage_type": "image_render",
        "reason": "Fix composition and lighting issues identified in QA"
    }
)

# 3. Wait for completion
workflow_run_id = response.json()["workflow_run_id"]
wait_for_completion(workflow_run_id)
```

### Example 3: Rerun with Configuration Overrides

```python
# Scenario: Want to try different image provider settings

response = requests.post(
    f"/api/episodes/{episode_id}/rerun",
    json={
        "from_stage": "image_render",
        "reason": "Testing new image provider settings",
        "config_overrides": {
            "image_provider": "stable_diffusion_xl",
            "quality": "high",
            "style_strength": 0.8
        }
    }
)
```

### Example 4: Partial Rerun (Specific Stage Range)

```python
# Scenario: Only need to regenerate audio and preview, not images

response = requests.post(
    f"/api/episodes/{episode_id}/rerun",
    json={
        "from_stage": "tts",
        "to_stage": "edit_export_preview",
        "reason": "New voice actor, regenerate audio and preview only"
    }
)
```

### Example 5: Review-Triggered Rerun

```python
# Scenario: User reviews content and requests revision

# 1. Submit review with revision decision
review_response = requests.post(
    f"/api/stage-tasks/{stage_task_id}/review",
    json={
        "decision": "revision_required",
        "comment": "Shots 3, 5, and 7 need better character expressions",
        "payload": {
            "rerun_from_stage": "image_render",
            "rerun_shot_ids": ["shot-3-uuid", "shot-5-uuid", "shot-7-uuid"],
            "reason": "Character expression improvements"
        }
    }
)

# 2. System automatically triggers rerun based on review payload
# No additional API call needed - rerun starts automatically
```

## Best Practices

### 1. Use Shot-Level Reruns When Possible

Shot-level reruns are more efficient:

```python
# Good: Only rerun problematic shots
POST /api/episodes/{episode_id}/rerun-shots
{
    "shot_ids": ["shot-3", "shot-7"],
    "stage_type": "image_render"
}

# Less efficient: Rerun entire workflow
POST /api/episodes/{episode_id}/rerun
{
    "from_stage": "image_render"
}
```

### 2. Provide Clear Rerun Reasons

Document why reruns are needed:

```python
# Good
{
    "reason": "Shot 3: Character expression doesn't match dialogue. Shot 7: Background too dark."
}

# Bad
{
    "reason": "Fix issues"
}
```

### 3. Monitor Rerun Progress

Track rerun status to handle failures:

```python
def monitor_rerun(workflow_run_id: str):
    """Monitor rerun progress and handle failures."""
    while True:
        status = get_workflow_status(workflow_run_id)
        
        if status["status"] == "completed":
            print("Rerun completed successfully")
            break
        elif status["status"] == "failed":
            print(f"Rerun failed: {status['error']}")
            handle_failure(workflow_run_id)
            break
        
        print(f"Progress: {status['progress']['percentage']}%")
        time.sleep(5)
```

### 4. Leverage Rerun History

Analyze rerun patterns to identify recurring issues:

```python
# Get rerun history
history = requests.get(f"/api/episodes/{episode_id}/rerun-history")

# Analyze patterns
rerun_reasons = [r["rerun_reason"] for r in history.json()["reruns"]]
most_rerun_stage = Counter([r["rerun_from_stage"] for r in history.json()["reruns"]]).most_common(1)

print(f"Most frequently rerun stage: {most_rerun_stage}")
```

### 5. Use Configuration Overrides Carefully

Test configuration changes before applying broadly:

```python
# Test with single shot first
test_response = requests.post(
    f"/api/episodes/{episode_id}/rerun-shots",
    json={
        "shot_ids": ["test-shot-uuid"],
        "stage_type": "image_render",
        "config_overrides": {"style_strength": 0.9}
    }
)

# If successful, apply to all shots
if test_successful:
    full_response = requests.post(
        f"/api/episodes/{episode_id}/rerun",
        json={
            "from_stage": "image_render",
            "config_overrides": {"style_strength": 0.9}
        }
    )
```

## Data Management

### Version Control

Reruns create new versions:

```python
# Original workflow creates version 1
original_run = create_workflow(episode_id)
# Creates: document_v1, asset_v1

# First rerun creates version 2
rerun_1 = rerun_workflow(episode_id, "image_render")
# Creates: document_v2, asset_v2
# Preserves: document_v1, asset_v1

# Second rerun creates version 3
rerun_2 = rerun_workflow(episode_id, "image_render")
# Creates: document_v3, asset_v3
# Preserves: document_v1, document_v2, asset_v1, asset_v2
```

### Accessing Previous Versions

```python
# Get all versions of a document
GET /api/episodes/{episode_id}/documents/{doc_type}/versions

# Get specific version
GET /api/episodes/{episode_id}/documents/{doc_type}/versions/{version}

# Compare versions
GET /api/episodes/{episode_id}/documents/{doc_type}/compare?v1=1&v2=2
```

### Cleanup Old Versions

Periodically clean up old versions to save storage:

```python
# Keep only last N versions
def cleanup_old_versions(episode_id: str, keep_versions: int = 3):
    """Keep only the most recent N versions."""
    documents = get_all_documents(episode_id)
    
    for doc_type in documents:
        versions = get_document_versions(episode_id, doc_type)
        
        # Sort by version descending
        versions.sort(key=lambda v: v["version"], reverse=True)
        
        # Delete old versions
        for version in versions[keep_versions:]:
            delete_document_version(episode_id, doc_type, version["version"])
```

## Troubleshooting

### Rerun Fails to Start

**Issue:** Rerun request returns error.

**Solutions:**
- Verify episode exists and is in valid state
- Check `from_stage` is a valid stage name
- Ensure no other rerun is currently running
- Verify user has rerun permissions

```python
# Check episode status
episode = requests.get(f"/api/episodes/{episode_id}")
if episode.json()["status"] == "running":
    print("Wait for current workflow to complete")
```

### Rerun Produces Same Results

**Issue:** Rerun generates identical output to previous run.

**Solutions:**
- Verify input documents were actually updated
- Check configuration overrides are being applied
- Ensure provider settings have changed
- Review rerun logs for actual changes

```python
# Verify document was updated
doc_before = get_document(episode_id, "script", version=1)
doc_after = get_document(episode_id, "script", version=2)

if doc_before == doc_after:
    print("Document not updated, rerun will produce same results")
```

### Shot-Level Rerun Affects Other Shots

**Issue:** Rerun of specific shots changes other shots.

**Solutions:**
- Verify `shot_ids` parameter is correctly specified
- Check rerun implementation properly filters shots
- Review logs to confirm only target shots processed

```python
# Verify shot filtering
rerun_info = requests.get(f"/api/workflow-runs/{workflow_run_id}")
processed_shots = rerun_info.json()["rerun_shot_ids"]

if set(processed_shots) != set(requested_shot_ids):
    print("Warning: Processed shots don't match requested shots")
```

### Rerun Fails Midway

**Issue:** Rerun starts but fails during execution.

**Solutions:**
- Check provider availability and quotas
- Review error logs for specific failure
- Verify input data is valid
- Retry with same parameters

```python
# Get failure details
workflow_run = requests.get(f"/api/workflow-runs/{workflow_run_id}")
error_info = workflow_run.json()["error"]

print(f"Failed at stage: {error_info['stage']}")
print(f"Error: {error_info['message']}")

# Retry if transient error
if is_transient_error(error_info):
    retry_rerun(episode_id, from_stage)
```

## Performance Considerations

### Rerun Efficiency

**Full Workflow Rerun:**
- Time: ~5-15 minutes (depends on episode length)
- Cost: Full provider API calls for all stages
- Use when: Major changes affect all content

**Shot-Level Rerun:**
- Time: ~1-3 minutes per shot
- Cost: Provider API calls only for target shots
- Use when: Specific shots need adjustment

### Parallel Processing

Shot-level reruns can process multiple shots in parallel:

```python
# Configure parallel processing
POST /api/episodes/{episode_id}/rerun-shots
{
    "shot_ids": ["shot-1", "shot-2", "shot-3", "shot-4", "shot-5"],
    "stage_type": "image_render",
    "parallel": true,  // Process shots in parallel
    "max_concurrent": 3  // Max 3 shots at once
}
```

### Resource Management

Monitor and limit concurrent reruns:

```python
# Check active reruns
active_reruns = requests.get("/api/workflow-runs?status=running&is_rerun=true")

if len(active_reruns.json()["runs"]) >= MAX_CONCURRENT_RERUNS:
    print("Too many active reruns, wait before starting new one")
```

## Security and Permissions

### Rerun Authorization

Implement proper access control:

```python
def authorize_rerun(user_id: str, episode_id: str) -> bool:
    """Check if user can trigger rerun for episode."""
    episode = get_episode(episode_id)
    
    # Check user is project member
    if not is_project_member(user_id, episode.project_id):
        return False
    
    # Check user has rerun permission
    if not has_permission(user_id, "rerun"):
        return False
    
    return True
```

### Audit Trail

All reruns are logged:

```python
# WorkflowRun includes
- parent_workflow_run_id: Links to original run
- rerun_from_stage: What stage was rerun
- rerun_reason: Why rerun was triggered
- rerun_shot_ids: Which shots were targeted
- created_by_user_id: Who triggered rerun
- created_at: When rerun started
```

### Rate Limiting

Prevent abuse with rate limits:

```python
# Limit reruns per user per hour
RERUN_RATE_LIMIT = 10  # Max 10 reruns per hour

def check_rate_limit(user_id: str) -> bool:
    """Check if user has exceeded rerun rate limit."""
    recent_reruns = count_recent_reruns(user_id, hours=1)
    return recent_reruns < RERUN_RATE_LIMIT
```

## Advanced Usage

### Conditional Reruns

Trigger reruns based on conditions:

```python
def conditional_rerun(episode_id: str):
    """Rerun if QA score below threshold."""
    qa_report = get_latest_qa_report(episode_id)
    
    if qa_report["score"] < 70:
        # Trigger rerun
        rerun_workflow(
            episode_id=episode_id,
            from_stage="image_render",
            reason=f"QA score {qa_report['score']} below threshold"
        )
```

### Batch Reruns

Rerun multiple episodes:

```python
def batch_rerun(episode_ids: List[str], from_stage: str):
    """Trigger reruns for multiple episodes."""
    results = []
    
    for episode_id in episode_ids:
        try:
            result = rerun_workflow(episode_id, from_stage)
            results.append({"episode_id": episode_id, "status": "started"})
        except Exception as e:
            results.append({"episode_id": episode_id, "status": "failed", "error": str(e)})
    
    return results
```

### Scheduled Reruns

Schedule reruns for off-peak hours:

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# Schedule rerun for 2 AM
scheduler.add_job(
    func=lambda: rerun_workflow(episode_id, "image_render"),
    trigger="cron",
    hour=2,
    minute=0
)

scheduler.start()
```

## Related Documentation

- **QA Runtime**: `apps/api/docs/QA_RUNTIME.md`
- **Review Flow**: `apps/api/docs/REVIEW_FLOW.md`
- **Design Document**: `.kiro/specs/qa-review-rerun/design.md`
- **Requirements**: `.kiro/specs/qa-review-rerun/requirements.md`
- **API Implementation**: `apps/api/RERUN_API_IMPLEMENTATION.md`

## Requirements Implemented

This implementation satisfies:

- **Requirement 7.1**: Creates new WorkflowRun for reruns
- **Requirement 7.2**: Sets rerun_from_stage field
- **Requirement 7.3**: Executes from specified stage through end
- **Requirement 7.4**: Preserves old versions of documents and assets
- **Requirement 7.5**: Records failure reasons and maintains old versions
- **Requirement 8.1**: Processes only specified shots
- **Requirement 8.2**: Generates new assets for specified shots only
- **Requirement 8.3**: Preserves other shots' existing assets
- **Requirement 8.4**: Preserves old assets on failure
- **Requirement 8.5**: Supports batch processing of multiple shots
- **Requirement 9.1**: Uses latest input document versions
- **Requirement 9.2**: Doesn't modify earlier stage outputs
- **Requirement 9.3**: Doesn't overwrite existing data on failure
- **Requirement 9.5**: Updates version numbers and preserves history
