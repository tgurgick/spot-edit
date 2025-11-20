# Spot Edit Backend

Backend services for AI-powered document editing with field detection and natural language updates.

## Overview

This backend provides core AI services for the Spot Edit application:

- **Document Parsing**: Extract text from .txt, .pdf, and .docx files
- **AI-Powered Field Detection**: Automatically identify editable fields in documents
- **Natural Language Updates**: Process commands like "Change client name to Jane Smith"
- **LLM Integration**: Support for OpenAI and Anthropic APIs

## Project Structure

```
backend/
├── src/
│   ├── models/           # Data models and schemas
│   │   └── schema.py     # Field, Template, UpdateRequest models
│   ├── services/         # Core business logic
│   │   ├── document_parser.py    # Document text extraction
│   │   ├── ai_client.py          # LLM API integration
│   │   ├── field_detector.py     # AI field detection
│   │   └── field_updater.py      # Natural language updates
│   ├── api/              # FastAPI routes (future)
│   └── storage/          # Template storage (future)
├── tests/                # Unit tests
│   ├── services/         # Service tests
│   └── sample_documents/ # Test documents
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip

### Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables:

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required environment variables:

- `AI_PROVIDER`: Choose "openai" or "anthropic" (default: "anthropic")
- `ANTHROPIC_API_KEY`: Your Anthropic API key (if using Anthropic)
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)

## Usage

### Document Parser

```python
from backend.src.services.document_parser import DocumentParser

# Parse from file path
text = DocumentParser.parse_file_path("path/to/document.pdf")

# Parse from file object
with open("document.docx", "rb") as f:
    text = DocumentParser.parse_document(f, "docx")
```

### AI Client

```python
from backend.src.services.ai_client import get_ai_client

# Initialize client (uses environment variables)
client = get_ai_client()

# Call LLM
response = client.call_llm(
    prompt="What is the capital of France?",
    system_message="You are a helpful assistant.",
    temperature=0.7
)
```

### Field Detector

```python
from backend.src.services.ai_client import get_ai_client
from backend.src.services.field_detector import FieldDetector

# Initialize
ai_client = get_ai_client()
detector = FieldDetector(ai_client)

# Detect fields in document
document_text = "Contract with John Doe dated 2024-01-15..."
fields = detector.detect_fields(document_text)

for field in fields:
    print(f"{field.name}: {field.current_value} at positions {field.positions}")
```

### Field Updater

```python
from backend.src.services.ai_client import get_ai_client
from backend.src.services.field_updater import FieldUpdater

# Initialize
ai_client = get_ai_client()
updater = FieldUpdater(ai_client)

# Parse and apply natural language command
updated_text, parsed = updater.parse_and_apply(
    command="Change the client name to Jane Smith and set date to Feb 20, 2024",
    document_text=original_text,
    existing_fields=detected_fields
)

print(f"Applied {len(parsed.updates)} updates")
print(updated_text)
```

## Running Tests

```bash
# Run all tests
pytest backend/tests/

# Run specific test file
pytest backend/tests/services/test_document_parser.py

# Run with coverage
pytest --cov=backend.src backend/tests/

# Run with verbose output
pytest -v backend/tests/
```

## Supported File Formats

### Document Parser

- **Plain Text (.txt)**: UTF-8 and Latin-1 encoding
- **PDF (.pdf)**: Requires PyPDF2
- **Microsoft Word (.docx)**: Requires python-docx

## AI Provider Support

### Anthropic (Claude)

- Default model: `claude-3-5-sonnet-20241022`
- Requires: `ANTHROPIC_API_KEY` environment variable
- Recommended for high-quality field detection and parsing

### OpenAI (GPT)

- Default model: `gpt-4-turbo-preview`
- Requires: `OPENAI_API_KEY` environment variable
- Alternative option with similar capabilities

## Data Models

### Field

Represents an editable field in a document:

```python
{
    "id": "field_1",
    "name": "client_name",
    "type": "text",  # or "date", "number"
    "positions": [[100, 115], [450, 465]],  # character ranges
    "current_value": "John Doe"
}
```

### Template

Represents a document template with fields:

```python
{
    "id": "tmpl_123",
    "name": "Contract Template",
    "document_text": "Full text...",
    "fields": [...]  # List of Field objects
}
```

### FieldUpdate

Represents a field update operation:

```python
{
    "field_name": "client_name",
    "new_value": "Jane Smith",
    "confidence": 0.95  # Optional confidence score
}
```

## Error Handling

All services raise specific exceptions:

- `DocumentParsingError`: Document parsing failures
- `UnsupportedFileTypeError`: Unsupported file format
- `AIClientError`: LLM API errors
- `AIRateLimitError`: Rate limit exceeded
- `FieldDetectionError`: Field detection failures
- `FieldUpdateError`: Update operation failures

## Development

### Code Structure

- **Models** (`src/models/`): Pydantic models for data validation
- **Services** (`src/services/`): Business logic and AI operations
- **Tests** (`tests/`): Unit tests with mocks

### Adding New Features

1. Define data models in `src/models/schema.py`
2. Implement service logic in `src/services/`
3. Add unit tests in `tests/services/`
4. Update this README with usage examples

## Path 2 Deliverables

This implementation fulfills Path 2 requirements:

- ✅ Document parser supporting 3 formats (.txt, .pdf, .docx)
- ✅ LLM integration with error handling and retries
- ✅ Field detection with structured output
- ✅ Natural language update processing
- ✅ Unit tests with mock LLM responses
- ✅ Sample documents for testing

## Next Steps

Path 2 provides the foundation for:

- **Path 3**: Backend API Layer (FastAPI routes)
- **Path 1**: Storage layer for templates and documents
- **Path 4-5**: Frontend integration

## License

[To be determined]
