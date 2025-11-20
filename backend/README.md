# Spot Edit Backend API

FastAPI backend for Spot Edit - AI-powered document editing with spot-targeting capabilities.

## Features

- **Document Upload & Parsing**: Support for .txt, .pdf, and .docx files
- **AI Field Detection**: Automatically detect editable fields in documents using LLMs
- **Template Management**: Save, update, and manage document templates
- **Natural Language Updates**: Update document fields using natural language commands
- **RESTful API**: Clean, well-documented API endpoints

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Run the server:
```bash
python -m src.main
```

Or with uvicorn directly:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Document Upload
- `POST /api/upload` - Upload and analyze document

### Template Management
- `GET /api/templates` - List all templates
- `GET /api/templates/{id}` - Get specific template
- `POST /api/templates` - Create new template
- `PUT /api/templates/{id}` - Update template metadata
- `DELETE /api/templates/{id}` - Delete template

### Template Operations
- `POST /api/templates/{id}/update` - Apply natural language update
- `GET /api/templates/{id}/download` - Download updated document

### Health Check
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

## Testing

Run tests with pytest:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── middleware.py      # Middleware
│   ├── models/
│   │   └── schema.py          # Data models
│   ├── services/
│   │   ├── document_parser.py # Document parsing
│   │   ├── field_detector.py  # AI field detection
│   │   ├── field_updater.py   # Field updates
│   │   └── ai_client.py       # LLM integration
│   ├── storage/
│   │   ├── template_store.py  # Template storage
│   │   └── document_store.py  # Document storage
│   └── main.py                # FastAPI app
├── tests/
│   ├── conftest.py            # Test configuration
│   └── test_api_routes.py     # API tests
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

### AI Provider

The backend supports both Anthropic (Claude) and OpenAI (GPT) models. Configure your preferred provider in `.env`:

**Anthropic (Recommended):**
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**OpenAI:**
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
```

### CORS

Configure allowed origins for CORS in `.env`:
```env
FRONTEND_URL=http://localhost:3000
```

## Storage

Templates and uploaded files are stored in the `storage/` directory:
- `storage/templates/` - Template data
- `storage/uploads/` - Temporary uploaded files

Each template is stored as a directory containing:
- `document.txt` - Original document text
- `fields.json` - Field definitions
- `metadata.json` - Template metadata

## Development

### Adding New Endpoints

1. Define route in `src/api/routes.py`
2. Add request/response models in `src/models/schema.py`
3. Implement business logic in appropriate service
4. Add tests in `tests/test_api_routes.py`

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

## Troubleshooting

### Import Errors

If you encounter import errors, make sure you're running from the `backend/` directory:
```bash
cd backend
python -m src.main
```

### AI API Errors

Make sure you have a valid API key set in `.env` and that you have credits/quota available.

### File Upload Errors

- Maximum file size: 10MB
- Supported formats: .txt, .pdf, .docx
- Ensure files are not corrupted

## License

Part of the Spot Edit project.
