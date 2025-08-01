"""
Main FastAPI application for Legal Intel Dashboard
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import create_tables
from app.api import documents, dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting Legal Intel Dashboard API")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    # Verify OpenAI configuration
    if settings.openai_api_key:
        logger.info("OpenAI API key configured - AI features enabled")
    else:
        logger.warning("OpenAI API key not configured - using fallback methods")
    
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"Max file size: {settings.max_file_size / (1024*1024):.1f} MB")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Legal Intel Dashboard API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered legal document analysis and query platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    documents.router,
    prefix="/api/v1",
    tags=["documents"]
)

app.include_router(
    dashboard.router,
    prefix="/api/v1",
    tags=["dashboard"]
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Legal Intel Dashboard API",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "upload": "/api/v1/upload",
            "query": "/api/v1/query",
            "dashboard": "/api/v1/dashboard",
            "documents": "/api/v1/documents"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "ai_enabled": bool(settings.openai_api_key)
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled error in {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )