# Spot Edit - System Architecture

## Overview

Spot Edit is an AI-powered document editing system that enables intelligent, context-aware editing through natural language commands. The architecture follows a clean separation between frontend, backend, and AI services.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User/Browser                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   Upload UI  │  │  Confirm UI  │  │  Template Library  │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   Chat UI    │  │  Preview UI  │  │    API Client      │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI/Python)                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      API Layer                             │ │
│  │  /upload | /templates | /templates/{id}/update            │ │
│  └─────────────────────┬─────────────────────────────────────┘ │
│                        │                                         │
│  ┌─────────────────────┼─────────────────────────────────────┐ │
│  │              Service Layer                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │   Document   │  │    Field     │  │    Field     │    │ │
│  │  │    Parser    │  │   Detector   │  │   Updater    │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └─────────────────────┼─────────────────────────────────────┘ │
│                        │                                         │
│  ┌─────────────────────┼─────────────────────────────────────┐ │
│  │              Storage Layer                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐                       │ │
│  │  │   Template   │  │   Document   │                       │ │
│  │  │    Store     │  │    Store     │                       │ │
│  │  └──────────────┘  └──────────────┘                       │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI/LLM Services                             │
│               (OpenAI / Anthropic Claude)                        │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    File System Storage                           │
│              (Templates, Uploads, Metadata)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Components

### Frontend (React + TypeScript)

#### Technology Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Testing**: Vitest + React Testing Library

#### Key Components

**1. DocumentUpload Component**
- Handles file drag-and-drop
- Validates file types (.txt, .pdf, .docx)
- Shows upload progress
- Triggers document analysis

**2. FieldConfirmation Component**
- Displays AI-detected fields
- Allows user to confirm/reject/edit fields
- Manages field metadata (name, type, positions)
- Triggers template save

**3. TemplateLibrary Component**
- Lists all saved templates
- Provides search/filter functionality
- Allows template deletion
- Navigates to edit page

**4. ChatInterface Component**
- Natural language input for updates
- Displays conversation history
- Shows proposed changes
- Applies updates to document

**5. DocumentPreview Component**
- Renders document text
- Highlights field positions
- Shows current field values
- Updates in real-time

#### Data Flow

```
User Action → Component → API Client → Backend API
     ↓
   Store Update (Zustand)
     ↓
   Component Re-render
```

---

### Backend (FastAPI + Python)

#### Technology Stack
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic v2
- **Document Parsing**: PyPDF2, python-docx
- **AI Integration**: OpenAI SDK, Anthropic SDK
- **Testing**: pytest, pytest-asyncio

#### Architecture Layers

**1. API Layer** (`src/api/`)

Handles HTTP requests and responses:
- Request validation
- Response formatting
- Error handling
- CORS middleware
- File upload handling

**2. Service Layer** (`src/services/`)

Business logic implementation:

**Document Parser Service**
```python
class DocumentParser:
    def parse_document(file: UploadFile) -> str
    def extract_text_from_pdf(file) -> str
    def extract_text_from_docx(file) -> str
    def extract_text_from_txt(file) -> str
```

**Field Detector Service**
```python
class FieldDetector:
    def detect_fields(document_text: str) -> List[Field]
    # Uses AI to identify editable fields
    # Returns structured field data
```

**Field Updater Service**
```python
class FieldUpdater:
    def parse_command(command: str, fields: List[Field]) -> Dict
    def apply_updates(doc_text: str, updates: Dict) -> str
    # Uses AI to understand natural language
    # Applies changes to document
```

**AI Client Service**
```python
class AIClient:
    def call_llm(prompt: str, system: str) -> str
    # Abstracts OpenAI/Anthropic API calls
    # Handles retries and errors
```

**3. Storage Layer** (`src/storage/`)

Data persistence:

**Template Store**
```python
class TemplateStore:
    def save_template(template: Template) -> str
    def load_template(template_id: str) -> Template
    def list_templates() -> List[Template]
    def delete_template(template_id: str) -> None
```

