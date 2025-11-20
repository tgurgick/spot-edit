"""
Data models and schema definitions for Spot Edit backend.

This module defines the core data structures used throughout the application,
including templates, fields, and various request/response models.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


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
    """Represents a position in the document where a field appears."""
    page: int = Field(..., ge=1, description="Page number (1-indexed)")
    start: int = Field(..., ge=0, description="Start character position")
    end: int = Field(..., gt=0, description="End character position")

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


class FieldModel(BaseModel):
    """
    Represents an editable field within a document template.

    Fields are detected by AI and confirmed by users. They represent
    specific areas in the document that can be updated with new values.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique field identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Field name")
    field_type: FieldType = Field(..., description="Type of the field")
    positions: List[Position] = Field(
        ...,
        min_length=1,
        description="List of positions where this field appears in the document"
    )
    current_value: Optional[str] = Field(
        None,
        description="Current value of the field (if set)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the field"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "recipient_name",
                "field_type": "text",
                "positions": [
                    {"page": 1, "start": 100, "end": 120}
                ],
                "current_value": "John Doe",
                "metadata": {}
            }
        }


class Template(BaseModel):
    """
    Represents a document template with editable fields.

    Templates are created from uploaded documents after AI field detection
    and user confirmation. They can be reused with different field values.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique template identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Template name")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Template creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Template last update timestamp"
    )
    document_text: str = Field(
        ...,
        min_length=1,
        description="Full text content of the document"
    )
    fields: List[FieldModel] = Field(
        default_factory=list,
        description="List of editable fields in the template"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (file type, original filename, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Welcome Letter Template",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "document_text": "Dear {{recipient_name}}, Welcome to...",
                "fields": [],
                "metadata": {
                    "file_type": "pdf",
                    "original_filename": "welcome_letter.pdf"
                }
            }
        }


class TemplateCreateRequest(BaseModel):
    """Request model for creating a new template."""
    name: str = Field(..., min_length=1, max_length=200)
    document_text: str = Field(..., min_length=1)
    fields: List[FieldModel] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemplateUpdateRequest(BaseModel):
    """Request model for updating an existing template."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    document_text: Optional[str] = Field(None, min_length=1)
    fields: Optional[List[FieldModel]] = None
    metadata: Optional[Dict[str, Any]] = None


class FieldUpdateRequest(BaseModel):
    """Request model for updating field values in a template."""
    field_updates: Dict[str, str] = Field(
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
    success: bool = Field(..., description="Whether the operation succeeded")
    template_id: Optional[UUID] = Field(None, description="ID of the template")
    message: str = Field(..., description="Response message")
    template: Optional[Template] = Field(None, description="Template data (if applicable)")


class TemplateListResponse(BaseModel):
    """Response model for listing templates."""
    success: bool = Field(..., description="Whether the operation succeeded")
    templates: List[Template] = Field(default_factory=list, description="List of templates")
    count: int = Field(..., ge=0, description="Total number of templates")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload operations."""
    success: bool = Field(..., description="Whether the operation succeeded")
    file_id: Optional[UUID] = Field(None, description="ID of the uploaded file")
    message: str = Field(..., description="Response message")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Upload metadata (filename, size, type, etc.)"
    )


class ErrorResponse(BaseModel):
    """Response model for error cases."""
    success: bool = Field(default=False, description="Always False for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    details: Optional[Dict[str, Any]] = Field(
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
