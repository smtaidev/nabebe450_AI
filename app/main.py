from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from core.config import settings
from core.dependencies import setup_logging, validate_api_key
from api.endpoints import emoticare, prescription, surgismart, heygen

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting EmotiCare Support API...")
    try:
        settings.validate()
        if not await validate_api_key():
            logger.error("Google API key validation failed")
            raise Exception("Invalid or missing Google API key")
        logger.info("EmotiCare Support API started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down EmotiCare Support API...")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="EmotiCare API - AI-powered emotional support and prescription analysis",
    contact={"name": "EmotiCare Support Team"},
    license_info={"name": "MIT License"},
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only 4 essential routers
app.include_router(emoticare.router, prefix="/api/v1", tags=["emoticare"])
app.include_router(prescription.router, prefix="/api/v1", tags=["prescription"]) 
app.include_router(surgismart.router, prefix="/api/v1", tags=["surgismart"])
app.include_router(heygen.router, prefix="/api/v1", tags=["heygen"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to EmotiCare API",
        "version": settings.app_version,
        "endpoints": {
            "emoticare": "/api/v1/emoticare/support",
            "prescription": "/api/v1/prescription/analyze",
            "surgismart": "/api/v1/surgismart/simulate", 
            "heygen": "/api/v1/heygen/generate",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "EmotiCare API"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )