from PIL import Image
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from pypdf import PdfMerger, PdfReader, PdfWriter
import io
import httpx
from typing import List
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """Handle all PDF generation operations"""

    def __init__(self):
        self.page_size = A4
        self.mbc_red = HexColor('#d11720')
        self.mbc_dark = HexColor('#000000')
        self.mbc_gray = HexColor('#9CA3AF')
    
    async def generate_front_page(
        self,
        customer_name: str,
        customer_image: bytes = None,
    ) -> bytes:
        """Generate front page PDF with customer name and optional image"""
        try:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=self.page_size)
            width, height = self.page_size

            header_height = height * 0.11
            c.setFillColor(self.mbc_red)
            c.rect(0, height - header_height, width, header_height, stroke=0, fill=1)

            try:
                base_dir = Path(__file__).resolve().parent
                logo_path = base_dir / "assets" / "logo.png"
                logo = Image.open(logo_path)

                if logo:
                    logo_reader = ImageReader(logo)
                    logo_width = 300
                    logo_height = 90
                    logo_y = height - header_height + (header_height - logo_height) / 2
                    c.drawImage(
                        logo_reader,
                        -50,
                        logo_y,
                        width=logo_width,
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'
                    )
                else:
                    raise FileNotFoundError("Logo not found")
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
                c.setFillColor(HexColor('#FFFFFF'))
                c.setFont("Helvetica-Bold", 64)
                logo_y = height - header_height + (header_height / 2) - 10
                c.drawString(15, logo_y, "MBC")
                c.setFont("Helvetica", 18)
                c.drawString(15, logo_y - 30, "FARDAMENTO")

            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont("Helvetica", 18)
            tagline = "Uniformes com identidade"
            text_width = c.stringWidth(tagline, "Helvetica", 18)
            tagline_y = height - header_height + (header_height / 2) - 6
            c.drawString(width - text_width - 40, tagline_y, tagline)

            c.setFillColor(self.mbc_dark)
            c.setFont("Helvetica-Bold", 30)
            title = "Catálogo Personalizado"
            text_width = c.stringWidth(title, "Helvetica-Bold", 30)
            c.drawString((width - text_width) / 2, height - 150, title)

            c.setFont("Helvetica-Bold", 48)
            text_width = c.stringWidth(customer_name, "Helvetica-Bold", 48)
            c.drawString((width - text_width) / 2, height - 220, customer_name)

            image_width = 900
            image_height = 650
            image_x = (width - image_width) / 2
            image_y = height - 900
            
            if customer_image:
                try:
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
                    self._draw_image_placeholder(c, image_x, image_y, image_width, image_height)
            else:
                self._draw_image_placeholder(c, image_x, image_y, image_width, image_height)

            c.setStrokeColor(self.mbc_red)
            c.setLineWidth(2)
            line_y = height - 280
            line_margin = 100
            c.line(line_margin, line_y, width - line_margin, line_y)

            footer_height = 100

            for i in range(30):
                opacity = (30 - i) / 30.0 * 0.15
                c.setFillColorRGB(0.82, 0.09, 0.125, alpha=opacity)
                c.rect(0, footer_height + (i * 2), width, 2, stroke=0, fill=1)

            c.setFillColor(self.mbc_red)
            c.rect(0, 0, width, footer_height, stroke=0, fill=1)

            c.setFillColor(HexColor('#FFFFFF'))

            c.setFont("Helvetica-Bold", 14)
            company_text = "MBC FARDAMENTO"
            company_width = c.stringWidth(company_text, "Helvetica-Bold", 14)
            c.drawString((width - company_width) / 2, 65, company_text)

            c.setFont("Helvetica", 11)

            c.drawString(40, 35, "✉ geral@mbcfardamento.com")

            phone = "📞 +351 939 557 088"
            text_width = c.stringWidth(phone, "Helvetica", 11)
            c.drawString((width - text_width) / 2, 35, phone)

            location = "📍 Dalvares, Viseu, Portugal"
            text_width = c.stringWidth(location, "Helvetica", 11)
            c.drawString(width - text_width - 40, 35, location)

            c.setFont("Helvetica", 10)
            website = "www.mbcfardamento.com"
            website_width = c.stringWidth(website, "Helvetica", 10)
            c.drawString((width - website_width) / 2, 15, website)

            c.save()

            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"Front page generated for {customer_name}")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error generating front page: {e}")
            raise
    
    async def download_image(self, url: str) -> bytes:
        """Download image from URL"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            raise

    def _draw_image_placeholder(self, canvas_obj, x, y, width, height):
        """Draw placeholder rectangle with text"""
        canvas_obj.setFillColor(self.mbc_gray)
        canvas_obj.rect(x, y, width, height, stroke=0, fill=1)

        canvas_obj.setFillColor(HexColor('#FFFFFF'))
        canvas_obj.setFont("Helvetica", 16)
        text = "Picture placeholder"
        text_width = canvas_obj.stringWidth(text, "Helvetica", 16)
        canvas_obj.drawString(
            x + (width - text_width) / 2,
            y + (height / 2) - 8,
            text
        )
    async def convert_image_to_pdf(
        self,
        image_data: bytes,
        fit_to_page: bool = True
    ) -> bytes:
        """Convert image to PDF page"""
        try:
            img = Image.open(io.BytesIO(image_data))

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
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=self.page_size)
                width, height = self.page_size

                img_width, img_height = img.size

                margin = 20
                available_width = width - (2 * margin)
                available_height = height - (2 * margin)

                scale = min(
                    available_width / img_width,
                    available_height / img_height
                )

                scaled_width = img_width * scale
                scaled_height = img_height * scale
                x = (width - scaled_width) / 2
                y = (height - scaled_height) / 2

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
        """Merge multiple PDFs into one"""
        try:
            merger = PdfMerger()

            for pdf_bytes in pdf_list:
                merger.append(io.BytesIO(pdf_bytes))

            output_buffer = io.BytesIO()
            merger.write(output_buffer)

            if metadata:
                output_buffer.seek(0)
                reader = PdfReader(output_buffer)
                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                writer.add_metadata({
                    '/Title': metadata.get('title', 'Catalog'),
                    '/Author': metadata.get('author', 'Catalog Generator'),
                    '/Subject': metadata.get('subject', 'Product Catalog'),
                    '/Creator': 'Catalog Generator System',
                    '/Producer': 'FastAPI + ReportLab',
                })

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
        job_id: str,
        front_page_image_url: str = None
    ) -> bytes:
        """Generate complete catalog PDF"""
        try:
            pdfs = []

            logger.info(f"[Job {job_id}] Generating front page...")

            customer_image = None
            if front_page_image_url:
                try:
                    logger.info(f"[Job {job_id}] Downloading front page image from: {front_page_image_url}")
                    customer_image = await self.download_image(front_page_image_url)
                    logger.info(f"[Job {job_id}] Successfully downloaded front page image. Size: {len(customer_image)} bytes")
                except Exception as e:
                    logger.warning(f"[Job {job_id}] Failed to download front page image: {e}. Using placeholder.")
                    customer_image = None
            else:
                logger.warning(f"[Job {job_id}] No front_page_image_url provided. Using placeholder.")

            front_page = await self.generate_front_page(customer_name, customer_image)
            logger.info(f"[Job {job_id}] Front page generated with {'customer image' if customer_image else 'placeholder'}")
            pdfs.append(front_page)

            logger.info(f"[Job {job_id}] Converting {len(page_image_urls)} pages to PDF...")
            for idx, image_url in enumerate(page_image_urls, 1):
                try:
                    image_data = await self.download_image(image_url)
                    page_pdf = await self.convert_image_to_pdf(image_data, fit_to_page=False)
                    pdfs.append(page_pdf)
                    logger.info(f"[Job {job_id}] Converted page {idx}/{len(page_image_urls)}")
                except Exception as e:
                    logger.error(f"[Job {job_id}] Failed to convert page {idx}: {e}")

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

