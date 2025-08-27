from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.orgs import router as orgs_router
from app.routes.admin import router as admin_router
from app.routes.scraper import router as scraper_router

# Main API router that combines all route modules
api_router = APIRouter()  # Removed prefix="/api/v1"

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(orgs_router)
api_router.include_router(admin_router)
api_router.include_router(scraper_router)  # Include the scraper route

