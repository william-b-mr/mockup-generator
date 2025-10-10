"""
Integration tests for complete workflow orchestration.
Tests multiple services working together.
"""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
@pytest.mark.asyncio
class TestWorkflowIntegration:
    """Test suite for workflow integration"""
    
    @patch('app.services.catalog_service.DatabaseService')
    @patch('app.services.catalog_service.StorageService')
    @patch('app.services.catalog_service.N8NService')
    async def test_complete_catalog_generation_flow(
        self,
        mock_n8n,
        mock_storage,
        mock_db,
        sample_catalog_request,
        sample_template,
        mock_n8n_logo_response,
        mock_n8n_page_response,
        mock_n8n_pdf_response
    ):
        """Test complete flow from request to PDF generation"""
        # Setup all mocks
        mock_db_instance = AsyncMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.create_job = AsyncMock(return_value={'id': 'job-123'})
        mock_db_instance.get_template = AsyncMock(return_value=sample_template)
        mock_db_instance.update_job_status = AsyncMock()
        
        mock_storage_instance = AsyncMock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.upload_file = AsyncMock(
            return_value='https://example.com/logo.png'
        )
        
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
        
        # Execute
        from app.services.catalog_service import CatalogService
        from app.models.schemas import CatalogRequest
        
        service = CatalogService()
        request = CatalogRequest(**sample_catalog_request)
        result = await service.create_catalog(request)
        
        # Verify
        assert 'job_id' in result
        assert result['status'] == 'processing'
        
        # Verify all steps were called
        mock_db_instance.create_job.assert_called_once()
        mock_storage_instance.upload_file.assert_called_once()
        mock_n8n_instance.process_logo.assert_called_once()

