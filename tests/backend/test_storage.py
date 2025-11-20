"""
Unit tests for storage layer (template and document stores).
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from backend.src.models.schema import (
    Template,
    Field,
    FieldModel,  # Alias
    FieldType,
    Position,
    TemplateUpdateRequest,
)
from backend.src.storage.template_store import (
    TemplateStore,
    TemplateStoreError,
    TemplateNotFoundError,
)
from backend.src.storage.document_store import (
    DocumentStore,
    DocumentStoreError,
    DocumentNotFoundError,
)


class TestTemplateStore:
    """Tests for TemplateStore class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def template_store(self, temp_dir):
        """Create a TemplateStore instance with temporary storage."""
        return TemplateStore(storage_path=f"{temp_dir}/templates")

    @pytest.fixture
    def sample_fields(self):
        """Create sample fields for testing."""
        return [
            Field(
                name="recipient_name",
                type="text",
                positions=[Position(page=1, start=100, end=120)],
                current_value="John Doe"
            ),
            Field(
                name="date",
                type="date",
                positions=[Position(page=1, start=150, end=160)],
                current_value="2024-01-15"
            ),
        ]

    def test_save_template(self, template_store, sample_fields):
        """Test saving a new template."""
        template_id = template_store.save_template(
            document_text="Dear {{recipient_name}}, This is dated {{date}}.",
            fields=sample_fields,
            name="Welcome Letter",
            metadata={"file_type": "pdf"}
        )

        assert isinstance(template_id, str)
        assert template_store.template_exists(template_id)

    def test_load_template(self, template_store, sample_fields):
        """Test loading a saved template."""
        # Save template
        template_id = template_store.save_template(
            document_text="Dear {{recipient_name}}, This is dated {{date}}.",
            fields=sample_fields,
            name="Welcome Letter"
        )

        # Load template
        template = template_store.load_template(template_id)

        assert template.id == template_id
        assert template.name == "Welcome Letter"
        assert len(template.fields) == 2
        assert template.fields[0].name == "recipient_name"
        assert template.fields[0].current_value == "John Doe"

    def test_load_nonexistent_template(self, template_store):
        """Test loading a template that doesn't exist."""
        fake_id = str(uuid4())
        with pytest.raises(TemplateNotFoundError):
            template_store.load_template(fake_id)

    def test_list_templates(self, template_store, sample_fields):
        """Test listing all templates."""
        # Save multiple templates
        id1 = template_store.save_template(
            document_text="Template 1",
            fields=[],
            name="Template 1"
        )
        id2 = template_store.save_template(
            document_text="Template 2",
            fields=sample_fields,
            name="Template 2"
        )

        # List templates
        templates = template_store.list_templates()

        assert len(templates) == 2
        template_ids = {t.id for t in templates}
        assert id1 in template_ids
        assert id2 in template_ids

    def test_list_templates_sorted_by_date(self, template_store):
        """Test that templates are sorted by creation date (newest first)."""
        # Save templates
        id1 = template_store.save_template(
            document_text="First template",
            fields=[],
            name="First"
        )
        id2 = template_store.save_template(
            document_text="Second template",
            fields=[],
            name="Second"
        )

        templates = template_store.list_templates()

        # Second template should be first (newer)
        assert templates[0].id == id2
        assert templates[1].id == id1

    def test_update_template(self, template_store, sample_fields):
        """Test updating an existing template."""
        # Save template
        template_id = template_store.save_template(
            document_text="Original text",
            fields=sample_fields,
            name="Original Name"
        )

        # Update template
        updates = TemplateUpdateRequest(
            name="Updated Name",
            document_text="Updated text"
        )
        updated = template_store.update_template(template_id, updates)

        assert updated.name == "Updated Name"
        assert updated.document_text == "Updated text"
        assert len(updated.fields) == 2  # Fields unchanged

        # Verify persistence
        loaded = template_store.load_template(template_id)
        assert loaded.name == "Updated Name"

    def test_update_template_metadata(self, template_store):
        """Test updating template metadata."""
        template_id = template_store.save_template(
            document_text="Text",
            fields=[],
            name="Test",
            metadata={"key1": "value1"}
        )

        # Update metadata
        updates = TemplateUpdateRequest(
            metadata={"key2": "value2"}
        )
        updated = template_store.update_template(template_id, updates)

        # Both keys should be present (merge)
        assert updated.metadata["key1"] == "value1"
        assert updated.metadata["key2"] == "value2"

    def test_update_nonexistent_template(self, template_store):
        """Test updating a template that doesn't exist."""
        fake_id = str(uuid4())
        updates = TemplateUpdateRequest(name="New Name")

        with pytest.raises(TemplateNotFoundError):
            template_store.update_template(fake_id, updates)

    def test_delete_template(self, template_store, sample_fields):
        """Test deleting a template."""
        # Save template
        template_id = template_store.save_template(
            document_text="To be deleted",
            fields=sample_fields,
            name="Delete Me"
        )

        # Verify it exists
        assert template_store.template_exists(template_id)

        # Delete it
        result = template_store.delete_template(template_id)
        assert result is True

        # Verify it's gone
        assert not template_store.template_exists(template_id)

        # Trying to load should fail
        with pytest.raises(TemplateNotFoundError):
            template_store.load_template(template_id)

    def test_delete_nonexistent_template(self, template_store):
        """Test deleting a template that doesn't exist."""
        fake_id = str(uuid4())
        with pytest.raises(TemplateNotFoundError):
            template_store.delete_template(fake_id)

    def test_template_count(self, template_store):
        """Test getting template count."""
        assert template_store.get_template_count() == 0

        template_store.save_template(
            document_text="Template 1",
            fields=[],
            name="Template 1"
        )
        assert template_store.get_template_count() == 1

        template_store.save_template(
            document_text="Template 2",
            fields=[],
            name="Template 2"
        )
        assert template_store.get_template_count() == 2

    def test_template_persistence(self, temp_dir, sample_fields):
        """Test that templates persist across store instances."""
        # Create first store and save template
        store1 = TemplateStore(storage_path=f"{temp_dir}/templates")
        template_id = store1.save_template(
            document_text="Persistent template",
            fields=sample_fields,
            name="Persistence Test"
        )

        # Create second store with same path
        store2 = TemplateStore(storage_path=f"{temp_dir}/templates")
        template = store2.load_template(template_id)

        assert template.name == "Persistence Test"
        assert len(template.fields) == 2


