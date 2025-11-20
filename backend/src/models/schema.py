"""Data models and schemas for Spot Edit API."""
from datetime import datetime
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field as PydanticField


class Field(BaseModel):
    """Represents an editable field in a document."""

    id: str
    name: str
    type: str  # text, date, number, etc.
    positions: List[Tuple[int, int]]  # List of (start, end) positions in document
    current_value: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "field_1",
                "name": "client_name",
                "type": "text",
                "positions": [[100, 115], [450, 465]],
                "current_value": "John Doe"
            }
        }


class TemplateMetadata(BaseModel):
    """Metadata for a template."""

    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    field_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "id": "template_123",
                "name": "Contract Template",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00",
                "field_count": 5
            }
        }


class Template(BaseModel):
    """Complete template with document and fields."""

    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    document_text: str
    fields: List[Field]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "template_123",
                "name": "Contract Template",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00",
                "document_text": "This is a contract between...",
                "fields": [
                    {
                        "id": "field_1",
                        "name": "client_name",
                        "type": "text",
                        "positions": [[100, 115]],
                        "current_value": "John Doe"
                    }
                ]
            }
        }


class UpdateRequest(BaseModel):
    """Request to update fields using natural language."""

    command: str = PydanticField(..., description="Natural language command to update fields")

    class Config:
        json_schema_extra = {
            "example": {
                "command": "Change client name to Acme Corp and set contract date to January 20, 2024"
            }
        }


class UpdateResponse(BaseModel):
    """Response after applying updates."""

    success: bool
    message: str
    updated_fields: List[str]
    document_text: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Updated 2 fields",
                "updated_fields": ["client_name", "contract_date"],
                "document_text": "Updated document text..."
            }
        }


class UploadResponse(BaseModel):
    """Response after uploading and analyzing a document."""

    file_id: str
    document_text: str
    detected_fields: List[Field]

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "upload_456",
                "document_text": "This is a contract...",
                "detected_fields": [
                    {
                        "id": "field_1",
                        "name": "client_name",
                        "type": "text",
                        "positions": [[100, 115]],
                        "current_value": "John Doe"
                    }
                ]
            }
        }


class TemplateCreateRequest(BaseModel):
    """Request to create a new template."""

    name: str
    document_text: str
    fields: List[Field]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Contract Template",
                "document_text": "This is a contract...",
                "fields": [
                    {
                        "id": "field_1",
                        "name": "client_name",
                        "type": "text",
                        "positions": [[100, 115]],
                        "current_value": "John Doe"
                    }
                ]
            }
        }


class TemplateUpdateMetadataRequest(BaseModel):
    """Request to update template metadata."""

    name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Contract Template"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Template not found",
                "detail": "Template with id 'template_123' does not exist"
            }
        }
