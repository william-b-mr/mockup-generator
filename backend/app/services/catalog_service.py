import base64
import uuid
from typing import List, Dict, Any
import logging
from datetime import datetime

from app.services.supabase_service import DatabaseService, StorageService
from app.services.n8n_service import N8NService
from app.models.schemas import (
    CatalogRequest,
    JobStatus,
    N8NLogoProcessingPayload,
    N8NPageGeneratorPayload,
    N8NPDFAssemblyPayload
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
                    'items': request.items,
                    'colors': request.colors,
                    'total_pages': len(request.items) * len(request.colors)
                }
            }
            await self.db.create_job(job_data)
            
            # 2. Upload logo to Supabase Storage
            logo_url = await self._upload_logo(job_id, request.logo)
            
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
                logo_url
            )
            
            return {
                'job_id': job_id,
                'status': JobStatus.PROCESSING.value,
                'message': 'Catalog generation started',
                'estimated_time_seconds': self._estimate_processing_time(
                    len(request.items) * len(request.colors)
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
    
    async def _upload_logo(self, job_id: str, logo_data: str) -> str:
        """Upload logo to Supabase Storage"""
        try:
            # Decode base64 logo
            if ',' in logo_data:
                logo_data = logo_data.split(',')[1]
            
            logo_bytes = base64.b64decode(logo_data)
            
            # Upload to Supabase Storage
            file_path = f"logos/{job_id}/original.png"
            logo_url = await self.storage.upload_file(
                file_path,
                logo_bytes,
                content_type='image/png'
            )
            
            logger.info(f"Logo uploaded for job {job_id}: {logo_url}")
            return logo_url
            
        except Exception as e:
            logger.error(f"Error uploading logo: {e}")
            raise LogoProcessingException(detail=str(e))
    
    async def _validate_templates(self, items: List[str], colors: List[str]):
        """Validate that all required templates exist"""
        missing_templates = []
        
        for item in items:
            for color in colors:
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
        logo_url: str
    ):
        """Process the entire catalog generation workflow"""
        try:
            # Step 1: Process logo (remove background, resize)
            logger.info(f"[Job {job_id}] Step 1: Processing logo...")
            logo_response = await self.n8n.process_logo(
                N8NLogoProcessingPayload(
                    job_id=job_id,
                    logo_url=logo_url
                )
            )
            
            if not logo_response.success:
                raise LogoProcessingException(
                    detail="n8n logo processing workflow failed"
                )
            
            await self.db.update_job_status(job_id, JobStatus.PROCESSING.value, progress=30)
            
            # Step 2: Validate templates exist
            logger.info(f"[Job {job_id}] Step 2: Validating templates...")
            await self._validate_templates(request.items, request.colors)
            
            # Step 3: Generate pages
            logger.info(f"[Job {job_id}] Step 3: Generating pages...")
            page_urls = []
            total_pages = len(request.items) * len(request.colors)
            processed_pages = 0
            
            for item in request.items:
                for color in request.colors:
                    page_response = await self.n8n.generate_page(
                        N8NPageGeneratorPayload(
                            job_id=job_id,
                            item=item,
                            color=color,
                            logo_large_url=logo_response.logo_large_url,
                            logo_small_url=logo_response.logo_small_url
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
            pdf_response = await self.n8n.assemble_pdf(
                N8NPDFAssemblyPayload(
                    job_id=job_id,
                    customer_name=request.customer_name,
                    industry=request.industry,
                    page_urls=page_urls
                )
            )
            
            if not pdf_response.success:
                raise Exception("PDF assembly failed")
            
            # Step 5: Update job as completed
            logger.info(f"[Job {job_id}] Completed! PDF: {pdf_response.pdf_url}")
            await self.db.update_job_status(
                job_id,
                JobStatus.COMPLETED.value,
                pdf_url=pdf_response.pdf_url,
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
