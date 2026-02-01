"""
Health check endpoints.
"""

# # Standard library imports
from datetime import datetime

# # Third-party imports
from fastapi import APIRouter

# # Local application imports
from app.models.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0", timestamp=datetime.now())
