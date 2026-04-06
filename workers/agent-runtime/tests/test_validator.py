"""
Unit tests for the Validator component.

Tests JSON schema validation, required field checking, and locked field protection.
"""

import pytest
from uuid import uuid4
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.validator import Validator, ValidationError, ValidationResult
from agents.base_agent import LockedRef


class TestValidator:
    """Test suite for Validator component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = Validator()
    
    # Test Required Field Validation (Requirement 2.4, 9.5)
    
    def test_validate_all_required_fields_present(self):
        """Test that validation passes when all required fields are present."""
        content = {
            "genre": "romance",
            "target_audience": "young adults",
            "core_selling_points": ["love", "drama"]
        }
        schema = {
            "required": ["genre", "target_audience", "core_selling_points"],
            "properties": {
                "genre": {"type": "string"},
                "target_audience": {"type": "string"},
                "core_selling_points": {"type": "array"}
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_missing_required_field(self):
        """Test that validation fails when a required field is missing."""
        content = {
            "genre": "romance"
        }
        schema = {
            "required": ["genre", "target_audience"],
            "properties": {
                "genre": {"type": "string"},
                "target_audience": {"type": "string"}
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_path == "target_audience"
        assert result.errors[0].error_type == "missing_required"
    
    def test_validate_null_required_field(self):
        """Test that validation fails when a required field is null."""
        content = {
            "genre": "romance",
            "target_audience": None
        }
        schema = {
            "required": ["genre", "target_audience"],
            "properties": {
                "genre": {"type": "string"},
                "target_audience": {"type": "string"}
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_path == "target_audience"
        assert "cannot be null" in result.errors[0].message
    
    def test_validate_empty_string_required_field(self):
        """Test that validation fails when a required string field is empty."""
        content = {
            "genre": "romance",
            "target_audience": "   "
        }
        schema = {
            "required": ["genre", "target_audience"],
            "properties": {
                "genre": {"type": "string"},
                "target_audience": {"type": "string"}
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_path == "target_audience"
        assert "cannot be empty" in result.errors[0].message
    
    def test_validate_empty_list_required_field(self):
        """Test that validation fails when a required list field is empty."""
        content = {
            "genre": "romance",
            "core_selling_points": []
        }
        schema = {
            "required": ["genre", "core_selling_points"],
            "properties": {
                "genre": {"type": "string"},
                "core_selling_points": {"type": "array"}
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_path == "core_selling_points"
        assert "cannot be an empty list" in result.errors[0].message
    
    # Test Schema Type Validation (Requirement 9.5)
    
    def test_validate_correct_field_types(self):
        """Test that validation passes when field types match schema."""
        content = {
            "genre": "romance",
            "episode_count": 10,
            "is_published": True,
            "tags": ["love", "drama"]
        }
        schema = {
            "properties": {
                "genre": {"type": "string"},
                "episode_count": {"type": "integer"},
                "is_published": {"type": "boolean"},
                "tags": {"type": "array"}
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_incorrect_field_type(self):
        """Test that validation fails when field type doesn't match schema."""
        content = {
            "genre": "romance",
            "episode_count": "ten"  # Should be integer
        }
        schema = {
            "properties": {
                "genre": {"type": "string"},
                "episode_count": {"type": "integer"}
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_path == "episode_count"
        assert result.errors[0].error_type == "schema_violation"
    
    def test_validate_nested_object_structure(self):
        """Test validation of nested object structures."""
        content = {
            "character": {
                "name": "Alice",
                "age": 25
            }
        }
        schema = {
            "properties": {
                "character": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    },
                    "required": ["name", "age"]
                }
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_nested_object_missing_required(self):
        """Test that validation fails when nested required field is missing."""
        content = {
            "character": {
                "name": "Alice"
            }
        }
        schema = {
            "properties": {
                "character": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    },
                    "required": ["name", "age"]
                }
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_path == "character.age"
        assert result.errors[0].error_type == "missing_required"
    
    def test_validate_array_items(self):
        """Test validation of array item types."""
        content = {
            "characters": [
                {"name": "Alice", "role": "protagonist"},
                {"name": "Bob", "role": "antagonist"}
            ]
        }
        schema = {
            "properties": {
                "characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"}
                        },
                        "required": ["name", "role"]
                    }
                }
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_array_item_wrong_type(self):
        """Test that validation fails when array item has wrong type."""
        content = {
            "tags": ["romance", 123, "drama"]  # 123 should be string
        }
        schema = {
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "tags[1]" in result.errors[0].field_path
        assert result.errors[0].error_type == "schema_violation"
    
    # Test Locked Field Protection (Requirement 7.5, 9.3)
    
    def test_validate_no_locked_fields_modified(self):
        """Test that validation passes when no locked fields are present."""
        content = {
            "genre": "romance",
            "target_audience": "young adults"
        }
        schema = {
            "properties": {
                "genre": {"type": "string"},
                "target_audience": {"type": "string"}
            }
        }
        locked_refs = []
        
        result = self.validator.validate(content, schema, locked_refs)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_locked_field_modification_rejected(self):
        """Test that validation fails when a locked field is modified."""
        content = {
            "genre": "romance",
            "core_selling_points": ["new point"]  # Locked field
        }
        schema = {
            "properties": {
                "genre": {"type": "string"},
                "core_selling_points": {"type": "array"}
            }
        }
        locked_refs = [
            LockedRef(
                document_id=uuid4(),
                document_type="brief",
                locked_fields=["core_selling_points"]
            )
        ]
        
        result = self.validator.validate(content, schema, locked_refs)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_path == "core_selling_points"
        assert result.errors[0].error_type == "locked_field_modified"
    
    def test_validate_nested_locked_field_modification_rejected(self):
        """Test that validation fails when a nested locked field is modified."""
        content = {
            "characters": [
                {"name": "Alice", "visual_anchor": "new anchor"}
            ]
        }
        schema = {
            "properties": {
                "characters": {
                    "type": "array",
                    "items": {"type": "object"}
                }
            }
        }
        locked_refs = [
            LockedRef(
                document_id=uuid4(),
                document_type="character_profile",
                locked_fields=["characters[0].visual_anchor"]
            )
        ]
        
        result = self.validator.validate(content, schema, locked_refs)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].field_path == "characters[0].visual_anchor"
        assert result.errors[0].error_type == "locked_field_modified"
    
    def test_validate_multiple_locked_fields(self):
        """Test validation with multiple locked fields."""
        content = {
            "core_selling_points": ["point1"],
            "main_conflict": "conflict",
            "genre": "romance"
        }
        schema = {
            "properties": {
                "core_selling_points": {"type": "array"},
                "main_conflict": {"type": "string"},
                "genre": {"type": "string"}
            }
        }
        locked_refs = [
            LockedRef(
                document_id=uuid4(),
                document_type="brief",
                locked_fields=["core_selling_points", "main_conflict"]
            )
        ]
        
        result = self.validator.validate(content, schema, locked_refs)
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        error_fields = [e.field_path for e in result.errors]
        assert "core_selling_points" in error_fields
        assert "main_conflict" in error_fields
    
    # Test Combined Validation Scenarios
    
    def test_validate_multiple_error_types(self):
        """Test that validation catches multiple types of errors."""
        content = {
            "genre": 123,  # Wrong type
            "core_selling_points": ["point"]  # Locked field
        }
        schema = {
            "required": ["genre", "target_audience"],  # Missing target_audience
            "properties": {
                "genre": {"type": "string"},
                "target_audience": {"type": "string"},
                "core_selling_points": {"type": "array"}
            }
        }
        locked_refs = [
            LockedRef(
                document_id=uuid4(),
                document_type="brief",
                locked_fields=["core_selling_points"]
            )
        ]
        
        result = self.validator.validate(content, schema, locked_refs)
        
        assert result.is_valid is False
        assert len(result.errors) == 3
        error_types = [e.error_type for e in result.errors]
        assert "missing_required" in error_types
        assert "schema_violation" in error_types
        assert "locked_field_modified" in error_types
    
    def test_validate_complex_document_structure(self):
        """Test validation of a complex document structure like character_profile."""
        content = {
            "characters": [
                {
                    "name": "Alice",
                    "role": "protagonist",
                    "goal": "Save the world",
                    "motivation": "Love",
                    "speaking_style": "Formal",
                    "visual_anchor": "Red dress"
                }
            ]
        }
        schema = {
            "required": ["characters"],
            "properties": {
                "characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "goal": {"type": "string"},
                            "motivation": {"type": "string"},
                            "speaking_style": {"type": "string"},
                            "visual_anchor": {"type": "string"}
                        },
                        "required": ["name", "role", "goal", "motivation"]
                    }
                }
            }
        }
        
        result = self.validator.validate(content, schema)
        
        assert result.is_valid is True
        assert len(result.errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
