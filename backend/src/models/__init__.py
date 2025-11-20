"""Data models and schema definitions for Spot Edit application."""

from .schema import (
    # Core models (used by both Path 1 & Path 2)
    Field,
    FieldModel,  # Alias for Field (backward compatibility)
    Template,
    # Field types and structures
    FieldType,
    Position,
    # AI Service models (Path 2)
    FieldUpdate,
    UpdateRequest,
    ParsedUpdate,
    # API Request models (Path 3)
    TemplateCreateRequest,
    TemplateUpdateRequest,
    FieldUpdateRequest,
    # API Response models (Path 3)
    TemplateResponse,
    TemplateListResponse,
    DocumentUploadResponse,
    ErrorResponse,
)

__all__ = [
    # Core models
    "Field",
    "FieldModel",
    "Template",
    # Field types and structures
    "FieldType",
    "Position",
    # AI Service models
    "FieldUpdate",
    "UpdateRequest",
    "ParsedUpdate",
    # API Request models
    "TemplateCreateRequest",
    "TemplateUpdateRequest",
    "FieldUpdateRequest",
    # API Response models
    "TemplateResponse",
    "TemplateListResponse",
    "DocumentUploadResponse",
    "ErrorResponse",
]
