from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.data_enrichment import router as data_enrichment_router
from app.routes.organization import router as orgs_router
from app.routes.account import router as account_router
from app.routes.opportunity import router as opportunity_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(data_enrichment_router)
api_router.include_router(orgs_router)
api_router.include_router(account_router)
api_router.include_router(opportunity_router)