"""
Template storage implementation using JSON file storage.

This module provides CRUD operations for template persistence using
the file system with JSON format. Designed for MVP; can be replaced
with database storage later.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from ..models.schema import (
    Template,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    FieldModel
)


class TemplateStoreError(Exception):
    """Base exception for template storage errors."""
    pass


class TemplateNotFoundError(TemplateStoreError):
    """Raised when a template is not found."""
    pass


class TemplateStore:
    """
    Template storage manager using JSON file system.

    Each template is stored as a separate JSON file in the templates directory.
    File naming: {template_id}.json
    """

    def __init__(self, storage_path: str = "storage/templates"):
        """
        Initialize the template store.

        Args:
            storage_path: Path to the templates storage directory
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Create storage directory if it doesn't exist."""
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_template_file_path(self, template_id: UUID) -> Path:
        """Get the file path for a template."""
        return self.storage_path / f"{template_id}.json"

    def _template_to_dict(self, template: Template) -> Dict[str, Any]:
        """
        Convert a Template object to a JSON-serializable dictionary.

        Args:
            template: Template object to convert

        Returns:
            Dictionary representation with serialized UUIDs and datetimes
        """
        data = template.model_dump(mode='json')
        # Ensure UUIDs and datetimes are strings
        data['id'] = str(template.id)
        data['created_at'] = template.created_at.isoformat()
        data['updated_at'] = template.updated_at.isoformat()
        data['fields'] = [
            {
                **field.model_dump(mode='json'),
                'id': str(field.id)
            }
            for field in template.fields
        ]
        return data

    def _dict_to_template(self, data: Dict[str, Any]) -> Template:
        """
        Convert a dictionary to a Template object.

        Args:
            data: Dictionary representation of a template

        Returns:
            Template object
        """
        return Template.model_validate(data)

    def save_template(
        self,
        document_text: str,
        fields: List[FieldModel],
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Save a new template to storage.

        Args:
            document_text: Full text content of the document
            fields: List of editable fields
            name: Template name
            metadata: Additional metadata (optional)

        Returns:
            UUID of the created template

        Raises:
            TemplateStoreError: If saving fails
        """
        try:
            # Create template object
            template = Template(
                id=uuid4(),
                name=name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                document_text=document_text,
                fields=fields,
                metadata=metadata or {}
            )

            # Save to file
            file_path = self._get_template_file_path(template.id)
            template_data = self._template_to_dict(template)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            return template.id

        except Exception as e:
            raise TemplateStoreError(f"Failed to save template: {str(e)}") from e

    def load_template(self, template_id: UUID) -> Template:
        """
        Load a template from storage.

        Args:
            template_id: UUID of the template to load

        Returns:
            Template object

        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateStoreError: If loading fails
        """
        file_path = self._get_template_file_path(template_id)

        if not file_path.exists():
            raise TemplateNotFoundError(
                f"Template with ID {template_id} not found"
            )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return self._dict_to_template(data)

        except json.JSONDecodeError as e:
            raise TemplateStoreError(
                f"Failed to parse template {template_id}: {str(e)}"
            ) from e
        except Exception as e:
            raise TemplateStoreError(
                f"Failed to load template {template_id}: {str(e)}"
            ) from e

    def list_templates(self) -> List[Template]:
        """
        List all templates in storage.

        Returns:
            List of Template objects, sorted by creation date (newest first)

        Raises:
            TemplateStoreError: If listing fails
        """
        try:
            templates = []

            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    template = self._dict_to_template(data)
                    templates.append(template)
                except Exception as e:
                    # Log error but continue with other templates
                    print(f"Warning: Failed to load template from {file_path}: {e}")
                    continue

            # Sort by created_at, newest first
            templates.sort(key=lambda t: t.created_at, reverse=True)

            return templates

        except Exception as e:
            raise TemplateStoreError(f"Failed to list templates: {str(e)}") from e

    def update_template(
        self,
        template_id: UUID,
        updates: TemplateUpdateRequest
    ) -> Template:
        """
        Update an existing template.

        Args:
            template_id: UUID of the template to update
            updates: TemplateUpdateRequest with fields to update

        Returns:
            Updated Template object

        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateStoreError: If update fails
        """
        # Load existing template
        template = self.load_template(template_id)

        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)

        if 'name' in update_data:
            template.name = update_data['name']
        if 'document_text' in update_data:
            template.document_text = update_data['document_text']
        if 'fields' in update_data:
            template.fields = update_data['fields']
        if 'metadata' in update_data:
            # Merge metadata instead of replacing
            template.metadata.update(update_data['metadata'])

        # Update timestamp
        template.updated_at = datetime.utcnow()

        # Save updated template
        try:
            file_path = self._get_template_file_path(template_id)
            template_data = self._template_to_dict(template)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            return template

        except Exception as e:
            raise TemplateStoreError(
                f"Failed to update template {template_id}: {str(e)}"
            ) from e

    def delete_template(self, template_id: UUID) -> bool:
        """
        Delete a template from storage.

        Args:
            template_id: UUID of the template to delete

        Returns:
            True if deletion was successful

        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateStoreError: If deletion fails
        """
        file_path = self._get_template_file_path(template_id)

        if not file_path.exists():
            raise TemplateNotFoundError(
                f"Template with ID {template_id} not found"
            )

        try:
            file_path.unlink()
            return True

        except Exception as e:
            raise TemplateStoreError(
                f"Failed to delete template {template_id}: {str(e)}"
            ) from e

    def template_exists(self, template_id: UUID) -> bool:
        """
        Check if a template exists.

        Args:
            template_id: UUID of the template to check

        Returns:
            True if template exists, False otherwise
        """
        file_path = self._get_template_file_path(template_id)
        return file_path.exists()

    def get_template_count(self) -> int:
        """
        Get the total number of templates.

        Returns:
            Number of templates in storage
        """
        return len(list(self.storage_path.glob("*.json")))


# Singleton instance for easy import
_default_store: Optional[TemplateStore] = None


def get_template_store(storage_path: str = "storage/templates") -> TemplateStore:
    """
    Get or create the default template store instance.

    Args:
        storage_path: Path to the templates storage directory

    Returns:
        TemplateStore instance
    """
    global _default_store
    if _default_store is None:
        _default_store = TemplateStore(storage_path)
    return _default_store
