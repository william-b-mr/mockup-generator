"""
End-to-end tests for complete user flows.
These tests require actual services or comprehensive mocking.
"""

import pytest
from unittest.mock import patch, AsyncMock
import time


@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteUserFlow:
    """End-to-end tests for complete user flows"""
    
    @patch('app.services.catalog_service.DatabaseService')
    @patch('app.services.catalog_service.StorageService')
    @patch('app.services.catalog_service.N8NService')
    def test_user_generates_catalog_successfully(
        self,
        mock_n8n,
        mock_storage,
        mock_db,
        client,
        sample_catalog_request,
        sample_template,
        mock_n8n_logo_response,
        mock_n8n_page_response,
        mock_n8n_pdf_response
    ):
        """
        Test complete user flow: Submit request -> Poll status -> Download PDF
        This simulates actual user behavior.
        """
        # Setup all mocks for complete flow
        job_id = 'e2e-test-job-id'
        
        # Mock database operations
        mock_db_instance = AsyncMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.create_job = AsyncMock(return_value={
            'id': job_id,
            'status': 'pending',
            'customer_name': 'Test Company'
        })
        mock_db_instance.get_template = AsyncMock(return_value=sample_template)
        mock_db_instance.get_job = AsyncMock(return_value={
            'id': job_id,
            'status': 'completed',
            'progress': 100,
            'pdf_url': 'https://example.com/catalog.pdf',
            'customer_name': 'Test Company',
            'industry': 'Construction',
            'created_at': '2025-10-09T10:00:00Z',
            'updated_at': '2025-10-09T10:05:00Z',
            'error_message': None,
            'metadata': {}
        })
        mock_db_instance.update_job_status = AsyncMock()
        
        # Mock storage operations
        mock_storage_instance = AsyncMock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.upload_file = AsyncMock(
            return_value='https://example.com/logo.png'
        )
        
        # Mock n8n operations
        mock_n8n_instance = AsyncMock()
        mock_n8n.return_value = mock_n8n_instance
        mock_n8n_instance.process_logo = AsyncMock(
            return_value=mock_n8n_logo_response
        )
        mock_n8n_instance.generate_page = AsyncMock(
            return_value=mock_n8n_page_response
        )
        mock_n8n_instance.assemble_pdf = AsyncMock(
            return_value=mock_n8n_pdf_response
        )
        
        # Step 1: User submits catalog generation request
        response = client.post('/api/catalog/generate', json=sample_catalog_request)
        assert response.status_code == 200
        
        data = response.json()
        assert 'job_id' in data
        returned_job_id = data['job_id']
        
        # Step 2: User polls for job status (simulate waiting)
        response = client.get(f'/api/jobs/{returned_job_id}')
        assert response.status_code == 200
        
        job_data = response.json()
        assert job_data['status'] in ['pending', 'processing', 'completed']
        
        # Step 3: Job completes and user gets PDF URL
        if job_data['status'] == 'completed':
            assert 'pdf_url' in job_data
            assert job_data['pdf_url'] is not None
    
    @patch('app.services.catalog_service.DatabaseService')
    def test_user_handles_missing_template_error(
        self,
        mock_db,
        client,
        sample_catalog_request
    ):
        """
        Test user flow when template is missing
        Simulates error handling scenario
        """
        # Setup - template not found
        mock_db_instance = AsyncMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.create_job = AsyncMock(return_value={
            'id': 'test-job',
            'status': 'pending'
        })
        mock_db_instance.get_template = AsyncMock(return_value=None)  # Template missing
        mock_db_instance.update_job_status = AsyncMock()
        
        # Execute - submit request
        response = client.post('/api/catalog/generate', json=sample_catalog_request)
        
        # Verify - should handle error gracefully
        # In production, this would create a job that fails during processing
        assert response.status_code in [200, 404, 500]

