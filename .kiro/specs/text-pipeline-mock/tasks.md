# Implementation Plan

- [x] 1. Set up core data models and repositories
  - Database models already exist (WorkflowRun, StageTask, Document, Shot)
  - Repositories already implemented for all models
  - _Requirements: 1.1, 1.3, 2.3, 3.3, 4.3, 5.3, 6.3_

- [x] 2. Implement workflow orchestration service
  - WorkflowService already exists with start_episode_workflow
  - TextWorkflowService already implements text chain execution
  - Stage sequence and document creation working
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 3. Implement workspace aggregation API
  - Workspace endpoint already exists at GET /workspace
  - DatabaseStore.build_workspace aggregates all data
  - Returns project, episode, documents, shots, stage_tasks
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 4. Create API endpoints for workflow control
  - POST /workflow/start endpoint exists
  - GET /workflow endpoint exists
  - Review submission endpoint exists
  - _Requirements: 1.1, 9.1, 9.2_

- [-] 5. Implement agent runtime framework



  - [x] 5.1 Create BaseAgent class with common pipeline


    - Implement Loader → Normalizer → Planner → Generator → Critic → Validator → Committer pipeline
    - Define StageTaskInput and StageTaskOutput dataclasses
    - Create abstract methods for each pipeline stage
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 5.2 Implement mock LLM service


    - Create MockLLMService that returns valid JSON responses
    - Include schema-compliant responses for each document type
    - Add intentional inconsistencies for testing warning generation
    - _Requirements: 2.2, 3.2, 4.2, 5.2, 6.2_

  - [x] 5.3 Create consistency checker (Critic component)


    - Implement brief anchor checking
    - Implement character consistency checking
    - Implement world rule violation checking
    - Generate warnings for deviations
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 5.4 Create validator component


















    - Implement JSON schema validation
    - Implement required field checking
    - Implement locked field protection
    - _Requirements: 2.4, 7.5, 9.3, 9.5_

- [-] 6. Implement individual agents



  - [x] 6.1 Implement Brief Agent


    - Extend BaseAgent with brief-specific logic
    - Define brief output schema
    - Implement brief generation with mock LLM
    - Validate required fields (genre, target_audience, core_selling_points, main_conflict, target_style)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 6.2 Implement Story Bible Agent


    - Extend BaseAgent with story bible-specific logic
    - Define story_bible output schema
    - Load brief as input reference
    - Validate required fields (world_rules, forbidden_conflicts)
    - Check for conflicts with brief
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 6.3 Implement Character Agent


    - Extend BaseAgent with character-specific logic
    - Define character_profile output schema
    - Load brief and story_bible as input references
    - Validate character structure (name, role, goal, motivation, speaking_style, visual_anchor)
    - Mark visual_anchors as lockable
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 6.4 Implement Script Agent


    - Extend BaseAgent with script-specific logic
    - Define script_draft output schema
    - Load brief, story_bible, and character_profile as input references
    - Validate scene structure (scene_no, location, characters, dialogue, emotion_beats)
    - Check character behaviors against character_profile
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 6.5 Implement Storyboard Agent







    - Extend BaseAgent with storyboard-specific logic
    - Define visual_spec output schema and shot structure
    - Load script_draft and platform constraints
    - Generate shot records with all required fields
    - Validate total duration against target
    - Check character visual anchors
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 7. Integrate agents with workflow service




  - [x] 7.1 Update TextWorkflowService to call real agents


    - Replace mock document generation with agent execution
    - Build StageTaskInput for each stage
    - Handle StageTaskOutput and extract document_refs
    - Preserve failure isolation (keep intermediate artifacts)
    - _Requirements: 1.2, 1.5, 11.1, 11.2, 11.3_

  - [x] 7.2 Implement error handling and retry logic


    - Add try-catch around agent execution
    - Record error_code and error_message on failure
    - Implement retry logic (max 3 attempts)
    - Update workflow status on failure
    - _Requirements: 1.5, 2.5, 3.5, 4.5, 5.5, 11.4_

  - [x] 7.3 Add execution logging and metrics


    - Log stage start with stage_type, started_at, attempt_no
    - Log stage completion with finished_at, duration_ms, token_usage
    - Log LLM calls with prompt, model, temperature, response
    - Log document commits with document_type, version, created_by
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 8. Implement document editing functionality





  - [x] 8.1 Create document update endpoint


    - Add PUT /documents/{document_id} endpoint
    - Validate document exists and belongs to correct episode
    - Create new version instead of overwriting
    - Set created_by to user_id (not null)
    - Update updated_at timestamp
    - _Requirements: 9.1, 9.2, 9.4_

  - [x] 8.2 Add locked field validation for edits


    - Check if document has locked fields
    - Reject edits that modify locked fields
    - Return validation error with details
    - _Requirements: 9.3_

  - [x] 8.3 Add schema validation for edits


    - Validate content_jsonb against document type schema
    - Check for required fields
    - Check for correct field types
    - Return schema validation errors
    - _Requirements: 9.5_