**Document Store**
```python
class DocumentStore:
    def save_upload(file: UploadFile) -> str
    def get_upload(file_id: str) -> bytes
    def delete_upload(file_id: str) -> None
```

**4. Models Layer** (`src/models/`)

Data models using Pydantic:

```python
class Field(BaseModel):
    id: str
    name: str
    type: FieldType
    positions: List[Tuple[int, int]]
    current_value: str

class Template(BaseModel):
    id: str
    name: str
    created_at: datetime
    document_text: str
    fields: List[Field]
```

---

## Data Flow

### 1. Document Upload & Analysis Flow

```
┌──────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ User │────>│ Frontend │────>│ Backend  │────>│   LLM    │
└──────┘     └──────────┘     └──────────┘     └──────────┘
                  │                 │                 │
                  │                 │                 │
                  │            Parse Document          │
                  │            Extract Text            │
                  │                 │                 │
                  │                 │<────Detect─────┤
                  │                 │     Fields      │
                  │                 │                 │
                  │<───Return───────┤                 │
                  │    Fields       │                 │
                  │                 │                 │
                  ▼                 ▼                 ▼
```

**Steps:**
1. User uploads document (PDF/DOCX/TXT)
2. Frontend sends file to `/api/upload`
3. Backend parses document to extract text
4. AI analyzes text to detect editable fields
5. Backend returns detected fields to frontend
6. User confirms/edits fields in UI

### 2. Template Save Flow

```
┌──────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ User │────>│ Frontend │────>│ Backend  │────>│  Storage │
└──────┘     └──────────┘     └──────────┘     └──────────┘
   Confirm       Send            Create           Write
   Fields      Template         Template          JSON
                Data            Object            Files
```

**Steps:**
1. User confirms fields
2. Frontend sends template data to `/api/templates`
3. Backend creates Template object
4. Storage layer writes to file system
5. Returns template ID to frontend

### 3. Natural Language Update Flow

```
┌──────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ User │────>│ Frontend │────>│ Backend  │────>│   LLM    │
└──────┘     └──────────┘     └──────────┘     └──────────┘
  "Change        Send           Parse with        Identify
  name to      Command          AI Client         Fields &
  Acme"                                           Values
                  │                 │                 │
                  │                 │<───Extract──────┤
                  │                 │    Changes      │
                  │                 │                 │
                  │            Apply Updates          │
                  │            to Document            │
                  │                 │                 │
                  │<───Return───────┤                 │
                  │    Updated      │                 │
                  │    Document     │                 │
```

**Steps:**
1. User types natural language command
2. Frontend sends to `/api/templates/{id}/update`
3. AI parses command to identify field changes
4. Backend applies changes to document text
5. Returns updated document and change log

---

## Storage Structure

### File System Layout

```
storage/
├── templates/
│   ├── {template_id}/
│   │   ├── metadata.json         # Template info
│   │   ├── document.txt          # Original document
│   │   └── fields.json           # Field definitions
│   └── ...
└── uploads/
    ├── {upload_id}.pdf           # Temporary uploads
    └── ...
```

### Template Metadata Format

```json
{
  "id": "template-abc123",
  "name": "Contract Template",
  "created_at": "2024-01-15T10:00:00Z",
  "file_type": "pdf",
  "field_count": 5
}
```

### Fields Format

```json
{
  "fields": [
    {
      "id": "field_1",
      "name": "client_name",
      "type": "text",
      "positions": [[100, 115], [450, 465]],
      "current_value": "John Doe"
    }
  ]
}
```

---

## AI Integration

### Prompt Design

**Field Detection Prompt:**
```
System: You are a document analysis AI. Identify editable fields in documents.

User: Analyze this document and find all fields that should be editable:
{document_text}

Return a JSON array of fields with: name, type, positions, and current value.
```

**Field Update Prompt:**
```
System: You are a document editing AI. Parse natural language commands.

User: I have these fields: {fields}
Apply this command: "{user_command}"

Return JSON with field IDs and new values.
```

### AI Provider Abstraction

