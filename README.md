# Spot Edit

A simple, lean AI-powered document editing tool that identifies and updates key fields in documents through natural language chat. Save document templates once, reuse them repeatedly.

## Overview

Spot Edit is a focused document editing assistant built around a straightforward workflow: upload a document, confirm the fields AI detects, save it as a template, then reuse it anytime by telling the AI what needs to change in plain English. The approach is designed to be simple, repeatable, and effective.

## Core Concept

The project centers on four key principles:

1. **Simple & Lean**: Minimal interface, maximum utility. No bloat, just effective document editing.
2. **Smart Field Detection**: Upload any document (with automatic text conversion if needed), and the AI identifies key fields and areas that need updating.
3. **Human-in-the-Loop**: You confirm which fields the AI detects before they become editable—ensuring accuracy and control.
4. **Template Reuse**: Save documents with their field mappings once, then reuse them repeatedly with natural language updates.

## How It Works

### Initial Document Setup
1. **Upload Document**: Drop your document into the chat window (supports various formats with automatic text conversion)
2. **AI Field Detection**: The AI automatically analyzes the document and identifies key editable fields (names, dates, prices, company info, etc.)
3. **Confirm Fields (HITL)**: Review and confirm which fields the AI found are the ones you want to make editable—this human-in-the-loop step ensures accuracy
4. **Save Template**: Once confirmed, the document and its identified variable fields are saved for future reuse

### Making Updates
1. **Load Saved Document**: Pull up any previously saved document template
2. **Tell the Agent**: Describe your changes in natural language (e.g., "update the contract date to March 15, 2024" or "change client name to Acme Corp")
3. **AI Updates Fields**: The agent intelligently updates the confirmed fields throughout the document
4. **Download**: Export your updated document with all changes applied

## Key Features

- **Document Upload & Conversion**: Accept various document formats, automatically convert to text for processing
- **AI-Powered Field Detection**: Automatically identifies key editable fields (names, dates, prices, addresses, etc.)
- **Human-in-the-Loop Confirmation**: Review and confirm AI-detected fields before saving—you stay in control
- **Document Templates & Storage**: Save documents with their confirmed field mappings for easy reuse
- **Natural Language Commands**: No complex syntax—just tell the agent what you want in plain English
- **Multi-Field Updates**: Update multiple related fields across the document in one operation
- **Template Library**: Access and reuse your saved document templates anytime
- **Export & Download**: Get your updated documents in the original format

## Design Philosophy

- **Simplicity First**: Every feature must earn its place. If it doesn't directly serve the core workflow, it doesn't belong.
- **Reliable & Repeatable**: The same input should produce predictable, consistent results.
- **Focused Scope**: Do one thing exceptionally well—AI-assisted document field updates.

## Use Cases

- **Contract Management**: Upload a contract template once, then quickly generate new versions by updating client names, dates, and terms
- **Invoice Generation**: Save an invoice template and update amounts, dates, and client details for each new invoice
- **Proposal Customization**: Maintain proposal templates and customize company names, project details, and pricing per client
- **Form Processing**: Identify form fields once, then rapidly fill different versions with updated information
- **Report Updates**: Save report templates and update key metrics, dates, and data points as needed
- **Document Localization**: Update addresses, currencies, and region-specific information across document sets

## Technology Approach

