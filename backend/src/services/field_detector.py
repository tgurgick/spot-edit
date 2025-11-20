"""
Field detection service using AI to identify editable fields in documents.

Uses LLM to analyze document text and identify fields that should be editable,
along with their positions, types, and current values.
"""

import json
import re
from typing import List, Dict, Any, Optional
from ..models.schema import Field
from .ai_client import AIClient, AIClientError


class FieldDetectionError(Exception):
    """Raised when field detection fails."""
    pass


class FieldDetector:
    """
    Service for detecting editable fields in document text using AI.

    Uses an LLM to analyze document content and identify fields that should
    be editable (e.g., names, dates, amounts, addresses).
    """

    SYSTEM_PROMPT = """You are an expert at analyzing documents and identifying editable fields.

Your task is to analyze document text and identify fields that would typically need to be
customized or filled in, such as:
- Names (people, companies, organizations)
- Dates
- Addresses
- Monetary amounts
- Email addresses
- Phone numbers
- Reference numbers or IDs
- Any placeholder text (e.g., [PLACEHOLDER], {{variable}}, ____, etc.)

For each field you identify, provide:
1. A descriptive name (snake_case, e.g., "client_name", "contract_date")
2. The type: "text", "date", or "number"
3. All positions where this field appears in the document (as character indices)
4. The current value of the field

Return your response as a valid JSON array of field objects. Each field object should have:
{
  "name": "field_name",
  "type": "text|date|number",
  "positions": [[start1, end1], [start2, end2], ...],
  "current_value": "value"
}

IMPORTANT:
- Position indices are character positions (0-based) in the original text
- If a value appears multiple times, include all positions
- Be conservative - only identify fields that clearly should be editable
- If no editable fields are found, return an empty array []
"""

    def __init__(self, ai_client: AIClient):
        """
        Initialize field detector.

        Args:
            ai_client: Configured AI client for LLM calls
        """
        self.ai_client = ai_client

    def detect_fields(self, document_text: str) -> List[Field]:
        """
        Detect editable fields in document text using AI.

        Args:
            document_text: Text content of the document to analyze

        Returns:
            List of detected Field objects

        Raises:
            FieldDetectionError: If field detection fails
        """
        if not document_text or not document_text.strip():
            return []

        try:
            # Construct prompt
            prompt = self._build_detection_prompt(document_text)

            # Call LLM
            response = self.ai_client.call_llm(
                prompt=prompt,
                system_message=self.SYSTEM_PROMPT,
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=3000,
            )

            # Parse response
            fields = self._parse_llm_response(response, document_text)

            return fields

        except AIClientError as e:
            raise FieldDetectionError(f"AI client error during field detection: {str(e)}") from e
        except Exception as e:
            raise FieldDetectionError(f"Unexpected error during field detection: {str(e)}") from e

    def _build_detection_prompt(self, document_text: str) -> str:
        """
        Build the prompt for field detection.

        Args:
            document_text: Document text to analyze

        Returns:
            Formatted prompt
        """
        # Truncate very long documents to avoid token limits
        max_chars = 8000
        if len(document_text) > max_chars:
            document_text = document_text[:max_chars] + "\n\n[Document truncated...]"

        return f"""Analyze the following document and identify all editable fields.

Document:
```
{document_text}
```

Return a JSON array of field objects with name, type, positions, and current_value for each field.
Remember to use 0-based character indices for positions.
"""

    def _parse_llm_response(self, response: str, document_text: str) -> List[Field]:
        """
        Parse LLM response into Field objects.

        Args:
            response: Raw LLM response
            document_text: Original document text (for validation)

        Returns:
            List of Field objects

        Raises:
            FieldDetectionError: If response cannot be parsed
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = self._extract_json(response)

            # Parse JSON
            field_data = json.loads(json_str)

            if not isinstance(field_data, list):
                raise FieldDetectionError("LLM response is not a JSON array")

            # Convert to Field objects with validation
            fields = []
            for item in field_data:
                try:
                    field = self._create_field_from_dict(item, document_text)
                    if field:
                        fields.append(field)
                except Exception as e:
                    # Log warning but continue with other fields
                    print(f"Warning: Skipping invalid field: {e}")
                    continue

            return fields

        except json.JSONDecodeError as e:
            raise FieldDetectionError(f"Failed to parse LLM response as JSON: {str(e)}") from e
        except Exception as e:
            raise FieldDetectionError(f"Failed to parse LLM response: {str(e)}") from e

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text, handling markdown code blocks.

        Args:
            text: Text that may contain JSON

        Returns:
            Extracted JSON string
        """
        # Try to find JSON in markdown code block
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)

        # Try to find JSON array directly
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            return json_match.group(0)

        # Return as-is if no pattern matches
        return text.strip()

    def _create_field_from_dict(
        self,
        data: Dict[str, Any],
        document_text: str
    ) -> Optional[Field]:
        """
        Create a Field object from dictionary data.

        Args:
            data: Dictionary with field data
            document_text: Original document text for validation

        Returns:
            Field object or None if invalid

        Raises:
            ValueError: If field data is invalid
        """
        # Validate required fields
        if "name" not in data:
            raise ValueError("Field missing 'name'")
        if "type" not in data:
            raise ValueError("Field missing 'type'")
        if "positions" not in data:
            raise ValueError("Field missing 'positions'")

        name = data["name"]
        field_type = data["type"]
        positions = data["positions"]
        current_value = data.get("current_value")

        # Validate type
        if field_type not in ["text", "date", "number"]:
            raise ValueError(f"Invalid field type: {field_type}")

        # Validate and clean positions
        validated_positions = []
        doc_length = len(document_text)

        for pos in positions:
            if not isinstance(pos, list) or len(pos) != 2:
                print(f"Warning: Invalid position format: {pos}")
                continue

            start, end = pos

            # Validate indices
            if not isinstance(start, int) or not isinstance(end, int):
                print(f"Warning: Position indices must be integers: {pos}")
                continue

            if start < 0 or end < 0 or start >= end:
                print(f"Warning: Invalid position range: {pos}")
                continue

            if end > doc_length:
                print(f"Warning: Position exceeds document length: {pos}")
                continue

            validated_positions.append((start, end))

        if not validated_positions:
            raise ValueError("No valid positions found for field")

        # Create Field object
        return Field(
            name=name,
            type=field_type,
            positions=validated_positions,
            current_value=current_value,
        )

    def detect_fields_with_hints(
        self,
        document_text: str,
        field_hints: Optional[List[str]] = None
    ) -> List[Field]:
        """
        Detect fields with optional hints about what to look for.

        Args:
            document_text: Text content to analyze
            field_hints: Optional list of field names to look for (e.g., ["client_name", "date"])

        Returns:
            List of detected Field objects

        Raises:
            FieldDetectionError: If field detection fails
        """
        if not field_hints:
            return self.detect_fields(document_text)

        # Enhance system prompt with hints
        enhanced_system = self.SYSTEM_PROMPT + f"""

The user has indicated they expect these fields to be present:
{', '.join(field_hints)}

Pay special attention to identifying these fields, but also look for other editable fields.
"""

        try:
            prompt = self._build_detection_prompt(document_text)

            response = self.ai_client.call_llm(
                prompt=prompt,
                system_message=enhanced_system,
                temperature=0.3,
                max_tokens=3000,
            )

            fields = self._parse_llm_response(response, document_text)

            return fields

        except AIClientError as e:
            raise FieldDetectionError(f"AI client error during field detection: {str(e)}") from e
        except Exception as e:
            raise FieldDetectionError(f"Unexpected error during field detection: {str(e)}") from e
