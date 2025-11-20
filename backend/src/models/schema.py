"""
Data models and schemas for Spot Edit application.

This module defines the core data structures used throughout the application,
including templates, fields, and update requests.
"""

from datetime import datetime
from typing import List, Optional, Tuple, Literal
from uuid import uuid4
from pydantic import BaseModel, Field as PydanticField, validator


class Field(BaseModel):
    """
    Represents an editable field within a document template.

    Fields can appear multiple times in a document (e.g., client name in header and footer).
    Positions track all occurrences using character ranges.
    """
    id: str = PydanticField(default_factory=lambda: str(uuid4()))
    name: str = PydanticField(..., description="Identifier for the field (e.g., 'client_name')")
    type: Literal["text", "date", "number"] = PydanticField(
        default="text",
        description="Data type of the field"
    )
    positions: List[Tuple[int, int]] = PydanticField(
        default_factory=list,
        description="List of (start, end) character positions where field appears"
    )
    current_value: Optional[str] = PydanticField(
        default=None,
        description="Current value of the field"
    )

    @validator('positions')
    def validate_positions(cls, v):
        """Ensure all positions are valid ranges."""
        for start, end in v:
            if start < 0 or end < 0:
                raise ValueError("Position indices must be non-negative")
            if start >= end:
                raise ValueError("Start position must be less than end position")
        return v

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


class Template(BaseModel):
    """
    Represents a document template with editable fields.

    Templates contain the original document text and metadata about
    editable fields within that text.
    """
    id: str = PydanticField(default_factory=lambda: str(uuid4()))
    name: str = PydanticField(..., description="Human-readable template name")
    created_at: datetime = PydanticField(default_factory=datetime.utcnow)
    document_text: str = PydanticField(..., description="Full text content of the document")
    fields: List[Field] = PydanticField(
        default_factory=list,
        description="List of editable fields in the document"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "tmpl_123",
                "name": "Contract Template",
                "created_at": "2024-01-01T00:00:00Z",
                "document_text": "This contract is between...",
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


class FieldUpdate(BaseModel):
    """
    Represents a single field update operation.
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
