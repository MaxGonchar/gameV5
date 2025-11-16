"""
FastAPI main application for the interactive story bot.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import settings
from app.api.routes import story, health, characters, locations

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
    
    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(story.router, prefix="/api/v1", tags=["story"])
    app.include_router(characters.router, prefix="/api/v1", tags=["characters"])
    app.include_router(locations.router, prefix="/api/v1", tags=["locations"])
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)