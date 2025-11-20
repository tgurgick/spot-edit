"""
Unit tests for field_updater.py

Tests the FieldUpdater service with mock LLM responses.
"""

import pytest
from unittest.mock import MagicMock
from backend.src.services.field_updater import (
    FieldUpdater,
    FieldUpdateError,
)
from backend.src.models.schema import Field, FieldUpdate, ParsedUpdate


class TestFieldUpdater:
    """Test cases for FieldUpdater class."""

    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        return MagicMock()

    @pytest.fixture
    def updater(self, mock_ai_client):
        """Create FieldUpdater with mock AI client."""
        return FieldUpdater(mock_ai_client)

    @pytest.fixture
    def sample_fields(self):
        """Create sample fields for testing."""
        return [
            Field(
                name="client_name",
                type="text",
                positions=[(18, 26), (100, 108)],
                current_value="John Doe"
            ),
            Field(
                name="contract_date",
                type="date",
                positions=[(50, 60)],
                current_value="2024-01-15"
            ),
            Field(
                name="amount",
                type="number",
                positions=[(80, 85)],
                current_value="$5000"
            ),
        ]

    def test_init(self, mock_ai_client):
        """Test FieldUpdater initialization."""
        updater = FieldUpdater(mock_ai_client)
        assert updater.ai_client == mock_ai_client

    def test_parse_update_command_empty(self, updater):
        """Test parsing empty command."""
        result = updater.parse_update_command("", [])

        assert isinstance(result, ParsedUpdate)
        assert result.updates == []

    def test_parse_update_command_success(self, updater, mock_ai_client, sample_fields):
        """Test successful command parsing."""
        mock_response = """
{
  "updates": [
    {
      "field_name": "client_name",
      "new_value": "Jane Smith",
      "confidence": 0.95
    }
  ],
  "unrecognized_parts": []
}
"""
        mock_ai_client.call_llm.return_value = mock_response

        result = updater.parse_update_command(
            "Change the client name to Jane Smith",
            sample_fields
        )

        assert len(result.updates) == 1
        assert result.updates[0].field_name == "client_name"
        assert result.updates[0].new_value == "Jane Smith"
        assert result.updates[0].confidence == 0.95
        assert result.unrecognized_parts == []

    def test_parse_update_command_multiple_updates(self, updater, mock_ai_client, sample_fields):
        """Test parsing command with multiple updates."""
        mock_response = """
{
  "updates": [
    {
      "field_name": "client_name",
      "new_value": "Jane Smith",
      "confidence": 0.95
    },
    {
      "field_name": "contract_date",
      "new_value": "2024-02-20",
      "confidence": 0.90
    }
  ],
  "unrecognized_parts": []
}
"""
        mock_ai_client.call_llm.return_value = mock_response

        result = updater.parse_update_command(
            "Set client to Jane Smith and date to February 20, 2024",
            sample_fields
        )

        assert len(result.updates) == 2
        assert result.updates[0].field_name == "client_name"
        assert result.updates[1].field_name == "contract_date"

    def test_parse_update_command_with_unrecognized(self, updater, mock_ai_client, sample_fields):
        """Test parsing with unrecognized parts."""
        mock_response = """
{
  "updates": [
    {
      "field_name": "client_name",
      "new_value": "Jane Smith",
      "confidence": 0.8
    }
  ],
  "unrecognized_parts": ["something unclear"]
}
"""
        mock_ai_client.call_llm.return_value = mock_response

        result = updater.parse_update_command(
            "Change client to Jane Smith and something unclear",
            sample_fields
        )

        assert len(result.updates) == 1
        assert len(result.unrecognized_parts) == 1
        assert result.unrecognized_parts[0] == "something unclear"

    def test_parse_update_command_calls_llm_correctly(self, updater, mock_ai_client, sample_fields):
        """Test that LLM is called with correct parameters."""
        mock_ai_client.call_llm.return_value = '{"updates": [], "unrecognized_parts": []}'

        updater.parse_update_command("Test command", sample_fields)

        mock_ai_client.call_llm.assert_called_once()
        call_kwargs = mock_ai_client.call_llm.call_args[1]

        assert 'prompt' in call_kwargs
        assert 'system_message' in call_kwargs
        assert call_kwargs['temperature'] == 0.2
        assert "Test command" in call_kwargs['prompt']

        # Check that field context is included
        assert "client_name" in call_kwargs['prompt']
        assert "contract_date" in call_kwargs['prompt']

    def test_apply_updates_single_field(self, updater, sample_fields):
        """Test applying update to single field."""
        document = "The contract with John Doe was signed on 2024-01-15 for $5000. Contact John Doe for details."

        updates = [
            FieldUpdate(
                field_name="client_name",
                new_value="Jane Smith"
            )
        ]

        result = updater.apply_updates(document, updates, sample_fields)

        # Both occurrences should be updated
        assert "Jane Smith" in result
        assert "John Doe" not in result

    def test_apply_updates_multiple_fields(self, updater, sample_fields):
        """Test applying updates to multiple fields."""
        document = "The contract with John Doe was signed on 2024-01-15 for $5000. Contact John Doe for details."

        updates = [
            FieldUpdate(field_name="client_name", new_value="Jane Smith"),
            FieldUpdate(field_name="contract_date", new_value="2024-02-20"),
        ]

        result = updater.apply_updates(document, updates, sample_fields)

        assert "Jane Smith" in result
        assert "2024-02-20" in result

    def test_apply_updates_empty_list(self, updater, sample_fields):
        """Test applying empty update list."""
        document = "Original text"

        result = updater.apply_updates(document, [], sample_fields)

        assert result == document

    def test_apply_updates_field_not_found(self, updater, sample_fields):
        """Test applying update to non-existent field."""
        document = "Test document"

        updates = [
            FieldUpdate(field_name="nonexistent_field", new_value="Value")
        ]

        with pytest.raises(FieldUpdateError) as exc_info:
            updater.apply_updates(document, updates, sample_fields)

        assert "field not found" in str(exc_info.value).lower()

    def test_fuzzy_match_field_exact(self, updater, sample_fields):
        """Test fuzzy matching with exact match."""
        result = updater._fuzzy_match_field("client_name", sample_fields)

        assert result is not None
        assert result.name == "client_name"

    def test_fuzzy_match_field_case_insensitive(self, updater, sample_fields):
        """Test fuzzy matching is case-insensitive."""
        result = updater._fuzzy_match_field("CLIENT_NAME", sample_fields)

        assert result is not None
        assert result.name == "client_name"

    def test_fuzzy_match_field_partial(self, updater, sample_fields):
        """Test fuzzy matching with partial match."""
        result = updater._fuzzy_match_field("client", sample_fields)

        assert result is not None
        assert result.name == "client_name"

    def test_fuzzy_match_field_not_found(self, updater, sample_fields):
        """Test fuzzy matching when no match found."""
        result = updater._fuzzy_match_field("completely_different", sample_fields)

        assert result is None

    def test_parse_and_apply(self, updater, mock_ai_client, sample_fields):
        """Test combined parse and apply operation."""
        mock_response = """
{
  "updates": [
    {
      "field_name": "client_name",
      "new_value": "Jane Smith",
      "confidence": 0.95
    }
  ],
  "unrecognized_parts": []
}
"""
        mock_ai_client.call_llm.return_value = mock_response

        document = "Contract with John Doe signed on 2024-01-15 for $5000. Contact John Doe."

        updated_doc, parsed = updater.parse_and_apply(
            "Change client to Jane Smith",
            document,
            sample_fields
        )

        assert "Jane Smith" in updated_doc
        assert "John Doe" not in updated_doc
        assert len(parsed.updates) == 1
        assert parsed.updates[0].field_name == "client_name"

    def test_extract_json_from_markdown(self, updater):
        """Test extracting JSON object from markdown."""
        text = """
```json
{"updates": [], "unrecognized_parts": []}
```
"""
        result = updater._extract_json(text)
        assert "updates" in result

    def test_extract_json_plain(self, updater):
        """Test extracting plain JSON."""
        text = '{"updates": [], "unrecognized_parts": []}'
        result = updater._extract_json(text)
        assert result == text

    def test_build_parse_prompt(self, updater, sample_fields):
        """Test building parse prompt."""
        prompt = updater._build_parse_prompt(
            "Change client name",
            sample_fields
        )

        assert "client_name" in prompt
        assert "contract_date" in prompt
        assert "amount" in prompt
        assert "Change client name" in prompt

    def test_build_parse_prompt_no_fields(self, updater):
        """Test building prompt with no fields."""
        prompt = updater._build_parse_prompt("Test command", [])

        assert "No fields available" in prompt

    def test_apply_updates_multiple_occurrences(self, updater):
        """Test updating field with multiple occurrences."""
        fields = [
            Field(
                name="name",
                type="text",
                positions=[(0, 4), (10, 14), (20, 24)],
                current_value="John"
            )
        ]

        document = "John works at John's company. John is the CEO."

        updates = [FieldUpdate(field_name="name", new_value="Jane")]

        result = updater.apply_updates(document, updates, fields)

        # All occurrences should be replaced
        assert result.count("Jane") == 3
        assert "John" not in result

    def test_parse_invalid_json_response(self, updater, mock_ai_client, sample_fields):
        """Test handling invalid JSON response."""
        mock_ai_client.call_llm.return_value = "This is not JSON"

        with pytest.raises(FieldUpdateError):
            updater.parse_update_command("Test", sample_fields)

    def test_parse_response_not_dict(self, updater, mock_ai_client, sample_fields):
        """Test handling response that's not a dict."""
        mock_ai_client.call_llm.return_value = "[]"

        with pytest.raises(FieldUpdateError):
            updater.parse_update_command("Test", sample_fields)

    def test_parse_skips_invalid_updates(self, updater, mock_ai_client, sample_fields):
        """Test that invalid updates are skipped."""
        mock_response = """
{
  "updates": [
    {
      "field_name": "client_name",
      "new_value": "Jane Smith"
    },
    {
      "field_name": "missing_value"
    }
  ],
  "unrecognized_parts": []
}
"""
        mock_ai_client.call_llm.return_value = mock_response

        result = updater.parse_update_command("Test", sample_fields)

        # Only valid update should be included
        assert len(result.updates) == 1
        assert result.updates[0].field_name == "client_name"
