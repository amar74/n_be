from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.organization import router as orgs_router
from app.routes.scraper import router as scraper_router

# Main API router that combines all route modules
api_router = APIRouter()  # Removed prefix="/api/v1"

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(orgs_router)
api_router.include_router(scraper_router)  # Include the scraper route
# Add more routers here as you create them
# api_router.include_router(post_router)
