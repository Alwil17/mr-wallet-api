from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.base import get_db

router = APIRouter(tags=["Health Check"])


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the API is running and database is accessible",
)
async def health_check(db: Session = Depends(get_db)):
    """
    Simple health check endpoint to verify:
    - API is responding
    - Database connection is working
    - Current timestamp
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "1.0.1",
    }


@router.get("/", summary="API Root", description="Welcome message and API information")
async def root():
    """
    API root endpoint providing basic information about Mr Wallet API.
    """
    return {
        "message": "Welcome to Mr Wallet API - Personal Finance Management",
        "version": "1.0.1",
        "docs": "/docs or /redoc",
        "health": "/health",
    }
