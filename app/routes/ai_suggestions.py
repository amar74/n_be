from fastapi import APIRouter, Depends
from app.schemas.ai_suggestions import AISuggestionRequest, AISuggestionResponse
from app.services.ai_suggestions import ai_suggestion_service
from app.models.user import User
from app.dependencies.user_auth import get_current_user
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException

router = APIRouter(prefix="/ai", tags=["ai-suggestions"])

@router.post(
    "/suggestions", 
    response_model=AISuggestionResponse,
    operation_id="getAISuggestions"
)
async def get_ai_suggestions(
    request: AISuggestionRequest, 
    current_user: User = Depends(get_current_user)
) -> AISuggestionResponse:
    try:
        result = await ai_suggestion_service.get_suggestions(request)
        
        logger.info(
            f"AI suggestions generated for context: {request.context[:50]}..."
        )
        
        return result
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in AI suggestions: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Internal server error during AI suggestions generation",
            details=str(e)
        )

@router.get(
    "/suggestions/{suggestion_id}", 
    response_model=AISuggestionResponse,
    operation_id="getAISuggestion"
)
async def get_ai_suggestion(
    suggestion_id: str,
    current_user: User = Depends(get_current_user)
) -> AISuggestionResponse:
    try:
        result = await ai_suggestion_service.get_suggestion_by_id(suggestion_id)
        
        logger.info(f"Retrieved AI suggestion: {suggestion_id}")
        
        return result
        
    except MegapolisHTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving AI suggestion: {e}")
        raise MegapolisHTTPException(
            status_code=500,
            message="Internal server error retrieving AI suggestion",
            details=str(e)
        )
# @author rose11