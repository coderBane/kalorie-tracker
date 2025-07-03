from typing import Any

from fastapi import APIRouter


utils_router = APIRouter(tags=["Utils"])


@utils_router.get("/health", responses={
    200: {
        "content": {
            "application/json": {
                "example": {"status": "Healthy"}
            }
        },
    }
})
async def health_check() -> Any:
    """Health check endpoint to verify the API is running.
    """
    return {"status": "Healthy"}
