# Parallel Development Paths for Spot Edit

## Overview

This document defines 5 independent development paths that can be worked on simultaneously by different agents/developers. Each path is designed to minimize dependencies and allow parallel progress.

---

## Path 1: Backend Foundation & Storage

**Owner:** Agent 1
**Priority:** High (blocking for other backend work)
**Estimated Effort:** Medium

### Scope
- Data models and schema definitions
- Template storage system
- Document storage system
- Basic file system operations

### Tasks
1. **Define Data Models** (`backend/src/models/schema.py`)
   - Template model (id, name, created_at, document_text, fields)
   - Field model (id, name, type, positions, current_value)
   - UpdateRequest model
   - Response models

2. **Implement Template Storage** (`backend/src/storage/template_store.py`)
   - `save_template(document, fields, metadata)` → template_id
   - `load_template(template_id)` → Template
   - `list_templates()` → List[Template]
   - `update_template(template_id, updates)`
   - `delete_template(template_id)`
   - Use JSON file storage for MVP

3. **Implement Document Storage** (`backend/src/storage/document_store.py`)
   - `save_upload(file)` → file_id
   - `get_upload(file_id)` → file content
   - `delete_upload(file_id)`
   - Handle temporary file cleanup

4. **Create Storage Directory Structure**
   - Set up `storage/templates/` with subdirectories
   - Set up `storage/uploads/` for temporary files

### Deliverables
- ✅ Complete data models with type hints
- ✅ Template CRUD operations
- ✅ Document upload/retrieval system
- ✅ Unit tests for storage layer
- ✅ Example JSON templates for testing

### Dependencies
- **Blocks:** Path 2, Path 3
- **Requires:** None

---

## Path 2: Backend AI Services

**Owner:** Agent 2
**Priority:** High (core functionality)
**Estimated Effort:** High

### Scope
- Document parsing and text extraction
- AI-powered field detection
- AI-powered field updates
- LLM API integration

### Tasks
1. **Document Parser** (`backend/src/services/document_parser.py`)
   - `parse_document(file, file_type)` → text
   - `extract_text_from_pdf(file)` → text
   - `extract_text_from_docx(file)` → text
   - `extract_text_from_txt(file)` → text
   - Support for .txt, .pdf, .docx initially

2. **AI Client** (`backend/src/services/ai_client.py`)
   - `get_ai_client()` → LLM client instance
   - `call_llm(prompt, system_message)` → response
   - Support OpenAI and/or Anthropic APIs
   - Handle API errors and retries
   - Configuration from environment variables

3. **Field Detector** (`backend/src/services/field_detector.py`)
   - `detect_fields(document_text)` → List[Field]
   - Use LLM to identify editable fields
   - Prompt engineering for field detection
   - Return field names, types, positions, and current values
   - Handle edge cases (no fields found, ambiguous fields)

4. **Field Updater** (`backend/src/services/field_updater.py`)
   - `parse_update_command(command, existing_fields)` → field updates
   - `apply_updates(document_text, field_updates)` → updated document
   - Use LLM to understand natural language commands
   - Map commands to specific field updates
   - Handle multi-field updates in one command

### Deliverables
- ✅ Document parser supporting 3 formats
- ✅ LLM integration with error handling
- ✅ Field detection with structured output
- ✅ Natural language update processing
- ✅ Unit tests with mock LLM responses
- ✅ Sample documents for testing

### Dependencies
- **Blocks:** Path 3
- **Requires:** Path 1 (data models)

---

## Path 3: Backend API Layer

**Owner:** Agent 3
**Priority:** High (integration layer)
**Estimated Effort:** Medium

### Scope
- FastAPI application setup
- API endpoints
- Request/response handling
- Middleware and error handling

### Tasks
1. **FastAPI Setup** (`backend/src/main.py`)
   - Initialize FastAPI app
   - Configure CORS
   - Add middleware (logging, error handling)
   - Environment configuration
   - Health check endpoint

2. **API Routes** (`backend/src/api/routes.py`)
   - `POST /api/upload` - Upload and analyze document
   - `GET /api/templates` - List all templates
   - `GET /api/templates/{id}` - Get specific template
   - `POST /api/templates` - Save new template
   - `PUT /api/templates/{id}` - Update template metadata
   - `DELETE /api/templates/{id}` - Delete template
   - `POST /api/templates/{id}/update` - Apply natural language update
   - `GET /api/templates/{id}/download` - Download updated document

3. **Middleware** (`backend/src/api/middleware.py`)
   - Request validation
   - Error handling and formatting
   - Request logging
   - File size limits
   - Rate limiting (optional for MVP)

4. **Integration Layer**
   - Wire up services from Path 1 and Path 2
   - Handle file uploads (multipart/form-data)
   - Response formatting
   - Error responses (400, 404, 500)

5. **Backend Dependencies**
   - Create `backend/requirements.txt`
   - FastAPI, uvicorn, pydantic
   - Document parsing libraries (PyPDF2, python-docx)
   - LLM SDK (openai/anthropic)
   - Testing dependencies

