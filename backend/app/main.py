"""
FastAPI main application for the interactive story bot.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import settings, get_logger
from app.api.routes import story, health, characters, locations
from app.exceptions import (
    CoreException,
    EntityNotFoundException,
    DataValidationException,
    ExternalServiceException,
    BusinessLogicException,
    ServiceException,
    InitializationException
)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Interactive Story Bot API",
        description="REST API for LLM-driven interactive story application",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add global exception handlers
    setup_exception_handlers(app)
    
    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(story.router, prefix="/api/v1", tags=["story"])
    app.include_router(characters.router, prefix="/api/v1", tags=["characters"])
    app.include_router(locations.router, prefix="/api/v1", tags=["locations"])
    
    return app


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup global exception handlers for the application."""
    logger = get_logger(__name__)
    
    @app.exception_handler(EntityNotFoundException)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
        """Handle EntityNotFoundException globally."""
        logger.warning(f"Entity not found on {request.method} {request.url}: {exc.message}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": "The requested resource was not found",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(DataValidationException)
    async def data_validation_handler(request: Request, exc: DataValidationException):
        """Handle DataValidationException globally."""
        logger.error(f"Data validation error on {request.method} {request.url}: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Bad Request",
                "message": "Invalid request data",
                "details": exc.message,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(ExternalServiceException)
    async def external_service_handler(request: Request, exc: ExternalServiceException):
        """Handle ExternalServiceException globally."""
        logger.error(f"External service error on {request.method} {request.url}: {exc.message}")
        return JSONResponse(
            status_code=502,
            content={
                "error": "Service Unavailable",
                "message": "External service temporarily unavailable. Please try again.",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(BusinessLogicException)
    async def business_logic_handler(request: Request, exc: BusinessLogicException):
        """Handle BusinessLogicException globally."""
        logger.warning(f"Business logic error on {request.method} {request.url}: {exc.message}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Unprocessable Entity",
                "message": exc.message,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(InitializationException)
    async def initialization_handler(request: Request, exc: InitializationException):
        """Handle InitializationException globally."""
        logger.error(f"Initialization error on {request.method} {request.url}: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Service Initialization Error",
                "message": "Service initialization failed. Please try again.",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(ServiceException)
    async def service_handler(request: Request, exc: ServiceException):
        """Handle ServiceException globally."""
        logger.error(f"Service error on {request.method} {request.url}: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "Internal service error. Please try again.",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(CoreException)
    async def core_exception_handler(request: Request, exc: CoreException):
        """Handle any CoreException that wasn't caught by specific handlers."""
        logger.error(f"Unhandled CoreException on {request.method} {request.url}: {exc.message}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again.",
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle any unexpected exceptions as a safety net."""
        logger.exception(f"Unexpected error on {request.method} {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again.",
                "path": str(request.url.path)
            }
        )

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)