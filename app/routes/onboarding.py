from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Optional
from uuid import UUID
import logging

from app.models.user import User
from app.dependencies.user_auth import get_current_user
from app.schemas.candidate import (
    ProfileExtractRequest,
    AIEnrichmentResponse,
    CandidateResponse,
    CandidateCreate
)
from app.services.candidate_service import candidate_service
from app.models.candidate import Candidate

router = APIRouter(prefix="/onboarding", tags=["onboarding"])
logger = logging.getLogger(__name__)


@router.post("/profile-extract", response_model=AIEnrichmentResponse)
async def extract_profile(
    request: ProfileExtractRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Extract candidate information from LinkedIn or portfolio URL using Gemini AI
    """
    try:
        logger.info(f"Profile extraction requested by {current_user.email}")
        enrichment = await candidate_service.extract_from_profile(
            profile_data=request,
            company_id=current_user.org_id
        )
        return enrichment
    except Exception as e:
        logger.error(f"Profile extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile extraction failed: {str(e)}"
        )


@router.post("/upload-cv", response_model=AIEnrichmentResponse)
async def upload_cv(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse CV/Resume using Gemini AI
    Returns comprehensive extracted data
    """
    try:
        logger.info(f"CV upload: {file.filename} by {current_user.email}")
        
        # Read file content
        file_content = await file.read()
        
        # Parse with Gemini
        enrichment = await candidate_service.parse_uploaded_cv(
            file_content=file_content,
            file_name=file.filename,
            name=name
        )
        
        logger.info(f"✅ CV parsed successfully: {file.filename}")
        return enrichment
        
    except Exception as e:
        logger.error(f"CV upload/parsing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV parsing failed: {str(e)}"
        )


@router.get("/candidates", response_model=list[CandidateResponse])
async def get_candidates(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all candidates for current company"""
    try:
        candidates = await Candidate.get_all(
            company_id=current_user.org_id,
            status=status_filter,
            skip=skip,
            limit=limit
        )
        return [CandidateResponse.model_validate(c.to_dict()) for c in candidates]
    except Exception as e:
        logger.error(f"Error fetching candidates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch candidates: {str(e)}"
        )


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get candidate details"""
    try:
        candidate = await Candidate.get_by_id(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return CandidateResponse.model_validate(candidate.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch candidate: {str(e)}"
        )

