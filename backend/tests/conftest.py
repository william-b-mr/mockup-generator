
"""
This file contains pytest fixtures that are shared across all tests.
Fixtures provide reusable test data and setup/teardown logic.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from typing import Dict, Any
import uuid

from app.main import app
from app.core.database import db
from app.services.supabase_service import DatabaseService, StorageService
from app.services.n8n_service import N8NService
from app.models.schemas import (
    N8NLogoProcessingResponse,
    N8NPageGeneratorResponse
)

# ===== HTTP CLIENT FIXTURES =====

@pytest.fixture
def client():
    """
    FastAPI test client for making HTTP requests to the API.
    Use this for testing API endpoints without running a real server.
    """
    return TestClient(app)


# ===== SAMPLE DATA FIXTURES =====

@pytest.fixture
def sample_job_id() -> str:
    """Generate a sample job ID"""
    return str(uuid.uuid4())


@pytest.fixture
def sample_catalog_request() -> Dict[str, Any]:
    """
    Sample catalog request payload for testing.
    Contains all required fields with valid test data.
    """
    return {
        'customer_name': 'Test Company',
        'industry': 'Construction',
        # 1x1 transparent PNG in base64
        'logo': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        'items': ['Sweatshirt', 'T-Shirt'],
        'colors': ['Red', 'Blue']
    }


@pytest.fixture
def sample_template() -> Dict[str, Any]:
    """Sample template data"""
    return {
        'id': str(uuid.uuid4()),
        'item_name': 'Sweatshirt',
        'color': 'Red',
        'template_url': 'https://example.com/template.png',
        'logo_position_x': 150,
        'logo_position_y': 200,
        'logo_size': 'large',
        'created_at': '2025-10-09T10:00:00Z',
        'updated_at': '2025-10-09T10:00:00Z'
    }


@pytest.fixture
def sample_job_data(sample_job_id: str) -> Dict[str, Any]:
    """Sample job data"""
    return {
        'id': sample_job_id,
        'customer_name': 'Test Company',
        'industry': 'Construction',
        'status': 'pending',
        'progress': 0,
        'pdf_url': None,
        'error_message': None,
        'metadata': {
            'items': ['Sweatshirt', 'T-Shirt'],
            'colors': ['Red', 'Blue'],
            'total_pages': 4
        },
        'created_at': '2025-10-09T10:00:00Z',
        'updated_at': '2025-10-09T10:00:00Z'
    }


# ===== MOCK SERVICE FIXTURES =====

@pytest.fixture
def mock_database_service():
    """
    Mock DatabaseService to avoid actual database calls in unit tests.
    Returns an AsyncMock that can be configured for specific test cases.
    """
    mock = AsyncMock(spec=DatabaseService)
    return mock


@pytest.fixture
def mock_storage_service():
    """Mock StorageService to avoid actual file uploads in unit tests"""
    mock = AsyncMock(spec=StorageService)
    return mock


@pytest.fixture
def mock_n8n_service():
    """Mock N8NService to avoid actual n8n webhook calls in unit tests"""
    mock = AsyncMock(spec=N8NService)
    return mock


# ===== N8N RESPONSE FIXTURES =====

@pytest.fixture
def mock_n8n_logo_response(sample_job_id: str) -> N8NLogoProcessingResponse:
    """Mock successful logo processing response from n8n"""
    return N8NLogoProcessingResponse(
        job_id=sample_job_id,
        logo_large_url='https://example.com/logos/large.png',
        logo_small_url='https://example.com/logos/small.png',
        success=True
    )


@pytest.fixture
def mock_n8n_page_response(sample_job_id: str) -> N8NPageGeneratorResponse:
    """Mock successful page generation response from n8n"""
    return N8NPageGeneratorResponse(
        job_id=sample_job_id,
        page_url='https://example.com/pages/sweatshirt_red.png',
        item='Sweatshirt',
        color='Red',
        success=True
    )






# ===== DATABASE FIXTURES (for integration tests) =====

@pytest.fixture
async def database_connection():
    """
    Real database connection for integration tests.
    Sets up and tears down test database.
    """
    # Setup: Connect to database
    await db.connect()
    
    yield db
    
    # Teardown: Clean up and disconnect
    # In production, you might want to clean test data here
    await db.disconnect()


# ===== EVENT LOOP FIXTURE =====

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for async tests.
    Required for pytest-asyncio.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
