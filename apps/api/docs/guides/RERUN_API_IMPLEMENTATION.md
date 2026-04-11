# Rerun API Implementation Summary

## Overview

This document summarizes the implementation of Task 9 "Rerun API" from the QA/Review/Rerun iteration. The implementation provides three REST API endpoints for managing workflow and shot-level reruns.

## Implementation Status

✅ **Task 9.1**: Created Workflow Rerun endpoint  
✅ **Task 9.2**: Created Shot Rerun endpoint  
✅ **Task 9.3**: Created Rerun History query endpoint  
✅ **Task 9.4**: Implemented Rerun schemas

## Files Created

### 1. Schema Definitions
**File**: `apps/api/app/schemas/rerun.py`

Defines Pydantic schemas for API requests and responses:
- `RerunWorkflowRequest`: Request to rerun from a specific stage
- `RerunShotsRequest`: Request to rerun specific shots
- `RerunWorkflowResponse`: Response after creating a rerun
- `RerunHistoryItem`: Single workflow run in history
- `RerunHistoryResponse`: Complete rerun history for an episode

**Requirements Implemented**: 7.1, 7.2, 8.1, 8.2, 12.1, 12.2, 12.3

### 2. API Routes
**File**: `apps/api/app/api/routes/rerun.py`

Implements three REST API endpoints:

#### POST /api/episodes/{episode_id}/rerun
Creates a workflow rerun from a specified stage.

**Request Body**:
```json
{
  "from_stage": "script",
  "reason": "Need to adjust dialogue"
}
```

**Response**:
```json
{
  "id": "uuid",
  "episode_id": "uuid",
  "workflow_kind": "episode",
  "status": "running",
  "rerun_from_stage": "script",
  "parent_workflow_run_id": "uuid",
  "rerun_reason": "Need to adjust dialogue",
  "rerun_shot_ids": null,
  "started_at": "2026-04-11T10:00:00Z"
}
```

**Requirements Implemented**: 7.1, 7.2

#### POST /api/episodes/{episode_id}/rerun-shots
Creates a shot-level rerun for specific shots.

**Request Body**:
```json
{
  "shot_ids": ["uuid1", "uuid2"],
  "stage_type": "image_render"
}
```

**Response**: Same as workflow rerun, but includes `rerun_shot_ids` array.

**Requirements Implemented**: 8.1, 8.2

#### GET /api/episodes/{episode_id}/rerun-history
Gets all workflow runs (including reruns) for an episode.

**Response**:
```json
{
  "episode_id": "uuid",
  "workflow_runs": [
    {
      "id": "uuid",
      "workflow_kind": "episode",
      "status": "completed",
      "rerun_from_stage": "script",
      "parent_workflow_run_id": "uuid",
      "rerun_reason": "Adjust dialogue",
      "rerun_shot_ids": null,
      "is_rerun": true,
      "started_at": "2026-04-11T10:00:00Z",
      "completed_at": "2026-04-11T10:15:00Z",
      "failure_reason": null
    }
  ],
  "total_count": 3,
  "rerun_count": 2
}
```

**Requirements Implemented**: 12.1, 12.2, 12.3

### 3. Router Registration
**File**: `apps/api/app/main.py`

Added rerun router to the FastAPI application:
```python
from app.api.routes.rerun import router as rerun_router
app.include_router(rerun_router)
```

### 4. Unit Tests
**File**: `apps/api/tests/unit/test_rerun_api.py`

Comprehensive test suite covering:
- Workflow rerun creation (success and error cases)
- Shot rerun creation (success and error cases)
- Rerun history retrieval (empty and with data)
- Rerun type identification (full vs shot-level)
- Error handling (episode not found, empty shot list, invalid stage type)

**Test Coverage**:
- 11 test cases covering all endpoints
- Tests for success paths and error conditions
- Validation of response schemas
- Database state verification

### 5. Manual Verification Script
**File**: `apps/api/test_rerun_api_manual.py`

Simple script to manually test the API endpoints when the server is running.

