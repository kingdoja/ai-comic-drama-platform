# Design Document

## Overview

文本主链路是 AI 漫剧创作者工作台的核心功能，负责将原始素材转化为结构化的分镜脚本。本设计实现了从素材输入到分镜输出的完整文本生产流程，包括 5 个文本 agent 的协作、workflow 编排、数据持久化和一致性保证机制。

本设计遵循以下核心原则：
- **Workflow First**: 主业务流程由 workflow 驱动，而不是由 agent 自行串接
- **Artifact First**: 系统事实来源是结构化产物，不是聊天上下文
- **Runtime Separation**: 文本生成、workflow 编排和数据持久化职责分离
- **Explicit State**: 所有状态都显式建模，可追踪、可回滚
- **Anti-Drift**: 通过多层机制防止内容偏离原始设定

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                          API Layer                              │
│  POST /workflow/start  │  GET /workspace  │  PUT /documents    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────────┐
│                      Workflow Service                           │
│  - Episode Workflow Orchestrator                                │
│  - Stage Task Input Builder                                     │
│  - State Machine Controller                                     │
│  - Retry & Failure Handler                                      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Runtime                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Brief Agent  │  │ Story Bible  │  │  Character   │         │
│  │              │  │    Agent     │  │    Agent     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │ Script Agent │  │  Storyboard  │                           │
│  │              │  │    Agent     │                           │
│  └──────────────┘  └──────────────┘                           │
│                                                                 │
│  Common Pipeline: Loader → Normalizer → Planner →              │
│                   Generator → Critic → Validator → Committer   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                 │
│  PostgreSQL: projects, episodes, workflow_runs, stage_tasks,    │
│              documents, shots                                   │
│  Repositories: ProjectRepo, EpisodeRepo, WorkflowRepo,          │
│                DocumentRepo, ShotRepo, StageTaskRepo            │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Request
    ↓
API: POST /projects/{id}/episodes/{id}/workflow/start
    ↓
Workflow Service: create WorkflowRun
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 1: Brief                                             │
│  Input: raw_material, platform, duration_target             │
│  Output: brief document                                     │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 2: Story Bible                                       │
│  Input: brief, raw_material_summary                         │
│  Output: story_bible document                               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 3: Character                                         │
│  Input: brief, story_bible                                  │
│  Output: character_profile document                         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 4: Script                                            │
│  Input: brief, story_bible, character_profile               │
│  Output: script_draft document                              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  Stage 5: Storyboard                                        │
│  Input: script_draft, platform_constraints                  │
│  Output: shots, visual_spec document                        │
└────────────────────┬────────────────────────────────────────┘
                     ↓
Workflow Service: update WorkflowRun status
    ↓
API: GET /workspace returns aggregated view
```

## Components and Interfaces

### 1. Workflow Service

**Responsibilities:**
- Orchestrate episode workflow execution
- Build StageTaskInput for each stage
- Control state machine transitions
- Handle stage failures and retries
- Persist workflow execution records

**Key Methods:**

```python
class WorkflowService:
    def start_episode_workflow(
        self,
        project_id: UUID,
        episode_id: UUID,
        payload: StartEpisodeWorkflowRequest
    ) -> WorkflowRun:
        """Start a new episode workflow execution"""
        
    def build_stage_input(
        self,
        workflow_run_id: UUID,
        stage_type: str,
        previous_outputs: List[StageTaskOutput]
    ) -> StageTaskInput:
        """Build input for a specific stage"""
        
    def handle_stage_output(
        self,
        stage_output: StageTaskOutput
    ) -> NextAction:
        """Process stage output and decide next action"""
        
    def update_workflow_state(
        self,
        workflow_run_id: UUID,
        new_status: str
    ) -> None:
        """Update workflow run status"""
```

**StageTaskInput Schema:**

```python
@dataclass
class StageTaskInput:
    workflow_run_id: UUID
    project_id: UUID
    episode_id: UUID
    stage_type: str  # "brief", "story_bible", "character", "script", "storyboard"
    input_refs: List[DocumentRef]  # References to input documents
    locked_refs: List[LockedRef]  # References to locked fields
    constraints: Dict[str, Any]  # Stage-specific constraints
    target_ref_ids: List[UUID]  # For targeted rerun (empty for full run)
