from fastapi import APIRouter, HTTPException, Path
from app.models.schemas import JobStatusResponse
from app.services.catalog_service import CatalogService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

catalog_service = CatalogService()

@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str = Path(..., description="Job ID to check status")
):
    """
    Get the status of a catalog generation job
    
    Returns job status, progress, and PDF URL when completed
    """
    try:
        job_data = await catalog_service.get_job_status(job_id)
        return JobStatusResponse(**job_data)
    except Exception as e:
        logger.error(f"Error fetching job status: {e}")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
