from fastapi import APIRouter, Depends
from app.schemas.data_enrichment import AccountEnhancementRequest, AccountEnhancementResponse
from app.services.data_enrichment import data_enrichment_service
from app.models.user import User
from app.dependencies.user_auth import get_current_user
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException

router = APIRouter(prefix="/ai", tags=["ai-suggestions"])

@router.post(
    "/enhance-opportunity-data", 
    response_model=AccountEnhancementResponse,
    operation_id="enhanceOpportunityData"
)
async def enhance_opportunity_data(
    request: AccountEnhancementRequest, 
    current_user: User = Depends(get_current_user)
) -> AccountEnhancementResponse:
    try:
        result = await ai_suggestion_service.enhance_opportunity_data(request)
        
        logger.info(
            f"Opportunity enhancement completed for {request.company_website}: "
            f"{len(result.enhanced_data)} fields updated, "
            f"{result.suggestions_applied} auto-applied in {result.processing_time_ms}ms"
        )
        
        return result
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in opportunity enhancement: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Internal server error during opportunity enhancement",
            details=str(e)
        )

@router.post(
    "/enhance-account-data", 
    response_model=AccountEnhancementResponse,
    operation_id="enhanceAccountData"
)
async def enhance_account_data(
    request: AccountEnhancementRequest, 
    current_user: User = Depends(get_current_user)
) -> AccountEnhancementResponse:
    try:
            result = await data_enrichment_service.enhance_account_data(request)
        
        logger.info(
            f"Account enhancement completed for {request.company_website}: "
            f"{len(result.enhanced_data)} fields updated, "
            f"{result.suggestions_applied} auto-applied in {result.processing_time_ms}ms"
        )
        
        return result
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in account enhancement: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Internal server error during account enhancement",
            details=str(e)
        )
# @author rose11