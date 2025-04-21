from fastapi import APIRouter
from .schemas import HealthResponse

router = APIRouter()


@router.get("/healthcheck", response_model=HealthResponse)
async def health():
    """
    Health check endpoint to verify if the service is running.
    """
    return HealthResponse(status="ok")
