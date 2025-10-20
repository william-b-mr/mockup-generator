from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ArticleColorSelection(BaseModel):
    """Represents a specific article-color combination selected by the user"""
    item: str = Field(..., min_length=1, max_length=100)
    color: str = Field(..., min_length=1, max_length=100)

    @field_validator('item', 'color')
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip()

class LogoPosition(str, Enum):
    PEITO_ESQUERDO = "peito_esquerdo"
    PEITO_DIREITO = "peito_direito"

class CatalogRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    logo_dark: str = Field(..., description="Base64 encoded logo for dark backgrounds")
    logo_light: str = Field(..., description="Base64 encoded logo for light backgrounds")
    front_logo_position: LogoPosition = Field(..., description="Position for the front logo: peito_esquerdo or peito_direito")
    selections: List[ArticleColorSelection] = Field(..., min_length=1, max_length=100, description="List of article-color pairs to generate")

    @field_validator('customer_name', 'industry')
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip()

class CatalogResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    estimated_time_seconds: Optional[int] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    customer_name: str
    progress: Optional[int] = None  # Percentage 0-100
    pdf_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class Template(BaseModel):
    id: Union[str, int]          # Support both str and int IDs
    item_name: str
    color: str
    template_url: Optional[str] = None
    background: Optional[str] = None  # "light" or "dark"

class TemplateCreate(BaseModel):
    item_name: str
    color: str
    template_url: str
    logo_position_x: int = 0
    logo_position_y: int = 0
    logo_size: str = "small"

class N8NLogoProcessingPayload(BaseModel):
    job_id: str
    logo_dark_url: str
    logo_light_url: str

class N8NLogoProcessingResponse(BaseModel):
    job_id: str
    logo_dark_large_url: str
    logo_dark_small_url: str
    logo_light_large_url: str
    logo_light_small_url: str
    success: bool

class N8NPageGeneratorPayload(BaseModel):
    job_id: str
    item: str
    color: str
    logo_large_url: str
    logo_small_url: str
    background: str  # "light" or "dark" - determines which logo to use
    front_logo_position: str  # "peito_esquerdo" or "peito_direito"

class N8NPageGeneratorResponse(BaseModel):
    job_id: str
    page_url: str
    item: str
    color: str
    success: bool

class N8NFrontPageImagePayload(BaseModel):
    job_id: str
    industry: str

class N8NFrontPageImageResponse(BaseModel):
    job_id: str
    image_url: str
    success: bool



