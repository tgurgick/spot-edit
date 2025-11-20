"""
Document storage implementation for uploaded files.

This module provides storage operations for uploaded documents (PDFs, DOCX, etc.)
before they are processed into templates. Includes automatic cleanup of old files.
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO, Union
from uuid import UUID, uuid4
import json


class DocumentStoreError(Exception):
    """Base exception for document storage errors."""
    pass


class DocumentNotFoundError(DocumentStoreError):
    """Raised when a document is not found."""
    pass


class DocumentStore:
    """
    Document upload storage manager using file system.

    Stores uploaded documents temporarily before processing into templates.
    Each upload is stored with metadata for tracking and cleanup.
    """

    def __init__(
        self,
        storage_path: str = "storage/uploads",
        auto_cleanup_hours: int = 24
    ):
        """
        Initialize the document store.

        Args:
            storage_path: Path to the uploads storage directory
            auto_cleanup_hours: Automatically delete files older than this (hours)
        """
        self.storage_path = Path(storage_path)
        self.auto_cleanup_hours = auto_cleanup_hours
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Create storage directory if it doesn't exist."""
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_document_path(self, file_id: UUID) -> Path:
        """Get the file path for a document."""
        return self.storage_path / str(file_id)

    def _get_metadata_path(self, file_id: UUID) -> Path:
        """Get the metadata file path for a document."""
        return self.storage_path / f"{file_id}.meta.json"

    def _save_metadata(
        self,
        file_id: UUID,
        filename: str,
        content_type: str,
        size: int
    ) -> None:
        """
        Save metadata for an uploaded document.

        Args:
            file_id: UUID of the uploaded file
            filename: Original filename
            content_type: MIME type of the file
            size: File size in bytes
        """
        metadata = {
            "file_id": str(file_id),
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "uploaded_at": datetime.utcnow().isoformat()
        }

        metadata_path = self._get_metadata_path(file_id)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def _load_metadata(self, file_id: UUID) -> Dict[str, Any]:
        """
        Load metadata for a document.

        Args:
            file_id: UUID of the file

        Returns:
            Metadata dictionary

        Raises:
            DocumentNotFoundError: If metadata doesn't exist
        """
        metadata_path = self._get_metadata_path(file_id)

        if not metadata_path.exists():
            raise DocumentNotFoundError(
                f"Metadata for document {file_id} not found"
            )

        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_upload(
        self,
        file_data: Union[bytes, BinaryIO],
        filename: str,
        content_type: str = "application/octet-stream"
    ) -> UUID:
        """
        Save an uploaded file to storage.

        Args:
            file_data: File content as bytes or file-like object
            filename: Original filename
            content_type: MIME type of the file

        Returns:
            UUID of the saved file

        Raises:
            DocumentStoreError: If saving fails
        """
        try:
            file_id = uuid4()
            file_path = self._get_document_path(file_id)

            # Save file content
            if isinstance(file_data, bytes):
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                size = len(file_data)
            else:
                # Handle file-like object
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(file_data, f)
                size = file_path.stat().st_size

            # Save metadata
            self._save_metadata(file_id, filename, content_type, size)

            return file_id

        except Exception as e:
            # Cleanup on failure
            if 'file_id' in locals():
                self._cleanup_file(file_id)
            raise DocumentStoreError(
                f"Failed to save upload: {str(e)}"
            ) from e

    def get_upload(self, file_id: UUID) -> bytes:
        """
        Retrieve an uploaded file's content.

        Args:
            file_id: UUID of the file to retrieve

        Returns:
            File content as bytes

        Raises:
            DocumentNotFoundError: If file doesn't exist
            DocumentStoreError: If retrieval fails
        """
        file_path = self._get_document_path(file_id)

        if not file_path.exists():
            raise DocumentNotFoundError(
                f"Document with ID {file_id} not found"
            )

        try:
            with open(file_path, 'rb') as f:
                return f.read()

        except Exception as e:
            raise DocumentStoreError(
                f"Failed to read document {file_id}: {str(e)}"
            ) from e

    def get_upload_metadata(self, file_id: UUID) -> Dict[str, Any]:
        """
        Get metadata for an uploaded file.

        Args:
            file_id: UUID of the file

        Returns:
            Metadata dictionary with filename, content_type, size, uploaded_at

        Raises:
            DocumentNotFoundError: If metadata doesn't exist
        """
        return self._load_metadata(file_id)

    def delete_upload(self, file_id: UUID) -> bool:
        """
        Delete an uploaded file and its metadata.

        Args:
            file_id: UUID of the file to delete

        Returns:
            True if deletion was successful

        Raises:
            DocumentNotFoundError: If file doesn't exist
            DocumentStoreError: If deletion fails
        """
        file_path = self._get_document_path(file_id)
        metadata_path = self._get_metadata_path(file_id)

        if not file_path.exists():
            raise DocumentNotFoundError(
                f"Document with ID {file_id} not found"
            )

        try:
            # Delete file
            if file_path.exists():
                file_path.unlink()

            # Delete metadata
            if metadata_path.exists():
                metadata_path.unlink()

            return True

        except Exception as e:
            raise DocumentStoreError(
                f"Failed to delete document {file_id}: {str(e)}"
            ) from e

    def _cleanup_file(self, file_id: UUID) -> None:
        """
        Cleanup a file and its metadata (no error if doesn't exist).

        Args:
            file_id: UUID of the file to cleanup
        """
        try:
            file_path = self._get_document_path(file_id)
            metadata_path = self._get_metadata_path(file_id)

            if file_path.exists():
                file_path.unlink()
            if metadata_path.exists():
                metadata_path.unlink()

        except Exception:
            # Silently ignore cleanup errors
            pass

    def upload_exists(self, file_id: UUID) -> bool:
        """
        Check if an uploaded file exists.

        Args:
            file_id: UUID of the file to check

        Returns:
            True if file exists, False otherwise
        """
        file_path = self._get_document_path(file_id)
        return file_path.exists()

    def cleanup_old_uploads(self, older_than_hours: Optional[int] = None) -> int:
        """
        Delete uploaded files older than specified hours.

        Args:
            older_than_hours: Delete files older than this (uses auto_cleanup_hours if None)

        Returns:
            Number of files deleted
        """
        hours = older_than_hours or self.auto_cleanup_hours
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        deleted_count = 0

        try:
            for metadata_path in self.storage_path.glob("*.meta.json"):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    uploaded_at = datetime.fromisoformat(metadata['uploaded_at'])

                    if uploaded_at < cutoff_time:
                        file_id = UUID(metadata['file_id'])
                        self._cleanup_file(file_id)
                        deleted_count += 1

                except Exception as e:
                    # Log but continue with other files
                    print(f"Warning: Failed to cleanup {metadata_path}: {e}")
                    continue

            return deleted_count

        except Exception as e:
            raise DocumentStoreError(
                f"Failed to cleanup old uploads: {str(e)}"
            ) from e

    def get_upload_count(self) -> int:
        """
        Get the total number of uploaded files.

        Returns:
            Number of uploads in storage
        """
        return len(list(self.storage_path.glob("*.meta.json")))

    def get_total_storage_size(self) -> int:
        """
        Get total storage size used by uploads.

        Returns:
            Total size in bytes
        """
        total_size = 0
        for file_path in self.storage_path.iterdir():
            if file_path.is_file() and not file_path.name.endswith('.meta.json'):
                total_size += file_path.stat().st_size
        return total_size


# Singleton instance for easy import
_default_store: Optional[DocumentStore] = None


def get_document_store(
    storage_path: str = "storage/uploads",
    auto_cleanup_hours: int = 24
) -> DocumentStore:
    """
    Get or create the default document store instance.

    Args:
        storage_path: Path to the uploads storage directory
        auto_cleanup_hours: Automatically delete files older than this (hours)

    Returns:
        DocumentStore instance
    """
    global _default_store
    if _default_store is None:
        _default_store = DocumentStore(storage_path, auto_cleanup_hours)
    return _default_store
