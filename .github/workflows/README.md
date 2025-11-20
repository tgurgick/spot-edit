# CI/CD Workflows

This directory contains GitHub Actions workflows for automated testing and deployment.

## Workflows

### ci.yml - Continuous Integration

Runs on every push and pull request to `main`, `develop`, and `claude/*` branches.

**Jobs:**
1. **Backend Tests** - Linting, formatting, type checking, and pytest
2. **Frontend Tests** - Linting, type checking, and Vitest
3. **Backend Build** - Docker image build
4. **Frontend Build** - Docker image build
5. **Integration Tests** - Docker compose end-to-end tests
6. **Security Scan** - Trivy vulnerability scanning
7. **Notify** - Build status summary

**MVP Configuration:**
- Most checks are set to `continue-on-error: true` for MVP flexibility
- Tests requiring AI API keys are skipped with `-m "not ai"`
- Formatting and linting issues are non-blocking warnings
- Focus is on catching critical errors (syntax, imports, major bugs)

### deploy.yml - Deployment

Manual or tag-triggered deployment workflow (currently placeholder).

## Running Tests Locally

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests (skip AI tests)
pytest tests/ -v -m "not ai"

# Run all tests (requires API keys)
export OPENAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key
pytest tests/ -v

# Linting
flake8 src
black --check src
mypy src --ignore-missing-imports
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run tests
npm test

# Linting
npm run lint
npm run type-check
```

### Docker Build

```bash
# Backend
docker build -t spot-edit-backend ./backend

# Frontend
docker build -t spot-edit-frontend ./frontend

# Full stack
docker-compose up --build
```

## Environment Variables

Tests require these environment variables:

```bash
OPENAI_API_KEY=test-key-for-ci
ANTHROPIC_API_KEY=test-key-for-ci
STORAGE_PATH=./storage
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

**Tests failing locally but not in CI:**
- Check Python/Node versions match (Python 3.11, Node 20)
- Ensure dependencies are up to date (`pip install -r requirements.txt`, `npm ci`)
- Check environment variables are set

**CI always failing:**
- Check the workflow logs in GitHub Actions tab
- Ensure all required files exist (package-lock.json, etc.)
- Verify Docker builds succeed locally first

**Security scan failures:**
- Trivy scans for CRITICAL and HIGH vulnerabilities only
- Update dependencies to resolve vulnerabilities
- Use `npm audit fix` or `pip-audit` to check locally

## Future Improvements

Once the MVP is stable:
1. Make formatting and linting checks blocking
2. Add more comprehensive integration tests
3. Enable full test suite (including AI tests with secrets)
4. Add deployment automation
5. Set up code coverage thresholds
6. Add performance testing