```

**StageTaskOutput Schema:**

```python
@dataclass
class StageTaskOutput:
    status: str  # "succeeded", "failed", "partial"
    document_refs: List[DocumentRef]  # Created/updated documents
    asset_refs: List[AssetRef]  # Created assets (for storyboard stage)
    warnings: List[Warning]  # Non-fatal issues
    quality_notes: List[str]  # Quality observations
    metrics: Dict[str, Any]  # duration_ms, token_usage, etc.
```

### 2. Agent Runtime

**Responsibilities:**
- Execute text generation stages
- Implement common agent pipeline
- Call LLM with structured prompts
- Validate and commit outputs
- Perform consistency checks

**Common Agent Pipeline:**

```python
class BaseAgent:
    def execute(self, task_input: StageTaskInput) -> StageTaskOutput:
        # 1. Loader: Load input documents and refs
        context = self.loader.load(task_input.input_refs, task_input.locked_refs)
        
        # 2. Normalizer: Clean and structure context
        normalized = self.normalizer.normalize(context, task_input.constraints)
        
        # 3. Planner: Create execution plan
        plan = self.planner.build(normalized, task_input.stage_type)
        
        # 4. Generator: Call LLM to generate content
        draft = self.generator.generate(plan, schema=self.output_schema)
        
        # 5. Critic: Self-review for consistency
        reviewed = self.critic.review(draft, normalized)
        
        # 6. Validator: Validate schema and constraints
        valid = self.validator.validate(reviewed, task_input.locked_refs)
        
        # 7. Committer: Persist to database
        refs = self.committer.commit(valid, task_input.project_id, task_input.episode_id)
        
        return StageTaskOutput(
            status="succeeded",
            document_refs=refs.documents,
            asset_refs=refs.assets,
            warnings=refs.warnings,
            metrics=refs.metrics
        )
```

### 3. Individual Agents

#### Brief Agent

**Input:**
- Raw material (novel excerpt or script)
- Platform (e.g., "douyin", "kuaishou")
- Target duration (e.g., 60 seconds)
- Target audience

**Output:**
- Brief document with fields:
  - genre: str
  - target_audience: str
  - core_selling_points: List[str] (3-5 items)
  - main_conflict: str
  - adaptation_risks: List[str]
  - target_style: str
  - tone: str

**Consistency Anchors:**
- Core selling points (locked for downstream)
- Main conflict (locked for downstream)

#### Story Bible Agent

**Input:**
- Brief document
- Raw material summary

**Output:**
- Story Bible document with fields:
  - world_rules: List[str]
  - timeline: List[TimelineEvent]
  - relationship_baseline: Dict[str, List[str]]
  - forbidden_conflicts: List[str]
  - key_settings: Dict[str, str]

**Consistency Anchors:**
- Forbidden conflicts (hard constraints for downstream)
- World rules (hard constraints for downstream)

#### Character Agent

**Input:**
- Brief document
- Story Bible document

**Output:**
- Character Profile document with fields:
  - characters: List[Character]
    - name: str
    - role: str (protagonist, antagonist, supporting)
    - goal: str
    - motivation: str
    - speaking_style: str
    - visual_anchor: str (for image generation)
    - personality_traits: List[str]
    - relationships: Dict[str, str]

**Consistency Anchors:**
- Character names (locked)
- Visual anchors (locked)
- Core personality traits (locked)

#### Script Agent

**Input:**
- Brief document
- Story Bible document
- Character Profile document

**Output:**
- Script Draft document with fields:
  - scenes: List[Scene]
    - scene_no: int
    - location: str
    - characters: List[str]
    - goal: str
    - dialogue: List[DialogueLine]
    - emotion_beats: List[str]
    - duration_estimate_sec: int

**Consistency Anchors:**
- Character behaviors must match character_profile
- Scene conflicts must not violate story_bible.forbidden_conflicts

#### Storyboard Agent

**Input:**
- Script Draft document
- Platform constraints (aspect ratio, max shots, etc.)

**Output:**
- Shots (database records)
  - shot_code: str (e.g., "S01_001")
  - scene_no: int
  - shot_no: int
  - duration_ms: int
  - camera_size: str (close-up, medium, wide)
  - camera_angle: str (eye-level, high, low)
  - characters: List[str]
  - action_text: str
  - dialogue_text: str
  - visual_constraints: Dict[str, Any]
- Visual Spec document with fields:
  - shots: List[ShotSpec]
    - shot_id: UUID
    - render_prompt: str
    - character_refs: List[str]
    - style_keywords: List[str]
    - composition: str

**Consistency Anchors:**
- Character appearances must match character_profile.visual_anchor
- Total duration must not exceed target_duration * 1.2

### 4. Workspace Service

**Responsibilities:**
- Aggregate project, episode, workflow, documents, and shots
- Provide unified view for frontend
- Handle document versioning

**Key Method:**

```python
class WorkspaceService:
    def build_workspace(
        self,
        project_id: UUID,
        episode_id: UUID
    ) -> EpisodeWorkspaceResponse:
        """Build aggregated workspace view"""
        project = self.project_repo.get(project_id)
        episode = self.episode_repo.get(episode_id)
        workflow = self.workflow_repo.get_latest_for_episode(episode_id)
        documents = self.document_repo.get_latest_by_episode(episode_id)
        shots = self.shot_repo.get_by_episode(episode_id)
        stage_tasks = self.stage_task_repo.get_by_workflow(workflow.id)
        
        return EpisodeWorkspaceResponse(
            project=project,
            episode=episode,
            workflow=workflow,
            documents=self._group_documents_by_type(documents),
            shots=shots,
            stage_tasks=stage_tasks
        )
