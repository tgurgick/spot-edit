# Spot Edit API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication for MVP. Authentication will be added in future versions.

---

## Endpoints

### Health Check

#### `GET /health`

Health check endpoint to verify API is running.

**Response**
```json
{
  "status": "healthy",
  "service": "spot-edit-api"
}
```

**Status Codes**
- `200 OK` - Service is healthy

---

### Root

#### `GET /`

Root endpoint with API information.

**Response**
```json
{
  "message": "Spot Edit API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

**Status Codes**
- `200 OK` - Success

---

## Document Upload

### Upload Document

#### `POST /api/upload`

Upload a document and detect editable fields using AI.

**Request**
- Content-Type: `multipart/form-data`
- Body:
  - `file` (required): Document file (.txt, .pdf, or .docx)

**Example Request**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@contract.pdf"
```

**Response**
```json
{
  "file_id": "abc123",
  "document_text": "Full text content of the document...",
  "detected_fields": [
    {
      "id": "field_1",
      "name": "client_name",
      "type": "text",
      "positions": [[100, 115], [450, 465]],
      "current_value": "John Doe"
    },
    {
      "id": "field_2",
      "name": "contract_date",
      "type": "date",
      "positions": [[200, 213]],
      "current_value": "2024-01-15"
    }
  ]
}
```

**Status Codes**
- `200 OK` - Document uploaded and analyzed successfully
- `400 Bad Request` - Invalid file format or missing file
- `413 Payload Too Large` - File exceeds size limit
- `500 Internal Server Error` - Server error during processing

---

## Template Management

### List Templates

#### `GET /api/templates`

Get a list of all saved templates.

**Example Request**
```bash
curl http://localhost:8000/api/templates
```

**Response**
```json
[
  {
    "id": "template-123",
    "name": "Contract Template",
    "created_at": "2024-01-15T10:00:00Z",
    "document_text": "...",
    "fields": [...]
  }
]
```

**Status Codes**
- `200 OK` - Success

---

### Get Template

#### `GET /api/templates/{template_id}`

Get a specific template by ID.

**Parameters**
- `template_id` (path, required): Template ID

**Example Request**
```bash
curl http://localhost:8000/api/templates/template-123
```

**Response**
```json
{
  "id": "template-123",
  "name": "Contract Template",
  "created_at": "2024-01-15T10:00:00Z",
  "document_text": "This is a contract for {client_name} dated {contract_date}...",
  "fields": [
    {
      "id": "field_1",
      "name": "client_name",
      "type": "text",
      "positions": [[25, 37]],
      "current_value": "John Doe"
    },
    {
      "id": "field_2",
      "name": "contract_date",
      "type": "date",
      "positions": [[44, 54]],
      "current_value": "2024-01-15"
    }
  ]
}
```

**Status Codes**
- `200 OK` - Success
- `404 Not Found` - Template not found

---

### Create Template

#### `POST /api/templates`

Save a new document template with confirmed fields.

**Request Body**
```json
{
  "name": "Contract Template",
  "document_text": "Contract content...",
  "fields": [
    {
      "name": "client_name",
      "type": "text",
      "positions": [[25, 37]],
      "current_value": "John Doe"
    }
  ]
}
```

**Example Request**
```bash
curl -X POST http://localhost:8000/api/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Contract Template",
    "document_text": "...",
    "fields": [...]
  }'
```

**Response**
```json
{
  "template_id": "template-123",
  "message": "Template saved successfully"
}
```

**Status Codes**
- `201 Created` - Template created successfully
- `400 Bad Request` - Invalid request body
- `500 Internal Server Error` - Server error

---

### Update Template

#### `PUT /api/templates/{template_id}`

Update template metadata (name, etc.). Does not update field values.

**Parameters**
- `template_id` (path, required): Template ID

**Request Body**
```json
{
  "name": "Updated Contract Template"
}
```