- [x] 9. Add testing infrastructure




  - [x] 9.1 Set up pytest and Hypothesis


    - Add pytest, pytest-asyncio, and hypothesis to dependencies
    - Create pytest.conftest with database fixtures
    - Create test database setup/teardown
    - _Requirements: All_

  - [ ]* 9.2 Create test data generators
    - Create Hypothesis strategies for UUIDs, documents, shots
    - Create sample novel excerpts and scripts
    - Create mock LLM response fixtures
    - _Requirements: All_

- [ ]* 10. Write property-based tests for workflow
  - [ ]* 10.1 Property 1: Workflow启动创建记录
    - **Property 1: Workflow启动创建记录**
    - **Validates: Requirements 1.1**

  - [ ]* 10.2 Property 2: Stage执行顺序保持
    - **Property 2: Stage执行顺序保持**
    - **Validates: Requirements 1.2**

  - [ ]* 10.3 Property 3: Stage完成创建任务记录
    - **Property 3: Stage完成创建任务记录**
    - **Validates: Requirements 1.3**

  - [ ]* 10.4 Property 4: Workflow完成更新状态
    - **Property 4: Workflow完成更新状态**
    - **Validates: Requirements 1.4**

  - [ ]* 10.5 Property 5: Workflow失败保留产物
    - **Property 5: Workflow失败保留产物**
    - **Validates: Requirements 1.5**

- [ ]* 11. Write property-based tests for documents
  - [ ]* 11.1 Property 6: Brief包含必需元素
    - **Property 6: Brief包含必需元素**
    - **Validates: Requirements 2.1, 2.2**

  - [ ]* 11.2 Property 7: Brief持久化关联正确
    - **Property 7: Brief持久化关联正确**
    - **Validates: Requirements 2.3**

  - [ ]* 11.3 Property 8: Brief缺失字段拒绝
    - **Property 8: Brief缺失字段拒绝**
    - **Validates: Requirements 2.4**

  - [ ]* 11.4 Property 10: Story Bible包含必需元素
    - **Property 10: Story Bible包含必需元素**
    - **Validates: Requirements 3.1, 3.2**

  - [ ]* 11.5 Property 14: Character Profile包含必需元素
    - **Property 14: Character Profile包含必需元素**
    - **Validates: Requirements 4.1, 4.2**

  - [ ]* 11.6 Property 18: Script包含场次和台词
    - **Property 18: Script包含场次和台词**
    - **Validates: Requirements 5.1, 5.2**

  - [ ]* 11.7 Property 22: Storyboard生成Shot记录
    - **Property 22: Storyboard生成Shot记录**
    - **Validates: Requirements 6.1**

  - [ ]* 11.8 Property 23: Shot包含必需字段且ID唯一
    - **Property 23: Shot包含必需字段且ID唯一**
    - **Validates: Requirements 6.2**

- [ ]* 12. Write property-based tests for consistency
  - [ ]* 12.1 Property 27: 内容与Brief一致性检查
    - **Property 27: 内容与Brief一致性检查**
    - **Validates: Requirements 7.1**

  - [ ]* 12.2 Property 28: 角色行为一致性检查
    - **Property 28: 角色行为一致性检查**
    - **Validates: Requirements 7.2**

  - [ ]* 12.3 Property 29: 世界规则一致性检查
    - **Property 29: 世界规则一致性检查**
    - **Validates: Requirements 7.3**

  - [ ]* 12.4 Property 31: 锁定字段修改拒绝
    - **Property 31: 锁定字段修改拒绝**
    - **Validates: Requirements 7.5**