```python
class AIProvider(ABC):
    @abstractmethod
    async def call(prompt: str, system: str) -> str
        pass

class OpenAIProvider(AIProvider):
    async def call(prompt: str, system: str) -> str:
        # OpenAI implementation

class AnthropicProvider(AIProvider):
    async def call(prompt: str, system: str) -> str:
        # Anthropic implementation
```

---

## Security Considerations

### Current MVP
- No authentication (development only)
- CORS configured for localhost
- File size limits enforced
- File type validation

### Future Enhancements
- JWT-based authentication
- User-specific storage isolation
- API rate limiting
- Input sanitization
- Encrypted storage
- Audit logging

---

## Scalability Considerations

### Current MVP
- File-based storage
- Synchronous processing
- Single server deployment

### Future Enhancements

**Backend:**
- Database storage (PostgreSQL)
- Async queue for long operations (Celery/Redis)
- Caching layer (Redis)
- Horizontal scaling with load balancer

**Storage:**
- Cloud object storage (S3/GCS)
- CDN for document delivery
- Database for metadata

**AI:**
- Request queuing
- Response caching
- Fallback providers

---

## Testing Strategy

### Backend Testing

**Unit Tests:**
- Individual service functions
- Data model validation
- Storage operations

**Integration Tests:**
- API endpoint behavior
- Service layer integration
- File upload/download

**Mocking:**
- Mock LLM responses
- Mock file uploads
- Mock storage operations

### Frontend Testing

**Unit Tests:**
- Component rendering
- User interactions
- API client calls

**Integration Tests:**
- User workflows
- State management
- Routing

---

## Deployment

### Development (Docker Compose)

```bash
docker-compose up
```

Services:
- Frontend: http://localhost:5173 (dev) or http://localhost:80 (prod)
- Backend: http://localhost:8000

### Production (Future)

**Option 1: Traditional VPS**
- Nginx reverse proxy
- Gunicorn/Uvicorn workers
- Systemd service management

**Option 2: Cloud Platform**
- Frontend: Vercel/Netlify
- Backend: Railway/Render/AWS
- Storage: S3/GCS
- Database: Managed PostgreSQL

**Option 3: Kubernetes**
- Container orchestration
- Auto-scaling
- Load balancing

---

## Monitoring & Observability

### Metrics to Track
- API response times
- Error rates
- Document processing times
- AI API call latency
- Storage usage

### Logging
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation

### Future Tools
- Prometheus for metrics
- Grafana for visualization
- Sentry for error tracking
- OpenTelemetry for tracing

---

## Technology Choices Rationale

### Why FastAPI?
- High performance (async support)
- Auto-generated API docs
- Built-in validation (Pydantic)
- Modern Python features

### Why React?
- Component-based architecture
- Large ecosystem
- TypeScript support
- Excellent tooling

### Why File Storage (MVP)?
- Simple to implement
- No database setup needed
- Easy to migrate later
- Sufficient for prototype

### Why OpenAI/Anthropic?
- State-of-the-art language understanding
- Good structured output support
- Reliable APIs
- Reasonable pricing

---

## Future Architecture Enhancements

1. **Multi-tenancy**: User accounts and permissions
2. **Real-time Collaboration**: WebSocket support for live editing
3. **Version Control**: Document history and rollback
4. **Export Formats**: Support for more document types
5. **Batch Processing**: Process multiple documents
6. **Custom AI Models**: Fine-tuned models for specific domains
7. **Plugin System**: Extensible architecture for custom processors

---

## Conclusion

The Spot Edit architecture is designed to be:
- **Simple**: Easy to understand and modify
- **Modular**: Clear separation of concerns
- **Scalable**: Can grow with user demands
- **Maintainable**: Clean code and good testing
- **Extensible**: Ready for future enhancements

For implementation details, see:
- [API Documentation](./API.md)
- [Project Structure](../PROJECT_STRUCTURE.md)
- [Development Paths](../PARALLEL_DEVELOPMENT_PATHS.md)
