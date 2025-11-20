"""Field updater service for applying natural language updates to document fields."""
import json
from typing import List, Dict, Any

from ..models.schema import Field
from .ai_client import call_llm


def parse_update_command(command: str, existing_fields: List[Field]) -> Dict[str, str]:
    """
    Parse a natural language update command and map it to field updates.

    Args:
        command: Natural language command (e.g., "Change client name to Acme Corp")
        existing_fields: List of fields available in the template

    Returns:
        Dictionary mapping field names to new values
    """
    # Create a description of available fields
    fields_description = "\n".join([
        f"- {field.name} (type: {field.type}, current value: '{field.current_value}')"
        for field in existing_fields
    ])

    system_message = """You are an expert at parsing natural language commands to update document fields.
Given a list of available fields and a user command, determine which fields should be updated and to what values.

Return your response as a JSON object mapping field names to new values:
{
  "field_name_1": "new value",
  "field_name_2": "new value"
}

Be precise and only include fields that should be updated based on the command.
If the command is unclear or doesn't match any fields, return an empty object: {}
"""

    prompt = f"""Available fields in the document:
{fields_description}

User command: "{command}"

Which fields should be updated and to what values? Return a JSON object."""

    try:
        response = call_llm(prompt, system_message, max_tokens=1000, temperature=0.3)

        # Extract JSON from response
        response = response.strip()

        # Try to find JSON object in response
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1

        if start_idx == -1 or end_idx == 0:
            return {}

        json_str = response[start_idx:end_idx]
        updates = json.loads(json_str)

        return updates

    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response as JSON: {e}")
        return {}
    except Exception as e:
        print(f"Error parsing update command: {e}")
        return {}


def apply_updates(document_text: str, field_updates: Dict[str, str], fields: List[Field]) -> tuple[str, List[Field]]:
    """
    Apply field updates to document text.

    Args:
        document_text: Original document text
        field_updates: Dictionary mapping field names to new values
        fields: List of all fields in the document

    Returns:
        Tuple of (updated document text, updated fields list)
    """
    # Create a mapping of field names to field objects
    field_map = {field.name: field for field in fields}

    # Track changes to be applied (in reverse order to maintain positions)
    changes = []

    for field_name, new_value in field_updates.items():
        if field_name not in field_map:
            continue

        field = field_map[field_name]

        # Collect all positions for this field
        for start, end in field.positions:
            changes.append((start, end, new_value))

    # Sort changes by start position in reverse order
    changes.sort(key=lambda x: x[0], reverse=True)

    # Apply changes from end to start to maintain positions
    updated_text = document_text
    for start, end, new_value in changes:
        updated_text = updated_text[:start] + new_value + updated_text[end:]

    # Update the fields list with new values and positions
    updated_fields = []
    position_offset = 0

    for field in fields:
        if field.name in field_updates:
            new_value = field_updates[field.name]
            old_value = field.current_value

            # Calculate new positions
            new_positions = []
            value_diff = len(new_value) - len(old_value)

            for start, end in field.positions:
                new_end = start + len(new_value)
                new_positions.append([start, new_end])

            updated_field = Field(
                id=field.id,
                name=field.name,
                type=field.type,
                positions=new_positions,
                current_value=new_value
            )
            updated_fields.append(updated_field)
        else:
            updated_fields.append(field)

    return updated_text, updated_fields


async def parse_update_command_async(command: str, existing_fields: List[Field]) -> Dict[str, str]:
    """
    Async version of parse_update_command.

    Args:
        command: Natural language command
        existing_fields: List of available fields

    Returns:
        Dictionary mapping field names to new values
    """
    # For now, call sync version
    return parse_update_command(command, existing_fields)