- [ ]* 13. Write property-based tests for workspace
  - [ ]* 13.1 Property 32: Workspace返回完整聚合
    - **Property 32: Workspace返回完整聚合**
    - **Validates: Requirements 8.1**

  - [ ]* 13.2 Property 33: Workspace返回最新文档版本
    - **Property 33: Workspace返回最新文档版本**
    - **Validates: Requirements 8.2**

  - [ ]* 13.3 Property 34: Workspace返回完整Shot列表
    - **Property 34: Workspace返回完整Shot列表**
    - **Validates: Requirements 8.3**

- [ ]* 14. Write property-based tests for document editing
  - [ ]* 14.1 Property 36: Document编辑创建新版本
    - **Property 36: Document编辑创建新版本**
    - **Validates: Requirements 9.1**

  - [ ]* 14.2 Property 37: Document编辑记录来源
    - **Property 37: Document编辑记录来源**
    - **Validates: Requirements 9.2**

  - [ ]* 14.3 Property 38: Document锁定字段编辑拒绝
    - **Property 38: Document锁定字段编辑拒绝**
    - **Validates: Requirements 9.3**

  - [ ]* 14.4 Property 39: Document编辑更新时间戳
    - **Property 39: Document编辑更新时间戳**
    - **Validates: Requirements 9.4**

- [ ]* 15. Write property-based tests for agent pipeline
  - [ ]* 15.1 Property 41: Agent执行遵循Pipeline顺序
    - **Property 41: Agent执行遵循Pipeline顺序**
    - **Validates: Requirements 10.1**

  - [ ]* 15.2 Property 42: Loader加载Refs
    - **Property 42: Loader加载Refs**
    - **Validates: Requirements 10.2**

  - [ ]* 15.3 Property 43: Generator调用LLM
    - **Property 43: Generator调用LLM**
    - **Validates: Requirements 10.3**

  - [ ]* 15.4 Property 44: Validator校验Schema
    - **Property 44: Validator校验Schema**
    - **Validates: Requirements 10.4**

  - [ ]* 15.5 Property 45: Committer持久化并返回Refs
    - **Property 45: Committer持久化并返回Refs**
    - **Validates: Requirements 10.5**

- [ ]* 16. Write property-based tests for orchestration
  - [ ]* 16.1 Property 46: Workflow构造StageTaskInput
    - **Property 46: Workflow构造StageTaskInput**
    - **Validates: Requirements 11.1**

  - [ ]* 16.2 Property 47: Agent返回Output不修改状态
    - **Property 47: Agent返回Output不修改状态**
    - **Validates: Requirements 11.2**

  - [ ]* 16.3 Property 48: Workflow根据Output决定下一步
    - **Property 48: Workflow根据Output决定下一步**
    - **Validates: Requirements 11.3**

- [x] 17. Checkpoint - Ensure all tests pass









  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 18. Write integration tests
  - [ ]* 18.1 Full text pipeline integration test
    - Start workflow with sample material
    - Verify all 5 stages execute in order
    - Verify all documents and shots are created
    - Verify workspace returns complete data
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 8.1_

  - [ ]* 18.2 Failure recovery integration test
    - Inject failure at each stage
    - Verify intermediate artifacts are preserved
    - Verify workflow can be retried
    - _Requirements: 1.5, 2.5, 3.5, 4.5, 5.5_

  - [ ]* 18.3 Consistency check integration test
    - Create conflicting content at each stage
    - Verify warnings are generated
    - Verify content is still persisted
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 18.4 Document edit integration test
    - Generate documents via workflow
    - Edit documents via API
    - Verify versions are created correctly
    - Verify locked fields are protected
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 19. Add database indexes for performance





  - [x] 19.1 Create index on documents (episode_id, document_type, version DESC)


    - Add migration or update schema
    - _Requirements: 8.2_

  - [x] 19.2 Create index on shots (episode_id, scene_no, shot_no)


    - Add migration or update schema
    - _Requirements: 8.3_

  - [x] 19.3 Create index on stage_tasks (workflow_run_id, stage_type, created_at)


    - Add migration or update schema
    - _Requirements: 8.4_

- [x] 20. Final checkpoint - Ensure all tests pass















  - Ensure all tests pass, ask the user if questions arise.
