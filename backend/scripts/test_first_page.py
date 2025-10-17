from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import io
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """Handle all PDF generation operations"""
    
    def __init__(self):
        self.page_size = A4  # (595, 842) points
        # MBC Brand colors
        self.mbc_red = HexColor('#d11720')  # Red color from the template
        self.mbc_dark = HexColor('#000000')  # Black for text
        self.mbc_gray = HexColor('#9CA3AF')  # Gray for placeholder
        
    async def generate_front_page(
        self, 
        customer_name: str, 
        customer_image: bytes = None,
        logo_path: str = "assets/logo.png"
    ) -> bytes:
        """
        Generate a front page PDF matching MBC Fardamento template
        
        Args:
            customer_name: Customer name to display
            customer_image: Optional customer image bytes (if None, shows placeholder)
            logo_path: Path to MBC logo file
            
        Returns:
            PDF bytes
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=self.page_size)
            width, height = self.page_size
            
            # 1. RED HEADER SECTION
            # Draw red header rectangle (reduced to ~15% of page height)
            header_height = height * 0.10
            c.setFillColor(self.mbc_red)
            c.rect(0, height - header_height, width, header_height, stroke=0, fill=1)
            
            # Add MBC Logo (bigger, more to the left)
            try:
                logo = Image.open(logo_path)
                logo_reader = ImageReader(logo)
                # Position: 20pt from left, centered vertically in header
                logo_width = 230  # Increased from 160
                logo_height = 75  # Increased from 60
                logo_y = height - header_height + (header_height - logo_height) / 2
                c.drawImage(
                    logo_reader,
                    10,  # More to the left (was 40)
                    logo_y,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
                # Fallback: Draw text logo (also bigger and more left)
                c.setFillColor(HexColor('#FFFFFF'))
                c.setFont("Helvetica-Bold", 56)  # Bigger font
                logo_y = height - header_height + (header_height / 2) - 10
                c.drawString(20, logo_y, "MBC")
                c.setFont("Helvetica", 16)
                c.drawString(20, logo_y - 25, "FARDAMENTO")
            
            # Add tagline (right side of header, vertically centered)
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont("Helvetica", 18)
            tagline = "Uniformes com identidade"
            text_width = c.stringWidth(tagline, "Helvetica", 18)
            tagline_y = height - header_height + (header_height / 2) - 6
            c.drawString(width - text_width - 40, tagline_y, tagline)
            
            # 2. MAIN CONTENT SECTION (White background)
            # Title: "Catálogo Personalizado"
            c.setFillColor(self.mbc_dark)
            c.setFont("Helvetica-Bold", 24)
            title = "Catálogo Personalizado"
            text_width = c.stringWidth(title, "Helvetica-Bold", 36)
            c.drawString((width - text_width) / 2, height - 150, title)
            
            # Customer Name (large, centered)
            c.setFont("Helvetica-Bold", 48)
            text_width = c.stringWidth(customer_name, "Helvetica-Bold", 48)
            c.drawString((width - text_width) / 2, height - 200, customer_name)
            
            # 3. CUSTOMER IMAGE OR PLACEHOLDER
            image_width = 350
            image_height = 250
            image_x = (width - image_width) / 2
            image_y = height - 700  # Position below customer name
            
            if customer_image:
                try:
                    # Use provided customer image
                    img = Image.open(io.BytesIO(customer_image))
                    img_reader = ImageReader(img)
                    c.drawImage(
                        img_reader,
                        image_x,
                        image_y,
                        width=image_width,
                        height=image_height,
                        preserveAspectRatio=True
                    )
                except Exception as e:
                    logger.error(f"Error loading customer image: {e}")
                    # Fall back to placeholder
                    self._draw_image_placeholder(c, image_x, image_y, image_width, image_height)
            else:
                # Draw placeholder rectangle
                self._draw_image_placeholder(c, image_x, image_y, image_width, image_height)
            
            # 4. FOOTER SECTION (Red gradient)
            # Create gradient effect at bottom
            footer_height = 80
            gradient_start = 120
            
            # Draw gradient (fade from transparent to red)
            for i in range(50):
                opacity = i / 50.0
                # Create pink to red gradient effect
                r = 220 + (220 - 220) * opacity
                g = 38 + (150 - 38) * opacity
                b = 38 + (150 - 38) * opacity
                c.setFillColorRGB(r/255, g/255, b/255, alpha=opacity * 0.3)
                c.rect(0, gradient_start - (i * 2), width, 2, stroke=0, fill=1)
            
            # Solid red footer
            c.setFillColor(self.mbc_red)
            c.rect(0, 0, width, footer_height, stroke=0, fill=1)
            
            # Footer contact information
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont("Helvetica", 12)
            
            # Email (left)
            c.drawString(40, 40, "geral@mbcfardamento.com")
            
            # Phone (center)
            phone = "+351 939 557 088"
            text_width = c.stringWidth(phone, "Helvetica", 12)
            c.drawString((width - text_width) / 2, 40, phone)
            
            # Location (right)
            location = "Dalvares, Viseu, Portugal"
            text_width = c.stringWidth(location, "Helvetica", 12)
            c.drawString(width - text_width - 40, 40, location)
            
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
    
    def _draw_image_placeholder(self, canvas_obj, x, y, width, height):
        """
        Draw a gray placeholder rectangle with text
        
        Args:
            canvas_obj: ReportLab canvas object
            x, y: Position coordinates
            width, height: Dimensions of placeholder
        """
        # Draw gray rectangle
        canvas_obj.setFillColor(self.mbc_gray)
        canvas_obj.rect(x, y, width, height, stroke=0, fill=1)
        
        # Add placeholder text
        canvas_obj.setFillColor(HexColor('#FFFFFF'))
        canvas_obj.setFont("Helvetica", 16)
        text = "Picture placeholder"
        text_width = canvas_obj.stringWidth(text, "Helvetica", 16)
        canvas_obj.drawString(
            x + (width - text_width) / 2,
            y + (height / 2) - 8,
            text
        )
    
    async def generate_front_page_with_custom_image_url(
        self,
        customer_name: str,
        image_url: str = None,
        logo_path: str = "assets/logo.png"
    ) -> bytes:
        """
        Generate front page with image from URL
        
        Args:
            customer_name: Customer name
            image_url: Optional URL to customer image
            logo_path: Path to logo file
            
        Returns:
            PDF bytes
        """
        customer_image = None
        
        if image_url:
            try:
                customer_image = await self.download_image(image_url)
            except Exception as e:
                logger.warning(f"Could not download image from {image_url}: {e}")
        
        return await self.generate_front_page(
            customer_name=customer_name,
            customer_image=customer_image,
            logo_path=logo_path
        )


# Example usage
async def main():
    """Example of how to use the PDF generator"""
    pdf_service = PDFService()
    
    # Generate PDF with placeholder
    pdf_bytes = await pdf_service.generate_front_page(
        customer_name="Nome do Cliente",
        customer_image=None,  # Will show placeholder
        logo_path="assets/logo.png"
    )
    
    # Save to file
    with open("catalog_front_page.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print("PDF generated successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())