"""Pytest configuration and fixtures."""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add backend/src to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing."""
    content = b"""CONTRACT AGREEMENT

This agreement is made between John Doe (the Client) and Acme Corp (the Service Provider).

Contract Date: January 15, 2024
Contract Amount: $5,000
Project Duration: 30 days

The Client agrees to pay the Service Provider the amount specified above for services rendered.

Signed: John Doe
Date: January 15, 2024
"""
    return ("sample.txt", content, "text/plain")


@pytest.fixture
def sample_template_data():
    """Sample template data for testing."""
    return {
        "name": "Test Contract Template",
        "document_text": "This is a test contract for John Doe dated January 15, 2024.",
        "fields": [
            {
                "id": "field_1",
                "name": "client_name",
                "type": "text",
                "positions": [[30, 38]],
                "current_value": "John Doe"
            },
            {
                "id": "field_2",
                "name": "contract_date",
                "type": "date",
                "positions": [[45, 61]],
                "current_value": "January 15, 2024"
            }
        ]
    }


@pytest.fixture(autouse=True)
def setup_env():
    """Set up environment variables for testing."""
    # Mock AI API key if not present
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = "test-key-mock"

    yield

    # Cleanup after tests
    # Note: In a real test environment, you'd want to clean up test data
