"""
Field updater service for processing natural language update commands.

Uses AI to understand natural language commands and apply updates to document fields.
"""

import json
import re
from typing import List, Dict, Any, Tuple
from ..models.schema import Field, FieldUpdate, ParsedUpdate
from .ai_client import AIClient, AIClientError


class FieldUpdateError(Exception):
    """Raised when field update operations fail."""
    pass


class FieldUpdater:
    """
    Service for parsing natural language update commands and applying updates to documents.

    Uses LLM to understand natural language commands like:
    - "Change the client name to Jane Smith"
    - "Set the date to January 15, 2024 and the amount to $5000"
    - "Update contact email to john@example.com"
    """

    PARSE_SYSTEM_PROMPT = """You are an expert at parsing natural language commands for document editing.

Your task is to analyze a natural language command and extract field update instructions.

The command will reference fields in a document that the user wants to update. You need to:
1. Identify which fields are being referenced
2. Determine the new values for those fields
3. Extract each update as a structured object

You will be provided with:
- A list of existing fields in the document
- A natural language command

Return your response as a valid JSON object with this structure:
{
  "updates": [
    {
      "field_name": "name_of_field",
      "new_value": "new value",
      "confidence": 0.95
    }
  ],
  "unrecognized_parts": ["any parts of the command you couldn't interpret"]
}

Guidelines:
- Match field names flexibly (e.g., "client" could match "client_name")
- Extract the exact values mentioned in the command
- Use confidence score 0.0-1.0 to indicate how certain you are
- If you can't parse part of the command, add it to unrecognized_parts
- If the command is completely unclear, return empty updates array
"""

    def __init__(self, ai_client: AIClient):
        """
        Initialize field updater.

        Args:
            ai_client: Configured AI client for LLM calls
        """
        self.ai_client = ai_client

    def parse_update_command(
        self,
        command: str,
        existing_fields: List[Field]
    ) -> ParsedUpdate:
        """
        Parse a natural language update command into structured field updates.

        Args:
            command: Natural language command (e.g., "Change client name to Jane Smith")
            existing_fields: List of fields that exist in the document

        Returns:
            ParsedUpdate object with list of updates and any unrecognized parts

        Raises:
            FieldUpdateError: If parsing fails
        """
        if not command or not command.strip():
            return ParsedUpdate(updates=[], unrecognized_parts=[])

        try:
            # Build prompt with field context
            prompt = self._build_parse_prompt(command, existing_fields)

            # Call LLM
            response = self.ai_client.call_llm(
                prompt=prompt,
                system_message=self.PARSE_SYSTEM_PROMPT,
                temperature=0.2,  # Low temperature for consistent parsing
                max_tokens=1500,
            )

            # Parse response
            parsed = self._parse_llm_response(response, existing_fields)

            return parsed

        except AIClientError as e:
            raise FieldUpdateError(f"AI client error during command parsing: {str(e)}") from e
        except Exception as e:
            raise FieldUpdateError(f"Unexpected error during command parsing: {str(e)}") from e

    def apply_updates(
        self,
        document_text: str,
        field_updates: List[FieldUpdate],
        existing_fields: List[Field]
    ) -> str:
        """
        Apply field updates to document text.

        Args:
            document_text: Original document text
            field_updates: List of field updates to apply
            existing_fields: List of fields in the document

        Returns:
            Updated document text

        Raises:
            FieldUpdateError: If updates cannot be applied
        """
        if not field_updates:
            return document_text

        # Create a mapping of field names to Field objects
        field_map = {field.name: field for field in existing_fields}

        # Collect all replacements (position, old_value, new_value)
        replacements: List[Tuple[int, int, str]] = []

        for update in field_updates:
            field = field_map.get(update.field_name)

            if not field:
                # Try fuzzy matching
                field = self._fuzzy_match_field(update.field_name, existing_fields)

            if not field:
                raise FieldUpdateError(f"Field not found: {update.field_name}")

            # Add all positions for this field to replacements
            for start, end in field.positions:
                replacements.append((start, end, update.new_value))

        # Sort replacements by position (reverse order to avoid offset issues)
        replacements.sort(key=lambda x: x[0], reverse=True)

        # Apply replacements
        updated_text = document_text
        for start, end, new_value in replacements:
            updated_text = updated_text[:start] + new_value + updated_text[end:]

        return updated_text

    def parse_and_apply(
        self,
        command: str,
        document_text: str,
        existing_fields: List[Field]
    ) -> Tuple[str, ParsedUpdate]:
        """
        Convenience method to parse command and apply updates in one call.

        Args:
            command: Natural language command
            document_text: Original document text
            existing_fields: List of fields in the document

        Returns:
            Tuple of (updated_document_text, parsed_update)

        Raises:
            FieldUpdateError: If parsing or updating fails
        """
        # Parse command
        parsed = self.parse_update_command(command, existing_fields)

        # Apply updates
        updated_text = self.apply_updates(document_text, parsed.updates, existing_fields)

        return updated_text, parsed

    def _build_parse_prompt(self, command: str, existing_fields: List[Field]) -> str:
        """
        Build prompt for parsing update command.

        Args:
            command: Natural language command
            existing_fields: List of existing fields

        Returns:
            Formatted prompt
        """
        # Build field list for context
        field_descriptions = []
        for field in existing_fields:
            field_descriptions.append(
                f"- {field.name} (type: {field.type}, current value: {field.current_value or 'N/A'})"
            )

        field_list = "\n".join(field_descriptions) if field_descriptions else "No fields available"

        return f"""Parse the following update command.

Available fields in the document:
{field_list}

User command:
"{command}"

Extract the field updates from this command and return them as JSON.
Remember to match field names flexibly and provide confidence scores.
"""

    def _parse_llm_response(
        self,
        response: str,
        existing_fields: List[Field]
    ) -> ParsedUpdate:
        """
        Parse LLM response into ParsedUpdate object.

        Args:
            response: Raw LLM response
            existing_fields: List of existing fields for validation

        Returns:
            ParsedUpdate object

        Raises:
            FieldUpdateError: If response cannot be parsed
        """
        try:
            # Extract JSON from response
            json_str = self._extract_json(response)

            # Parse JSON
            data = json.loads(json_str)

            if not isinstance(data, dict):
                raise FieldUpdateError("LLM response is not a JSON object")

            # Extract updates
            updates = []
            for update_data in data.get("updates", []):
                try:
                    update = FieldUpdate(
                        field_name=update_data["field_name"],
                        new_value=update_data["new_value"],
                        confidence=update_data.get("confidence"),
                    )
                    updates.append(update)
                except Exception as e:
                    print(f"Warning: Skipping invalid update: {e}")
                    continue

            # Extract unrecognized parts
            unrecognized = data.get("unrecognized_parts", [])

            return ParsedUpdate(
                updates=updates,
                unrecognized_parts=unrecognized
            )

        except json.JSONDecodeError as e:
            raise FieldUpdateError(f"Failed to parse LLM response as JSON: {str(e)}") from e
        except Exception as e:
            raise FieldUpdateError(f"Failed to parse LLM response: {str(e)}") from e

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text, handling markdown code blocks.

        Args:
            text: Text that may contain JSON

        Returns:
            Extracted JSON string
        """
        # Try to find JSON in markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)

        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)

        # Return as-is if no pattern matches
        return text.strip()

    def _fuzzy_match_field(
        self,
        field_name: str,
        existing_fields: List[Field]
    ) -> Field | None:
        """
        Try to find a matching field using fuzzy matching.

        Args:
            field_name: Field name to match
            existing_fields: List of existing fields

        Returns:
            Matching Field or None
        """
        field_name_lower = field_name.lower().replace(" ", "_").replace("-", "_")

        # Try exact match first
        for field in existing_fields:
            if field.name.lower() == field_name_lower:
                return field

        # Try substring match
        for field in existing_fields:
            if field_name_lower in field.name.lower() or field.name.lower() in field_name_lower:
                return field

        return None