```

## Data Models

### WorkflowRun

```python
class WorkflowRun:
    id: UUID
    project_id: UUID
    episode_id: UUID
    workflow_kind: str  # "episode_workflow"
    temporal_workflow_id: str
    temporal_run_id: str
    status: str  # "created", "running", "succeeded", "failed"
    started_by_user_id: UUID | None
    rerun_from_stage: str | None
    failure_reason: str | None
    started_at: datetime
    finished_at: datetime | None
    created_at: datetime
```

### StageTask

```python
class StageTask:
    id: UUID
    workflow_run_id: UUID
    project_id: UUID
    episode_id: UUID
    stage_type: str  # "brief", "story_bible", "character", "script", "storyboard"
    task_status: str  # "pending", "running", "succeeded", "failed"
    agent_name: str | None
    worker_kind: str  # "agent_runtime"
    attempt_no: int
    max_retries: int
    input_ref_jsonb: List[Dict]
    output_ref_jsonb: List[Dict]
    review_required: bool
    review_status: str | None
    error_code: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

### Document

```python
class Document:
    id: UUID
    project_id: UUID
    episode_id: UUID | None
    stage_task_id: UUID | None
    document_type: str  # "brief", "story_bible", "character_profile", "script_draft", "visual_spec"
    version: int
    status: str  # "draft", "confirmed", "locked"
    title: str | None
    content_jsonb: Dict  # Type-specific structured content
    summary_text: str | None
    created_by: UUID | None  # None for AI-generated
    created_at: datetime
    updated_at: datetime
```

### Shot

