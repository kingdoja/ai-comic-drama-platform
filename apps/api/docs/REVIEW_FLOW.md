# Review Flow Documentation

## Overview

The Review Flow is a human-in-the-loop quality control mechanism that allows content creators to review, approve, or reject workflow outputs at critical checkpoints. Implemented as part of Iteration 5, it enables the system to pause workflows for human decision-making and trigger appropriate actions based on review outcomes.

## Key Concepts

### Review Gate

A **Review Gate** is a checkpoint in the workflow where execution pauses to await human review. When a stage is marked with `review_required=True`, the workflow will:

1. Complete the stage execution
2. Update the StageTask status to `review_pending`
3. Pause workflow execution
4. Wait for human review decision

### Review Decision

A **Review Decision** is the outcome of a human review, which can be:

- **approved**: Content meets quality standards, continue workflow
- **rejected**: Content is unacceptable, terminate workflow
- **revision_required**: Content needs improvement, trigger rerun

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                  Workflow Orchestrator                  │
│  Executes stages and checks for review gates           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
         ┌──────────────────┐
         │ Review Gate      │
         │ Service          │
         │                  │
         │ - Pause workflow │
         │ - Process review │
         │ - Resume/Stop    │
         └────────┬─────────┘
                  │
                  ↓
         ┌──────────────────┐
         │ Review           │
         │ Repository       │
         │                  │
         │ - Store reviews  │
         │ - Query history  │
         └──────────────────┘
```

### Data Flow

```
Stage Completion
    ↓
Check review_required flag
    ↓
If True → Pause Workflow
    ↓
Update StageTask.review_status = "pending"
    ↓
Notify User (Review Required)
    ↓
User Reviews Content
    ↓
User Submits Decision
    ↓
Create ReviewDecision Record
    ↓
Process Decision:
  - approved → Resume Workflow
  - rejected → Terminate Workflow
  - revision_required → Trigger Rerun
```

## Review Process

### Step 1: Workflow Pauses for Review

When a stage completes and `review_required=True`:

```python
# In workflow orchestrator
if stage.review_required:
    review_service.pause_for_review(stage_task_id)
    # Workflow execution stops here
```

The system:
- Sets `StageTask.review_status = "pending"`
- Sets `StageTask.task_status = "review_pending"`
- Notifies relevant users
- Displays review interface in workspace

### Step 2: User Reviews Content

The user accesses the review interface which displays:
- Stage output (documents, assets, preview)
- QA report (if available)
- Previous review comments
- Review decision options

### Step 3: User Submits Review Decision

The user submits a review with:
- **Decision**: approved/rejected/revision_required
- **Comment**: Explanation of the decision
- **Payload**: Additional data (e.g., rerun parameters)

```python
# API call
POST /api/stage-tasks/{stage_task_id}/review
{
    "decision": "revision_required",
    "comment": "Character expressions need adjustment",
    "payload": {
        "rerun_from_stage": "image_render",
        "rerun_shot_ids": ["shot-uuid-1", "shot-uuid-2"]
    }
}
```

### Step 4: System Processes Decision

The Review Service processes the decision:

```python
review = review_service.submit_review(
    stage_task_id=stage_task_id,
    reviewer_user_id=user_id,
    decision="revision_required",
    comment="Character expressions need adjustment",
    payload={"rerun_from_stage": "image_render"}
)

