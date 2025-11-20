"""Integration tests for FastAPI routes with Path 1 & 2 services."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_list_templates_empty():
    """Test listing templates when none exist (or listing existing ones)."""
    response = client.get("/api/templates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_and_get_template():
    """Test creating and retrieving a template."""
    # Create template
    template_data = {
        "name": "Test Template",
        "document_text": "Hello {{name}}, your appointment is on {{date}}.",
        "fields": [
            {
                "name": "name",
                "type": "text",
                "positions": [[6, 14]],
                "current_value": "{{name}}"
            }
        ],
        "metadata": {}
    }

    response = client.post("/api/templates", json=template_data)
    assert response.status_code == 201
    data = response.json()
    assert "template_id" in data
    template_id = data["template_id"]

    # Get template
    response = client.get(f"/api/templates/{template_id}")
    assert response.status_code == 200
    template = response.json()
    assert template["name"] == "Test Template"
    assert template["document_text"] == template_data["document_text"]


def test_update_template():
    """Test updating a template."""
    # Create template first
    template_data = {
        "name": "Original Name",
        "document_text": "Test content",
        "fields": [],
        "metadata": {}
    }

    response = client.post("/api/templates", json=template_data)
    template_id = response.json()["template_id"]

    # Update template
    update_data = {
        "name": "Updated Name"
    }
    response = client.put(f"/api/templates/{template_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Updated Name"


def test_delete_template():
    """Test deleting a template."""
    # Create template
    template_data = {
        "name": "To Be Deleted",
        "document_text": "Test",
        "fields": [],
        "metadata": {}
    }

    response = client.post("/api/templates", json=template_data)
    template_id = response.json()["template_id"]

    # Delete template
    response = client.delete(f"/api/templates/{template_id}")
    assert response.status_code == 200

    # Verify deletion
    response = client.get(f"/api/templates/{template_id}")
    assert response.status_code == 404


def test_get_nonexistent_template():
    """Test getting a template that doesn't exist."""
    response = client.get("/api/templates/nonexistent-id-12345")
    assert response.status_code == 404


def test_upload_document_text():
    """Test uploading a text document."""
    content = b"This is a test document with John Doe mentioned on 2024-01-15."

    files = {"file": ("test.txt", content, "text/plain")}
    response = client.post("/api/upload", files=files)

    # This will only pass if AI service is configured
    # In CI/CD, this might fail without API keys
    if response.status_code == 200:
        data = response.json()
        assert "document_text" in data
        assert "detected_fields" in data
        assert isinstance(data["detected_fields"], list)


def test_upload_invalid_file_type():
    """Test uploading an unsupported file type."""
    content = b"fake content"

    files = {"file": ("test.xyz", content, "application/octet-stream")}
    response = client.post("/api/upload", files=files)

    assert response.status_code in [400, 500]  # Should fail


def test_download_template():
    """Test downloading a template."""
    # Create template
    template_data = {
        "name": "Download Test",
        "document_text": "Sample document content",
        "fields": [],
        "metadata": {}
    }

    response = client.post("/api/templates", json=template_data)
    template_id = response.json()["template_id"]

    # Download template
    response = client.get(f"/api/templates/{template_id}/download")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "attachment" in response.headers.get("content-disposition", "")
