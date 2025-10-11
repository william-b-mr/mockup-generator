import httpx
from app.core.config import settings
from app.core.exceptions import N8NWorkflowException
from app.models.schemas import (
    N8NLogoProcessingPayload,
    N8NLogoProcessingResponse,
    N8NPageGeneratorPayload,
    N8NPageGeneratorResponse,
)
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class N8NService:
    def __init__(self):
        self.base_url = settings.N8N_WEBHOOK_BASE_URL
        self.timeout = settings.JOB_TIMEOUT_SECONDS
    
    async def _call_webhook(
        self, 
        webhook_id: str, 
        payload: Dict[str, Any],
        workflow_name: str
    ) -> Dict[str, Any]:
        """Generic method to call n8n webhooks"""
        url = f"{self.base_url}/{webhook_id}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {workflow_name} workflow")
            raise N8NWorkflowException(
                workflow_name=workflow_name,
                detail="Workflow execution timed out"
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling {workflow_name}: {e}")
            raise N8NWorkflowException(
                workflow_name=workflow_name,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error calling {workflow_name}: {e}")
            raise N8NWorkflowException(
                workflow_name=workflow_name,
                detail=str(e)
            )
    
    async def process_logo(
        self, 
        payload: N8NLogoProcessingPayload
    ) -> N8NLogoProcessingResponse:
        """Call logo processing workflow"""
        logger.info(f"Calling logo processing workflow for job {payload.job_id}")
        
        response = await self._call_webhook(
            webhook_id=settings.N8N_LOGO_PROCESSING_WEBHOOK,
            payload=payload.dict(),
            workflow_name="logo_processing"
        )
        
        return N8NLogoProcessingResponse(**response)
    
    async def generate_page(
        self, 
        payload: N8NPageGeneratorPayload
    ) -> N8NPageGeneratorResponse:
        """Call page generator workflow"""
        logger.info(
            f"Generating page for job {payload.job_id}: "
            f"{payload.item} - {payload.color}"
        )
        
        response = await self._call_webhook(
            webhook_id=settings.N8N_PAGE_GENERATOR_WEBHOOK,
            payload=payload.dict(),
            workflow_name="page_generator"
        )
        
        return N8NPageGeneratorResponse(**response)
    