review_service.process_decision(review)
```

Based on the decision:

**Approved:**
- Update `StageTask.review_status = "approved"`
- Resume workflow execution
- Continue to next stage

**Rejected:**
- Update `StageTask.review_status = "rejected"`
- Set `WorkflowRun.status = "failed"`
- Terminate workflow
- Record rejection reason

**Revision Required:**
- Update `StageTask.review_status = "revision_required"`
- Trigger rerun from specified stage
- Create new WorkflowRun
- Execute rerun workflow

## Review Decision Types

### 1. Approved

**When to use:** Content meets quality standards and requirements.

**Example:**
```python
{
    "decision": "approved",
    "comment": "All shots look great, character designs are consistent"
}
```

**System action:**
- Resume workflow
- Continue to next stage
- Mark review as approved

### 2. Rejected

**When to use:** Content is fundamentally flawed or unacceptable.

**Example:**
```python
{
    "decision": "rejected",
    "comment": "Content violates brand guidelines, cannot proceed"
}
```

**System action:**
- Terminate workflow
- Mark episode as failed
- Require manual intervention

### 3. Revision Required

**When to use:** Content needs specific improvements or adjustments.

**Example:**
```python
{
    "decision": "revision_required",
    "comment": "Shot 3 and Shot 7 need better lighting",
    "payload": {
        "rerun_from_stage": "image_render",
        "rerun_shot_ids": ["shot-3-uuid", "shot-7-uuid"],
        "reason": "Lighting adjustments needed"
    }
}
```

**System action:**
- Trigger rerun with specified parameters
- Create new WorkflowRun
- Execute from specified stage
- Preserve other content

## API Reference

### Submit Review

**Endpoint:** `POST /api/stage-tasks/{stage_task_id}/review`

**Request Body:**
```json
{
    "decision": "approved|rejected|revision_required",
    "comment": "Review comments",
    "payload": {
        "rerun_from_stage": "stage_name",
        "rerun_shot_ids": ["uuid1", "uuid2"],
        "reason": "Specific reason for rerun"
    }
}
```

**Response:**
```json
{
    "id": "review-uuid",
    "stage_task_id": "stage-task-uuid",
    "decision": "revision_required",
    "comment": "Review comments",
    "reviewer_user_id": "user-uuid",
    "created_at": "2026-04-11T10:30:00Z"
}
```

### Get Review History

**Endpoint:** `GET /api/episodes/{episode_id}/reviews`

**Response:**
```json
{
    "reviews": [
        {
            "id": "review-uuid",
            "stage_task_id": "stage-task-uuid",
            "stage_type": "qa",
            "decision": "approved",
            "comment": "Looks good",
            "reviewer_user_id": "user-uuid",
            "created_at": "2026-04-11T10:30:00Z"
        }
    ]
}
```

### Get Pending Reviews

**Endpoint:** `GET /api/episodes/{episode_id}/pending-reviews`

**Response:**
```json
{
    "pending_reviews": [
        {
            "stage_task_id": "stage-task-uuid",
            "stage_type": "qa",
            "workflow_run_id": "workflow-uuid",
            "created_at": "2026-04-11T10:00:00Z",
            "qa_report": {
                "score": 75.0,
                "issue_count": 3,
                "severity": "major"
            }
        }
    ]
}
```

## Integration with QA

The Review Flow is tightly integrated with QA checks:

### QA-Triggered Reviews

When QA fails, the system can automatically pause for review:

```python
# In QA Stage
qa_result = qa_runtime.execute_qa(...)

if qa_runtime.should_block_workflow(qa_result):
    # Pause for review
    review_service.pause_for_review(stage_task_id)
```

### Review with QA Context

The review interface displays QA results:

```python
# Get QA report for review context
qa_report = qa_repository.get_latest_for_stage(stage_task_id, db)

# Display in review UI
{
    "stage_task": stage_task,
    "qa_report": qa_report,
    "review_options": ["approved", "rejected", "revision_required"]
}
```

## Integration with Rerun

Review decisions can trigger reruns:

### Automatic Rerun Trigger

When decision is `revision_required`:

```python
if review.decision == "revision_required":
    # Extract rerun parameters from payload
    rerun_params = review.payload_jsonb
    
    # Trigger rerun
    rerun_service.rerun_workflow(
        episode_id=episode_id,
        from_stage=rerun_params.get("rerun_from_stage"),
        user_id=review.reviewer_user_id,
        reason=review.comment_text
    )
```

### Rerun with Shot Selection

For targeted improvements:

```python
if review.payload_jsonb.get("rerun_shot_ids"):
    # Trigger shot-level rerun
    rerun_service.rerun_shots(
        episode_id=episode_id,
        shot_ids=review.payload_jsonb["rerun_shot_ids"],
        stage_type=review.payload_jsonb["rerun_from_stage"],
        user_id=review.reviewer_user_id
    )
```

## Usage Examples

### Example 1: Simple Approval

```python
# User reviews and approves
response = requests.post(
    f"/api/stage-tasks/{stage_task_id}/review",
    json={
        "decision": "approved",
        "comment": "Content looks great, ready to proceed"
    }
)

# Workflow automatically resumes
```

### Example 2: Rejection with Reason

```python
# User reviews and rejects
response = requests.post(
    f"/api/stage-tasks/{stage_task_id}/review",
    json={
        "decision": "rejected",
        "comment": "Content violates brand guidelines. Major rework needed."
    }
)

# Workflow terminates, manual intervention required
```

### Example 3: Revision with Full Rerun

```python
# User requests full rerun from image_render stage
response = requests.post(
    f"/api/stage-tasks/{stage_task_id}/review",
    json={
        "decision": "revision_required",
        "comment": "All images need better composition",
        "payload": {
            "rerun_from_stage": "image_render",
            "reason": "Composition improvements needed"
        }
    }
)

