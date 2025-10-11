"""
Unit tests for N8NService.
Tests n8n webhook calls with mocked HTTP responses.
"""

import pytest
from unittest.mock import AsyncMock, patch
import httpx
from app.services.n8n_service import N8NService
from app.models.schemas import (
    N8NLogoProcessingPayload,
    N8NPageGeneratorPayload
)
from app.core.exceptions import N8NWorkflowException


@pytest.mark.unit
@pytest.mark.asyncio
class TestN8NService:
    """Test suite for N8NService"""
    
    @patch('httpx.AsyncClient')
    async def test_process_logo_success(
        self, 
        mock_client, 
        sample_job_id,
        mock_n8n_logo_response
    ):
        """Test successful logo processing workflow call"""
        # Setup
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_n8n_logo_response.dict()
        mock_response.raise_for_status = MagicMock()
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        service = N8NService()
        payload = N8NLogoProcessingPayload(
            job_id=sample_job_id,
            logo_url='https://example.com/logo.png'
        )
        
        # Execute
        result = await service.process_logo(payload)
        
        # Verify
        assert result.success is True
        assert result.job_id == sample_job_id
        assert 'large.png' in result.logo_large_url
        assert 'small.png' in result.logo_small_url
    
    @patch('httpx.AsyncClient')
    async def test_process_logo_timeout(self, mock_client, sample_job_id):
        """Test logo processing fails on timeout"""
        # Setup
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            side_effect=httpx.TimeoutException("Request timeout")
        )
        
        service = N8NService()
        payload = N8NLogoProcessingPayload(
            job_id=sample_job_id,
            logo_url='https://example.com/logo.png'
        )
        
        # Execute & Assert
        with pytest.raises(N8NWorkflowException) as exc_info:
            await service.process_logo(payload)
        
        assert 'timeout' in str(exc_info.value.detail).lower()
    
    @patch('httpx.AsyncClient')
    async def test_generate_page_success(
        self, 
        mock_client,
        sample_job_id,
        mock_n8n_page_response
    ):
        """Test successful page generation workflow call"""
        # Setup
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_n8n_page_response.dict()
        mock_response.raise_for_status = MagicMock()
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        service = N8NService()
        payload = N8NPageGeneratorPayload(
            job_id=sample_job_id,
            item='Sweatshirt',
            color='Red',
            logo_large_url='https://example.com/large.png',
            logo_small_url='https://example.com/small.png'
        )
        
        # Execute
        result = await service.generate_page(payload)
        
        # Verify
        assert result.success is True
        assert result.item == 'Sweatshirt'
        assert result.color == 'Red'

