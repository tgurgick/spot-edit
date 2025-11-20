"""
Pytest configuration and fixtures for backend tests
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    from src.main import app
    return TestClient(app)


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory for testing"""
    temp_dir = tempfile.mkdtemp()
    storage_path = Path(temp_dir)

    # Create subdirectories
    (storage_path / "templates").mkdir(exist_ok=True)
    (storage_path / "uploads").mkdir(exist_ok=True)

    yield storage_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_text_file(tmp_path):
    """Create a sample text file for testing"""
    file_path = tmp_path / "sample.txt"
    content = """Sample Document

This is a sample document for testing.
Client Name: John Doe
Contract Date: 2024-01-15
Amount: $5,000

Please sign below.
"""
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_template_data():
    """Sample template data for testing"""
    return {
        "id": "test-template-123",
        "name": "Test Contract Template",
        "created_at": "2024-01-15T10:00:00Z",
        "document_text": "Sample document with {client_name} and {date}",
        "fields": [
            {
                "id": "field_1",
                "name": "client_name",
                "type": "text",
                "positions": [[20, 30]],
                "current_value": "John Doe"
            },
            {
                "id": "field_2",
                "name": "date",
                "type": "date",
                "positions": [[40, 50]],
                "current_value": "2024-01-15"
            }
        ]
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM API response for testing"""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"fields": [{"name": "client_name", "type": "text", "value": "John Doe"}]}'
                }
            }
        ]
    }


# Marker for tests that require AI API calls
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "ai: mark test as requiring AI/LLM API calls"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
