"""
Unit tests for CatalogService.
Tests business logic in isolation using mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.catalog_service import CatalogService
from app.models.schemas import CatalogRequest, JobStatus
from app.core.exceptions import TemplateNotFoundException, LogoProcessingException


@pytest.mark.unit
@pytest.mark.asyncio
class TestCatalogService:
    """Test suite for CatalogService"""
    
    async def test_estimate_processing_time(self):
        """Test that processing time is estimated correctly"""
        service = CatalogService()
        
        # 1 page should take ~40 seconds (10 * 1 + 30)
        time_1_page = service._estimate_processing_time(1)
        assert time_1_page == 40
        
        # 10 pages should take ~130 seconds (10 * 10 + 30)
        time_10_pages = service._estimate_processing_time(10)
        assert time_10_pages == 130
    
    @patch('app.services.catalog_service.DatabaseService')
    @patch('app.services.catalog_service.StorageService')
    @patch('app.services.catalog_service.N8NService')
    async def test_validate_templates_success(
        self, 
        mock_n8n, 
        mock_storage, 
        mock_db
    ):
        """Test template validation succeeds when all templates exist"""
        # Setup
        service = CatalogService()
        service.db = AsyncMock()
        service.db.get_template.return_value = {'id': 'test', 'item_name': 'Sweatshirt'}
        
        # Execute - should not raise exception
        await service._validate_templates(['Sweatshirt'], ['Red'])
        
        # Verify
        service.db.get_template.assert_called_once_with('Sweatshirt', 'Red')
    
    @patch('app.services.catalog_service.DatabaseService')
    @patch('app.services.catalog_service.StorageService')
    @patch('app.services.catalog_service.N8NService')
    async def test_validate_templates_missing(
        self, 
        mock_n8n, 
        mock_storage, 
        mock_db
    ):
        """Test template validation fails when template is missing"""
        # Setup
        service = CatalogService()
        service.db = AsyncMock()
        service.db.get_template.return_value = None  # Template not found
        
        # Execute & Assert
        with pytest.raises(TemplateNotFoundException) as exc_info:
            await service._validate_templates(['T-Shirt'], ['Purple'])
        
        assert 'T-Shirt' in str(exc_info.value.message)
        assert 'Purple' in str(exc_info.value.message)
    
    @patch('app.services.catalog_service.DatabaseService')
    @patch('app.services.catalog_service.StorageService')
    @patch('app.services.catalog_service.N8NService')
    async def test_upload_logos_success(
        self, 
        mock_n8n, 
        mock_storage, 
        mock_db
    ):
        """Test dual logos upload succeeds with valid base64 data"""
        # Setup
        service = CatalogService()
        service.storage = AsyncMock()
        service.storage.upload_file.side_effect = [
            'https://example.com/logo_dark.png',
            'https://example.com/logo_light.png'
        ]
        
        job_id = 'test-job-id'
        # Valid 1x1 PNG in base64
        logo_data = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        
        # Execute
        logo_dark_url, logo_light_url = await service._upload_logos(job_id, logo_data, logo_data)
        
        # Verify
        assert logo_dark_url == 'https://example.com/logo_dark.png'
        assert logo_light_url == 'https://example.com/logo_light.png'
        assert service.storage.upload_file.call_count == 2
        
        # Check file paths
        call_args = service.storage.upload_file.call_args_list
        assert call_args[0][0][0] == f'logos/{job_id}/logo_fundo_escuro.png'
        assert call_args[1][0][0] == f'logos/{job_id}/logo_fundo_claro.png'
    
    @patch('app.services.catalog_service.DatabaseService')
    @patch('app.services.catalog_service.StorageService')
    @patch('app.services.catalog_service.N8NService')
    async def test_upload_logos_invalid_base64(
        self, 
        mock_n8n, 
        mock_storage, 
        mock_db
    ):
        """Test dual logos upload fails with invalid base64 data"""
        # Setup
        service = CatalogService()
        service.storage = AsyncMock()
        
        job_id = 'test-job-id'
        invalid_logo = 'not-valid-base64!!!'
        valid_logo = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        
        # Execute & Assert
        with pytest.raises(LogoProcessingException):
            await service._upload_logos(job_id, invalid_logo, valid_logo)
