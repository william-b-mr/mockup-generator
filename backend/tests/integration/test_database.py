"""
Database integration tests.
These require a test database connection.
Mark as @pytest.mark.database and skip if DB not available.
"""

import pytest


@pytest.mark.asyncio
class TestDatabaseIntegration:
    """
    Integration tests with actual database.
    These tests require DATABASE_URL to be set to a test database.
    """
    
    async def test_create_and_retrieve_template(self, database_connection):
        """Test creating and retrieving a template from database"""
        
        from app.services.supabase_service import DatabaseService
        service = DatabaseService()
        
        # # Create template
        template_data = {
             'item_name': 'Test Item',
             'color': 'Test Color',
             'template_url': 'https://example.com/test.png',
             'logo_position_x': 100,
             'logo_position_y': 100,
             'logo_size': 'small'
        }
        created = await service.create_template(template_data)
        
        # Retrieve template
        retrieved = await service.get_template('Test Item', 'Test Color')
        
        # # Verify
        assert retrieved is not None
        assert retrieved['item_name'] == 'Test Item'
        
 
    
    async def test_job_lifecycle(self, database_connection):
        """Test complete job lifecycle in database"""
        pytest.skip("Requires test database - implement when DB is available")
        
        # Test: Create job -> Update status -> Retrieve job -> Verify
