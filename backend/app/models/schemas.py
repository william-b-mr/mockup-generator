from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CatalogRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    logo: str = Field(..., description="Base64 encoded logo or file upload")
    items: List[str] = Field(..., min_length=1, max_length=50)
    colors: List[str] = Field(..., min_length=1, max_length=20)
    
    @field_validator('customer_name', 'industry')
    @classmethod
    def strip_whitespace(cls, v):
        return v.strip()
    
    @field_validator('items', 'colors')
    @classmethod
    def validate_lists(cls, v):
        return [item.strip() for item in v if item.strip()]

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
    id: str
    item_name: str
    color: str
    template_url: str
    logo_position_x: int
    logo_position_y: int
    logo_size: str  # "large" or "small"
    created_at: Optional[datetime] = None

class TemplateCreate(BaseModel):
    item_name: str
    color: str
    template_url: str
    logo_position_x: int = 0
    logo_position_y: int = 0
    logo_size: str = "small"

class N8NLogoProcessingPayload(BaseModel):
    job_id: str
    logo_url: str

class N8NLogoProcessingResponse(BaseModel):
    job_id: str
    logo_large_url: str
    logo_small_url: str
    success: bool

class N8NPageGeneratorPayload(BaseModel):
    job_id: str
    item: str
    color: str
    logo_large_url: str
    logo_small_url: str

class N8NPageGeneratorResponse(BaseModel):
    job_id: str
    page_url: str
    item: str
    color: str
    success: bool

class N8NPDFAssemblyPayload(BaseModel):
    job_id: str
    customer_name: str
    industry: str
    page_urls: List[str]

class N8NPDFAssemblyResponse(BaseModel):
    job_id: str
    pdf_url: str
    success: bool

