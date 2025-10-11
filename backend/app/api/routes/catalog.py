from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import CatalogRequest, CatalogResponse
from app.services.catalog_service import CatalogService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

catalog_service = CatalogService()

@router.post("/generate", response_model=CatalogResponse)
async def generate_catalog(
    request: CatalogRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a personalized catalog
    
    - **customer_name**: Name for the front page
    - **industry**: Industry for the front page
    - **logo**: Base64 encoded logo image
    - **items**: List of items to include (e.g., ["Sweatshirt", "T-Shirt"])
    - **colors**: List of colors for each item (e.g., ["Red", "Blue"])
    """
    try:
        result = await catalog_service.create_catalog(request)
        return CatalogResponse(**result)
    except Exception as e:
        logger.error(f"Error generating catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))


