import base64
import uuid
from typing import List, Dict, Any
import logging
from datetime import datetime

from app.services.supabase_service import DatabaseService, StorageService
from app.services.n8n_service import N8NService
from app.services.pdf_service import PDFService
from app.models.schemas import (
    CatalogRequest,
    JobStatus,
    N8NLogoProcessingPayload,
    N8NPageGeneratorPayload,
)
from app.core.exceptions import (
    TemplateNotFoundException,
    LogoProcessingException
)

logger = logging.getLogger(__name__)

class CatalogService:
    def __init__(self):
        self.db = DatabaseService()
        self.storage = StorageService()
        self.n8n = N8NService()
        self.pdf = PDFService()
    
    async def create_catalog(self, request: CatalogRequest) -> Dict[str, Any]:
        """Main orchestration method for catalog generation"""
        job_id = str(uuid.uuid4())
        
        try:
            # 1. Create job in database
            job_data = {
                'id': job_id,
                'customer_name': request.customer_name,
                'industry': request.industry,
                'status': JobStatus.PENDING.value,
                'metadata': {
                    'selections': [{'item': s.item, 'color': s.color} for s in request.selections],
                    'total_pages': len(request.selections)
                }
            }
            await self.db.create_job(job_data)
            
            # 2. Upload both logos to Supabase Storage
            logo_dark_url, logo_light_url = await self._upload_logos(job_id, request.logo_dark, request.logo_light)
            
            # 3. Update job status to processing
            await self.db.update_job_status(
                job_id, 
                JobStatus.PROCESSING.value,
                progress=10
            )
            
            # 4. Process catalog generation
            await self._process_catalog_generation(
                job_id, 
                request, 
                logo_dark_url,
                logo_light_url
            )
            
            return {
                'job_id': job_id,
                'status': JobStatus.PROCESSING.value,
                'message': 'Catalog generation started',
                'estimated_time_seconds': self._estimate_processing_time(
                    len(request.selections)
                )
            }
            
        except Exception as e:
            logger.error(f"Error creating catalog for job {job_id}: {e}")
            await self.db.update_job_status(
                job_id,
                JobStatus.FAILED.value,
                error_message=str(e)
            )
            raise
    
    async def _upload_logos(self, job_id: str, logo_dark_data: str, logo_light_data: str) -> tuple[str, str]:
        """Upload both logos to Supabase Storage with background-specific naming"""
        try:
            # Process dark logo
            if ',' in logo_dark_data:
                logo_dark_data = logo_dark_data.split(',')[1]
            logo_dark_bytes = base64.b64decode(logo_dark_data)
            
            # Process light logo
            if ',' in logo_light_data:
                logo_light_data = logo_light_data.split(',')[1]
            logo_light_bytes = base64.b64decode(logo_light_data)
            
            # Upload both logos with descriptive names
            dark_file_path = f"logos/{job_id}/logo_fundo_escuro.png"
            light_file_path = f"logos/{job_id}/logo_fundo_claro.png"
            
            logo_dark_url = await self.storage.upload_file(
                dark_file_path,
                logo_dark_bytes,
                content_type='image/png'
            )
            
            logo_light_url = await self.storage.upload_file(
                light_file_path,
                logo_light_bytes,
                content_type='image/png'
            )
            
            logger.info(f"Logos uploaded for job {job_id}:")
            logger.info(f"  Dark background logo: {logo_dark_url}")
            logger.info(f"  Light background logo: {logo_light_url}")
            
            return logo_dark_url, logo_light_url
            
        except Exception as e:
            logger.error(f"Error uploading logos: {e}")
            raise LogoProcessingException(detail=str(e))
    
    async def _validate_templates(self, selections: List[tuple[str, str]]):
        """Validate that all required templates exist"""
        missing_templates = []

        for item, color in selections:
            template = await self.db.get_template(item, color)
            if not template:
                missing_templates.append(f"{item} - {color}")

        if missing_templates:
            raise TemplateNotFoundException(
                item=missing_templates[0].split(' - ')[0],
                color=missing_templates[0].split(' - ')[1]
            )
    
    async def _process_catalog_generation(
        self, 
        job_id: str, 
        request: CatalogRequest,
        logo_dark_url: str,
        logo_light_url: str
    ):
        """Process the entire catalog generation workflow"""
        try:
            # Step 1: Process logos (remove background, resize)
            logger.info(f"[Job {job_id}] Step 1: Processing both logos...")
            logo_response = await self.n8n.process_logo(
                N8NLogoProcessingPayload(
                    job_id=job_id,
                    logo_dark_url=logo_dark_url,
                    logo_light_url=logo_light_url
                )
            )
            
            if not logo_response.success:
                raise LogoProcessingException(
                    detail="n8n logo processing workflow failed"
                )
            
            await self.db.update_job_status(job_id, JobStatus.PROCESSING.value, progress=30)

            # Step 2: Validate templates exist
            logger.info(f"[Job {job_id}] Step 2: Validating templates...")
            selections_list = [(s.item, s.color) for s in request.selections]
            await self._validate_templates(selections_list)

            # Step 3: Generate pages
            logger.info(f"[Job {job_id}] Step 3: Generating pages...")
            page_urls = []
            total_pages = len(request.selections)
            processed_pages = 0

            for selection in request.selections:
                item = selection.item
                color = selection.color

                # Get template to determine background
                template = await self.db.get_template(item, color)
                if not template:
                    logger.warning(f"Template not found for {item} - {color}, skipping")
                    continue

                background = template.get('background', 'light')  # Default to light

                # Choose appropriate logo URLs based on background
                if background == 'dark':
                    logo_large_url = logo_response.logo_light_large_url
                    logo_small_url = logo_response.logo_light_small_url
                else:  # light background
                    logo_large_url = logo_response.logo_dark_large_url
                    logo_small_url = logo_response.logo_dark_small_url

                page_response = await self.n8n.generate_page(
                    N8NPageGeneratorPayload(
                        job_id=job_id,
                        item=item,
                        color=color,
                        logo_large_url=logo_large_url,
                        logo_small_url=logo_small_url,
                        background=background,
                        front_logo_position=request.front_logo_position.value
                    )
                )

                if page_response.success:
                    page_urls.append(page_response.page_url)
                    processed_pages += 1

                    # Update progress
                    progress = 30 + int((processed_pages / total_pages) * 50)
                    await self.db.update_job_status(
                        job_id,
                        JobStatus.PROCESSING.value,
                        progress=progress
                    )
                else:
                    logger.warning(
                        f"Failed to generate page for {item} - {color}"
                    )
            
            # Step 4: Assemble PDF
            logger.info(f"[Job {job_id}] Step 4: Assembling PDF...")
            pdf_bytes = await self.pdf.generate_complete_catalog(
                            customer_name=request.customer_name,
                            industry=request.industry,
                            page_image_urls=page_urls,
                            job_id=job_id
                        )

            # Upload PDF with formatted filename
            current_date = datetime.now().strftime("%Y-%m-%d")
            # Sanitize customer name for filename (replace spaces and special chars)
            safe_customer_name = "".join(
                c if c.isalnum() or c in ('-', '_') else '_'
                for c in request.customer_name
            )
            pdf_filename = f"{safe_customer_name}_catalogo_{current_date}.pdf"

            pdf_url = await self.storage.upload_file(
                f"catalogs/{pdf_filename}",
                pdf_bytes,
                content_type='application/pdf'
            )

            if not pdf_url:
                raise Exception("PDF upload failed")

            # Step 5: Update job as completed
            logger.info(f"[Job {job_id}] Completed! PDF: {pdf_url}")
            await self.db.update_job_status(
                job_id,
                JobStatus.COMPLETED.value,
                pdf_url=pdf_url,
                progress=100
            )
            
        except Exception as e:
            logger.error(f"[Job {job_id}] Error: {e}")
            await self.db.update_job_status(
                job_id,
                JobStatus.FAILED.value,
                error_message=str(e)
            )
            raise
    
    def _estimate_processing_time(self, total_pages: int) -> int:
        """Estimate processing time in seconds"""
        # Rough estimate: 10 seconds per page + 30 seconds overhead
        return (total_pages * 10) + 30
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status from database"""
        job = await self.db.get_job(job_id)
        if not job:
            raise Exception(f"Job {job_id} not found")
        return job
