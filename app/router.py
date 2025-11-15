from fastapi import APIRouter
from app.routes.auth import router as auth_router
from app.routes.password_reset import router as password_reset_router
from app.routes.data_enrichment import router as data_enrichment_router
from app.routes.organization import router as orgs_router
from app.routes.account import router as account_router
from app.routes.account_note import router as account_note_router
from app.routes.account_document import router as account_document_router
from app.routes.account_team import router as account_team_router
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
from app.routes.survey import router as survey_router
from app.routes.public_survey import router as public_survey_router
from app.routes.profile_stats import router as profile_stats_router
from app.routes.dashboard import router as dashboard_router
from app.routes.employees import router as employees_router
from app.routes.onboarding import router as onboarding_router
from app.routes.employee_surveys import router as employee_surveys_router
from app.routes.staff_planning import router as staff_planning_router
from app.routes.finance_dashboard import router as finance_dashboard_router
from app.routes.finance_planning import router as finance_planning_router
from app.routes.delivery_model_templates import router as delivery_model_templates_router
from app.routes.proposal import router as proposal_router
from app.routes.opportunity_ingestion import router as opportunity_ingestion_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(password_reset_router)
api_router.include_router(profile_stats_router)
api_router.include_router(dashboard_router)
api_router.include_router(data_enrichment_router)
api_router.include_router(orgs_router)
api_router.include_router(account_router)
api_router.include_router(account_note_router)
api_router.include_router(account_document_router)
api_router.include_router(account_team_router)
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
api_router.include_router(survey_router)
api_router.include_router(public_survey_router)
api_router.include_router(employees_router)
api_router.include_router(onboarding_router)
api_router.include_router(employee_surveys_router)
api_router.include_router(staff_planning_router)
api_router.include_router(finance_dashboard_router)
api_router.include_router(finance_planning_router)
api_router.include_router(delivery_model_templates_router)
api_router.include_router(proposal_router)
api_router.include_router(opportunity_ingestion_router)