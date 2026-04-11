# QA Runtime Documentation

## Overview

The QA Runtime is a quality assurance system that executes automated checks on generated content during the workflow pipeline. It was implemented as part of Iteration 5 to enable the system to move from "能生成" (can generate) to "能返工、能审核、能放行" (can rework, can review, can approve).

## Components

### 1. QA Runtime Service (`app/services/qa_runtime.py`)

The core QA execution engine that:
- Executes different types of QA checks (rule, semantic, asset)
- Calculates quality scores and severity levels
- Generates QA reports
- Decides whether to block workflow continuation

**Key Methods:**
- `execute_qa()`: Main entry point for QA execution
- `should_block_workflow()`: Determines if QA results should block workflow
- `_calculate_qa_result()`: Calculates scores and severity from issues
- `_create_qa_report()`: Persists QA results to database

### 2. QA Stage Service (`app/services/qa_stage.py`)

Integrates QA checks into the workflow pipeline:
- Executes QA checks after media chain completion
- Updates StageTask with QA metrics
- Handles errors gracefully
- Provides workflow continuation decisions

**Key Methods:**
- `execute()`: Runs QA stage in workflow context
- `_update_stage_task()`: Records QA results in StageTask metrics

### 3. QA Repository (`app/repositories/qa_repository.py`)

Data access layer for QA reports:
- `list_for_episode()`: Get all QA reports for an episode
- `get_by_id()`: Get specific QA report
- `get_latest_for_stage()`: Get most recent QA report for a stage

## Data Models

### Issue

Represents a single QA issue:
```python
@dataclass
class Issue:
    type: str              # e.g., "missing_field", "invalid_format"
    severity: str          # "info", "minor", "major", "critical"
    location: str          # e.g., "brief.genre", "shot_3.dialogue"
    message: str           # Human-readable description
    suggestion: Optional[str]  # Suggested fix
```

### QAResult

Result of a QA check execution:
```python
@dataclass
class QAResult:
    result: str            # "passed", "failed", "warning"
    score: float           # Quality score 0-100
    severity: str          # Highest severity found
    issue_count: int
    issues: List[Issue]
    rerun_stage_type: Optional[str]  # Suggested stage to rerun
```

### QAReportModel (Database)

Persisted QA report in database:
- `qa_type`: Type of check (rule_check, semantic_check, asset_check)
- `target_ref_type`: What was checked (document, shot, asset, episode)
- `result`: Overall result (passed, failed, warning)
- `score`: Quality score (0-100)
- `severity`: Highest severity (info, minor, major, critical)
- `issues_jsonb`: List of issues found
- `rerun_stage_type`: Suggested stage to rerun if failed

## Scoring System

The QA Runtime uses a point-deduction scoring system:

- **Starting score**: 100.0
- **Critical issue**: -25 points each
- **Major issue**: -10 points each
- **Minor issue**: -3 points each
- **Info issue**: -1 point each
- **Minimum score**: 0.0 (never goes below zero)

## Workflow Blocking Logic

The QA Runtime blocks workflow continuation when:
1. Any issue has `severity == "critical"`
2. The overall `result == "failed"`

Workflows continue when:
- `result == "passed"` (no issues or only info/minor issues)
- `result == "warning"` (major issues but not critical)

## Integration with Media Workflow

The QA stage is integrated into the media workflow sequence:

```python
MEDIA_STAGE_SEQUENCE = [
    "image_render",
    "subtitle",
    "tts",
    "edit_export_preview",
    "qa",  # QA check after media chain
]
```

After the preview export completes, the QA stage:
1. Executes rule checks on the episode
2. Executes semantic checks on the episode
3. Records results in QAReport table
4. Updates StageTask with metrics
5. Decides whether to block further workflow stages

## Usage Example

```python
from app.services.qa_runtime import QARuntime

# Initialize QA Runtime
qa_runtime = QARuntime(db_session)

# Execute QA check
qa_result = qa_runtime.execute_qa(
    episode_id=episode_id,
    stage_task_id=stage_task_id,
    qa_type="rule_check",
    target_ref_type="episode",
    target_ref_id=None,
)

# Check if workflow should be blocked
should_block = qa_runtime.should_block_workflow(qa_result)

if should_block:
    # Handle blocking (e.g., pause workflow, notify user)
    print(f"QA failed with {qa_result.issue_count} issues")
else:
    # Continue workflow
    print(f"QA passed with score {qa_result.score}")
```

## QA Check Types

The QA Runtime supports three main types of checks:

### 1. Rule Checks (`rule_check`)

Validates content against predefined structural and format rules.

**Brief Document Checks:**
- Required fields: title, genre, target_audience, tone, themes
- Field format validation
- Content length constraints

