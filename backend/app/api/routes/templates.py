from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Template, TemplateCreate
from app.services.supabase_service import DatabaseService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

database_service = DatabaseService()


@router.get("/", response_model=List[Template])
async def get_all_templates():
    """Get all available templates"""
    try:
        templates = await database_service.get_all_templates()
        return templates
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grouped")
async def get_templates_grouped():
    """Get templates grouped by article with available colors for each"""
    try:
        templates = await database_service.get_all_templates()

        # Group templates by item_name with their available colors
        grouped = {}
        for template in templates:
            item_name = template['item_name']
            color = template['color']

            if item_name not in grouped:
                grouped[item_name] = {
                    'item_name': item_name,
                    'colors': []
                }

            grouped[item_name]['colors'].append(color)

        # Convert to list and sort
        result = list(grouped.values())
        result.sort(key=lambda x: x['item_name'])

        return result
    except Exception as e:
        logger.error(f"Error fetching grouped templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_name}/{color}", response_model=Template)
async def get_template(item_name: str, color: str):
    """Get template for specific item and color"""
    try:
        template = await database_service.get_template(item_name, color)
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
        result = await database_service.create_template(template.dict())
        return result
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