## Integration with Existing Code

The implementation integrates seamlessly with existing services:

1. **RerunService**: Uses the existing `RerunService` class from `apps/api/app/services/rerun_service.py`
   - `rerun_workflow()`: Creates workflow reruns
   - `rerun_shots()`: Creates shot-level reruns
   - `get_rerun_history()`: Retrieves rerun history

2. **WorkflowRepository**: Uses existing repository for workflow operations

3. **Database Models**: Works with existing `WorkflowRunModel` fields:
   - `rerun_from_stage`
   - `parent_workflow_run_id`
   - `rerun_reason`
   - `rerun_shot_ids_jsonb`

## API Design Decisions

### 1. Consistent Response Format
All endpoints return a consistent `RerunWorkflowResponse` structure, making it easy for clients to handle responses uniformly.

### 2. Clear Rerun Type Identification
The `is_rerun` field in history responses makes it easy to distinguish initial runs from reruns. The presence of `rerun_shot_ids` distinguishes full reruns from shot-level reruns.

### 3. Parent-Child Relationship
The `parent_workflow_run_id` field maintains the relationship between reruns and their parent workflows, enabling full history tracking.

### 4. Error Handling
- 404: Episode not found
- 400: Validation errors (empty shot list, invalid stage type)
- 422: Schema validation errors (invalid decision values)

### 5. Optional Fields
The `reason` field in workflow reruns is optional, allowing quick reruns without requiring detailed explanations.

## Requirements Validation

### Requirement 7.1: Create rerun WorkflowRun
✅ Implemented via POST /episodes/{episode_id}/rerun

### Requirement 7.2: Set rerun fields
✅ Sets `rerun_from_stage`, `parent_workflow_run_id`, `rerun_reason`

### Requirement 8.1: Shot-level rerun
✅ Implemented via POST /episodes/{episode_id}/rerun-shots

### Requirement 8.2: Specify shot_ids and stage_type
✅ Request accepts `shot_ids` array and `stage_type` enum

### Requirement 12.1: Query rerun history
✅ Implemented via GET /episodes/{episode_id}/rerun-history

### Requirement 12.2: Return all workflow runs
✅ Returns complete history ordered by started_at DESC

### Requirement 12.3: Identify rerun type
✅ Includes `is_rerun` flag and `rerun_shot_ids` for type identification

## Testing Strategy

### Unit Tests
The test suite covers:
1. **Happy paths**: Successful rerun creation and history retrieval
2. **Error cases**: Missing episodes, empty shot lists, invalid stage types
3. **Data validation**: Response schema validation, database state verification
4. **Edge cases**: Reruns without reasons, distinguishing rerun types

### Manual Testing
Use the provided manual verification script:
```bash
# Start the API server
cd apps/api
uvicorn app.main:app --reload

# In another terminal, run the manual test
python test_rerun_api_manual.py
```

## Next Steps

1. **Execute Reruns**: The API creates rerun WorkflowRun records but doesn't execute them. Integration with the workflow execution engine is needed.

2. **Authentication**: Add user authentication to track who initiated reruns (currently `user_id` is None).

3. **Permissions**: Add authorization checks to ensure only authorized users can trigger reruns.

4. **Webhooks**: Consider adding webhook notifications when reruns complete.

5. **Rate Limiting**: Add rate limiting to prevent excessive rerun requests.

## Dependencies

The implementation depends on:
- `RerunService`: Existing service for rerun logic
- `WorkflowRepository`: Existing repository for workflow operations
- Database models with rerun fields (already implemented)
- FastAPI and Pydantic for API framework

## Conclusion

Task 9 "Rerun API" has been successfully implemented with all subtasks completed:
- ✅ 9.1: Workflow Rerun endpoint
- ✅ 9.2: Shot Rerun endpoint
- ✅ 9.3: Rerun History endpoint
- ✅ 9.4: Rerun schemas

The implementation provides a clean, RESTful API for managing workflow and shot-level reruns, with comprehensive error handling and clear documentation.