class TestDocumentStore:
    """Tests for DocumentStore class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def document_store(self, temp_dir):
        """Create a DocumentStore instance with temporary storage."""
        return DocumentStore(
            storage_path=f"{temp_dir}/uploads",
            auto_cleanup_hours=1
        )

    def test_save_upload_bytes(self, document_store):
        """Test saving an upload from bytes."""
        file_data = b"This is a test document content."
        file_id = document_store.save_upload(
            file_data=file_data,
            filename="test.txt",
            content_type="text/plain"
        )

        assert isinstance(file_id, str)
        assert document_store.upload_exists(file_id)

    def test_save_upload_file_object(self, document_store, temp_dir):
        """Test saving an upload from a file-like object."""
        # Create a temporary file
        test_file = Path(temp_dir) / "test_upload.txt"
        test_content = b"File object content"
        test_file.write_bytes(test_content)

        # Upload from file object
        with open(test_file, 'rb') as f:
            file_id = document_store.save_upload(
                file_data=f,
                filename="uploaded.txt",
                content_type="text/plain"
            )

        assert document_store.upload_exists(file_id)

        # Verify content
        content = document_store.get_upload(file_id)
        assert content == test_content

    def test_get_upload(self, document_store):
        """Test retrieving an uploaded file."""
        original_data = b"Original file content"
        file_id = document_store.save_upload(
            file_data=original_data,
            filename="test.txt"
        )

        retrieved_data = document_store.get_upload(file_id)
        assert retrieved_data == original_data

    def test_get_nonexistent_upload(self, document_store):
        """Test retrieving a file that doesn't exist."""
        fake_id = str(uuid4())
        with pytest.raises(DocumentNotFoundError):
            document_store.get_upload(fake_id)

    def test_get_upload_metadata(self, document_store):
        """Test retrieving upload metadata."""
        file_data = b"Test content"
        file_id = document_store.save_upload(
            file_data=file_data,
            filename="document.pdf",
            content_type="application/pdf"
        )

        metadata = document_store.get_upload_metadata(file_id)

        assert metadata["filename"] == "document.pdf"
        assert metadata["content_type"] == "application/pdf"
        assert metadata["size"] == len(file_data)
        assert "uploaded_at" in metadata
        assert metadata["file_id"] == str(file_id)

    def test_delete_upload(self, document_store):
        """Test deleting an uploaded file."""
        file_data = b"To be deleted"
        file_id = document_store.save_upload(
            file_data=file_data,
            filename="delete_me.txt"
        )

        # Verify it exists
        assert document_store.upload_exists(file_id)

        # Delete it
        result = document_store.delete_upload(file_id)
        assert result is True

        # Verify it's gone
        assert not document_store.upload_exists(file_id)

        # Trying to get should fail
        with pytest.raises(DocumentNotFoundError):
            document_store.get_upload(file_id)

    def test_delete_nonexistent_upload(self, document_store):
        """Test deleting a file that doesn't exist."""
        fake_id = str(uuid4())
        with pytest.raises(DocumentNotFoundError):
            document_store.delete_upload(fake_id)

    def test_upload_count(self, document_store):
        """Test getting upload count."""
        assert document_store.get_upload_count() == 0

        document_store.save_upload(b"File 1", "file1.txt")
        assert document_store.get_upload_count() == 1

        document_store.save_upload(b"File 2", "file2.txt")
        assert document_store.get_upload_count() == 2

    def test_total_storage_size(self, document_store):
        """Test getting total storage size."""
        initial_size = document_store.get_total_storage_size()

        file1_data = b"File 1 content"
        file2_data = b"File 2 with more content"

        document_store.save_upload(file1_data, "file1.txt")
        document_store.save_upload(file2_data, "file2.txt")

        total_size = document_store.get_total_storage_size()
        expected_size = len(file1_data) + len(file2_data)

        assert total_size >= expected_size  # May include some overhead

    def test_cleanup_old_uploads(self, temp_dir):
        """Test cleanup of old uploads."""
        store = DocumentStore(
            storage_path=f"{temp_dir}/uploads",
            auto_cleanup_hours=1
        )

        # Save a file
        file_id = store.save_upload(b"Old file", "old.txt")

        # Manually modify metadata to make it "old"
        metadata_path = store._get_metadata_path(file_id)
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Set upload time to 2 hours ago
        old_time = datetime.utcnow() - timedelta(hours=2)
        metadata['uploaded_at'] = old_time.isoformat()

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

        # Run cleanup (should delete files older than 1 hour)
        deleted_count = store.cleanup_old_uploads()

        assert deleted_count == 1
        assert not store.upload_exists(file_id)

    def test_cleanup_recent_uploads_not_deleted(self, document_store):
        """Test that recent uploads are not deleted during cleanup."""
        file_id = document_store.save_upload(b"Recent file", "recent.txt")

        # Run cleanup (file is recent, should not be deleted)
        deleted_count = document_store.cleanup_old_uploads()

        assert deleted_count == 0
        assert document_store.upload_exists(file_id)

    def test_upload_persistence(self, temp_dir):
        """Test that uploads persist across store instances."""
        # Create first store and save upload
        store1 = DocumentStore(storage_path=f"{temp_dir}/uploads")
        original_data = b"Persistent upload"
        file_id = store1.save_upload(original_data, "persistent.txt")

        # Create second store with same path
        store2 = DocumentStore(storage_path=f"{temp_dir}/uploads")
        retrieved_data = store2.get_upload(file_id)

        assert retrieved_data == original_data


