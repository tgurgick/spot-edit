"""
Pytest configuration and shared fixtures for backend tests.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# Add backend source to Python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def test_data_dir():
    """
    Create a session-wide temporary directory for test data.

    This directory persists for the entire test session and is
    cleaned up after all tests complete.
    """
    temp_dir = tempfile.mkdtemp(prefix="spot_edit_tests_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def clean_storage(test_data_dir):
    """
    Provide a clean storage directory for each test.

    Creates a fresh directory for each test and cleans it up after.
    """
    storage_dir = test_data_dir / f"storage_{os.getpid()}"
    storage_dir.mkdir(exist_ok=True)

    yield storage_dir

    # Cleanup after test
    if storage_dir.exists():
        shutil.rmtree(storage_dir)


@pytest.fixture
def sample_pdf_bytes():
    """
    Provide sample PDF file bytes for testing.

    Note: This is a minimal PDF for testing purposes.
    """
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
190
%%EOF"""


@pytest.fixture
def sample_text_bytes():
    """Provide sample text file bytes for testing."""
    return b"This is a sample text document.\nWith multiple lines.\nFor testing purposes."


@pytest.fixture
def sample_document_text():
    """Provide sample document text for template testing."""
    return """Dear {{recipient_name}},

We are pleased to inform you that your application has been approved.

Your account number is: {{account_number}}
Start date: {{start_date}}
Email: {{email}}

Please contact us at {{phone}} if you have any questions.

Sincerely,
{{sender_name}}
{{sender_title}}"""


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "storage: mark test as storage layer test"
    )
