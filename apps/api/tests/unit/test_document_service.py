"""
Unit tests for document service.

Tests document update functionality including:
- Creating new versions
- Schema validation
- Locked field protection
"""

from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2]))

# Import only the service classes, not the models
from app.services.document_service import (
    DocumentService,
    LockedFieldError,
    SchemaValidationError
)


class TestDocumentServiceValidation:
    """Test document service validation functionality without database."""
    
    def test_validate_schema_brief_valid(self):
        """Test schema validation for valid brief document."""
        service = DocumentService(db=None)
        
        valid_brief = {
            "genre": "romance",
            "target_audience": "young adults",
            "core_selling_points": ["emotional depth", "relatable characters"],
            "main_conflict": "love triangle",
            "target_style": "modern"
        }
        
        # Should not raise any exception
        service._validate_schema(valid_brief, "brief")
    
    def test_validate_schema_brief_missing_required(self):
        """Test schema validation rejects brief missing required fields."""
        service = DocumentService(db=None)
        
        invalid_brief = {
            "genre": "romance",
            "target_audience": "young adults"
            # Missing core_selling_points, main_conflict, target_style
        }
        
        with pytest.raises(SchemaValidationError) as exc_info:
            service._validate_schema(invalid_brief, "brief")
        
        error_msg = str(exc_info.value)
        assert "core_selling_points" in error_msg
        assert "main_conflict" in error_msg
        assert "target_style" in error_msg
    
    def test_validate_schema_brief_empty_required(self):
        """Test schema validation rejects brief with empty required fields."""
        service = DocumentService(db=None)
        
        invalid_brief = {
            "genre": "",  # Empty string
            "target_audience": "young adults",
            "core_selling_points": [],  # Empty list
            "main_conflict": "love triangle",
            "target_style": "modern"
        }
        
        with pytest.raises(SchemaValidationError) as exc_info:
            service._validate_schema(invalid_brief, "brief")
        
        error_msg = str(exc_info.value)
        assert "genre" in error_msg
        assert "core_selling_points" in error_msg
    
    def test_validate_schema_brief_wrong_type(self):
        """Test schema validation rejects brief with wrong field types."""
        service = DocumentService(db=None)
        
        invalid_brief = {
            "genre": "romance",
            "target_audience": "young adults",
            "core_selling_points": "not an array",  # Should be array
            "main_conflict": "love triangle",
            "target_style": "modern"
        }
        
        with pytest.raises(SchemaValidationError) as exc_info:
            service._validate_schema(invalid_brief, "brief")
        
        error_msg = str(exc_info.value)
        assert "core_selling_points" in error_msg
        assert "type" in error_msg.lower()
    
    def test_validate_schema_character_profile_valid(self):
        """Test schema validation for valid character profile."""
        service = DocumentService(db=None)
        
        valid_profile = {
            "characters": [
                {
                    "name": "Alice",
                    "role": "protagonist",
                    "goal": "find love",
                    "motivation": "loneliness",
                    "visual_anchor": "red hair"
                }
            ]
        }
        
        # Should not raise any exception
        service._validate_schema(valid_profile, "character_profile")
    
    def test_validate_schema_character_profile_missing_nested_required(self):
        """Test schema validation rejects character profile with missing nested fields."""
        service = DocumentService(db=None)
        
        invalid_profile = {
            "characters": [
                {
                    "name": "Alice",
                    "role": "protagonist"
                    # Missing goal and motivation
                }
            ]
        }
        
        with pytest.raises(SchemaValidationError) as exc_info:
            service._validate_schema(invalid_profile, "character_profile")
        
        error_msg = str(exc_info.value)
        assert "goal" in error_msg
        assert "motivation" in error_msg
    
    def test_check_locked_fields_simple_field_unchanged(self):
        """Test locked field check passes when simple field unchanged."""
        service = DocumentService(db=None)
        
        old_content = {
            "core_selling_points": ["point1", "point2"],
            "main_conflict": "conflict1",
            "genre": "romance"
        }
        
        new_content = {
            "core_selling_points": ["point1", "point2"],
            "main_conflict": "conflict1",
            "genre": "drama"  # Non-locked field can change
        }
        
        # Should not raise any exception
        service._check_locked_fields(old_content, new_content, "brief")
    
    def test_check_locked_fields_simple_field_modified(self):
        """Test locked field check rejects modification of simple locked field."""
        service = DocumentService(db=None)
        
        old_content = {
            "core_selling_points": ["point1", "point2"],
            "main_conflict": "conflict1"
        }
        
        new_content = {
            "core_selling_points": ["point1", "point3"],  # Modified locked field
            "main_conflict": "conflict1"
        }
        
        with pytest.raises(LockedFieldError) as exc_info:
            service._check_locked_fields(old_content, new_content, "brief")
        
        error_msg = str(exc_info.value)
        assert "core_selling_points" in error_msg
        assert "cannot be modified" in error_msg
    
    def test_check_locked_fields_array_field_unchanged(self):
        """Test locked field check passes when array field unchanged."""
        service = DocumentService(db=None)
        
        old_content = {
            "characters": [
                {"name": "Alice", "visual_anchor": "red hair", "goal": "find love"},
                {"name": "Bob", "visual_anchor": "tall", "goal": "save world"}
            ]
        }
        
        new_content = {
            "characters": [
                {"name": "Alice", "visual_anchor": "red hair", "goal": "find happiness"},  # goal can change
                {"name": "Bob", "visual_anchor": "tall", "goal": "save world"}
            ]
        }
        
        # Should not raise any exception
        service._check_locked_fields(old_content, new_content, "character_profile")
    
    def test_check_locked_fields_array_field_modified(self):
        """Test locked field check rejects modification of locked array field."""
        service = DocumentService(db=None)
        
        old_content = {
            "characters": [
                {"name": "Alice", "visual_anchor": "red hair"},
                {"name": "Bob", "visual_anchor": "tall"}
            ]
        }
        
        new_content = {
            "characters": [
                {"name": "Alice", "visual_anchor": "blue hair"},  # Modified locked field
                {"name": "Bob", "visual_anchor": "tall"}
            ]
        }
        
        with pytest.raises(LockedFieldError) as exc_info:
            service._check_locked_fields(old_content, new_content, "character_profile")
        
        error_msg = str(exc_info.value)
        assert "visual_anchor" in error_msg
        assert "cannot be modified" in error_msg
    
    def test_check_locked_fields_array_length_changed(self):
        """Test locked field check rejects array length change."""
        service = DocumentService(db=None)
        
        old_content = {
            "characters": [
                {"name": "Alice", "visual_anchor": "red hair"}
            ]
        }
        
        new_content = {
            "characters": [
                {"name": "Alice", "visual_anchor": "red hair"},
                {"name": "Bob", "visual_anchor": "tall"}  # Added new character
            ]
        }
        
        with pytest.raises(LockedFieldError) as exc_info:
            service._check_locked_fields(old_content, new_content, "character_profile")
        
        error_msg = str(exc_info.value)
        assert "array length" in error_msg.lower()
    
    def test_get_field_value_simple(self):
        """Test getting simple field value."""
        service = DocumentService(db=None)
        
        content = {"genre": "romance", "tone": "light"}
        
        assert service._get_field_value(content, "genre") == "romance"
        assert service._get_field_value(content, "tone") == "light"
        assert service._get_field_value(content, "missing") is None
    
    def test_get_field_value_nested(self):
        """Test getting nested field value."""
        service = DocumentService(db=None)
        
        content = {
            "metadata": {
                "author": "John",
                "version": 1
            }
        }
        
        assert service._get_field_value(content, "metadata.author") == "John"
        assert service._get_field_value(content, "metadata.version") == 1
        assert service._get_field_value(content, "metadata.missing") is None
