"""
Unit tests for input validators.
Tests validation logic for request data.
"""

import pytest
from pydantic import ValidationError
from app.models.schemas import CatalogRequest, TemplateCreate


@pytest.mark.unit
class TestValidators:
    """Test suite for input validation"""
    
    def test_catalog_request_valid(self, sample_catalog_request):
        """Test valid catalog request passes validation"""
        # Execute
        request = CatalogRequest(**sample_catalog_request)
        
        # Verify
        assert request.customer_name == 'Test Company'
        assert len(request.items) == 2
        assert len(request.colors) == 2
    
    def test_catalog_request_missing_customer_name(self, sample_catalog_request):
        """Test catalog request fails without customer name"""
        # Setup
        invalid_request = sample_catalog_request.copy()
        del invalid_request['customer_name']
        
        # Execute & Assert
        with pytest.raises(ValidationError) as exc_info:
            CatalogRequest(**invalid_request)
        
        assert 'customer_name' in str(exc_info.value)
    
    def test_catalog_request_empty_items(self, sample_catalog_request):
        """Test catalog request fails with empty items list"""
        # Setup
        invalid_request = sample_catalog_request.copy()
        invalid_request['items'] = []
        
        # Execute & Assert
        with pytest.raises(ValidationError) as exc_info:
            CatalogRequest(**invalid_request)
        
        assert 'items' in str(exc_info.value)
    
    def test_catalog_request_strips_whitespace(self):
        """Test that whitespace is stripped from string fields"""
        # Setup
        request_data = {
            'customer_name': '  Test Company  ',
            'industry': '  Construction  ',
            'logo_dark': 'base64data',
            'logo_light': 'base64data',
            'items': ['  Sweatshirt  ', '  T-Shirt  '],
            'colors': ['  Red  ', '  Blue  ']
        }
        
        # Execute
        request = CatalogRequest(**request_data)
        
        # Verify whitespace is stripped
        assert request.customer_name == 'Test Company'
        assert request.industry == 'Construction'
        assert 'Sweatshirt' in request.items
        assert 'Red' in request.colors
    
    def test_template_create_valid(self):
        """Test valid template creation"""
        # Setup
        template_data = {
            'item_name': 'Sweatshirt',
            'color': 'Red',
            'template_url': 'https://example.com/template.png',
            'logo_position_x': 150,
            'logo_position_y': 200,
            'logo_size': 'large'
        }
        
        # Execute
        template = TemplateCreate(**template_data)
        
        # Verify
        assert template.item_name == 'Sweatshirt'
        assert template.logo_size == 'large'