# System triggers full rerun from image_render stage
```

### Example 4: Revision with Partial Rerun

```python
# User requests rerun of specific shots
response = requests.post(
    f"/api/stage-tasks/{stage_task_id}/review",
    json={
        "decision": "revision_required",
        "comment": "Shots 3 and 7 need better lighting",
        "payload": {
            "rerun_from_stage": "image_render",
            "rerun_shot_ids": ["shot-3-uuid", "shot-7-uuid"],
            "reason": "Lighting adjustments for specific shots"
        }
    }
)

# System triggers rerun only for specified shots
```

## Best Practices

### 1. Provide Clear Comments

Always include specific, actionable feedback:

```python
# Good
"Shot 3: Character expression doesn't match dialogue emotion. Shot 7: Background too dark."

# Bad
"Some shots need work"
```

### 2. Use Appropriate Decision Types

- Use **approved** only when content truly meets standards
- Use **rejected** sparingly, for fundamental issues
- Use **revision_required** for specific, fixable issues

### 3. Leverage Partial Reruns

When only some content needs revision:

```python
# Rerun only problematic shots
{
    "decision": "revision_required",
    "payload": {
        "rerun_shot_ids": ["shot-3", "shot-7"]  # Only these shots
    }
}
```

### 4. Track Review History

Monitor review patterns to identify recurring issues:

```python
# Get all reviews for episode
reviews = requests.get(f"/api/episodes/{episode_id}/reviews")

# Analyze patterns
rejection_reasons = [r["comment"] for r in reviews if r["decision"] == "rejected"]
```

## Troubleshooting

### Workflow Not Resuming After Approval

**Issue:** Workflow remains paused after approval.

**Solution:**
- Check `StageTask.review_status` is set to "approved"
- Verify workflow orchestrator is polling for status changes
- Check for errors in workflow execution logs

### Review Submission Fails

**Issue:** API returns error when submitting review.

**Solution:**
- Verify `stage_task_id` is valid and in `review_pending` status
- Check user has review permissions
- Ensure payload format is correct

### Rerun Not Triggered After Revision Decision

**Issue:** Rerun doesn't start after `revision_required` decision.

**Solution:**
- Verify `payload` contains required rerun parameters
- Check `rerun_from_stage` is a valid stage name
- Verify rerun service is properly configured

## Security Considerations

### Review Permissions

Implement proper authorization:

```python
def submit_review(stage_task_id: UUID, user_id: UUID, ...):
    # Verify user has review permission
    if not has_review_permission(user_id, stage_task_id):
        raise PermissionError("User not authorized to review")
    
    # Process review
    ...
```

### Audit Trail

All reviews are logged:

```python
# ReviewDecision includes
- reviewer_user_id: Who made the decision
- created_at: When decision was made
- comment_text: What was decided and why
- payload_jsonb: Additional context
```

### Prevent Duplicate Reviews

Ensure only one active review per stage task:

```python
# Check for existing review
existing = review_repository.get_latest_for_stage_task(stage_task_id, db)
if existing and existing.created_at > stage_task.updated_at:
    raise ValueError("Stage task already reviewed")
```

## Related Documentation

- **QA Runtime**: `apps/api/docs/QA_RUNTIME.md`
- **Rerun Guide**: `apps/api/docs/RERUN_GUIDE.md`
- **Design Document**: `.kiro/specs/qa-review-rerun/design.md`
- **Requirements**: `.kiro/specs/qa-review-rerun/requirements.md`
- **API Implementation**: `apps/api/REVIEW_API_IMPLEMENTATION.md`

## Requirements Implemented

This implementation satisfies:

- **Requirement 5.1**: Workflow pauses when stage marked as review_required
- **Requirement 5.2**: StageTask review_status updated to "pending"
- **Requirement 5.3**: ReviewDecision records created on submission
- **Requirement 5.4**: Approved decisions resume workflow
- **Requirement 5.5**: Rejected decisions terminate workflow
- **Requirement 6.1**: Reviewer and decision recorded
- **Requirement 6.2**: Comments saved to ReviewDecision
- **Requirement 6.3**: Revision decisions record required changes
- **Requirement 6.4**: StageTask review_status updated after review
- **Requirement 6.5**: Revision decisions trigger rerun
- **Requirement 11.1**: Review status displayed in workspace
