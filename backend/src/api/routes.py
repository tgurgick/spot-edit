"""API routes for Spot Edit."""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import Response

from ..models.schema import (
    Template,
    TemplateMetadata,
    TemplateCreateRequest,
    TemplateUpdateMetadataRequest,
    UpdateRequest,
    UpdateResponse,
    UploadResponse,
    ErrorResponse,
)
from ..services import (
    parse_document,
    detect_fields,
    parse_update_command,
    apply_updates,
)
from ..storage import (
    save_template,
    load_template,
    list_templates,
    update_template,
    delete_template,
    save_upload,
)
from .middleware import validate_file_size, validate_file_extension


router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or file format"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    summary="Upload and analyze document",
    description="Upload a document (txt, pdf, docx) and detect editable fields using AI"
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document and detect editable fields.

    - **file**: Document file to upload (txt, pdf, docx)

    Returns detected fields and document text.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    validate_file_extension(file.filename)

    # Read file content
    file_content = await file.read()
    validate_file_size(len(file_content))

    # Save upload temporarily
    file_id = save_upload(file_content, file.filename)

    # Parse document
    try:
        document_text = parse_document(file_content, file.filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Detect fields using AI
    detected_fields = detect_fields(document_text)

    return UploadResponse(
        file_id=file_id,
        document_text=document_text,
        detected_fields=detected_fields
    )


@router.get(
    "/templates",
    response_model=List[TemplateMetadata],
    status_code=status.HTTP_200_OK,
    summary="List all templates",
    description="Get a list of all saved document templates"
)
async def get_templates():
    """
    List all saved templates.

    Returns list of template metadata (id, name, created_at, field_count).
    """
    templates = list_templates()
    return templates


@router.get(
    "/templates/{template_id}",
    response_model=Template,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Template not found"},
    },
    summary="Get specific template",
    description="Retrieve a template by its ID with full details"
)
async def get_template(template_id: str):
    """
    Get a specific template by ID.

    - **template_id**: Unique template identifier

    Returns complete template with document text and fields.
    """
    template = load_template(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )

    return template


@router.post(
    "/templates",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
    summary="Save new template",
    description="Create a new template from document and detected fields"
)
async def create_template(request: TemplateCreateRequest):
    """
    Save a new template.

    - **name**: Template name
    - **document_text**: Original document text
    - **fields**: List of detected/confirmed fields

    Returns the new template ID.
    """
    if not request.name or not request.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template name is required"
        )

    if not request.document_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document text is required"
        )

    template_id = save_template(
        document_text=request.document_text,
        fields=request.fields,
        name=request.name
    )

    return {
        "template_id": template_id,
        "message": "Template created successfully"
    }


@router.put(
    "/templates/{template_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Template not found"},
    },
    summary="Update template metadata",
    description="Update template name or other metadata"
)
async def update_template_metadata(template_id: str, request: TemplateUpdateMetadataRequest):
    """
    Update template metadata (name, etc.).

    - **template_id**: Template identifier
    - **name**: New template name (optional)

    Returns success message.
    """
    # Check if template exists
    template = load_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )

    # Prepare updates
    updates = {}
    if request.name is not None:
        updates["name"] = request.name

    # Apply updates
    success = update_template(template_id, updates)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template"
        )

    return {
        "message": "Template updated successfully",
        "template_id": template_id
    }


@router.delete(
    "/templates/{template_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Template not found"},
    },
    summary="Delete template",
    description="Delete a template by its ID"
)
async def delete_template_by_id(template_id: str):
    """
    Delete a template.

    - **template_id**: Template identifier

    Returns success message.
    """
    # Check if template exists
    template = load_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )

    # Delete template
    success = delete_template(template_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete template"
        )

    return {
        "message": "Template deleted successfully",
        "template_id": template_id
    }


@router.post(
    "/templates/{template_id}/update",
    response_model=UpdateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Template not found"},
        400: {"model": ErrorResponse, "description": "Invalid update command"},
    },
    summary="Apply natural language update",
    description="Update template fields using natural language commands"
)
async def update_template_fields(template_id: str, request: UpdateRequest):
    """
    Apply natural language updates to template fields.

    - **template_id**: Template identifier
    - **command**: Natural language command (e.g., "Change client name to Acme Corp")

    Returns updated document and list of updated fields.
    """
    # Load template
    template = load_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )

    # Parse update command
    field_updates = parse_update_command(request.command, template.fields)

    if not field_updates:
        return UpdateResponse(
            success=False,
            message="No field updates identified from command",
            updated_fields=[],
            document_text=template.document_text
        )

    # Apply updates
    updated_text, updated_fields = apply_updates(
        template.document_text,
        field_updates,
        template.fields
    )

    # Save updated template
    update_template(template_id, {
        "document_text": updated_text,
        "fields": updated_fields
    })

    return UpdateResponse(
        success=True,
        message=f"Updated {len(field_updates)} field(s)",
        updated_fields=list(field_updates.keys()),
        document_text=updated_text
    )


@router.get(
    "/templates/{template_id}/download",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Template not found"},
    },
    summary="Download updated document",
    description="Download the current document as plain text"
)
async def download_template(template_id: str):
    """
    Download the current document text.

    - **template_id**: Template identifier

    Returns document as plain text file.
    """
    # Load template
    template = load_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )

    # Return document as text file
    filename = f"{template.name.replace(' ', '_')}.txt"

    return Response(
        content=template.document_text,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
