"""
Unit tests for DatabaseService.
Tests database operations with mocked database connection.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.supabase_service import DatabaseService


@pytest.mark.unit
@pytest.mark.asyncio
class TestDatabaseService:
    """Test suite for DatabaseService"""
    
    @patch('app.services.supabase_service.db')
    async def test_get_template_found(self, mock_db, sample_template):
        """Test getting an existing template"""
        # Setup
        mock_db.fetch_one = AsyncMock(return_value=sample_template)
        service = DatabaseService()
        
        # Execute
        result = await service.get_template('Sweatshirt', 'Red')
        
        # Verify
        assert result is not None
        assert result['item_name'] == 'Sweatshirt'
        assert result['color'] == 'Red'
        mock_db.fetch_one.assert_called_once()
    
    @patch('app.services.supabase_service.db')
    async def test_get_template_not_found(self, mock_db):
        """Test getting a non-existent template"""
        # Setup
        mock_db.fetch_one = AsyncMock(return_value=None)
        service = DatabaseService()
        
        # Execute
        result = await service.get_template('NonExistent', 'Color')
        
        # Verify
        assert result is None
    
    @patch('app.services.supabase_service.db')
    async def test_create_job(self, mock_db, sample_job_data):
        """Test creating a new job"""
        # Setup
        mock_db.fetch_one = AsyncMock(return_value=sample_job_data)
        service = DatabaseService()
        
        # Execute
        result = await service.create_job(sample_job_data)
        
        # Verify
        assert result['id'] == sample_job_data['id']
        assert result['customer_name'] == 'Test Company'
        assert result['status'] == 'pending'
        mock_db.fetch_one.assert_called_once()
    
    @patch('app.services.supabase_service.db')
    async def test_update_job_status(self, mock_db, sample_job_id):
        """Test updating job status"""
        # Setup
        updated_job = {
            'id': sample_job_id,
            'status': 'completed',
            'progress': 100,
            'pdf_url': 'https://example.com/catalog.pdf'
        }
        mock_db.fetch_one = AsyncMock(return_value=updated_job)
        service = DatabaseService()
        
        # Execute
        result = await service.update_job_status(
            sample_job_id,
            'completed',
            pdf_url='https://example.com/catalog.pdf',
            progress=100
        )
        
        # Verify
        assert result['status'] == 'completed'
        assert result['progress'] == 100
        assert result['pdf_url'] == 'https://example.com/catalog.pdf'

