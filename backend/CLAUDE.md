# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- Run all tests: `pytest`
- Run specific test categories using markers:
  - Unit tests: `pytest -m unit`
  - Integration tests: `pytest -m integration` 
  - End-to-end tests: `pytest -m e2e`
  - Performance tests: `pytest -m performance`
  - Database tests: `pytest -m database`
  - External API tests: `pytest -m external`
- Run single test file: `pytest tests/units/test_catalog_service.py`
- Coverage is automatically generated to `htmlcov/` directory

### Development Server
- Start FastAPI server: `uvicorn app.main:app --reload --port 8000`
- API documentation available at `/api/docs` and `/api/redoc`

### Environment Setup
- Install dependencies: `pip install -r requirements.txt`
- Configure environment variables in `.env` file (see config.py for required variables)

## Architecture Overview

This is a FastAPI-based backend for a catalog/mockup generation service that orchestrates workflows through n8n webhooks and uses Supabase for file storage with direct PostgreSQL database connections.

### Core Components

**Database Layer (`app/core/database.py`)**
- Uses asyncpg for direct PostgreSQL connections (not Supabase SDK)
- Connection pooling with min_size=5, max_size=20
- Global `db` instance provides `fetch_one`, `fetch_all`, `execute`, `execute_many` methods

**Configuration (`app/core/config.py`)**
- Pydantic-based settings with environment variable loading
- Separate configurations for direct DB connection, Supabase storage, n8n webhooks, and Redis
- Database URL construction via `database_url` property

**API Structure (`app/api/routes/`)**
- RESTful endpoints for catalog generation, job status, templates, and health checks
- Background task processing for async catalog generation workflows

**Service Layer (`app/services/`)**
- `CatalogService`: Main orchestration service for catalog generation workflow
- `N8NService`: Handles webhook calls to n8n workflows for logo processing, page generation, and PDF assembly
- `SupabaseService`: Manages file uploads to Supabase storage bucket

### Workflow Architecture

The catalog generation follows this sequence:
1. Client uploads logo and catalog parameters via `/api/catalog/generate`
2. Logo uploaded to Supabase storage, job record created in PostgreSQL
3. Three-stage n8n webhook workflow:
   - Logo processing (resize to large/small versions)
   - Page generation (create mockup pages for each item/color combination)  
   - PDF assembly (combine pages into final catalog PDF)
4. Job status polling via `/api/jobs/{job_id}` until completion

### Data Models (`app/models/schemas.py`)

Key schemas:
- `CatalogRequest`: Input validation for catalog generation
- `JobStatusResponse`: Job tracking with progress percentage and PDF URL
- `N8N*Payload/Response`: Structured data for webhook communications
- `JobStatus` enum: PENDING → PROCESSING → COMPLETED/FAILED

### External Integrations

- **n8n**: Three webhook endpoints for workflow orchestration
- **Supabase Storage**: File upload/storage only (not using Supabase DB features)
- **PostgreSQL**: Direct asyncpg connection for all database operations
- **Redis**: Configured but usage depends on implementation needs

### Testing Structure

Well-organized test suite with pytest markers:
- `tests/units/`: Fast, isolated component tests
- `tests/integration/`: Multi-component integration tests  
- `tests/e2e/`: Complete user flow tests
- `tests/performance/`: Load and performance testing
- Coverage reporting enabled with HTML output