**Character Profile Checks:**
- Minimum character count (1-5 characters)
- Required fields per character: name, role, personality_traits
- Visual anchors validation

**Script Checks:**
- Scene structure validation
- Dialogue format verification
- Duration reasonableness (5-15 minutes per episode)
- Scene count validation

**Storyboard Checks:**
- Shot count validation (10-30 shots per episode)
- Total duration validation
- Shot structure completeness
- Visual description requirements

### 2. Semantic Checks (`semantic_check`)

Validates logical consistency and coherence across documents.

**Character Consistency:**
- Verifies characters in Script match Character Profile
- Checks character descriptions remain consistent
- Validates character relationships

**World-Building Consistency:**
- Compares Script against Story Bible settings
- Detects violations of established rules
- Validates location and setting consistency

**Plot Coherence:**
- Validates scene transitions
- Checks timeline continuity
- Verifies logical flow

### 3. Asset Quality Checks (`asset_check`)

Validates technical quality of generated media assets.

**Image Assets:**
- Resolution validation
- Format verification (PNG, JPEG)
- File integrity checks

**Audio Assets:**
- Duration validation
- Format verification (MP3, WAV)
- Audio quality metrics

**Subtitle Assets:**
- Timeline continuity
- Text completeness
- Synchronization validation

**Preview Video:**
- Playability verification
- Basic quality metrics
- Format validation

## Configuration

### Configuring QA Thresholds

You can customize QA behavior by modifying the scoring thresholds:

```python
# In qa_runtime.py or configuration file

QA_CONFIG = {
    "scoring": {
        "critical_penalty": 25,  # Points deducted per critical issue
        "major_penalty": 10,     # Points deducted per major issue
        "minor_penalty": 3,      # Points deducted per minor issue
        "info_penalty": 1,       # Points deducted per info issue
    },
    "blocking": {
        "block_on_critical": True,   # Block workflow if critical issues found
        "block_on_failed": True,     # Block workflow if result is "failed"
        "min_passing_score": 70.0,   # Minimum score to pass (optional)
    },
    "timeouts": {
        "rule_check": 5,      # Seconds
        "semantic_check": 15, # Seconds
        "asset_check": 10,    # Seconds
    }
}
```

### Configuring Check Execution

Control which checks run at which stages:

```python
# In workflow configuration
STAGE_QA_CONFIG = {
    "qa": {
        "checks": [
            {"type": "rule_check", "target": "episode"},
            {"type": "semantic_check", "target": "episode"},
        ],
        "review_required": True,  # Pause for human review after QA
    }
}
```

## Extending the QA Runtime

### Adding Custom Rule Checks

To add new rule checks, extend the rule checking logic:

```python
# In qa_runtime.py or custom checker module

def check_custom_rule(document: DocumentModel) -> List[Issue]:
    """
    Custom rule check example.
    
    Args:
        document: Document to check
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Example: Check for profanity in content
    if contains_profanity(document.content_jsonb):
        issues.append(Issue(
            type="content_policy_violation",
            severity="critical",
            location=f"document.{document.doc_type}",
            message="Content contains prohibited language",
            suggestion="Review and remove inappropriate content"
        ))
    
    return issues

# Register the custom check
QA_RUNTIME.register_rule_check("custom_profanity", check_custom_rule)
```

### Adding Custom Semantic Checks

Extend semantic checking with domain-specific logic:

```python
def check_brand_consistency(episode_id: UUID, db: Session) -> List[Issue]:
    """
    Check brand consistency across episode content.
    
    Args:
        episode_id: Episode to check
        db: Database session
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Load brand guidelines
    brand_guidelines = load_brand_guidelines(episode_id, db)
    
    # Load episode content
    script = get_document(episode_id, "script", db)
    
    # Check for brand violations
    if violates_brand_tone(script, brand_guidelines):
        issues.append(Issue(
            type="brand_consistency",
            severity="major",
            location="script.tone",
            message="Script tone doesn't match brand guidelines",
            suggestion=f"Adjust tone to match {brand_guidelines.tone}"
        ))
    
    return issues

# Register the custom check
QA_RUNTIME.register_semantic_check("brand_consistency", check_brand_consistency)
```

### Adding Custom Asset Checks

Validate custom asset requirements:

```python
def check_asset_accessibility(asset: AssetModel) -> List[Issue]:
    """
    Check asset meets accessibility requirements.
    
    Args:
        asset: Asset to check
        
    Returns:
        List of issues found
    """
    issues = []
    
    if asset.asset_type == "image":
        # Check for alt text
        if not asset.metadata_jsonb.get("alt_text"):
            issues.append(Issue(
                type="accessibility",
                severity="major",
                location=f"asset.{asset.id}.alt_text",
                message="Image missing alt text for accessibility",
                suggestion="Add descriptive alt text"
            ))
    
    return issues

# Register the custom check
QA_RUNTIME.register_asset_check("accessibility", check_asset_accessibility)
```