**Example Request**
```bash
curl -X PUT http://localhost:8000/api/templates/template-123 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Contract Template"}'
```

**Response**
```json
{
  "id": "template-123",
  "name": "Updated Contract Template",
  "created_at": "2024-01-15T10:00:00Z",
  "document_text": "...",
  "fields": [...]
}
```

**Status Codes**
- `200 OK` - Success
- `404 Not Found` - Template not found
- `400 Bad Request` - Invalid request body

---

### Delete Template

#### `DELETE /api/templates/{template_id}`

Delete a template permanently.

**Parameters**
- `template_id` (path, required): Template ID

**Example Request**
```bash
curl -X DELETE http://localhost:8000/api/templates/template-123
```

**Response**
```json
{
  "message": "Template deleted successfully"
}
```

**Status Codes**
- `200 OK` - Success
- `404 Not Found` - Template not found

---

## Template Updates

### Apply Natural Language Update

#### `POST /api/templates/{template_id}/update`

Apply a natural language command to update field values in a template.

**Parameters**
- `template_id` (path, required): Template ID

**Request Body**
```json
{
  "command": "Change client name to Acme Corp and set date to today"
}
```

**Example Request**
```bash
curl -X POST http://localhost:8000/api/templates/template-123/update \
  -H "Content-Type: application/json" \
  -d '{"command": "Change client name to Acme Corp"}'
```

**Response**
```json
{
  "updated_document": "This is a contract for Acme Corp dated 2024-01-20...",
  "changes": [
    {
      "field_id": "field_1",
      "field_name": "client_name",
      "old_value": "John Doe",
      "new_value": "Acme Corp"
    },
    {
      "field_id": "field_2",
      "field_name": "contract_date",
      "old_value": "2024-01-15",
      "new_value": "2024-01-20"
    }
  ]
}
```

**Status Codes**
- `200 OK` - Success
- `404 Not Found` - Template not found
- `400 Bad Request` - Invalid command or unable to parse
- `500 Internal Server Error` - AI processing error

---

### Download Document

#### `GET /api/templates/{template_id}/download`

Download the current version of the document with applied field values.

**Parameters**
- `template_id` (path, required): Template ID
- `format` (query, optional): Output format - `txt` (default), `pdf`, or `docx`

**Example Request**
```bash
curl http://localhost:8000/api/templates/template-123/download?format=pdf \
  --output document.pdf
```

**Response**
- Content-Type: `application/octet-stream` or specific format
- Body: Document file

**Status Codes**
- `200 OK` - Success
- `404 Not Found` - Template not found
- `400 Bad Request` - Unsupported format

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "details": {
    "additional": "context if available"
  }
}
```

### Common Error Codes

- `400 Bad Request` - Invalid input or malformed request
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - File size exceeds limit
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - AI service unavailable

---

## Rate Limiting

Currently not implemented. May be added in future versions.

---

## Field Types

Supported field types in templates:

- `text` - Plain text string
- `date` - Date in ISO format (YYYY-MM-DD)
- `number` - Numeric value
- `email` - Email address
- `phone` - Phone number

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Examples

### Complete Workflow Example

1. **Upload a document**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@contract.pdf"
```

2. **Review detected fields** (from response)

3. **Save as template**
```bash
curl -X POST http://localhost:8000/api/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Contract Template",
    "document_text": "...",
    "fields": [...]
  }'
```

4. **Update field values**
```bash
curl -X POST http://localhost:8000/api/templates/template-123/update \
  -H "Content-Type: application/json" \
  -d '{"command": "Change client to Acme Corp"}'
```

5. **Download updated document**
```bash
curl http://localhost:8000/api/templates/template-123/download \
  --output updated_contract.txt
```

---

## Changelog

### v0.1.0 (MVP)
- Initial API implementation
- Document upload and field detection
- Template CRUD operations
- Natural language updates
- Document download

---

## Support

For issues and questions, please refer to the main README or open an issue on GitHub.
