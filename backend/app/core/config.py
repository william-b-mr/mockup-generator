from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # Database (Direct PostgreSQL Connection)
    DATABASE_URL: Optional[str] = None
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    
    
    # Supabase Storage (for file uploads only)
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    STORAGE_BUCKET_NAME: str = "catalog-assets"
    
    # n8n
    N8N_WEBHOOK_BASE_URL: str
    N8N_LOGO_PROCESSING_WEBHOOK: str
    N8N_PAGE_GENERATOR_WEBHOOK: str
    N8N_FRONT_PAGE_IMAGE_WEBHOOK: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # File Upload
    MAX_LOGO_SIZE_MB: int = 10
    ALLOWED_LOGO_FORMATS: List[str] = ["image/png", "image/jpeg", "image/jpg"]
    
    # Job Settings
    JOB_TIMEOUT_SECONDS: int = 300
    MAX_RETRIES: int = 3
    
    # Google API
    GOOGLE_API_KEY: Optional[str] = None
    
    @property
    def database_url(self) -> str:
        """Construct database URL if not provided"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = ConfigDict(env_file=".env")

settings = Settings()
