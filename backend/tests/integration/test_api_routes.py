"""
Integration tests for API routes.
Tests HTTP endpoints with mocked services.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.models.schemas import JobStatus


@pytest.mark.integration
class TestCatalogRoutes:
    """Test suite for /api/catalog routes"""
    
    @patch('app.api.routes.catalog.catalog_service')
    def test_generate_catalog_success(
        self, 
        mock_service, 
        client, 
        sample_catalog_request,
        sample_job_id
    ):
        """Test POST /api/catalog/generate returns job ID"""
        # Setup
        mock_service.create_catalog = AsyncMock(return_value={
            'job_id': sample_job_id,
            'status': JobStatus.PROCESSING.value,
            'message': 'Catalog generation started',
            'estimated_time_seconds': 120
        })
        
        # Execute
        response = client.post('/api/catalog/generate', json=sample_catalog_request)
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert 'job_id' in data
        assert data['status'] == 'processing'
    
    @patch('app.api.routes.catalog.catalog_service')
    def test_generate_catalog_invalid_request(self, mock_service, client):
        """Test POST /api/catalog/generate fails with invalid data"""
        # Setup - missing required fields
        invalid_request = {
            'customer_name': 'Test'
            # Missing other required fields
        }
        
        # Execute
        response = client.post('/api/catalog/generate', json=invalid_request)
        
        # Verify
        assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.integration
class TestJobRoutes:
    """Test suite for /api/jobs routes"""
    
    @patch('app.api.routes.jobs.catalog_service')
    def test_get_job_status_success(
        self, 
        mock_service, 
        client, 
        sample_job_data
    ):
        """Test GET /api/jobs/{job_id} returns job status"""
        # Setup
        mock_service.get_job_status = AsyncMock(return_value=sample_job_data)
        job_id = sample_job_data['id']
        
        # Execute
        response = client.get(f'/api/jobs/{job_id}')
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == job_id
        assert data['customer_name'] == 'Test Company'
    
    @patch('app.api.routes.jobs.catalog_service')
    def test_get_job_status_not_found(self, mock_service, client):
        """Test GET /api/jobs/{job_id} returns 404 for non-existent job"""
        # Setup
        mock_service.get_job_status = AsyncMock(
            side_effect=Exception('Job not found')
        )
        
        # Execute
        response = client.get('/api/jobs/non-existent-id')
        
        # Verify
        assert response.status_code == 404


@pytest.mark.integration
class TestTemplateRoutes:
    """Test suite for /api/templates routes"""
    
    @patch('app.api.routes.templates.supabase_service')
    def test_get_all_templates(self, mock_service, client, sample_template):
        """Test GET /api/templates returns all templates"""
        # Setup
        mock_service.get_all_templates = AsyncMock(return_value=[sample_template])
        
        # Execute
        response = client.get('/api/templates')
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    @patch('app.api.routes.templates.supabase_service')
    def test_get_specific_template(self, mock_service, client, sample_template):
        """Test GET /api/templates/{item}/{color} returns specific template"""
        # Setup
        mock_service.get_template = AsyncMock(return_value=sample_template)
        
        # Execute
        response = client.get('/api/templates/Sweatshirt/Red')
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data['item_name'] == 'Sweatshirt'
        assert data['color'] == 'Red'


@pytest.mark.integration
class TestHealthRoutes:
    """Test suite for health check routes"""
    
    def test_health_check(self, client):
        """Test GET /api/health returns healthy status"""
        # Execute
        response = client.get('/api/health')
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_readiness_check(self, client):
        """Test GET /api/ready returns ready status"""
        # Execute
        response = client.get('/api/ready')
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data['ready'] is True

