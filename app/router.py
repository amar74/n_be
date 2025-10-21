from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.data_enrichment import router as data_enrichment_router
from app.routes.organization import router as orgs_router
from app.routes.account import router as account_router
from app.routes.account_note import router as account_note_router
from app.routes.account_document import router as account_document_router
from app.routes.opportunity import router as opportunity_router
from app.routes.opportunity_tabs import router as opportunity_tabs_router
from app.routes.opportunity_document import router as opportunity_document_router
from app.routes.super_admin import router as super_admin_router
from app.routes.vendor import router as vendor_router
from app.routes.ai_health_scoring import router as ai_health_scoring_router
from app.routes.ai_features import router as ai_features_router
from app.routes.health_score import router as health_score_router
from app.routes.user_permission import router as user_permission_router
from app.routes.user import router as user_router
from app.routes.admin import router as admin_router
from app.routes.ai_suggestions import router as ai_suggestions_router
from app.routes.scraper import router as scraper_router
from app.routes.formbricks import router as formbricks_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(data_enrichment_router)
api_router.include_router(orgs_router)
api_router.include_router(account_router)
api_router.include_router(account_note_router)
api_router.include_router(account_document_router)
api_router.include_router(opportunity_router)
api_router.include_router(opportunity_tabs_router)
api_router.include_router(opportunity_document_router)
api_router.include_router(super_admin_router)
api_router.include_router(vendor_router)
api_router.include_router(ai_health_scoring_router)
api_router.include_router(ai_features_router)
api_router.include_router(health_score_router)
api_router.include_router(user_permission_router)
api_router.include_router(user_router)
api_router.include_router(admin_router)
api_router.include_router(ai_suggestions_router)
api_router.include_router(scraper_router)
api_router.include_router(formbricks_router)