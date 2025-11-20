"""Template storage using JSON file system."""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..models.schema import Template, TemplateMetadata, Field


# Storage directory
STORAGE_DIR = Path(__file__).parent.parent.parent.parent / "storage" / "templates"


def _ensure_storage_dir():
    """Ensure storage directory exists."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _get_template_dir(template_id: str) -> Path:
    """Get directory path for a template."""
    return STORAGE_DIR / template_id


def save_template(document_text: str, fields: List[Field], name: str) -> str:
    """
    Save a new template.

    Args:
        document_text: The original document text
        fields: List of detected fields
        name: Template name

    Returns:
        template_id: Unique identifier for the template
    """
    _ensure_storage_dir()

    # Generate unique ID
    template_id = str(uuid.uuid4())
    template_dir = _get_template_dir(template_id)
    template_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamp
    now = datetime.now()

    # Save document text
    document_path = template_dir / "document.txt"
    document_path.write_text(document_text, encoding="utf-8")

    # Save fields
    fields_path = template_dir / "fields.json"
    fields_data = [field.model_dump() for field in fields]
    fields_path.write_text(json.dumps(fields_data, indent=2), encoding="utf-8")

    # Save metadata
    metadata_path = template_dir / "metadata.json"
    metadata = {
        "id": template_id,
        "name": name,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "field_count": len(fields),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return template_id


def load_template(template_id: str) -> Optional[Template]:
    """
    Load a template by ID.

    Args:
        template_id: Unique template identifier

    Returns:
        Template object or None if not found
    """
    template_dir = _get_template_dir(template_id)

    if not template_dir.exists():
        return None

    try:
        # Load document text
        document_path = template_dir / "document.txt"
        document_text = document_path.read_text(encoding="utf-8")

        # Load fields
        fields_path = template_dir / "fields.json"
        fields_data = json.loads(fields_path.read_text(encoding="utf-8"))
        fields = [Field(**field_dict) for field_dict in fields_data]

        # Load metadata
        metadata_path = template_dir / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        # Create template object
        template = Template(
            id=metadata["id"],
            name=metadata["name"],
            created_at=datetime.fromisoformat(metadata["created_at"]),
            updated_at=datetime.fromisoformat(metadata["updated_at"]),
            document_text=document_text,
            fields=fields,
        )

        return template

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading template {template_id}: {e}")
        return None


def list_templates() -> List[TemplateMetadata]:
    """
    List all available templates.

    Returns:
        List of template metadata
    """
    _ensure_storage_dir()

    templates = []

    for template_dir in STORAGE_DIR.iterdir():
        if not template_dir.is_dir():
            continue

        metadata_path = template_dir / "metadata.json"
        if not metadata_path.exists():
            continue

        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            template_meta = TemplateMetadata(
                id=metadata["id"],
                name=metadata["name"],
                created_at=datetime.fromisoformat(metadata["created_at"]),
                updated_at=datetime.fromisoformat(metadata["updated_at"]),
                field_count=metadata["field_count"],
            )
            templates.append(template_meta)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading template metadata in {template_dir}: {e}")
            continue

    # Sort by created_at descending
    templates.sort(key=lambda t: t.created_at, reverse=True)

    return templates


def update_template(template_id: str, updates: dict) -> bool:
    """
    Update template metadata or content.

    Args:
        template_id: Template identifier
        updates: Dictionary of updates (name, document_text, fields)

    Returns:
        True if successful, False otherwise
    """
    template_dir = _get_template_dir(template_id)

    if not template_dir.exists():
        return False

    try:
        # Load current metadata
        metadata_path = template_dir / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        # Update metadata fields
        if "name" in updates:
            metadata["name"] = updates["name"]

        metadata["updated_at"] = datetime.now().isoformat()

        # Update document text if provided
        if "document_text" in updates:
            document_path = template_dir / "document.txt"
            document_path.write_text(updates["document_text"], encoding="utf-8")

        # Update fields if provided
        if "fields" in updates:
            fields_path = template_dir / "fields.json"
            fields_data = [field.model_dump() if hasattr(field, 'model_dump') else field for field in updates["fields"]]
            fields_path.write_text(json.dumps(fields_data, indent=2), encoding="utf-8")
            metadata["field_count"] = len(updates["fields"])

        # Save updated metadata
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return True

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error updating template {template_id}: {e}")
        return False


def delete_template(template_id: str) -> bool:
    """
    Delete a template.

    Args:
        template_id: Template identifier

    Returns:
        True if successful, False otherwise
    """
    template_dir = _get_template_dir(template_id)

    if not template_dir.exists():
        return False

    try:
        # Delete all files in the directory
        for file_path in template_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()

        # Delete the directory
        template_dir.rmdir()

        return True

    except OSError as e:
        print(f"Error deleting template {template_id}: {e}")
        return False