### Deliverables
- ✅ Complete FastAPI application
- ✅ All 8 API endpoints implemented
- ✅ Error handling middleware
- ✅ Integration tests for each endpoint
- ✅ requirements.txt
- ✅ API documentation (auto-generated by FastAPI)

### Dependencies
- **Blocks:** Path 4, Path 5
- **Requires:** Path 1 (storage), Path 2 (services)

---

## Path 4: Frontend Core Upload & Confirmation

**Owner:** Agent 4
**Priority:** High (critical user flow)
**Estimated Effort:** Medium

### Scope
- Document upload interface
- Field confirmation UI
- Document preview component
- Initial upload workflow pages

### Tasks
1. **Frontend Setup**
   - Initialize Vite + React + TypeScript project in `frontend/`
   - Configure Tailwind CSS
   - Set up folder structure
   - Create `frontend/package.json`

2. **TypeScript Types** (`frontend/src/types/index.ts`)
   - Field type
   - Template type
   - API request/response types
   - Match backend schema

3. **DocumentUpload Component** (`frontend/src/components/DocumentUpload.tsx`)
   - Drag-and-drop zone
   - File picker button
   - File format validation (.txt, .pdf, .docx)
   - Upload progress indicator
   - Error display
   - File size validation

4. **FieldConfirmation Component** (`frontend/src/components/FieldConfirmation.tsx`)
   - Display detected fields in a list/table
   - Checkboxes to confirm/reject each field
   - Edit field name
   - Edit field type (text, date, number, etc.)
   - Select field occurrences in document
   - Save template button

5. **DocumentPreview Component** (`frontend/src/components/DocumentPreview.tsx`)
   - Display document text
   - Highlight detected fields
   - Show field positions
   - Responsive layout

6. **Upload Page** (`frontend/src/pages/Upload.tsx`)
   - Integrate DocumentUpload component
   - Handle file upload to backend
   - Show loading state
   - Navigate to confirmation page on success

7. **Confirm Page** (`frontend/src/pages/Confirm.tsx`)
   - Integrate FieldConfirmation and DocumentPreview
   - Display fields detected by AI
   - Allow user to confirm/edit fields
   - Save template to backend
   - Navigate to template library on success

8. **API Client** (`frontend/src/api/client.ts`)
   - Axios setup
   - `uploadDocument(file)` → detected fields
   - `saveTemplate(document, fields, metadata)` → template_id
   - Error handling
   - Base URL configuration

### Deliverables
- ✅ Vite + React + TypeScript project
- ✅ Upload and confirmation components
- ✅ Document preview with field highlighting
- ✅ Two complete pages (Upload, Confirm)
- ✅ API client for upload workflow
- ✅ Component tests (Vitest)
- ✅ Styled with Tailwind CSS

### Dependencies
- **Blocks:** None (can work with mock data)
- **Requires:** Path 3 (API endpoints) for full integration

---

## Path 5: Frontend Templates & Editing

**Owner:** Agent 5
**Priority:** Medium (depends on upload flow)
**Estimated Effort:** Medium

### Scope
- Template library interface
- Chat interface for updates
- Edit page workflow
- Template management

### Tasks
1. **TemplateLibrary Component** (`frontend/src/components/TemplateLibrary.tsx`)
   - List all saved templates
   - Template cards with metadata (name, date, field count)
   - Search/filter templates
   - Delete template action
   - Load template button
   - Empty state when no templates

2. **ChatInterface Component** (`frontend/src/components/ChatInterface.tsx`)
   - Message input field
   - Send button
   - Conversation history display
   - User messages vs AI responses styling
   - Loading indicator while processing
   - Display proposed changes
   - Apply/reject buttons for changes

3. **Edit Page** (`frontend/src/pages/Edit.tsx`)
   - Load template from ID
   - Display DocumentPreview with current values
   - Integrate ChatInterface
   - Show current field values
   - Handle update commands
   - Download updated document button
   - Export functionality

4. **API Client Extensions** (`frontend/src/api/client.ts`)
   - `getTemplates()` → List[Template]
   - `getTemplate(id)` → Template
   - `deleteTemplate(id)` → success
   - `updateTemplate(id, command)` → updated document
   - `downloadTemplate(id)` → file blob

5. **State Management** (`frontend/src/store/` or hooks)
   - Current template state
   - Chat history state
   - Template list state
   - Use Zustand or React Context + hooks

6. **Routing** (`frontend/src/App.tsx`)
   - Set up React Router
   - Routes: `/`, `/upload`, `/confirm`, `/templates`, `/edit/:id`
   - Navigation between pages
   - Layout component with header/nav

### Deliverables
- ✅ Template library with CRUD operations
- ✅ Chat interface for natural language updates
- ✅ Complete edit page workflow
- ✅ State management solution
- ✅ Routing and navigation
- ✅ Download/export functionality
- ✅ Component tests
- ✅ Integration with backend API

### Dependencies
- **Blocks:** None
- **Requires:** Path 3 (API endpoints), Path 4 (shared types/components)

---

## Path 6: DevOps & Infrastructure (Optional/Parallel)

**Owner:** Agent 6 or any available agent
**Priority:** Low (can be done later)
**Estimated Effort:** Small

