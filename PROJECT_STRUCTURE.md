# Spot Edit - Project Structure

## Proposed File Organization

```
spot-edit/
├── frontend/                      # Web UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUpload.tsx      # File drop/upload interface
│   │   │   ├── FieldConfirmation.tsx   # HITL field review UI
│   │   │   ├── ChatInterface.tsx       # Natural language chat
│   │   │   ├── TemplateLibrary.tsx     # Saved templates list
│   │   │   └── DocumentPreview.tsx     # Show doc with highlighted fields
│   │   ├── pages/
│   │   │   ├── Upload.tsx              # Initial upload page
│   │   │   ├── Confirm.tsx             # Field confirmation page
│   │   │   └── Edit.tsx                # Template editing page
│   │   ├── api/
│   │   │   └── client.ts               # API calls to backend
│   │   ├── types/
│   │   │   └── index.ts                # TypeScript types
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                       # API Server
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes.py               # API endpoints
│   │   │   └── middleware.py           # Auth, validation, etc.
│   │   ├── services/
│   │   │   ├── document_parser.py      # Convert docs to text
│   │   │   ├── field_detector.py       # AI field detection logic
│   │   │   ├── field_updater.py        # Update fields in documents
│   │   │   └── ai_client.py            # LLM API integration
│   │   ├── storage/
│   │   │   ├── template_store.py       # Save/load templates
│   │   │   └── document_store.py       # Document file storage
│   │   ├── models/
│   │   │   └── schema.py               # Data models
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── storage/                       # Local file storage (dev)
│   ├── templates/                 # Saved document templates
│   │   └── {template_id}/
│   │       ├── document.txt            # Original document text
│   │       ├── fields.json             # Field mappings
│   │       └── metadata.json           # Template info
│   └── uploads/                   # Temporary upload storage
│
├── tests/
│   ├── frontend/
│   │   └── components.test.tsx
│   └── backend/
│       ├── test_field_detector.py
│       └── test_document_parser.py
│
├── docs/
│   ├── API.md                     # API documentation
│   └── ARCHITECTURE.md            # System design
│
├── .env.example                   # Environment variables template
├── docker-compose.yml             # Local development setup
├── README.md
├── CLAUDE.md
└── PROJECT_STRUCTURE.md
```

## Key Files Explained

### Frontend Components

**DocumentUpload.tsx**
- Drag-and-drop interface
- File format validation
- Upload progress indicator

**FieldConfirmation.tsx**
- Display AI-detected fields
- Checkboxes to confirm/reject fields
- Edit field names/types
- Visual highlighting of fields in document

**ChatInterface.tsx**
- Natural language input
- Conversation history
- Display of proposed changes
- Apply/reject actions

**TemplateLibrary.tsx**
- List saved templates
- Search/filter templates
- Template metadata display
- Load template action

### Backend Services

**document_parser.py**
```python
# Handles document conversion
- parse_document(file) -> text
- extract_text_from_pdf()
- extract_text_from_docx()
- extract_text_from_txt()
```

**field_detector.py**
```python
# AI-powered field detection
- detect_fields(document_text) -> List[Field]
- Uses LLM to identify editable fields
- Returns field positions, types, values
```

**field_updater.py**
```python
# Updates fields based on natural language
- parse_user_command(command, fields) -> updates
- apply_updates(document, updates) -> updated_document
- Handles multi-field updates
```

**template_store.py**
```python
# Template persistence
- save_template(doc, fields, metadata)
- load_template(template_id)
- list_templates()
- delete_template(template_id)
```

### Data Models

**Template**
```json
{
  "id": "uuid",
  "name": "Contract Template",
  "created_at": "timestamp",
  "document_text": "original document...",
  "fields": [
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

## Technology Stack

### Frontend
- **Framework**: React + TypeScript
- **Build**: Vite
- **Styling**: Tailwind CSS
- **State**: Zustand (minimal state management)
- **HTTP**: Axios

### Backend
- **Framework**: FastAPI (Python)
- **Document Parsing**:
  - PyPDF2 (PDF)
  - python-docx (DOCX)
  - Basic text file handling
- **AI Integration**: OpenAI or Anthropic API client
- **Storage**: File system (for MVP), later SQLite or PostgreSQL

### Development
- **Containerization**: Docker + Docker Compose
- **Testing**: Pytest (backend), Vitest (frontend)

## Workflow Through the System

### 1. Initial Upload
```
User uploads file
  → Frontend: DocumentUpload.tsx
  → Backend: POST /api/upload
  → document_parser.py converts to text
  → field_detector.py uses AI to find fields
  → Returns detected fields to frontend
  → Frontend: FieldConfirmation.tsx displays fields
```

### 2. Field Confirmation
```
User confirms/edits fields
  → Frontend: FieldConfirmation.tsx
  → Backend: POST /api/templates
  → template_store.py saves template
  → Returns template_id
```

### 3. Template Reuse
```
User loads template
  → Frontend: TemplateLibrary.tsx
  → Backend: GET /api/templates/{id}
  → template_store.py loads template
  → Frontend: Edit.tsx shows document + chat
```

### 4. Natural Language Update
```
User: "Change client name to Acme Corp"
  → Frontend: ChatInterface.tsx
  → Backend: POST /api/templates/{id}/update
  → field_updater.py parses command with AI
  → Identifies field(s) to update
  → Applies updates to document
  → Returns updated document
  → Frontend: Shows preview, user downloads
```

## API Endpoints

```
POST   /api/upload                    # Upload and analyze document
GET    /api/templates                 # List all templates
GET    /api/templates/{id}            # Get specific template
POST   /api/templates                 # Save new template
PUT    /api/templates/{id}            # Update template
DELETE /api/templates/{id}            # Delete template
POST   /api/templates/{id}/update     # Apply natural language update
GET    /api/templates/{id}/download   # Download updated document
```

## Minimal First Implementation

For an MVP, start with:

1. **Backend Core**
   - `document_parser.py` (text and PDF only)
   - `field_detector.py` (basic AI integration)
   - `template_store.py` (JSON file storage)
   - Simple FastAPI routes

2. **Frontend Core**
   - Document upload page
   - Field confirmation UI
   - Basic template library
   - Simple chat interface

3. **Storage**
   - Local file system
   - JSON files for templates

This structure keeps things simple while allowing for growth as features are validated.
