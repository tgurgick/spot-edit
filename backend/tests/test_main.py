"""
Tests for main FastAPI application
"""

import pytest


@pytest.mark.unit
def test_health_check(test_client):
    """Test the health check endpoint"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "spot-edit-api"
    }


@pytest.mark.unit
def test_root_endpoint(test_client):
    """Test the root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Spot Edit API"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"


@pytest.mark.unit
def test_openapi_docs_available(test_client):
    """Test that OpenAPI documentation is available"""
    response = test_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.unit
def test_openapi_json_available(test_client):
    """Test that OpenAPI JSON schema is available"""
    response = test_client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Spot Edit API"
    assert schema["info"]["version"] == "0.1.0"
