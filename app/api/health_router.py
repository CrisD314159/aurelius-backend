"""
This router cotains health endpoints
"""

from fastapi import APIRouter


health_router = APIRouter()


@health_router.get("/health")
def check_health():
    """Health check endpoint"""
    return {"success": True, "status": "healthy", "message": "Service is running"}