```python
class Shot:
    id: UUID
    project_id: UUID
    episode_id: UUID
    stage_task_id: UUID | None
    scene_no: int
    shot_no: int
    shot_code: str  # "S01_001"
    status: str  # "draft", "confirmed", "locked"
    duration_ms: int
    camera_size: str | None  # "close-up", "medium", "wide"
    camera_angle: str | None  # "eye-level", "high", "low"
    movement_type: str | None  # "static", "pan", "zoom"
    characters_jsonb: List[str]
    action_text: str | None
    dialogue_text: str | None
    visual_constraints_jsonb: Dict
    version: int
    created_at: datetime
    updated_at: datetime
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Workflow启动创建记录
*For any* valid project and episode combination, when a workflow is started, a WorkflowRun record should be created with status "created" or "running" and all required fields populated.
**Validates: Requirements 1.1**

### Property 2: Stage执行顺序保持
*For any* completed workflow, the created_at timestamps of stage_tasks should follow the order: brief < story_bible < character < script < storyboard.
**Validates: Requirements 1.2**

### Property 3: Stage完成创建任务记录
*For any* stage execution, when the stage completes (successfully or with failure), a StageTask record should exist with the correct stage_type and final status.
**Validates: Requirements 1.3**

### Property 4: Workflow完成更新状态
*For any* workflow where all text stages have succeeded, the WorkflowRun status should be updated to "succeeded" or equivalent completion status.
**Validates: Requirements 1.4**

### Property 5: Workflow失败保留产物
*For any* workflow that fails at stage N, all documents created by stages 1 to N-1 should remain in the database unchanged.
**Validates: Requirements 1.5**

### Property 6: Brief包含必需元素
*For any* brief document generated by Brief Agent, the content_jsonb should contain non-empty values for genre, target_audience, core_selling_points, main_conflict, and target_style.
**Validates: Requirements 2.1, 2.2**

### Property 7: Brief持久化关联正确
*For any* successfully generated brief, a Document record should exist with document_type="brief", associated with the correct episode_id and stage_task_id.
**Validates: Requirements 2.3**

### Property 8: Brief缺失字段拒绝
*For any* brief document missing required fields (genre, core_selling_points, or main_conflict), the validator should reject submission and return a validation error.
**Validates: Requirements 2.4**

### Property 9: Brief失败保留错误
*For any* brief generation failure, the StageTask record should contain non-empty error_code and error_message fields.
**Validates: Requirements 2.5**

### Property 10: Story Bible包含必需元素
*For any* story_bible document generated by Story Bible Agent, the content_jsonb should contain non-empty values for world_rules and forbidden_conflicts.
**Validates: Requirements 3.1, 3.2**

### Property 11: Story Bible持久化标记约束
*For any* successfully generated story_bible, the Document record should be marked (via status or metadata) as a constraint source for downstream stages.
**Validates: Requirements 3.3**

### Property 12: Story Bible冲突生成警告
*For any* story_bible that contains rules conflicting with the brief's core_selling_points, the StageTaskOutput should include warnings describing the conflicts.
**Validates: Requirements 3.4**

### Property 13: Story Bible失败隔离
*For any* story_bible generation failure, the existing brief document should remain unchanged (same version, same content_jsonb).
**Validates: Requirements 3.5**

### Property 14: Character Profile包含必需元素
*For any* character_profile document generated by Character Agent, the content_jsonb should contain a non-empty characters array, and each character should have name, role, goal, and motivation fields.
**Validates: Requirements 4.1, 4.2**

### Property 15: Character Profile标记可锁定字段
*For any* successfully generated character_profile, key fields (character names, visual_anchors) should be marked as lockable in the document metadata or status.
**Validates: Requirements 4.3**

### Property 16: Character缺失视觉锚点生成警告
*For any* character_profile where at least one character lacks a visual_anchor, the StageTaskOutput should include a warning about the missing visual anchor.
**Validates: Requirements 4.4**

### Property 17: Character失败隔离上游
*For any* character_profile generation failure, the existing brief and story_bible documents should remain unchanged.
**Validates: Requirements 4.5**

### Property 18: Script包含场次和台词
*For any* script_draft document generated by Script Agent, the content_jsonb should contain a non-empty scenes array, and each scene should have scene_no, location, characters, and dialogue fields.
**Validates: Requirements 5.1, 5.2**

### Property 19: Script持久化更新版本
*For any* successfully generated script_draft, the episode's script_version field should be incremented by 1.
**Validates: Requirements 5.3**

### Property 20: Script角色冲突生成警告
*For any* script_draft where character behaviors deviate from character_profile settings, the StageTaskOutput should include warnings describing the inconsistencies.
**Validates: Requirements 5.4**

### Property 21: Script失败保护旧版本
*For any* script generation failure, if a previous script_draft version exists, it should remain unchanged and accessible.
**Validates: Requirements 5.5**

### Property 22: Storyboard生成Shot记录
*For any* successful storyboard stage execution, at least one Shot record should be created and associated with the correct episode_id.
**Validates: Requirements 6.1**

### Property 23: Shot包含必需字段且ID唯一
*For any* set of shots generated in a single storyboard execution, each shot should have a unique id, shot_code, scene_no, shot_no, duration_ms, and characters_jsonb.
**Validates: Requirements 6.2**

### Property 24: Shot持久化关联Episode
*For any* successfully generated shot, the Shot record should have a non-null episode_id matching the workflow's episode_id.
**Validates: Requirements 6.3**

### Property 25: Visual Spec包含渲染规格
*For any* visual_spec document generated by Storyboard Agent, the content_jsonb should contain a shots array where each shot has render_prompt and style_keywords.
**Validates: Requirements 6.4**

### Property 26: Shot超时生成警告
*For any* storyboard where the sum of all shot durations exceeds the episode's target_duration_sec * 1.2, the StageTaskOutput should include a warning about duration overflow.
**Validates: Requirements 6.5**

### Property 27: 内容与Brief一致性检查
*For any* agent output (story_bible, character_profile, script_draft, visual_spec), the critic should verify that the content aligns with the brief's core_selling_points, and any deviation should generate a warning.
**Validates: Requirements 7.1**

### Property 28: 角色行为一致性检查
*For any* script_draft or visual_spec that references characters, the critic should verify that character behaviors match the character_profile, and any inconsistency should generate a warning.
**Validates: Requirements 7.2**

### Property 29: 世界规则一致性检查
*For any* agent output that involves world rules, the critic should verify that no forbidden_conflicts from story_bible are violated, and any violation should generate a warning.
**Validates: Requirements 7.3**

### Property 30: 一致性偏离生成警告和建议
*For any* detected consistency deviation, the warning should include both a description of the deviation and a suggested correction.
**Validates: Requirements 7.4**

### Property 31: 锁定字段修改拒绝
*For any* document edit or agent output that attempts to modify a locked field, the validator should reject the operation and return a validation error.
**Validates: Requirements 7.5**

### Property 32: Workspace返回完整聚合
*For any* valid workspace request, the response should include non-null project, episode, workflow (if exists), documents (grouped by type), and shots (if exist).
**Validates: Requirements 8.1**

### Property 33: Workspace返回最新文档版本
*For any* workspace with multiple document versions of the same type, only the document with the highest version number should be included in the response.
**Validates: Requirements 8.2**

### Property 34: Workspace返回完整Shot列表
*For any* workspace with shots, all shots associated with the episode should be included with their complete visual_constraints_jsonb.
**Validates: Requirements 8.3**

### Property 35: Workspace返回Workflow状态
*For any* workspace with an active workflow, the response should include the workflow's current status and a list of stage_tasks with their statuses.
**Validates: Requirements 8.4**

### Property 36: Document编辑创建新版本
*For any* document edit operation, a new Document record should be created with version = old_version + 1, and the old document should remain unchanged.
**Validates: Requirements 9.1**

### Property 37: Document编辑记录来源
*For any* document edit, the new document's created_by field should be non-null (user ID) to distinguish it from AI-generated documents (created_by = null).
**Validates: Requirements 9.2**

### Property 38: Document锁定字段编辑拒绝
*For any* document with locked fields, an edit attempt that modifies those fields should be rejected with a validation error.
**Validates: Requirements 9.3**

### Property 39: Document编辑更新时间戳
*For any* successful document edit, the new document's updated_at timestamp should be greater than the old document's updated_at.
**Validates: Requirements 9.4**

### Property 40: Document编辑Schema校验
*For any* document edit with invalid content_jsonb (missing required fields or wrong types), the operation should be rejected with a schema validation error.
**Validates: Requirements 9.5**

### Property 41: Agent执行遵循Pipeline顺序
*For any* agent execution, the internal pipeline stages (Loader, Normalizer, Planner, Generator, Critic, Validator, Committer) should execute in that exact order.
**Validates: Requirements 10.1**

### Property 42: Loader加载Refs
*For any* agent execution, the Loader should retrieve all documents referenced in input_refs and locked_refs from the database.
**Validates: Requirements 10.2**

### Property 43: Generator调用LLM
*For any* agent execution, the Generator should make at least one LLM API call with a non-empty prompt and output schema.
**Validates: Requirements 10.3**

### Property 44: Validator校验Schema
*For any* agent execution, the Validator should verify that the generated content matches the expected JSON schema and contains all required fields.
**Validates: Requirements 10.4**

### Property 45: Committer持久化并返回Refs
*For any* successful agent execution, the Committer should persist the output to the database and return document_refs in the StageTaskOutput.
**Validates: Requirements 10.5**

### Property 46: Workflow构造StageTaskInput
*For any* stage execution initiated by the workflow orchestrator, a StageTaskInput should be constructed with correct workflow_run_id, stage_type, and input_refs.
**Validates: Requirements 11.1**

### Property 47: Agent返回Output不修改状态
*For any* agent execution, the agent should return a StageTaskOutput without directly modifying the WorkflowRun status or Episode status.
**Validates: Requirements 11.2**

### Property 48: Workflow根据Output决定下一步
*For any* StageTaskOutput with status="succeeded", the workflow should proceed to the next stage; for status="failed", the workflow should decide whether to retry or fail.
**Validates: Requirements 11.3**

### Property 49: Workflow控制重试
*For any* stage failure, the retry decision (whether to retry and how many times) should be made by the workflow orchestrator, not by the agent.
**Validates: Requirements 11.4**

### Property 50: Workflow控制审核暂停
*For any* stage that requires human review, the workflow orchestrator should pause execution and wait for a ReviewDecision before proceeding.
**Validates: Requirements 11.5**

### Property 51: Stage开始记录元数据
*For any* stage execution start, the StageTask record should have non-null stage_type, started_at, and attempt_no fields.
**Validates: Requirements 12.1**

### Property 52: Stage完成记录指标
*For any* stage execution completion, the StageTask record should have non-null finished_at, and the output_ref_jsonb should contain duration_ms and token_usage metrics.
**Validates: Requirements 12.2**

### Property 53: Stage失败记录错误
*For any* stage execution failure, the StageTask record should have non-null error_code and error_message fields.
**Validates: Requirements 12.3**

### Property 54: LLM调用记录详情
*For any* LLM API call, the system should log the prompt, model name, temperature, and response (or response summary) for debugging and analysis.
**Validates: Requirements 12.4**

### Property 55: Document提交记录元数据
*For any* document commit, the Document record should have non-null document_type, version, and created_by (or null for AI-generated) fields.
**Validates: Requirements 12.5**

## Error Handling

### Error Categories

1. **Input Validation Errors**
   - Missing required fields in API requests
   - Invalid UUIDs or references
   - Schema validation failures
   - Locked field modification attempts

2. **Agent Execution Errors**
   - LLM API failures (timeout, rate limit, invalid response)
   - JSON parsing errors
   - Schema validation failures
   - Consistency check failures (warnings, not errors)

3. **Data Persistence Errors**
   - Database connection failures
   - Constraint violations
   - Transaction rollback failures

4. **Workflow Orchestration Errors**
   - Stage dependency failures
   - Timeout errors
   - Unexpected state transitions

### Error Handling Strategies

1. **Validation Errors**: Return 400 Bad Request with detailed error message
2. **LLM Failures**: Retry up to 3 times with exponential backoff, then fail stage
3. **Database Errors**: Rollback transaction, log error, return 500 Internal Server Error
4. **Workflow Errors**: Mark workflow as failed, preserve intermediate artifacts, allow manual recovery

### Failure Isolation

- Brief failure: No impact on project/episode
- Story Bible failure: Brief remains intact
- Character failure: Brief and Story Bible remain intact
- Script failure: Previous script version protected, upstream documents intact
- Storyboard failure: Script and upstream documents intact

## Testing Strategy

### Unit Testing

Unit tests will verify specific behaviors and edge cases:

1. **Workflow Service Tests**
   - Test workflow creation with valid/invalid inputs
   - Test stage input construction for each stage type
   - Test state machine transitions
   - Test failure handling and retry logic

2. **Agent Pipeline Tests**
   - Test each pipeline stage (Loader, Normalizer, etc.) in isolation
   - Test error propagation through pipeline
   - Test locked field protection
   - Test consistency check logic

3. **Repository Tests**
   - Test CRUD operations for each model
   - Test version increment logic
   - Test query methods (get_latest_by_episode, etc.)
   - Test transaction rollback on errors

4. **Workspace Service Tests**
   - Test aggregation logic with various data states
   - Test document grouping by type
   - Test latest version selection
   - Test handling of missing data

### Property-Based Testing

Property-based tests will verify universal properties across all inputs using Hypothesis (Python's PBT library). Each test will run a minimum of 100 iterations with randomly generated inputs.

**PBT Library**: Hypothesis for Python
**Minimum Iterations**: 100 per property test

Property tests will be tagged with comments referencing the design document:
```python
# Feature: text-pipeline-mock, Property 1: Workflow启动创建记录
@given(project_id=uuids(), episode_id=uuids())
def test_workflow_start_creates_record(project_id, episode_id):
    ...
