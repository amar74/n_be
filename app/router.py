from fastapi import APIRouter

from app.routes.user import router as user_router
from app.routes.auth import router as auth_router

# Main API router that combines all route modules
api_router = APIRouter()  # Removed prefix="/api/v1"

# Include all route modules
api_router.include_router(user_router)
api_router.include_router(auth_router)

# Add more routers here as you create them
# api_router.include_router(post_router)
# api_router.include_router(auth_router)
