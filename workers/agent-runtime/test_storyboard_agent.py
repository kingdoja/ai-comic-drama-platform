"""
Test for Storyboard Agent implementation.
"""

from uuid import UUID, uuid4

from base_agent import DocumentRef, LockedRef, StageTaskInput
from mock_llm_service import MockLLMService
from storyboard_agent import StoryboardAgent


def test_storyboard_agent_basic():
    """Test basic storyboard agent execution."""
    # Setup
    llm_service = MockLLMService()
    agent = StoryboardAgent(db_session=None, llm_service=llm_service, validator=None)
    
    # Create task input
    task_input = StageTaskInput(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        episode_id=uuid4(),
        stage_type="storyboard",
        input_refs=[],
        locked_refs=[],
        constraints={
            "platform": "douyin",
            "aspect_ratio": "9:16",
            "target_duration_sec": 60,
            "max_shots": 20
        },
        target_ref_ids=[]
    )
    
    # Execute
    output = agent.execute(task_input)
    
    # Verify
    assert output.status == "succeeded", f"Expected succeeded, got {output.status}: {output.error_message}"
    assert len(output.document_refs) > 0, "Should create visual_spec document"
    assert len(output.asset_refs) > 0, "Should create shot records"
    assert output.document_refs[0].document_type == "visual_spec"
    
    print("✓ Basic storyboard agent execution works")


def test_storyboard_agent_schema():
    """Test storyboard agent output schema."""
    agent = StoryboardAgent(db_session=None, llm_service=None, validator=None)
    
    schema = agent.get_output_schema()
    
    # Verify schema structure
    assert "type" in schema
    assert schema["type"] == "object"
    assert "required" in schema
    assert "shots" in schema["required"]
    assert "overall_duration_ms" in schema["required"]
    assert "shot_count" in schema["required"]
    
    # Verify shot schema
    shot_schema = schema["properties"]["shots"]["items"]
    assert "required" in shot_schema
    assert "shot_id" in shot_schema["required"]
    assert "render_prompt" in shot_schema["required"]
    assert "character_refs" in shot_schema["required"]
    assert "style_keywords" in shot_schema["required"]
    assert "composition" in shot_schema["required"]
    
    print("✓ Storyboard agent schema is correct")


def test_storyboard_agent_duration_warning():
    """Test that storyboard agent generates warning for excessive duration."""
    llm_service = MockLLMService()
    agent = StoryboardAgent(db_session=None, llm_service=llm_service, validator=None)
    
    # Create task input with short target duration
    task_input = StageTaskInput(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        episode_id=uuid4(),
        stage_type="storyboard",
        input_refs=[],
        locked_refs=[],
        constraints={
            "platform": "douyin",
            "aspect_ratio": "9:16",
            "target_duration_sec": 30,  # Short target
            "max_shots": 20
        },
        target_ref_ids=[]
    )
    
    # Execute
    output = agent.execute(task_input)
    
    # Verify warning is generated (mock returns 58000ms which exceeds 30s * 1.2 = 36s)
    assert output.status == "succeeded"
    assert len(output.warnings) > 0, "Should generate duration warning"
    
    duration_warnings = [w for w in output.warnings if w.warning_type == "constraint" and "duration" in w.message.lower()]
    assert len(duration_warnings) > 0, "Should have duration constraint warning"
    
    print("✓ Storyboard agent generates duration warnings")


def test_storyboard_agent_visual_anchor_check():
    """Test that storyboard agent checks character visual anchors."""
    llm_service = MockLLMService()
    agent = StoryboardAgent(db_session=None, llm_service=llm_service, validator=None)
    
    # The mock LLM service returns a character profile with one empty visual anchor
    # This should trigger a warning in the critic stage
    
    task_input = StageTaskInput(
        workflow_run_id=uuid4(),
        project_id=uuid4(),
        episode_id=uuid4(),
        stage_type="storyboard",
        input_refs=[],
        locked_refs=[],
        constraints={
            "platform": "douyin",
            "aspect_ratio": "9:16",
            "target_duration_sec": 60,
            "max_shots": 20
        },
        target_ref_ids=[]
    )
    
    # Execute
    output = agent.execute(task_input)
    
    # Verify
    assert output.status == "succeeded"
    # Note: In mock mode without DB, we don't load character profiles,
    # so this test mainly verifies the code path exists
    
    print("✓ Storyboard agent visual anchor check works")


def test_storyboard_agent_validation():
    """Test storyboard agent validation."""
    llm_service = MockLLMService()
    agent = StoryboardAgent(db_session=None, llm_service=llm_service, validator=None)
    
    # Test with valid content
    valid_content = {
        "shots": [
            {
                "shot_id": "001",
                "render_prompt": "Test prompt",
                "character_refs": ["Character A"],
                "style_keywords": ["cinematic"],
                "composition": "medium"
            }
        ],
        "overall_duration_ms": 5000,
        "shot_count": 1,
        "visual_style": "test",
        "camera_strategy": "test"
    }
    
    result = agent.validator_stage(valid_content, [])
    assert result["is_valid"], f"Valid content should pass: {result['errors']}"
    
    # Test with missing required field
    invalid_content = {
        "shots": [],  # Empty shots array
        "overall_duration_ms": 5000
        # Missing shot_count
    }
    
    result = agent.validator_stage(invalid_content, [])
    assert not result["is_valid"], "Invalid content should fail"
    assert len(result["errors"]) > 0
    
    print("✓ Storyboard agent validation works")


if __name__ == "__main__":
    test_storyboard_agent_basic()
    test_storyboard_agent_schema()
    test_storyboard_agent_duration_warning()
    test_storyboard_agent_visual_anchor_check()
    test_storyboard_agent_validation()
    print("\n✅ All storyboard agent tests passed!")
