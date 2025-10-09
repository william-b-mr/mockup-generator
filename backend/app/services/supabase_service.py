from supabase import create_client, Client
from app.core.config import settings
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        self.bucket_name = settings.STORAGE_BUCKET_NAME
    
    # Template Operations
    async def get_template(self, item_name: str, color: str) -> Optional[Dict[str, Any]]:
        """Get template for specific item and color"""
        try:
            response = self.client.table('templates').select('*').eq(
                'item_name', item_name
            ).eq('color', color).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching template: {e}")
            return None
    
    async def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all templates"""
        try:
            response = self.client.table('templates').select('*').execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching templates: {e}")
            return []
    
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new template"""
        try:
            response = self.client.table('templates').insert(template_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise
    
    async def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing template"""
        try:
            response = self.client.table('templates').update(
                template_data
            ).eq('id', template_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            raise
    
    # Job Operations
    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new catalog generation job"""
        try:
            response = self.client.table('jobs').insert(job_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            raise
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        try:
            response = self.client.table('jobs').select('*').eq('id', job_id).execute()
            return response.data[0] if response.data and len(response.data) > 0 else None
        except Exception as e:
            logger.error(f"Error fetching job: {e}")
            return None
    
    async def update_job_status(
        self, 
        job_id: str, 
        status: str, 
        pdf_url: Optional[str] = None,
        error_message: Optional[str] = None,
        progress: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update job status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            if pdf_url:
                update_data['pdf_url'] = pdf_url
            if error_message:
                update_data['error_message'] = error_message
            if progress is not None:
                update_data['progress'] = progress
            
            response = self.client.table('jobs').update(
                update_data
            ).eq('id', job_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            raise
    
    # Storage Operations
    async def upload_file(
        self, 
        file_path: str, 
        file_content: bytes, 
        content_type: str = 'application/octet-stream'
    ) -> str:
        """Upload file to Supabase Storage"""
        try:
            response = self.client.storage.from_(self.bucket_name).upload(
                file_path,
                file_content,
                file_options={"content-type": content_type}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            return public_url
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file"""
        return self.client.storage.from_(self.bucket_name).get_public_url(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            self.client.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

