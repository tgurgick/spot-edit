# Example Templates

This directory contains example JSON templates demonstrating the storage format used by Spot Edit.

## Templates Included

### 1. Welcome Letter Template (`welcome_letter.json`)
A human resources welcome letter template with fields for:
- Recipient name
- Employee ID
- Start date
- Department
- Manager name
- HR representative name

### 2. Invoice Template (`invoice_template.json`)
A business invoice template with fields for:
- Invoice number
- Invoice date
- Client information (name, address, email)
- Service description
- Amount
- Payment due date

## Template Structure

Each template JSON file contains:

- **id**: Unique UUID identifier
- **name**: Human-readable template name
- **created_at**: Creation timestamp (ISO 8601 format)
- **updated_at**: Last update timestamp (ISO 8601 format)
- **document_text**: Full text of the document with placeholders
- **fields**: Array of field objects, each containing:
  - **id**: Unique field UUID
  - **name**: Field name
  - **field_type**: Type (text, number, date, email, phone, address, custom)
  - **positions**: Array of position objects (page, start, end)
  - **current_value**: Current value of the field
  - **metadata**: Additional field-specific metadata
- **metadata**: Template-level metadata (file type, category, etc.)

## Usage

These examples can be used for:
- Testing the template storage system
- Understanding the JSON schema
- Creating new templates based on existing patterns
- API integration testing

## Creating New Templates

To create a new template based on these examples:

1. Copy one of the example files
2. Generate new UUIDs for template and field IDs
3. Update the document text and field definitions
4. Adjust field positions based on actual document layout
5. Save with a descriptive filename
