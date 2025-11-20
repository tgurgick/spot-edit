"""API routes for Spot Edit - integrates Path 1, 2, and 3."""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel

from ..models.schema import (
    Template,
    TemplateCreateRequest,
    TemplateUpdateRequest,
)
from ..services.document_parser import DocumentParser, DocumentParsingError, UnsupportedFileTypeError
from ..services.field_detector import FieldDetector, FieldDetectionError
from ..services.field_updater import FieldUpdater, FieldUpdateError
from ..services.ai_client import get_ai_client, AIClientError
from ..storage.template_store import get_template_store, TemplateNotFoundError, TemplateStoreError


router = APIRouter()

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


class UpdateFieldsRequest(BaseModel):
    """Request model for updating fields."""
    command: str


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    summary="Upload and analyze document"
)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document and detect editable fields."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    # Read file content
    file_content = await file.read()

    # Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Parse document
    try:
        document_parser = DocumentParser()
        document_text = document_parser.parse_bytes(file_content, file.filename)
    except UnsupportedFileTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DocumentParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse document: {str(e)}"
        )

    # Detect fields using AI
    try:
        ai_client = get_ai_client()
        field_detector = FieldDetector(ai_client)
        detected_fields = field_detector.detect_fields(document_text)
    except (FieldDetectionError, AIClientError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect fields: {str(e)}"
        )

    return {
        "file_id": file.filename,
        "document_text": document_text,
        "detected_fields": [field.model_dump() for field in detected_fields]
    }


@router.get(
    "/templates",
    response_model=List[Template],
    status_code=status.HTTP_200_OK,
    summary="List all templates"
)
async def list_all_templates():
    """List all saved templates."""
    try:
        template_store = get_template_store()
        templates = template_store.list_templates()
        return templates
    except TemplateStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get(
    "/templates/{template_id}",
    response_model=Template,
    status_code=status.HTTP_200_OK,
    summary="Get specific template"
)
async def get_template(template_id: str):
    """Get a specific template by ID."""
    try:
        template_store = get_template_store()
        template = template_store.load_template(template_id)
        return template
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )
    except TemplateStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load template: {str(e)}"
        )


@router.post(
    "/templates",
    status_code=status.HTTP_201_CREATED,
    summary="Create new template"
)
async def create_template(request: TemplateCreateRequest):
    """Save a new template."""
    try:
        template_store = get_template_store()
        template_id = template_store.save_template(
            document_text=request.document_text,
            fields=request.fields,
            name=request.name,
            metadata=request.metadata
        )
        return {
            "template_id": template_id,
            "message": "Template created successfully"
        }
    except TemplateStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


@router.put(
    "/templates/{template_id}",
    response_model=Template,
    status_code=status.HTTP_200_OK,
    summary="Update template"
)
async def update_template(template_id: str, request: TemplateUpdateRequest):
    """Update template metadata or content."""
    try:
        template_store = get_template_store()
        updated_template = template_store.update_template(template_id, request)
        return updated_template
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )
    except TemplateStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete template"
)
async def delete_template(template_id: str):
    """Delete a template."""
    try:
        template_store = get_template_store()
        template_store.delete_template(template_id)
        return {
            "message": "Template deleted successfully",
            "template_id": template_id
        }
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )
    except TemplateStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}"
        )


@router.post(
    "/templates/{template_id}/update",
    status_code=status.HTTP_200_OK,
    summary="Apply natural language update"
)
async def update_template_fields(template_id: str, request: UpdateFieldsRequest):
    """Apply natural language updates to template fields."""
    try:
        template_store = get_template_store()

        # Load template
        template = template_store.load_template(template_id)

        # Parse and apply updates
        ai_client = get_ai_client()
        field_updater = FieldUpdater(ai_client)
        updated_text, parsed = field_updater.parse_and_apply(
            command=request.command,
            document_text=template.document_text,
            existing_fields=template.fields
        )

        # Update template
        update_req = TemplateUpdateRequest(
            document_text=updated_text,
            fields=parsed.updated_fields
        )
        updated_template = template_store.update_template(template_id, update_req)

        return {
            "success": True,
            "message": f"Applied {len(parsed.updates)} update(s)",
            "updated_fields": [u.field_name for u in parsed.updates],
            "template": updated_template.model_dump()
        }

    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )
    except (FieldUpdateError, AIClientError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply updates: {str(e)}"
        )
    except TemplateStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/templates/{template_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download template document"
)
async def download_template(template_id: str):
    """Download the current document text."""
    try:
        template_store = get_template_store()
        template = template_store.load_template(template_id)

        # Return document as text file
        filename = f"{template.name.replace(' ', '_')}.txt"

        return Response(
            content=template.document_text,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id '{template_id}' not found"
        )
    except TemplateStoreError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load template: {str(e)}"
        )
