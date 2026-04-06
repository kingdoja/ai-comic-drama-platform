"""
Document service for handling document updates with validation.

Implements Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import DocumentModel
from app.repositories.document_repository import DocumentRepository


class LockedFieldError(ValueError):
    """Raised when attempting to modify a locked field."""
    pass


class SchemaValidationError(ValueError):
    """Raised when document content fails schema validation."""
    pass


class DocumentService:
    """Service for managing document updates with validation."""
    
    # Define schemas for each document type
    DOCUMENT_SCHEMAS = {
        "brief": {
            "type": "object",
            "required": [
                "genre",
                "target_audience",
                "core_selling_points",
                "main_conflict",
                "target_style"
            ],
            "properties": {
                "genre": {"type": "string"},
                "target_audience": {"type": "string"},
                "core_selling_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "main_conflict": {"type": "string"},
                "adaptation_risks": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "target_style": {"type": "string"},
                "tone": {"type": "string"}
            }
        },
        "story_bible": {
            "type": "object",
            "required": ["world_rules", "forbidden_conflicts"],
            "properties": {
                "world_rules": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "timeline": {
                    "type": "array",
                    "items": {"type": "object"}
                },
                "relationship_baseline": {"type": "object"},
                "forbidden_conflicts": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "key_settings": {"type": "object"}
            }
        },
        "character_profile": {
            "type": "object",
            "required": ["characters"],
            "properties": {
                "characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "role", "goal", "motivation"],
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "goal": {"type": "string"},
                            "motivation": {"type": "string"},
                            "speaking_style": {"type": "string"},
                            "visual_anchor": {"type": "string"},
                            "personality_traits": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "relationships": {"type": "object"}
                        }
                    }
                }
            }
        },
        "script_draft": {
            "type": "object",
            "required": ["scenes"],
            "properties": {
                "scenes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["scene_no", "location", "characters", "dialogue"],
                        "properties": {
                            "scene_no": {"type": "integer"},
                            "location": {"type": "string"},
                            "characters": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "goal": {"type": "string"},
                            "dialogue": {"type": "array"},
                            "emotion_beats": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "duration_estimate_sec": {"type": "integer"}
                        }
                    }
                }
            }
        },
        "visual_spec": {
            "type": "object",
            "required": ["shots"],
            "properties": {
                "shots": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "shot_id": {"type": "string"},
                            "render_prompt": {"type": "string"},
                            "character_refs": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "style_keywords": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "composition": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
    
    # Define locked fields for each document type
    LOCKED_FIELDS = {
        "brief": ["core_selling_points", "main_conflict"],
        "story_bible": ["forbidden_conflicts", "world_rules"],
        "character_profile": ["characters[*].name", "characters[*].visual_anchor"],
        "script_draft": [],
        "visual_spec": []
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.document_repo = DocumentRepository(db)
    
    def update_document(
        self,
        document_id: UUID,
        new_content: Dict[str, Any],
        user_id: UUID
    ) -> DocumentModel:
        """
        Update a document by creating a new version.
        
        Implements:
        - Requirement 9.1: Create new version instead of overwriting
        - Requirement 9.2: Record editing source (user_id)
        - Requirement 9.3: Reject edits that modify locked fields
        - Requirement 9.4: Update updated_at timestamp
        - Requirement 9.5: Validate content against schema
        
        Args:
            document_id: ID of the document to update
            new_content: New content for the document
            user_id: ID of the user making the edit
            
        Returns:
            The newly created document version
            
        Raises:
            ValueError: If document not found
            LockedFieldError: If attempting to modify locked fields
            SchemaValidationError: If content fails schema validation
        """
        # Get the existing document
        existing_doc = self.document_repo.get_by_id(document_id)
        if not existing_doc:
            raise ValueError(f"Document {document_id} not found")
        
        # Validate schema (Requirement 9.5)
        self._validate_schema(new_content, existing_doc.document_type)
        
        # Check locked fields (Requirement 9.3)
        self._check_locked_fields(
            existing_doc.content_jsonb,
            new_content,
            existing_doc.document_type
        )
        
        # Create new version (Requirement 9.1)
        new_version = existing_doc.version + 1
        
        # Create new document record (Requirement 9.2: set created_by to user_id)
        new_document = self.document_repo.create(
            project_id=existing_doc.project_id,
            episode_id=existing_doc.episode_id,
            stage_task_id=existing_doc.stage_task_id,
            document_type=existing_doc.document_type,
            version=new_version,
            status=existing_doc.status,
            title=existing_doc.title,
            content_jsonb=new_content,
            summary_text=existing_doc.summary_text,
            created_by=user_id,  # Requirement 9.2: Record user as creator
            commit=True
        )
        
        # Requirement 9.4: updated_at is automatically set by the database
        
        return new_document
    
    def _validate_schema(self, content: Dict[str, Any], document_type: str) -> None:
        """
        Validate content against document type schema.
        
        Implements Requirement 9.5: Schema validation
        
        Raises:
            SchemaValidationError: If validation fails
        """
        schema = self.DOCUMENT_SCHEMAS.get(document_type)
        if not schema:
            # Unknown document type, skip validation
            return
        
        errors = []
        
        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in content:
                errors.append(f"Required field '{field}' is missing")
            elif content[field] is None:
                errors.append(f"Required field '{field}' cannot be null")
            elif isinstance(content[field], str) and not content[field].strip():
                errors.append(f"Required field '{field}' cannot be empty")
            elif isinstance(content[field], list) and len(content[field]) == 0:
                errors.append(f"Required field '{field}' cannot be an empty list")
        
        # Check field types
        properties = schema.get("properties", {})
        for field_name, field_schema in properties.items():
            if field_name not in content:
                continue
            
            field_value = content[field_name]
            expected_type = field_schema.get("type")
            
            if expected_type and not self._check_type(field_value, expected_type):
                errors.append(
                    f"Field '{field_name}' has incorrect type. "
                    f"Expected {expected_type}, got {type(field_value).__name__}"
                )
            
            # Validate nested structures
            if expected_type == "array" and isinstance(field_value, list):
                items_schema = field_schema.get("items", {})
                if items_schema.get("type") == "object":
                    for idx, item in enumerate(field_value):
                        if not isinstance(item, dict):
                            errors.append(f"Array item at '{field_name}[{idx}]' must be an object")
                            continue
                        
                        # Check required fields in array items
                        item_required = items_schema.get("required", [])
                        for req_field in item_required:
                            if req_field not in item:
                                errors.append(
                                    f"Required field '{field_name}[{idx}].{req_field}' is missing"
                                )
        
        if errors:
            raise SchemaValidationError("; ".join(errors))
    
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
            return True
        
        return isinstance(value, expected_python_type)
    
    def _check_locked_fields(
        self,
        old_content: Dict[str, Any],
        new_content: Dict[str, Any],
        document_type: str
    ) -> None:
        """
        Check if any locked fields have been modified.
        
        Implements Requirement 9.3: Locked field protection
        
        Raises:
            LockedFieldError: If locked fields have been modified
        """
        locked_fields = self.LOCKED_FIELDS.get(document_type, [])
        if not locked_fields:
            return
        
        errors = []
        
        for field_path in locked_fields:
            # Handle wildcard patterns like "characters[*].name"
            if "[*]" in field_path:
                errors.extend(self._check_array_locked_fields(
                    old_content, new_content, field_path
                ))
            else:
                # Simple field path
                old_value = self._get_field_value(old_content, field_path)
                new_value = self._get_field_value(new_content, field_path)
                
                if old_value != new_value:
                    errors.append(f"Locked field '{field_path}' cannot be modified")
        
        if errors:
            raise LockedFieldError("; ".join(errors))
    
    def _check_array_locked_fields(
        self,
        old_content: Dict[str, Any],
        new_content: Dict[str, Any],
        field_path: str
    ) -> List[str]:
        """Check locked fields in array items."""
        errors = []
        
        # Parse field path like "characters[*].name"
        parts = field_path.split("[*]")
        if len(parts) != 2:
            return errors
        
        array_field = parts[0]
        item_field = parts[1].lstrip(".")
        
        old_array = old_content.get(array_field, [])
        new_array = new_content.get(array_field, [])
        
        # Check if arrays have same length
        if len(old_array) != len(new_array):
            errors.append(
                f"Cannot modify array length for locked field '{array_field}'"
            )
            return errors
        
        # Check each item
        for idx, (old_item, new_item) in enumerate(zip(old_array, new_array)):
            if not isinstance(old_item, dict) or not isinstance(new_item, dict):
                continue
            
            old_value = old_item.get(item_field)
            new_value = new_item.get(item_field)
            
            if old_value != new_value:
                errors.append(
                    f"Locked field '{array_field}[{idx}].{item_field}' cannot be modified"
                )
        
        return errors
    
    def _get_field_value(self, content: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested field path."""
        parts = field_path.split(".")
        current = content
        
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
            if current is None:
                return None
        
        return current