```

Key property tests to implement:

1. **Workflow Properties** (Properties 1-5)
   - Test workflow creation, stage ordering, completion, and failure isolation

2. **Document Structure Properties** (Properties 6-25)
   - Test that all generated documents contain required fields
   - Test version management and persistence

3. **Consistency Properties** (Properties 27-31)
   - Test that consistency checks detect deviations
   - Test that locked fields are protected

4. **Workspace Properties** (Properties 32-35)
   - Test workspace aggregation with various data combinations

5. **Edit Properties** (Properties 36-40)
   - Test version creation, source tracking, and validation

6. **Pipeline Properties** (Properties 41-45)
   - Test agent pipeline execution order and behavior

7. **Orchestration Properties** (Properties 46-50)
   - Test workflow-agent separation and control flow

8. **Logging Properties** (Properties 51-55)
   - Test that all executions are properly logged

### Integration Testing

Integration tests will verify end-to-end workflows:

1. **Full Text Pipeline Test**
   - Start workflow with sample material
   - Verify all 5 stages execute in order
   - Verify all documents and shots are created
   - Verify workspace returns complete data

2. **Failure Recovery Test**
   - Inject failure at each stage
   - Verify intermediate artifacts are preserved
   - Verify workflow can be retried from failure point

3. **Consistency Check Test**
   - Create conflicting content at each stage
   - Verify warnings are generated
   - Verify content is still persisted (warnings don't block)

4. **Document Edit Test**
   - Generate documents via workflow
   - Edit documents via API
   - Verify versions are created correctly
   - Verify locked fields are protected

### Test Data Strategy

1. **Sample Materials**: Prepare 3-5 sample novel excerpts and scripts in Chinese
2. **Mock LLM**: Create mock LLM responses for deterministic testing
3. **Generators**: Use Hypothesis to generate random but valid inputs
4. **Fixtures**: Create database fixtures for common test scenarios

### Anti-Drift Testing

Special tests to verify content consistency:

1. **Brief Anchor Test**: Verify downstream content references brief's core_selling_points
2. **Character Consistency Test**: Verify script and storyboard use consistent character traits
3. **World Rule Test**: Verify no stage violates story_bible's forbidden_conflicts
4. **Visual Anchor Test**: Verify storyboard uses character_profile's visual_anchors

## Implementation Notes

### Mock vs Real LLM

For Iteration 2, we will use **mock LLM responses** to focus on workflow orchestration and data flow:

- Mock responses will return valid JSON matching expected schemas
- Mock responses will include some intentional inconsistencies to test warning generation
- Real LLM integration will be added in a later iteration

### Temporal Workflow Integration

For Iteration 2, we will create a **simplified Temporal workflow**:

- Single workflow definition for episode_workflow
- Activities for each stage (brief, story_bible, character, script, storyboard)
- Basic retry logic (3 attempts with exponential backoff)
- No human review gates yet (will be added in Iteration 5)

### Database Migrations

Required migrations for Iteration 2:

1. Ensure all tables from `001_initial_schema.sql` are created
2. Add indexes for common queries:
   - `idx_documents_episode_type_version` on (episode_id, document_type, version DESC)
   - `idx_shots_episode_scene_shot` on (episode_id, scene_no, shot_no)
   - `idx_stage_tasks_workflow_stage` on (workflow_run_id, stage_type, created_at)

### Performance Considerations

1. **Document Loading**: Use eager loading for input_refs to avoid N+1 queries
2. **Workspace Aggregation**: Consider caching workspace responses for 30 seconds
3. **LLM Calls**: Implement timeout (30 seconds) and circuit breaker pattern
4. **Database Transactions**: Keep transactions short, commit after each stage

### Observability

1. **Structured Logging**: Use JSON logs with correlation IDs (workflow_run_id)
2. **Metrics**: Track stage duration, LLM token usage, failure rates
3. **Tracing**: Add trace spans for each pipeline stage
4. **Alerts**: Alert on workflow failure rate > 10%, stage duration > 60s

## Future Enhancements

Items deferred to later iterations:

1. **Real LLM Integration**: Replace mocks with actual LLM API calls
2. **Human Review Gates**: Add pause/resume logic for manual approval
3. **Rerun Support**: Implement targeted rerun from specific stages
4. **Advanced Consistency Checks**: Use embeddings for semantic similarity
5. **Parallel Stage Execution**: Run independent stages in parallel
6. **Streaming Responses**: Stream LLM responses for better UX
7. **Multi-language Support**: Support materials in languages other than Chinese