### Scope
- Docker containerization
- Development environment setup
- Testing infrastructure
- Environment configuration

### Tasks
1. **Backend Dockerfile** (`backend/Dockerfile`)
   - Python base image
   - Install dependencies
   - Copy source code
   - Expose port
   - Run with uvicorn

2. **Frontend Dockerfile** (`frontend/Dockerfile`)
   - Node base image
   - Install dependencies
   - Build production bundle
   - Serve with nginx or node server

3. **Docker Compose** (`docker-compose.yml`)
   - Backend service
   - Frontend service
   - Volume mounts for development
   - Environment variables
   - Port mappings

4. **Environment Configuration**
   - `.env.example` with all required variables
   - LLM API keys
   - Backend URL
   - Storage paths

5. **Testing Setup**
   - Backend: pytest configuration
   - Frontend: Vitest configuration
   - Test data fixtures
   - CI/CD pipeline setup (GitHub Actions)

6. **Documentation**
   - `docs/API.md` - API endpoint documentation
   - `docs/ARCHITECTURE.md` - System design overview
   - Update README with setup instructions

### Deliverables
- ✅ Docker containers for frontend and backend
- ✅ docker-compose.yml for local development
- ✅ Environment configuration template
- ✅ Testing framework setup
- ✅ Documentation

### Dependencies
- **Blocks:** None
- **Requires:** Paths 1-5 for complete setup

---

## Integration Points

### Between Paths 1 & 2
- Path 2 imports data models from Path 1
- Coordinate on Field and Template structure

### Between Paths 1, 2 & 3
- Path 3 imports services from Path 1 and 2
- Integration testing once all three are complete

### Between Paths 3 & 4
- Path 4 calls APIs from Path 3
- Can develop with mock API responses initially
- Integration once backend is deployed

### Between Paths 4 & 5
- Path 5 uses types and some components from Path 4
- Share API client
- Coordinate on routing structure

---

## Development Timeline Suggestion

### Week 1
- **All Paths:** Start simultaneously
- **Paths 1, 2, 3:** Focus on backend (can be done independently)
- **Paths 4, 5:** Frontend work with mock data

### Week 2
- **Integration:** Connect frontend to backend
- **Testing:** End-to-end testing
- **Path 6:** Complete DevOps setup

### Week 3
- **Polish:** UI/UX refinements
- **Testing:** Comprehensive testing
- **Documentation:** Complete all docs
- **Deployment:** MVP launch

---

## Communication Protocol

### Daily Sync Points
Each agent should push commits daily with clear commit messages indicating:
- Which path/task is being worked on
- What was completed
- Any blockers or dependencies needed

### Merge Strategy
- Each path uses feature branches: `path-1-backend-foundation`, `path-2-ai-services`, etc.
- Merge to `main` only when a complete deliverable is ready
- Code review before merging

### Handoff Requirements
When one path completes a dependency for another:
1. Update this document with completion status
2. Tag dependent path owner
3. Provide integration instructions

---

## Success Criteria

### Path 1: Backend Foundation
✅ Can save and retrieve templates from file system
✅ All storage operations have tests
✅ Data models are well-typed and documented

### Path 2: Backend AI Services
✅ Can parse .txt, .pdf, .docx files
✅ Field detection returns structured data
✅ Natural language commands update fields correctly
✅ All services have unit tests with mocks

### Path 3: Backend API Layer
✅ All 8 endpoints return correct responses
✅ Error handling works for common cases
✅ API documentation is auto-generated and clear
✅ Integration tests pass

### Path 4: Frontend Core
✅ Users can upload documents
✅ Users can confirm/edit detected fields
✅ Templates can be saved
✅ UI is responsive and styled

### Path 5: Frontend Templates
✅ Users can view template library
✅ Users can chat with AI to update fields
✅ Updated documents can be downloaded
✅ All workflows are complete

### Path 6: DevOps
✅ Application runs with `docker-compose up`
✅ Tests can be run with single command
✅ Documentation is complete

---

## Getting Started

### For Agent 1 (Backend Foundation)
```bash
mkdir -p backend/src/{models,storage}
cd backend
# Start with schema.py
```

### For Agent 2 (Backend AI Services)
```bash
mkdir -p backend/src/services
cd backend
# Start with document_parser.py
# Wait for Path 1 to define models
```

### For Agent 3 (Backend API Layer)
```bash
mkdir -p backend/src/api
cd backend
# Start with main.py and basic structure
# Integration comes after Paths 1 & 2
```

### For Agent 4 (Frontend Core)
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
# Start with project setup and types
```

### For Agent 5 (Frontend Templates)
```bash
cd frontend
# Wait for Path 4 to set up project structure
# Can start planning components immediately
```

### For Agent 6 (DevOps)
```bash
# Start with .env.example and basic Dockerfile
# Can work independently initially
```

---

## Notes

- Each path is designed to be 80% independent
- Mock data can be used until dependencies are ready
- Prioritize Path 1-3 (backend) and Path 4 (frontend core) first
- Path 5 and 6 can be done in parallel with others
- Regular communication prevents integration issues

