from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.routes import catalog, jobs, templates, health
from app.core.config import settings
from app.core.exceptions import CatalogException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Catalog Generator API",
    description="Backend API for generating personalized mockup catalogs",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(CatalogException)
async def catalog_exception_handler(request: Request, exc: CatalogException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "detail": exc.detail}
    )

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(catalog.router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Catalog Generator API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Catalog Generator API...")