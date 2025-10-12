from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfMerger, PdfReader, PdfWriter
import io
import httpx
from typing import List, BinaryIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """Handle all PDF generation operations"""
    
    def __init__(self):
        self.page_size = A4  # (595, 842) points
    
    async def generate_front_page(
        self, 
        customer_name: str, 
        industry: str
    ) -> bytes:
        """
        Generate a beautiful front page PDF
        
        Args:
            customer_name: Customer name for the front page
            industry: Industry for the front page
            
        Returns:
            PDF bytes
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=self.page_size)
            width, height = self.page_size
            
            # Background gradient (simulated with rectangles)
            # Purple gradient: #667eea to #764ba2
            for i in range(100):
                # Create gradient effect
                r = int(102 + (118 - 102) * i / 100)  # 102 -> 118
                g = int(126 + (75 - 126) * i / 100)   # 126 -> 75
                b = int(234 + (162 - 234) * i / 100)  # 234 -> 162
                
                c.setFillColorRGB(r/255, g/255, b/255)
                c.rect(0, height - (height * i / 100), width, height / 100, 
                       stroke=0, fill=1)
            
            # White text
            c.setFillColorRGB(1, 1, 1)
            
            # Title: "PRODUCT CATALOG"
            c.setFont("Helvetica", 16)
            text_width = c.stringWidth("PRODUCT CATALOG", "Helvetica", 16)
            c.drawString((width - text_width) / 2, height - 200, "PRODUCT CATALOG")
            
            # Divider line
            c.setStrokeColorRGB(1, 1, 1)
            c.setLineWidth(2)
            c.line(width/2 - 100, height - 220, width/2 + 100, height - 220)
            
            # Customer Name (large)
            c.setFont("Helvetica-Bold", 48)
            text_width = c.stringWidth(customer_name, "Helvetica-Bold", 48)
            c.drawString((width - text_width) / 2, height - 300, customer_name)
            
            # Industry
            c.setFont("Helvetica", 24)
            text_width = c.stringWidth(industry, "Helvetica", 24)
            c.drawString((width - text_width) / 2, height - 350, industry)
            
            # Divider line
            c.line(width/2 - 100, height - 380, width/2 + 100, height - 380)
            
            # Date
            current_date = datetime.now().strftime("%B %d, %Y")
            c.setFont("Helvetica", 14)
            text_width = c.stringWidth(current_date, "Helvetica", 14)
            c.drawString((width - text_width) / 2, height - 500, current_date)
            
            # Save PDF
            c.save()
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Front page generated for {customer_name}")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating front page: {e}")
            raise
    
    async def download_image(self, url: str) -> bytes:
        """
        Download image from URL
        
        Args:
            url: Image URL
            
        Returns:
            Image bytes
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            raise
    
    async def convert_image_to_pdf(
        self, 
        image_data: bytes,
        fit_to_page: bool = True
    ) -> bytes:
        """
        Convert image to PDF page
        
        Args:
            image_data: Image bytes
            fit_to_page: Whether to fit image to page size
            
        Returns:
            PDF bytes
        """
        try:
            # Open image
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            if fit_to_page:
                # Create PDF with image fitted to A4 page
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=self.page_size)
                width, height = self.page_size
                
                # Get image dimensions
                img_width, img_height = img.size
                
                # Calculate scaling to fit page with margins
                margin = 20  # 20 points margin
                available_width = width - (2 * margin)
                available_height = height - (2 * margin)
                
                scale = min(
                    available_width / img_width,
                    available_height / img_height
                )
                
                # Calculate position to center
                scaled_width = img_width * scale
                scaled_height = img_height * scale
                x = (width - scaled_width) / 2
                y = (height - scaled_height) / 2
                
                # Draw image
                img_reader = ImageReader(img)
                c.drawImage(
                    img_reader, 
                    x, y, 
                    width=scaled_width, 
                    height=scaled_height
                )
                
                c.save()
                pdf_bytes = buffer.getvalue()
                buffer.close()
            else:
                # Direct image to PDF conversion (faster)
                import img2pdf
                pdf_bytes = img2pdf.convert(image_data)
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error converting image to PDF: {e}")
            raise
    
    async def merge_pdfs(
        self, 
        pdf_list: List[bytes],
        metadata: dict = None
    ) -> bytes:
        """
        Merge multiple PDFs into one
        
        Args:
            pdf_list: List of PDF bytes to merge
            metadata: Optional metadata to add to PDF
            
        Returns:
            Merged PDF bytes
        """
        try:
            merger = PdfMerger()
            
            # Add each PDF
            for pdf_bytes in pdf_list:
                merger.append(io.BytesIO(pdf_bytes))
            
            # Write to buffer
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            
            # Add metadata if provided
            if metadata:
                output_buffer.seek(0)
                reader = PdfReader(output_buffer)
                writer = PdfWriter()
                
                # Copy all pages
                for page in reader.pages:
                    writer.add_page(page)
                
                # Add metadata
                writer.add_metadata({
                    '/Title': metadata.get('title', 'Catalog'),
                    '/Author': metadata.get('author', 'Catalog Generator'),
                    '/Subject': metadata.get('subject', 'Product Catalog'),
                    '/Creator': 'Catalog Generator System',
                    '/Producer': 'FastAPI + ReportLab',
                })
                
                # Write with metadata
                final_buffer = io.BytesIO()
                writer.write(final_buffer)
                final_buffer.seek(0)
                pdf_bytes = final_buffer.read()
            else:
                output_buffer.seek(0)
                pdf_bytes = output_buffer.read()
            
            merger.close()
            
            logger.info(f"Merged {len(pdf_list)} PDFs")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            raise
    
    async def generate_complete_catalog(
        self,
        customer_name: str,
        industry: str,
        page_image_urls: List[str],
        job_id: str
    ) -> bytes:
        """
        Generate complete catalog PDF
        
        Args:
            customer_name: Customer name
            industry: Industry
            page_image_urls: List of URLs to page images
            job_id: Job ID for metadata
            
        Returns:
            Complete catalog PDF bytes
        """
        try:
            pdfs = []
            
            # 1. Generate front page
            logger.info(f"[Job {job_id}] Generating front page...")
            front_page = await self.generate_front_page(customer_name, industry)
            pdfs.append(front_page)
            
            # 2. Download and convert each page image to PDF
            logger.info(f"[Job {job_id}] Converting {len(page_image_urls)} pages to PDF...")
            for idx, image_url in enumerate(page_image_urls, 1):
                try:
                    # Download image
                    image_data = await self.download_image(image_url)
                    
                    # Convert to PDF
                    page_pdf = await self.convert_image_to_pdf(image_data, fit_to_page=True)
                    pdfs.append(page_pdf)
                    
                    logger.info(f"[Job {job_id}] Converted page {idx}/{len(page_image_urls)}")
                except Exception as e:
                    logger.error(f"[Job {job_id}] Failed to convert page {idx}: {e}")
                    # Continue with other pages
            
            # 3. Merge all PDFs
            logger.info(f"[Job {job_id}] Merging {len(pdfs)} PDFs...")
            final_pdf = await self.merge_pdfs(
                pdfs,
                metadata={
                    'title': f'{customer_name} - Product Catalog',
                    'author': 'Catalog Generator',
                    'subject': industry
                }
            )
            
            logger.info(f"[Job {job_id}] Catalog generation complete!")
            return final_pdf
            
        except Exception as e:
            logger.error(f"[Job {job_id}] Error generating catalog: {e}")
            raise

