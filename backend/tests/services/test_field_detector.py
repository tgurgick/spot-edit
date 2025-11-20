"""
Unit tests for field_detector.py

Tests the FieldDetector service with mock LLM responses.
"""

import pytest
from unittest.mock import Mock, MagicMock
from backend.src.services.field_detector import (
    FieldDetector,
    FieldDetectionError,
)
from backend.src.models.schema import Field


class TestFieldDetector:
    """Test cases for FieldDetector class."""

    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        return MagicMock()

    @pytest.fixture
    def detector(self, mock_ai_client):
        """Create FieldDetector with mock AI client."""
        return FieldDetector(mock_ai_client)

    def test_init(self, mock_ai_client):
        """Test FieldDetector initialization."""
        detector = FieldDetector(mock_ai_client)
        assert detector.ai_client == mock_ai_client

    def test_detect_fields_empty_text(self, detector):
        """Test detecting fields in empty text."""
        result = detector.detect_fields("")
        assert result == []

        result = detector.detect_fields("   ")
        assert result == []

    def test_detect_fields_success(self, detector, mock_ai_client):
        """Test successful field detection."""
        document_text = "Contract between John Doe and Acme Corp. Date: 2024-01-15."

        # Mock LLM response
        mock_response = """
```json
[
  {
    "name": "client_name",
    "type": "text",
    "positions": [[18, 26]],
    "current_value": "John Doe"
  },
  {
    "name": "company_name",
    "type": "text",
    "positions": [[31, 40]],
    "current_value": "Acme Corp"
  },
  {
    "name": "contract_date",
    "type": "date",
    "positions": [[48, 58]],
    "current_value": "2024-01-15"
  }
]
```
"""
        mock_ai_client.call_llm.return_value = mock_response

        # Detect fields
        fields = detector.detect_fields(document_text)

        # Verify
        assert len(fields) == 3
        assert fields[0].name == "client_name"
        assert fields[0].type == "text"
        assert fields[0].current_value == "John Doe"
        assert fields[1].name == "company_name"
        assert fields[2].name == "contract_date"
        assert fields[2].type == "date"

    def test_detect_fields_with_multiple_positions(self, detector, mock_ai_client):
        """Test detecting field that appears multiple times."""
        document_text = "Client: John Doe. Contact: John Doe at email."

        mock_response = """
[
  {
    "name": "client_name",
    "type": "text",
    "positions": [[8, 16], [27, 35]],
    "current_value": "John Doe"
  }
]
"""
        mock_ai_client.call_llm.return_value = mock_response

        fields = detector.detect_fields(document_text)

        assert len(fields) == 1
        assert fields[0].name == "client_name"
        assert len(fields[0].positions) == 2
        assert fields[0].positions == [(8, 16), (27, 35)]

    def test_detect_fields_no_fields_found(self, detector, mock_ai_client):
        """Test when LLM finds no editable fields."""
        mock_response = "[]"
        mock_ai_client.call_llm.return_value = mock_response

        fields = detector.detect_fields("Some document text")

        assert fields == []

    def test_detect_fields_invalid_json(self, detector, mock_ai_client):
        """Test handling of invalid JSON response."""
        mock_response = "This is not valid JSON"
        mock_ai_client.call_llm.return_value = mock_response

        with pytest.raises(FieldDetectionError):
            detector.detect_fields("Some text")

    def test_detect_fields_skips_invalid_entries(self, detector, mock_ai_client):
        """Test that invalid field entries are skipped."""
        mock_response = """
[
  {
    "name": "valid_field",
    "type": "text",
    "positions": [[0, 5]],
    "current_value": "Test"
  },
  {
    "name": "missing_type"
  },
  {
    "name": "invalid_positions",
    "type": "text",
    "positions": [[10, 5]],
    "current_value": "Bad"
  }
]
"""
        mock_ai_client.call_llm.return_value = mock_response

        fields = detector.detect_fields("Test document")

        # Only valid field should be returned
        assert len(fields) == 1
        assert fields[0].name == "valid_field"

    def test_detect_fields_validates_position_bounds(self, detector, mock_ai_client):
        """Test that positions exceeding document length are rejected."""
        document_text = "Short text"  # Length: 10

        mock_response = """
[
  {
    "name": "out_of_bounds",
    "type": "text",
    "positions": [[0, 100]],
    "current_value": "Test"
  }
]
"""
        mock_ai_client.call_llm.return_value = mock_response

        # Should skip the field with out-of-bounds positions
        fields = detector.detect_fields(document_text)
        assert len(fields) == 0

    def test_detect_fields_calls_llm_correctly(self, detector, mock_ai_client):
        """Test that LLM is called with correct parameters."""
        mock_ai_client.call_llm.return_value = "[]"

        detector.detect_fields("Test document")

        mock_ai_client.call_llm.assert_called_once()
        call_kwargs = mock_ai_client.call_llm.call_args[1]

        assert 'prompt' in call_kwargs
        assert 'system_message' in call_kwargs
        assert call_kwargs['temperature'] == 0.3
        assert "Test document" in call_kwargs['prompt']

    def test_detect_fields_with_hints(self, detector, mock_ai_client):
        """Test detecting fields with hints."""
        mock_response = """
[
  {
    "name": "client_name",
    "type": "text",
    "positions": [[0, 8]],
    "current_value": "John Doe"
  }
]
"""
        mock_ai_client.call_llm.return_value = mock_response

        fields = detector.detect_fields_with_hints(
            "John Doe, 2024-01-15",
            field_hints=["client_name", "date"]
        )

        assert len(fields) == 1
        mock_ai_client.call_llm.assert_called_once()

        # Verify hints are included in system message
        call_kwargs = mock_ai_client.call_llm.call_args[1]
        assert "client_name" in call_kwargs['system_message']
        assert "date" in call_kwargs['system_message']

    def test_extract_json_from_markdown(self, detector):
        """Test extracting JSON from markdown code blocks."""
        text_with_markdown = """
Here is the result:
```json
[{"name": "test"}]
```
"""
        result = detector._extract_json(text_with_markdown)
        assert result == '[{"name": "test"}]'

    def test_extract_json_without_markdown(self, detector):
        """Test extracting JSON without markdown."""
        json_text = '[{"name": "test"}]'
        result = detector._extract_json(json_text)
        assert result == json_text

    def test_build_detection_prompt(self, detector):
        """Test building detection prompt."""
        document_text = "Test document content"

        prompt = detector._build_detection_prompt(document_text)

        assert "Test document content" in prompt
        assert "JSON array" in prompt

    def test_truncates_long_documents(self, detector, mock_ai_client):
        """Test that very long documents are truncated."""
        # Create a document longer than 8000 characters
        long_text = "A" * 10000

        mock_ai_client.call_llm.return_value = "[]"

        detector.detect_fields(long_text)

        call_kwargs = mock_ai_client.call_llm.call_args[1]
        assert len(call_kwargs['prompt']) < len(long_text)
        assert "[Document truncated...]" in call_kwargs['prompt']

    def test_field_validation_negative_positions(self, detector):
        """Test that negative positions are rejected."""
        field_data = {
            "name": "test",
            "type": "text",
            "positions": [[-1, 5]],
            "current_value": "test"
        }

        # Should skip due to negative position
        result = detector._create_field_from_dict(field_data, "Test document")
        assert result is None

    def test_field_validation_invalid_type(self, detector):
        """Test that invalid field types are rejected."""
        field_data = {
            "name": "test",
            "type": "invalid_type",
            "positions": [[0, 5]],
            "current_value": "test"
        }

        with pytest.raises(ValueError):
            detector._create_field_from_dict(field_data, "Test document")

    def test_field_with_no_current_value(self, detector, mock_ai_client):
        """Test field without current_value (placeholder)."""
        mock_response = """
[
  {
    "name": "placeholder",
    "type": "text",
    "positions": [[0, 10]]
  }
]
"""
        mock_ai_client.call_llm.return_value = mock_response

        fields = detector.detect_fields("____placeholder____")

        assert len(fields) == 1
        assert fields[0].current_value is None