class TestPositionValidation:
    """Tests for Position model validation."""

    def test_valid_position(self):
        """Test creating a valid position."""
        pos = Position(page=1, start=0, end=10)
        assert pos.page == 1
        assert pos.start == 0
        assert pos.end == 10

    def test_invalid_end_position(self):
        """Test that end must be greater than start."""
        with pytest.raises(ValueError, match="end position must be greater than start"):
            Position(page=1, start=10, end=10)

        with pytest.raises(ValueError, match="end position must be greater than start"):
            Position(page=1, start=10, end=5)

    def test_position_page_validation(self):
        """Test that page number must be >= 1."""
        with pytest.raises(ValueError):
            Position(page=0, start=0, end=10)

        with pytest.raises(ValueError):
            Position(page=-1, start=0, end=10)


class TestFieldModel:
    """Tests for FieldModel (Field)."""

    def test_create_field(self):
        """Test creating a field model."""
        field = Field(
            name="test_field",
            type="text",
            positions=[Position(page=1, start=0, end=10)],
            current_value="Test Value"
        )

        assert field.name == "test_field"
        assert field.type == "text"
        assert len(field.positions) == 1
        assert field.current_value == "Test Value"

    def test_field_with_multiple_positions(self):
        """Test field with multiple positions."""
        field = Field(
            name="multi_pos",
            type="text",
            positions=[
                Position(page=1, start=0, end=10),
                Position(page=2, start=50, end=60),
            ]
        )

        assert len(field.positions) == 2

    def test_field_types(self):
        """Test all field types."""
        field_types = ["text", "number", "date", "email", "phone", "address", "custom"]

        for ft in field_types:
            field = Field(
                name="test",
                type=ft,
                positions=[Position(page=1, start=0, end=10)]
            )
            assert field.type == ft
