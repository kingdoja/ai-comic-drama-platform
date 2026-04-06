"""
Validator component for agent pipeline.

Validates agent outputs against JSON schemas, required fields, and locked field constraints.
Implements Requirements: 2.4, 7.5, 9.3, 9.5
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID
import json


@dataclass
class LockedRef:
    """Reference to a locked field that cannot be modified."""
    document_id: UUID
    document_type: str
    locked_fields: List[str]  # JSON paths like "characters[0].visual_anchor"


@dataclass
class ValidationError:
    """Represents a validation error."""
    field_path: str
    error_type: str  # "missing_required", "schema_violation", "locked_field_modified"
    message: str


@dataclass
class ValidationResult:
    """Result of validation."""
    is_valid: bool
    errors: List[ValidationError]


class Validator:
    """
    Validates agent outputs for schema compliance, required fields, and locked field protection.
    
    This component is part of the agent pipeline and runs after the Critic stage.
    """
    
    def __init__(self):
        """Initialize the validator."""
        pass
    
    def validate(
        self,
        content: Dict[str, Any],
        schema: Dict[str, Any],
        locked_refs: Optional[List[LockedRef]] = None
    ) -> ValidationResult:
        """
        Validate content against schema and locked field constraints.
        
        Args:
            content: The content to validate (agent output)
            schema: JSON schema defining required structure
            locked_refs: List of locked field references that cannot be modified
            
        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []
        
        # 1. Validate required fields
        required_errors = self._validate_required_fields(content, schema)
        errors.extend(required_errors)
        
        # Track fields that failed required validation to avoid duplicate errors
        failed_required_fields = {err.field_path for err in required_errors}
        
        # 2. Validate JSON schema (skip fields that failed required validation)
        schema_errors = self._validate_schema(content, schema, failed_required_fields)
        errors.extend(schema_errors)
        
        # 3. Validate locked field protection
        if locked_refs:
            locked_errors = self._validate_locked_fields(content, locked_refs)
            errors.extend(locked_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def _validate_required_fields(
        self,
        content: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> List[ValidationError]:
        """
        Validate that all required fields are present and non-empty.
        
        Implements Requirement 2.4: Brief缺失字段拒绝
        Implements Requirement 9.5: Document编辑Schema校验
        """
        errors = []
        required_fields = schema.get("required", [])
        
        for field in required_fields:
            if field not in content:
                errors.append(ValidationError(
                    field_path=field,
                    error_type="missing_required",
                    message=f"Required field '{field}' is missing"
                ))
            elif content[field] is None:
                errors.append(ValidationError(
                    field_path=field,
                    error_type="missing_required",
                    message=f"Required field '{field}' cannot be null"
                ))
            elif isinstance(content[field], str) and not content[field].strip():
                errors.append(ValidationError(
                    field_path=field,
                    error_type="missing_required",
                    message=f"Required field '{field}' cannot be empty"
                ))
            elif isinstance(content[field], list) and len(content[field]) == 0:
                errors.append(ValidationError(
                    field_path=field,
                    error_type="missing_required",
                    message=f"Required field '{field}' cannot be an empty list"
                ))
        
        return errors
    
    def _validate_schema(
        self,
        content: Dict[str, Any],
        schema: Dict[str, Any],
        skip_fields: Optional[set] = None
    ) -> List[ValidationError]:
        """
        Validate content against JSON schema structure.
        
        Implements Requirement 9.5: Document编辑Schema校验
        
        Args:
            content: Content to validate
            schema: JSON schema
            skip_fields: Set of field paths to skip (already validated)
        """
        errors = []
        properties = schema.get("properties", {})
        skip_fields = skip_fields or set()
        
        for field_name, field_schema in properties.items():
            if field_name in skip_fields:
                continue  # Skip fields that already failed required validation
            
            if field_name not in content:
                continue  # Already handled by required field validation
            
            field_value = content[field_name]
            expected_type = field_schema.get("type")
            
            if expected_type:
                type_valid = self._check_type(field_value, expected_type)
                if not type_valid:
                    errors.append(ValidationError(
                        field_path=field_name,
                        error_type="schema_violation",
                        message=f"Field '{field_name}' has incorrect type. Expected {expected_type}, got {type(field_value).__name__}"
                    ))
            
            # Validate nested objects
            if expected_type == "object" and isinstance(field_value, dict):
                nested_errors = self._validate_nested_object(
                    field_value,
                    field_schema,
                    field_name
                )
                errors.extend(nested_errors)
            
            # Validate arrays
            if expected_type == "array" and isinstance(field_value, list):
                array_errors = self._validate_array(
                    field_value,
                    field_schema,
                    field_name
                )
                errors.extend(array_errors)
        
        return errors
    
    def _validate_locked_fields(
        self,
        content: Dict[str, Any],
        locked_refs: List[LockedRef]
    ) -> List[ValidationError]:
        """
        Validate that locked fields have not been modified.
        
        Implements Requirement 7.5: 锁定字段修改拒绝
        Implements Requirement 9.3: Document锁定字段编辑拒绝
        """
        errors = []
        
        for locked_ref in locked_refs:
            for locked_field_path in locked_ref.locked_fields:
                # Check if the content attempts to modify a locked field
                # For simplicity, we check if the field exists in the content
                # In a real implementation, we would compare against the original value
                if self._field_exists_in_content(content, locked_field_path):
                    errors.append(ValidationError(
                        field_path=locked_field_path,
                        error_type="locked_field_modified",
                        message=f"Locked field '{locked_field_path}' from document {locked_ref.document_id} cannot be modified"
                    ))
        
        return errors
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected JSON schema type."""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, skip validation
        
        return isinstance(value, expected_python_type)
    
    def _validate_nested_object(
        self,
        obj: Dict[str, Any],
        schema: Dict[str, Any],
        parent_path: str
    ) -> List[ValidationError]:
        """Validate nested object against schema."""
        errors = []
        nested_properties = schema.get("properties", {})
        nested_required = schema.get("required", [])
        
        # Check required fields in nested object
        for field in nested_required:
            if field not in obj:
                errors.append(ValidationError(
                    field_path=f"{parent_path}.{field}",
                    error_type="missing_required",
                    message=f"Required nested field '{parent_path}.{field}' is missing"
                ))
        
        # Check types of nested fields
        for field_name, field_schema in nested_properties.items():
            if field_name in obj:
                expected_type = field_schema.get("type")
                if expected_type and not self._check_type(obj[field_name], expected_type):
                    errors.append(ValidationError(
                        field_path=f"{parent_path}.{field_name}",
                        error_type="schema_violation",
                        message=f"Nested field '{parent_path}.{field_name}' has incorrect type"
                    ))
        
        return errors
    
    def _validate_array(
        self,
        array: List[Any],
        schema: Dict[str, Any],
        parent_path: str
    ) -> List[ValidationError]:
        """Validate array items against schema."""
        errors = []
        items_schema = schema.get("items", {})
        
        if not items_schema:
            return errors
        
        expected_item_type = items_schema.get("type")
        
        for idx, item in enumerate(array):
            item_path = f"{parent_path}[{idx}]"
            
            if expected_item_type:
                if not self._check_type(item, expected_item_type):
                    errors.append(ValidationError(
                        field_path=item_path,
                        error_type="schema_violation",
                        message=f"Array item at '{item_path}' has incorrect type"
                    ))
            
            # Validate nested objects in array
            if expected_item_type == "object" and isinstance(item, dict):
                nested_errors = self._validate_nested_object(
                    item,
                    items_schema,
                    item_path
                )
                errors.extend(nested_errors)
        
        return errors
    
    def _field_exists_in_content(self, content: Dict[str, Any], field_path: str) -> bool:
        """
        Check if a field path exists in content.
        
        Supports simple paths like "field" and nested paths like "characters[0].visual_anchor"
        """
        parts = field_path.split(".")
        current = content
        
        for part in parts:
            # Handle array indexing like "characters[0]"
            if "[" in part and "]" in part:
                field_name = part[:part.index("[")]
                index_str = part[part.index("[")+1:part.index("]")]
                
                if field_name not in current:
                    return False
                
                if not isinstance(current[field_name], list):
                    return False
                
                try:
                    index = int(index_str)
                    if index >= len(current[field_name]):
                        return False
                    current = current[field_name][index]
                except (ValueError, IndexError):
                    return False
            else:
                if part not in current:
                    return False
                current = current[part]
        
        return True
