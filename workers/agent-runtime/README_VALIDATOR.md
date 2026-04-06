# Validator Component

## Overview

The Validator component is part of the agent pipeline and is responsible for validating agent outputs against JSON schemas, checking required fields, and protecting locked fields from modification.

## Requirements Implemented

- **Requirement 2.4**: Brief缺失字段拒绝 - Rejects brief documents with missing required fields
- **Requirement 7.5**: 锁定字段修改拒绝 - Rejects modifications to locked fields
- **Requirement 9.3**: Document锁定字段编辑拒绝 - Rejects document edits that modify locked fields
- **Requirement 9.5**: Document编辑Schema校验 - Validates document edits against JSON schema

## Features

### 1. JSON Schema Validation

Validates content structure against a JSON schema definition:
- Type checking (string, number, integer, boolean, array, object, null)
- Nested object validation
- Array item validation
- Property validation

### 2. Required Field Checking

Ensures all required fields are present and non-empty:
- Detects missing fields
- Detects null values in required fields
- Detects empty strings in required string fields
- Detects empty arrays in required array fields

### 3. Locked Field Protection

Prevents modification of locked fields:
- Simple field paths (e.g., "core_selling_points")
- Nested field paths (e.g., "character.visual_anchor")
- Array-indexed paths (e.g., "characters[0].visual_anchor")
- Multiple locked fields per document

## Usage

```python
from validator import Validator, LockedRef, ValidationResult
from uuid import uuid4

# Initialize validator
validator = Validator()

# Define content to validate
content = {
    "genre": "romance",
    "target_audience": "young adults",
    "core_selling_points": ["love", "drama", "suspense"]
}

# Define JSON schema
schema = {
    "required": ["genre", "target_audience", "core_selling_points"],
    "properties": {
        "genre": {"type": "string"},
        "target_audience": {"type": "string"},
        "core_selling_points": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# Define locked fields (optional)
locked_refs = [
    LockedRef(
        document_id=uuid4(),
        document_type="brief",
        locked_fields=["core_selling_points"]
    )
]

# Validate
result = validator.validate(content, schema, locked_refs)

if result.is_valid:
    print("Validation passed!")
else:
    for error in result.errors:
        print(f"Error in {error.field_path}: {error.message}")
```

## Data Structures

### ValidationError

```python
@dataclass
class ValidationError:
    field_path: str  # Path to the field with error
    error_type: str  # "missing_required", "schema_violation", "locked_field_modified"
    message: str     # Human-readable error message
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    is_valid: bool              # True if validation passed
    errors: List[ValidationError]  # List of validation errors
```

### LockedRef

```python
@dataclass
class LockedRef:
    document_id: UUID           # ID of document with locked fields
    document_type: str          # Type of document (e.g., "brief", "character_profile")
    locked_fields: List[str]    # List of field paths that are locked
```

## Error Types

### missing_required
Field is required but missing, null, empty string, or empty array.

**Example:**
```python
ValidationError(
    field_path="target_audience",
    error_type="missing_required",
    message="Required field 'target_audience' is missing"
)
```

### schema_violation
Field value doesn't match expected type from schema.

**Example:**
```python
ValidationError(
    field_path="episode_count",
    error_type="schema_violation",
    message="Field 'episode_count' has incorrect type. Expected integer, got str"
)
```

### locked_field_modified
Attempt to modify a field that is locked.

**Example:**
```python
ValidationError(
    field_path="core_selling_points",
    error_type="locked_field_modified",
    message="Locked field 'core_selling_points' from document abc-123 cannot be modified"
)
```

## Integration with Agent Pipeline

The Validator is designed to be used in the agent pipeline after the Critic stage:

```
Loader → Normalizer → Planner → Generator → Critic → Validator → Committer
```

The Validator ensures that:
1. Generated content meets schema requirements
2. All required fields are present
3. Locked fields from upstream documents are not modified

If validation fails, the agent should not proceed to the Committer stage.

## Testing

Run the test suite:

```bash
python -m pytest workers/agent-runtime/test_validator.py -v
```

The test suite includes:
- 17 unit tests covering all validation scenarios
- Tests for required field validation
- Tests for schema type validation
- Tests for locked field protection
- Tests for complex nested structures
- Tests for multiple error scenarios

## Future Enhancements

1. **Custom Validators**: Support for custom validation functions
2. **Conditional Validation**: Validate fields based on other field values
3. **Format Validation**: Validate string formats (email, URL, date, etc.)
4. **Range Validation**: Validate numeric ranges and string lengths
5. **Cross-Field Validation**: Validate relationships between fields
6. **Detailed Error Context**: Include more context in error messages
7. **Validation Warnings**: Support non-fatal validation warnings
