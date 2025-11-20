"""Field detection service using AI to identify editable fields in documents."""
import json
import uuid
from typing import List

from ..models.schema import Field
from .ai_client import call_llm


def detect_fields(document_text: str) -> List[Field]:
    """
    Detect editable fields in a document using AI.

    Args:
        document_text: The document text to analyze

    Returns:
        List of detected Field objects
    """
    system_message = """You are an expert at analyzing documents and identifying editable fields.
Your task is to identify fields in the document that could be edited or customized.
Look for things like names, dates, addresses, amounts, company names, etc.

Return your response as a JSON array of field objects with this structure:
[
  {
    "name": "field_name",
    "type": "text|date|number|email|phone",
    "positions": [[start_index, end_index], ...],
    "current_value": "the actual value in the document"
  }
]

Be specific and accurate with the positions. Include all occurrences of each field.
"""

    prompt = f"""Analyze this document and identify all editable fields:

--- DOCUMENT START ---
{document_text}
--- DOCUMENT END ---

Return a JSON array of detected fields with their positions in the document."""

    try:
        response = call_llm(prompt, system_message, max_tokens=3000, temperature=0.3)

        # Extract JSON from response
        response = response.strip()

        # Try to find JSON array in response
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1

        if start_idx == -1 or end_idx == 0:
            # No JSON found, return empty list
            return []

        json_str = response[start_idx:end_idx]
        fields_data = json.loads(json_str)

        # Convert to Field objects
        fields = []
        for field_dict in fields_data:
            field = Field(
                id=f"field_{uuid.uuid4().hex[:8]}",
                name=field_dict.get("name", "unknown_field"),
                type=field_dict.get("type", "text"),
                positions=field_dict.get("positions", []),
                current_value=field_dict.get("current_value", "")
            )
            fields.append(field)

        return fields

    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response as JSON: {e}")
        return []
    except Exception as e:
        print(f"Error detecting fields: {e}")
        return []


async def detect_fields_async(document_text: str) -> List[Field]:
    """
    Async version of detect_fields.

    Args:
        document_text: The document text to analyze

    Returns:
        List of detected Field objects
    """
    # For now, call sync version
    # In production, would use async AI client
    return detect_fields(document_text)
