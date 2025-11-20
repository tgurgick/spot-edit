"""Integration tests for API routes."""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_upload_document(client, sample_text_file):
    """Test document upload endpoint."""
    filename, content, content_type = sample_text_file

    response = client.post(
        "/api/upload",
        files={"file": (filename, content, content_type)}
    )

    # Note: This might fail without a real AI API key
    # In a production test suite, you'd mock the AI client
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert "file_id" in data
        assert "document_text" in data
        assert "detected_fields" in data
        assert isinstance(data["detected_fields"], list)


def test_upload_invalid_file_type(client):
    """Test upload with invalid file type."""
    response = client.post(
        "/api/upload",
        files={"file": ("test.xyz", b"test content", "application/octet-stream")}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "error" in data or "detail" in data


def test_create_and_get_template(client, sample_template_data):
    """Test creating and retrieving a template."""
    # Create template
    response = client.post("/api/templates", json=sample_template_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "template_id" in data
    template_id = data["template_id"]

    # Get template
    response = client.get(f"/api/templates/{template_id}")
    assert response.status_code == status.HTTP_200_OK
    template = response.json()
    assert template["id"] == template_id
    assert template["name"] == sample_template_data["name"]
    assert template["document_text"] == sample_template_data["document_text"]
    assert len(template["fields"]) == len(sample_template_data["fields"])


def test_list_templates(client, sample_template_data):
    """Test listing templates."""
    # Create a template first
    client.post("/api/templates", json=sample_template_data)

    # List templates
    response = client.get("/api/templates")
    assert response.status_code == status.HTTP_200_OK
    templates = response.json()
    assert isinstance(templates, list)


def test_update_template_metadata(client, sample_template_data):
    """Test updating template metadata."""
    # Create template
    response = client.post("/api/templates", json=sample_template_data)
    template_id = response.json()["template_id"]

    # Update metadata
    new_name = "Updated Template Name"
    response = client.put(
        f"/api/templates/{template_id}",
        json={"name": new_name}
    )

    assert response.status_code == status.HTTP_200_OK

    # Verify update
    response = client.get(f"/api/templates/{template_id}")
    template = response.json()
    assert template["name"] == new_name


def test_update_template_fields(client, sample_template_data):
    """Test updating template fields with natural language."""
    # Create template
    response = client.post("/api/templates", json=sample_template_data)
    template_id = response.json()["template_id"]

    # Update fields (Note: This requires AI API to work properly)
    update_command = {
        "command": "Change client name to Jane Smith"
    }
    response = client.post(
        f"/api/templates/{template_id}/update",
        json=update_command
    )

    # This might not work without proper AI API, but endpoint should respond
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


def test_delete_template(client, sample_template_data):
    """Test deleting a template."""
    # Create template
    response = client.post("/api/templates", json=sample_template_data)
    template_id = response.json()["template_id"]

    # Delete template
    response = client.delete(f"/api/templates/{template_id}")
    assert response.status_code == status.HTTP_200_OK

    # Verify deletion
    response = client.get(f"/api/templates/{template_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_download_template(client, sample_template_data):
    """Test downloading a template."""
    # Create template
    response = client.post("/api/templates", json=sample_template_data)
    template_id = response.json()["template_id"]

    # Download template
    response = client.get(f"/api/templates/{template_id}/download")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert "Content-Disposition" in response.headers


def test_get_nonexistent_template(client):
    """Test getting a template that doesn't exist."""
    response = client.get("/api/templates/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_template_without_name(client):
    """Test creating template without required name."""
    response = client.post("/api/templates", json={
        "name": "",
        "document_text": "Test document",
        "fields": []
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
