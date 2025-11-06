from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel

from app.models.survey import Survey, SurveyResponse, SurveyStatus
from app.db.session import get_request_transaction
from app.utils.logger import logger
from sqlalchemy import select
import secrets


router = APIRouter(prefix="/public/surveys", tags=["Public Surveys"])


class PublicSurveyResponse(BaseModel):
    id: str
    survey_code: str
    title: str
    description: Optional[str]
    questions: List[Dict[str, Any]]
    status: str


class SurveySubmission(BaseModel):
    response_data: Dict[str, Any]
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None


@router.get("/{survey_id}", response_model=PublicSurveyResponse)
async def get_public_survey(survey_id: UUID):
    """Get survey details for public access (no auth required)"""
    try:
        db = get_request_transaction()
        
        stmt = select(Survey).where(Survey.id == survey_id)
        result = await db.execute(stmt)
        survey = result.scalar_one_or_none()
        
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        # Only return active or draft surveys to public
        if survey.status not in [SurveyStatus.active, SurveyStatus.draft]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Survey is {survey.status.value}"
            )
        
        return PublicSurveyResponse(
            id=str(survey.id),
            survey_code=survey.survey_code,
            title=survey.title,
            description=survey.description,
            questions=survey.questions or [],
            status=survey.status.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Escape curly braces in error message to avoid format spec errors
        error_msg = str(e).replace('{', '{{').replace('}', '}}')
        logger.error(f"Error fetching public survey: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load survey"
        )


@router.post("/{survey_id}/submit")
async def submit_public_survey(
    survey_id: UUID,
    submission: SurveySubmission
):
    """Submit a survey response (no auth required)"""
    try:
        db = get_request_transaction()
        
        # Verify survey exists and is active
        stmt = select(Survey).where(Survey.id == survey_id)
        result = await db.execute(stmt)
        survey = result.scalar_one_or_none()
        
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found"
            )
        
        if survey.status != SurveyStatus.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Survey is not active (current status: {survey.status.value})"
            )
        
        # Create response with a unique response code
        response_code = f"RESP_{secrets.token_urlsafe(8).upper()}"
        
        # Store contact information in metadata
        meta_data = {
            "contact_name": submission.contact_name,
            "contact_email": submission.contact_email,
            "contact_phone": submission.contact_phone,
            "submission_type": "public_link"
        }
        
        survey_response = SurveyResponse(
            response_code=response_code,
            survey_id=survey_id,
            account_id=None,  # Public submission
            contact_id=None,  # Public submission
            response_data=submission.response_data,
            finished=True,
            meta=meta_data,
            time_to_complete=None
        )
        
        db.add(survey_response)
        await db.flush()
        await db.refresh(survey_response)
        
        logger.info(f"Public survey response submitted: {survey_response.id}")
        
        return {
            "success": True,
            "message": "Thank you for your response!",
            "response_code": response_code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Escape curly braces in error message to avoid format spec errors
        error_msg = str(e).replace('{', '{{').replace('}', '}}')
        logger.error(f"Error submitting public survey: {error_msg}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit response"
        )
