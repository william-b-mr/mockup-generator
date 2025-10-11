import pytest
from app.services.pdf_service import PDFService
from PIL import Image
import io

@pytest.mark.unit
@pytest.mark.asyncio
class TestPDFService:
    
    async def test_generate_front_page(self):
        """Test front page generation"""
        service = PDFService()
        
        pdf_bytes = await service.generate_front_page(
            customer_name="Test Company",
            industry="Testing"
        )
        
        # Verify it's a valid PDF
        assert pdf_bytes[:4] == b'%PDF'
        assert len(pdf_bytes) > 1000  # Should have some content
    
    async def test_convert_image_to_pdf(self):
        """Test image to PDF conversion"""
        service = PDFService()
        
        # Create test image
        img = Image.new('RGB', (800, 600), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Convert to PDF
        pdf_bytes = await service.convert_image_to_pdf(img_bytes)
        
        # Verify
        assert pdf_bytes[:4] == b'%PDF'
        assert len(pdf_bytes) > 0
    
    async def test_merge_pdfs(self):
        """Test PDF merging"""
        service = PDFService()
        
        # Create 2 test PDFs
        pdf1 = await service.generate_front_page("Company 1", "Industry 1")
        pdf2 = await service.generate_front_page("Company 2", "Industry 2")
        
        # Merge
        merged = await service.merge_pdfs([pdf1, pdf2])
        
        # Verify
        assert merged[:4] == b'%PDF'
        assert len(merged) > len(pdf1)  # Should be larger
    
    async def test_convert_rgba_image(self):
        """Test converting PNG with transparency"""
        service = PDFService()
        
        # Create RGBA image
        img = Image.new('RGBA', (800, 600), color=(255, 0, 0, 128))
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        # Should not raise error
        pdf_bytes = await service.convert_image_to_pdf(img_bytes)
        assert pdf_bytes[:4] == b'%PDF'