### Creating a Custom QA Plugin

For more complex extensions, create a QA plugin:

```python
from app.services.qa_runtime import QAPlugin, Issue

class CustomQAPlugin(QAPlugin):
    """
    Custom QA plugin for specialized checks.
    """
    
    def __init__(self, config: dict):
        self.config = config
    
    def check_rules(self, target: Any) -> List[Issue]:
        """Execute custom rule checks."""
        return []
    
    def check_semantics(self, episode_id: UUID, db: Session) -> List[Issue]:
        """Execute custom semantic checks."""
        return []
    
    def check_assets(self, asset: AssetModel) -> List[Issue]:
        """Execute custom asset checks."""
        return []

# Register the plugin
qa_runtime.register_plugin("custom_plugin", CustomQAPlugin(config))
```

## Advanced Usage

### Programmatic QA Execution

Execute QA checks programmatically outside the workflow:

```python
from app.services.qa_runtime import QARuntime
from app.db.session import get_db

# Initialize
db = next(get_db())
qa_runtime = QARuntime(db)

# Execute specific check type
result = qa_runtime.execute_qa(
    episode_id=episode_id,
    stage_task_id=None,  # Optional if running outside workflow
    qa_type="rule_check",
    target_ref_type="document",
    target_ref_id=document_id,
)

# Process results
for issue in result.issues:
    print(f"[{issue.severity}] {issue.location}: {issue.message}")
    if issue.suggestion:
        print(f"  Suggestion: {issue.suggestion}")
```

### Batch QA Execution

Run QA checks on multiple targets:

```python
def batch_qa_check(episode_ids: List[UUID], qa_type: str) -> Dict[UUID, QAResult]:
    """
    Execute QA checks on multiple episodes.
    
    Args:
        episode_ids: List of episode IDs
        qa_type: Type of QA check
        
    Returns:
        Dictionary mapping episode_id to QAResult
    """
    results = {}
    
    for episode_id in episode_ids:
        result = qa_runtime.execute_qa(
            episode_id=episode_id,
            stage_task_id=None,
            qa_type=qa_type,
            target_ref_type="episode",
            target_ref_id=None,
        )
        results[episode_id] = result
    
    return results
```

### Filtering and Analyzing QA Results

```python
def analyze_qa_results(episode_id: UUID) -> dict:
    """
    Analyze QA results for an episode.
    
    Returns:
        Summary statistics and insights
    """
    reports = qa_repository.list_for_episode(episode_id, db)
    
    analysis = {
        "total_checks": len(reports),
        "passed": sum(1 for r in reports if r.result == "passed"),
        "failed": sum(1 for r in reports if r.result == "failed"),
        "warnings": sum(1 for r in reports if r.result == "warning"),
        "avg_score": sum(r.score for r in reports) / len(reports) if reports else 0,
        "critical_issues": sum(
            1 for r in reports 
            for issue in r.issues_jsonb 
            if issue.get("severity") == "critical"
        ),
    }
    
    return analysis
```

## Future Enhancements

Planned enhancements for the QA Runtime:

1. **Custom Rules Engine**: Allow users to define custom QA rules via configuration
2. **Machine Learning Integration**: Use ML models for advanced semantic checks
3. **Performance Optimization**: Parallel execution of independent checks
4. **Real-time Feedback**: Stream QA results as checks complete
5. **Historical Analysis**: Track QA metrics over time for quality trends

## Testing

Unit tests are provided in:
- `tests/unit/test_qa_runtime.py`: Tests for QA Runtime core logic
- `tests/unit/test_qa_stage.py`: Tests for QA Stage integration

Run tests with:
```bash
python -m pytest tests/unit/test_qa_runtime.py -v
```

## Requirements Implemented

This implementation satisfies the following requirements from the design document:

- **Requirement 1.1**: QA Runtime executes checks and creates QAReport records
- **Requirement 1.2**: QA reports include issues_jsonb, score, and severity
- **Requirement 1.3**: QA results determine workflow continuation
- **Requirement 1.4**: QA stage executes after media chain completion
- **Requirement 1.5**: QA results decide whether to block workflow

## Related Documentation

- Design Document: `.kiro/specs/qa-review-rerun/design.md`
- Requirements: `.kiro/specs/qa-review-rerun/requirements.md`
- Tasks: `.kiro/specs/qa-review-rerun/tasks.md`