The technical stack will be chosen to support the core goals of simplicity and repeatability:
- Lightweight document parsing and text extraction
- LLM integration for natural language understanding and field identification
- Simple storage system for document templates and field mappings
- Intuitive UI for document upload, field confirmation, and chat interaction
- Minimal dependencies, maximum reliability

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended for easiest setup)
  - Docker: [Install Docker](https://docs.docker.com/get-docker/)
  - Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

**OR** for local development without Docker:

- **Backend**:
  - Python 3.11 or higher
  - pip (Python package manager)

- **Frontend**:
  - Node.js 20 or higher
  - npm or yarn

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/spot-edit.git
   cd spot-edit
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start the application**
   ```bash
   docker-compose up
   ```

4. **Access the application**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Setup with Docker

For development with hot-reload:

```bash
# Start with development profile
docker-compose --profile dev up

# Frontend dev server: http://localhost:5173
# Backend API: http://localhost:8000
```

### Local Development (Without Docker)

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp ../.env.example ../.env
   # Edit .env with your API keys
   ```

5. **Run the backend**
   ```bash
   cd src
   python main.py
   # Or use uvicorn directly:
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   echo "VITE_API_URL=http://localhost:8000" > .env.local
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000

### Environment Configuration

Key environment variables (see `.env.example` for full list):

```bash
# AI Provider (choose one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai  # or "anthropic"

# Backend
PORT=8000
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:80

# Frontend
VITE_API_URL=http://localhost:8000
```

### Running Tests

#### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run tests by marker
pytest -m unit
pytest -m integration
```

#### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Building for Production

#### Using Docker

```bash
# Build and run production containers
docker-compose up --build

# Frontend will be available at http://localhost:80
# Backend will be available at http://localhost:8000
```

#### Manual Build

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve the dist/ directory with your preferred web server
```

### Project Structure

```
spot-edit/
├── backend/                 # FastAPI backend
│   ├── src/                # Source code
│   │   ├── api/           # API routes
│   │   ├── services/      # Business logic
│   │   ├── storage/       # Data persistence
│   │   ├── models/        # Data models
│   │   └── main.py        # App entry point
│   ├── tests/             # Backend tests
│   ├── Dockerfile         # Production container
│   └── requirements.txt   # Python dependencies
├── frontend/               # React frontend
│   ├── src/               # Source code
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── api/          # API client
│   │   ├── types/        # TypeScript types
│   │   └── store/        # State management
│   ├── Dockerfile        # Production container
│   ├── Dockerfile.dev    # Development container
│   └── package.json      # Node dependencies
├── storage/               # File storage
│   ├── templates/        # Saved templates
│   └── uploads/          # Temporary uploads
├── docs/                  # Documentation
│   ├── API.md            # API documentation
│   └── ARCHITECTURE.md   # System architecture
├── docker-compose.yml    # Docker orchestration
├── .env.example          # Environment template
└── README.md             # This file
```

### Development Workflow

1. **Start the development environment**
   ```bash
   docker-compose --profile dev up
   ```

2. **Make your changes**
   - Edit files in `backend/src/` or `frontend/src/`
   - Changes will auto-reload

3. **Run tests**
   ```bash
   # Backend
   docker-compose exec backend pytest

   # Frontend
   docker-compose exec frontend-dev npm test
   ```

4. **Lint and type-check**
   ```bash
   # Backend
   cd backend
   black src/
   flake8 src/
   mypy src/

   # Frontend
   cd frontend
   npm run lint
   npm run type-check
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   git push
   ```

### Troubleshooting

**Port already in use:**
```bash
# Change ports in docker-compose.yml or stop conflicting services
docker-compose down
lsof -ti:8000 | xargs kill  # Kill process on port 8000
```

**Container build issues:**
```bash
# Rebuild without cache
docker-compose build --no-cache
```

**Permission issues with storage directory:**
```bash
chmod -R 755 storage/
```

**API not responding:**
- Check that `.env` file has correct API keys
- Check Docker logs: `docker-compose logs backend`
- Verify health endpoint: `curl http://localhost:8000/health`

### Documentation

- **[API Documentation](docs/API.md)** - Complete API reference
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and architecture
- **[Project Structure](PROJECT_STRUCTURE.md)** - Detailed file organization
- **[Development Paths](PARALLEL_DEVELOPMENT_PATHS.md)** - Development workflow

### Interactive API Documentation

When the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contributing

*Contribution guidelines will be added as the project matures.*

## License

*License to be determined.*
