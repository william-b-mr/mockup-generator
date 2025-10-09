from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Template, TemplateCreate
from app.services.supabase_service import SupabaseService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

supabase_service = SupabaseService()

@router.get("/", response_model=List[Template])
async def get_all_templates():
    """Get all available templates"""
    try:
        templates = await supabase_service.get_all_templates()
        return templates
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_name}/{color}", response_model=Template)
async def get_template(item_name: str, color: str):
    """Get template for specific item and color"""
    try:
        template = await supabase_service.get_template(item_name, color)
        if not template:
            raise HTTPException(
                status_code=404, 
                detail=f"Template not found for {item_name} - {color}"
            )
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Template)
async def create_template(template: TemplateCreate):
    """Create a new template"""
    try:
        result = await supabase_service.create_template(template.dict())
        return result
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

