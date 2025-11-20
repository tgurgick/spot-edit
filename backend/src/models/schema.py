"""
Data models and schemas for Spot Edit application.

This module defines the core data structures used throughout the application,
including templates, fields, and various request/response models.

Combines storage models (Path 1) with AI service models (Path 2).
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple, Union, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field as PydanticField, field_validator, validator


class FieldType(str, Enum):
    """Supported field types for template fields."""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    CUSTOM = "custom"


class Position(BaseModel):
    """
    Represents a structured position in the document where a field appears.

    Used for page-aware document formats like PDF.
    """
    page: int = PydanticField(..., ge=1, description="Page number (1-indexed)")
    start: int = PydanticField(..., ge=0, description="Start character position")
    end: int = PydanticField(..., gt=0, description="End character position")

    @field_validator('end')
    @classmethod
    def validate_end_after_start(cls, v: int, info) -> int:
        """Ensure end position is after start position."""
        if 'start' in info.data and v <= info.data['start']:
            raise ValueError("end position must be greater than start position")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "start": 100,
                "end": 150
            }
        }


class Field(BaseModel):
    """
    Represents an editable field within a document template.

    Fields can appear multiple times in a document (e.g., client name in header and footer).
    Supports both simple tuple positions and structured Position objects.
    """
    id: str = PydanticField(default_factory=lambda: str(uuid4()))
    name: str = PydanticField(..., description="Identifier for the field (e.g., 'client_name')")
    type: Literal["text", "date", "number", "email", "phone", "address", "custom"] = PydanticField(
        default="text",
        description="Data type of the field"
    )
    # Support both tuple positions (for simple docs) and Position objects (for complex docs)
    positions: Union[List[Tuple[int, int]], List[Position]] = PydanticField(
        default_factory=list,
        description="List of positions where field appears (tuples or Position objects)"
    )
    current_value: Optional[str] = PydanticField(
        default=None,
        description="Current value of the field"
    )
    metadata: Dict[str, Any] = PydanticField(
        default_factory=dict,
        description="Additional metadata for the field"
    )

    @validator('positions')
    def validate_positions(cls, v):
        """Ensure all positions are valid ranges."""
        for pos in v:
            if isinstance(pos, tuple):
                start, end = pos
                if start < 0 or end < 0:
                    raise ValueError("Position indices must be non-negative")
                if start >= end:
                    raise ValueError("Start position must be less than end position")
            # Position objects validate themselves
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "field_1",
                "name": "client_name",
                "type": "text",
                "positions": [[100, 115], [450, 465]],
                "current_value": "John Doe",
                "metadata": {}
            }
        }


# Alias for backward compatibility with storage layer
FieldModel = Field


class Template(BaseModel):
    """
    Represents a document template with editable fields.

    Templates contain the original document text and metadata about
    editable fields within that text.
    """
    id: str = PydanticField(default_factory=lambda: str(uuid4()))
    name: str = PydanticField(..., description="Human-readable template name")
    created_at: datetime = PydanticField(default_factory=datetime.utcnow)
    updated_at: datetime = PydanticField(
        default_factory=datetime.utcnow,
        description="Template last update timestamp"
    )
    document_text: str = PydanticField(..., description="Full text content of the document")
    fields: List[Field] = PydanticField(
        default_factory=list,
        description="List of editable fields in the document"
    )
    metadata: Dict[str, Any] = PydanticField(
        default_factory=dict,
        description="Additional metadata (file type, original filename, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "tmpl_123",
                "name": "Contract Template",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "document_text": "This contract is between...",
                "fields": [
                    {
                        "id": "field_1",
                        "name": "client_name",
                        "type": "text",
                        "positions": [[100, 115]],
                        "current_value": "John Doe"
                    }
                ],
                "metadata": {}
            }
        }


class FieldUpdate(BaseModel):
    """
    Represents a single field update operation.

    Used by AI services to represent parsed update commands.
    """
    field_name: str = PydanticField(..., description="Name of the field to update")
    new_value: str = PydanticField(..., description="New value for the field")
    confidence: Optional[float] = PydanticField(
        default=None,
        description="Confidence score of the update interpretation (0-1)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "field_name": "client_name",
                "new_value": "Jane Smith",
                "confidence": 0.95
            }
        }


class UpdateRequest(BaseModel):
    """
    Represents a natural language request to update document fields.

    Used by AI services for natural language processing.
    """
    template_id: str = PydanticField(..., description="ID of the template to update")
    command: str = PydanticField(
        ...,
        description="Natural language command describing the updates"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "tmpl_123",
                "command": "Change the client name to Jane Smith and set the date to January 15, 2024"
            }
        }


class ParsedUpdate(BaseModel):
    """
    Result of parsing an update command.

    Used by AI services to return parsed natural language commands.
    """
    updates: List[FieldUpdate] = PydanticField(
        default_factory=list,
        description="List of field updates extracted from the command"
    )
    unrecognized_parts: List[str] = PydanticField(
        default_factory=list,
        description="Parts of the command that couldn't be interpreted"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "updates": [
                    {
                        "field_name": "client_name",
                        "new_value": "Jane Smith",
                        "confidence": 0.95
                    }
                ],
                "unrecognized_parts": []
            }
        }


# API Request/Response Models (for Path 3)

class TemplateCreateRequest(BaseModel):
    """Request model for creating a new template."""
    name: str = PydanticField(..., min_length=1, max_length=200)
    document_text: str = PydanticField(..., min_length=1)
    fields: List[Field] = PydanticField(default_factory=list)
    metadata: Dict[str, Any] = PydanticField(default_factory=dict)


class TemplateUpdateRequest(BaseModel):
    """Request model for updating an existing template."""
    name: Optional[str] = PydanticField(None, min_length=1, max_length=200)
    document_text: Optional[str] = PydanticField(None, min_length=1)
    fields: Optional[List[Field]] = None
    metadata: Optional[Dict[str, Any]] = None


class FieldUpdateRequest(BaseModel):
    """Request model for updating field values in a template."""
    field_updates: Dict[str, str] = PydanticField(
        ...,
        description="Mapping of field names to their new values"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "field_updates": {
                    "recipient_name": "Jane Smith",
                    "date": "2024-01-20"
                }
            }
        }


class TemplateResponse(BaseModel):
    """Response model for template operations."""
    success: bool = PydanticField(..., description="Whether the operation succeeded")
    template_id: Optional[str] = PydanticField(None, description="ID of the template")
    message: str = PydanticField(..., description="Response message")
    template: Optional[Template] = PydanticField(None, description="Template data (if applicable)")


class TemplateListResponse(BaseModel):
    """Response model for listing templates."""
    success: bool = PydanticField(..., description="Whether the operation succeeded")
    templates: List[Template] = PydanticField(default_factory=list, description="List of templates")
    count: int = PydanticField(..., ge=0, description="Total number of templates")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload operations."""
    success: bool = PydanticField(..., description="Whether the operation succeeded")
    file_id: Optional[str] = PydanticField(None, description="ID of the uploaded file")
    message: str = PydanticField(..., description="Response message")
    metadata: Dict[str, Any] = PydanticField(
        default_factory=dict,
        description="Upload metadata (filename, size, type, etc.)"
    )


class ErrorResponse(BaseModel):
    """Response model for error cases."""
    success: bool = PydanticField(default=False, description="Always False for errors")
    error: str = PydanticField(..., description="Error type")
    message: str = PydanticField(..., description="Detailed error message")
    details: Optional[Dict[str, Any]] = PydanticField(
        None,
        description="Additional error details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "TemplateNotFound",
                "message": "Template with ID abc123 not found",
                "details": {"template_id": "abc123"}
            }
        }
