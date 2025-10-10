from app.core.database import db
from app.core.config import settings
from storage3 import create_client as create_storage_client
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class DatabaseService:
    """Handle all database operations using direct PostgreSQL connection"""
    
    # ===== TEMPLATE OPERATIONS =====
    
    async def get_template(self, item_name: str, color: str) -> Optional[Dict[str, Any]]:
        """Get template for specific item and color"""
        try:
            query = """
                SELECT id, item_name, color, template_url, 
                       logo_position_x, logo_position_y, logo_size,
                       created_at, updated_at
                FROM templates
                WHERE item_name = $1 AND color = $2
            """
            row = await db.fetch_one(query, item_name, color)
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error fetching template: {e}")
            return None
    
    async def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all templates"""
        try:
            query = """
                SELECT id, item_name, color, template_url,
                       logo_position_x, logo_position_y, logo_size,
                       created_at, updated_at
                FROM templates
                ORDER BY item_name, color
            """
            rows = await db.fetch_all(query)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching templates: {e}")
            return []
    
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new template"""
        try:
            template_id = str(uuid.uuid4())
            query = """
                INSERT INTO templates (
                    id, item_name, color, template_url,
                    logo_position_x, logo_position_y, logo_size
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, item_name, color, template_url,
                          logo_position_x, logo_position_y, logo_size,
                          created_at, updated_at
            """
            row = await db.fetch_one(
                query,
                template_id,
                template_data['item_name'],
                template_data['color'],
                template_data['template_url'],
                template_data.get('logo_position_x', 0),
                template_data.get('logo_position_y', 0),
                template_data.get('logo_size', 'small')
            )
            return dict(row)
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise
    
    async def update_template(
        self, 
        template_id: str, 
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing template"""
        try:
            query = """
                UPDATE templates
                SET item_name = $2,
                    color = $3,
                    template_url = $4,
                    logo_position_x = $5,
                    logo_position_y = $6,
                    logo_size = $7,
                    updated_at = NOW()
                WHERE id = $1
                RETURNING id, item_name, color, template_url,
                          logo_position_x, logo_position_y, logo_size,
                          created_at, updated_at
            """
            row = await db.fetch_one(
                query,
                template_id,
                template_data['item_name'],
                template_data['color'],
                template_data['template_url'],
                template_data.get('logo_position_x', 0),
                template_data.get('logo_position_y', 0),
                template_data.get('logo_size', 'small')
            )
            return dict(row)
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            raise
    
    # ===== JOB OPERATIONS =====
    
    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new catalog generation job"""
        try:
            query = """
                INSERT INTO jobs (
                    id, customer_name, industry, status,
                    progress, metadata, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                RETURNING id, customer_name, industry, status,
                          progress, pdf_url, error_message, metadata,
                          created_at, updated_at
            """
            row = await db.fetch_one(
                query,
                job_data['id'],
                job_data['customer_name'],
                job_data['industry'],
                job_data['status'],
                job_data.get('progress', 0),
                job_data.get('metadata', {})
            )
            return dict(row)
        except Exception as e:
            logger.error(f"Error creating job: {e}")
            raise
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        try:
            query = """
                SELECT id, customer_name, industry, status,
                       progress, pdf_url, error_message, metadata,
                       created_at, updated_at
                FROM jobs
                WHERE id = $1
            """
            row = await db.fetch_one(query, job_id)
            
            if row:
                return dict(row)
            return None
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
            # Build dynamic query based on provided parameters
            updates = ["status = $2", "updated_at = NOW()"]
            params = [job_id, status]
            param_count = 3
            
            if pdf_url is not None:
                updates.append(f"pdf_url = ${param_count}")
                params.append(pdf_url)
                param_count += 1
            
            if error_message is not None:
                updates.append(f"error_message = ${param_count}")
                params.append(error_message)
                param_count += 1
            
            if progress is not None:
                updates.append(f"progress = ${param_count}")
                params.append(progress)
                param_count += 1
            
            query = f"""
                UPDATE jobs
                SET {', '.join(updates)}
                WHERE id = $1
                RETURNING id, customer_name, industry, status,
                          progress, pdf_url, error_message, metadata,
                          created_at, updated_at
            """
            
            row = await db.fetch_one(query, *params)
            return dict(row)
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
            raise


class StorageService:
    """Handle all Supabase Storage operations"""
    
    def __init__(self):
        # Initialize Supabase Storage client only
        self.storage = create_storage_client(
            settings.SUPABASE_URL,
            {
                "apiKey": settings.SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"
            },
            is_async=False
        )
        self.bucket_name = settings.STORAGE_BUCKET_NAME
    
    async def upload_file(
        self, 
        file_path: str, 
        file_content: bytes, 
        content_type: str = 'application/octet-stream'
    ) -> str:
        """Upload file to Supabase Storage"""
        try:
            response = self.storage.from_(self.bucket_name).upload(
                file_path,
                file_content,
                file_options={"content-type": content_type}
            )
            
            # Get public URL
            public_url = self.storage.from_(self.bucket_name).get_public_url(file_path)
            logger.info(f"File uploaded successfully: {file_path}")
            return public_url
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file"""
        return self.storage.from_(self.bucket_name).get_public_url(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            self.storage.from_(self.bucket_name).remove([file_path])
            logger.info(f"File deleted successfully: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

