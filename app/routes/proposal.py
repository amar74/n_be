from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, status, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.auth import AuthUserResponse
from app.schemas.user_permission import UserPermissionResponse
from app.schemas.proposal import (
    ProposalCreate,
    ProposalResponse,
    ProposalListResponse,
    ProposalUpdate,
    ProposalSubmitRequest,
    ProposalApprovalDecision,
    ProposalStatusUpdateRequest,
    ProposalConversionResponse,
    ProposalConvertRequest,
    ProposalSectionCreate,
    ProposalSectionUpdate,
    ProposalDocumentCreate,
    ProposalStatus,
)
from app.models.proposal import ProposalType
from app.services.proposal import ProposalService


router = APIRouter(prefix="/proposals", tags=["Proposals"])


def _service(db: AsyncSession) -> ProposalService:
    return ProposalService(db)


@router.post(
    "/create",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new proposal from an opportunity",
)
async def create_proposal(
    payload: ProposalCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    try:
        # Get user from database
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create proposal via service
        service = _service(db)
        return await service.create_proposal(payload, user)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        from sqlalchemy.exc import IntegrityError
        logger.exception(f"Error creating proposal: {e}")
        
        error_detail = str(e)
        if isinstance(e, IntegrityError) and hasattr(e, 'orig'):
            error_detail = str(e.orig)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create proposal: {error_detail}"
        )


@router.get(
    "/",
    response_model=ProposalListResponse,
    summary="List proposals with pagination",
)
async def list_proposals(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status_filter: Optional[ProposalStatus] = Query(None),
    type_filter: Optional[ProposalType] = Query(None, description="Filter by proposal type (proposal, brochure, interview, campaign)"),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["view"]})),
) -> ProposalListResponse:
    try:
        service = _service(db)
        return await service.list_proposals(
            user=current_user,
            page=page,
            size=size,
            status_filter=status_filter,
            type_filter=type_filter,
            search=search,
        )
    except HTTPException:
        raise
    except Exception as e:
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.exception(f"Error in list_proposals endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list proposals: {str(e)}"
        )


@router.get(
    "/{proposal_id}",
    response_model=ProposalResponse,
    summary="Get proposal detail",
)
async def get_proposal(
    proposal_id: UUID = Path(..., description="Proposal identifier"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["view"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.get_proposal(proposal_id, current_user)


@router.get(
    "/by-opportunity/{opportunity_id}",
    response_model=list[ProposalResponse],
    summary="List proposals linked to an opportunity",
)
async def get_proposals_by_opportunity(
    opportunity_id: UUID = Path(..., description="Opportunity identifier"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["view"]})),
) -> list[ProposalResponse]:
    service = _service(db)
    return await service.get_proposals_by_opportunity(opportunity_id, current_user)


@router.put(
    "/{proposal_id}",
    response_model=ProposalResponse,
    summary="Update proposal metadata",
)
async def update_proposal(
    proposal_id: UUID,
    payload: ProposalUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.update_proposal(proposal_id, payload, current_user)


@router.post(
    "/submit/{proposal_id}",
    response_model=ProposalResponse,
    summary="Submit proposal for approval",
)
async def submit_proposal(
    proposal_id: UUID,
    payload: ProposalSubmitRequest,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.submit_proposal(proposal_id, payload, current_user)


@router.post(
    "/approve/{proposal_id}",
    response_model=ProposalResponse,
    summary="Record approval decision for a proposal stage",
)
async def decide_proposal_approval(
    proposal_id: UUID,
    payload: ProposalApprovalDecision,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.decide_approval(proposal_id, payload, current_user)


@router.post(
    "/status/{proposal_id}",
    response_model=ProposalResponse,
    summary="Update proposal lifecycle status",
)
async def update_proposal_status(
    proposal_id: UUID,
    payload: ProposalStatusUpdateRequest,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.update_status(proposal_id, payload, current_user)


@router.post(
    "/convert/{proposal_id}",
    response_model=ProposalConversionResponse,
    summary="Convert an approved proposal into a project",
)
async def convert_proposal(
    proposal_id: UUID,
    payload: ProposalConvertRequest,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalConversionResponse:
    service = _service(db)
    return await service.convert_to_project(proposal_id, payload.conversion_metadata, current_user)


@router.post(
    "/{proposal_id}/sections",
    response_model=ProposalResponse,
    summary="Add a new section to a proposal",
)
async def add_proposal_section(
    proposal_id: UUID,
    payload: ProposalSectionCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.add_or_update_section(proposal_id, None, payload, current_user)


@router.put(
    "/{proposal_id}/sections/{section_id}",
    response_model=ProposalResponse,
    summary="Update an existing proposal section",
)
async def update_proposal_section(
    proposal_id: UUID,
    section_id: UUID,
    payload: ProposalSectionUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.add_or_update_section(proposal_id, section_id, payload, current_user)


@router.post(
    "/{proposal_id}/documents/upload",
    response_model=ProposalResponse,
    summary="Upload and attach a document to proposal",
)
async def upload_proposal_document(
    proposal_id: UUID,
    file: UploadFile = File(..., description="File to upload"),
    category: str = Form(default="attachment", description="Document category"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: AuthUserResponse = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    """
    Upload document to proposal - CLEAN IMPLEMENTATION
    Uses UploadFile (not FormData) and returns ProposalResponse (JSON-serializable)
    """
    from app.utils.security import validate_file_type, validate_file_size, sanitize_filename
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    
    # Extract values early to avoid any FormData references
    filename = file.filename or ""
    content_type = file.content_type or "application/octet-stream"
    
    try:
        logger.info(f"Upload request - proposal_id: {proposal_id}, filename: {filename}, category: {category}")
        
        # Validate filename
        if not filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")
        
        # Sanitize filename
        safe_name = sanitize_filename(filename)
        
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.mp3']
        if not validate_file_type(safe_name, allowed_extensions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content (bytes - JSON serializable)
        file_content: bytes = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        if not validate_file_size(file_size, max_size_mb=10):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 10MB limit"
            )
        
        # Get user model
        user_id_uuid = UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id_uuid))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {current_user.id} not found"
            )
        
        # Call service with all primitive/bytes values (no FormData)
        service = _service(db)
        result = await service.upload_document(
            proposal_id=proposal_id,
            file_content=file_content,
            file_name=safe_name,
            content_type=content_type,
            category=category,
            user=user
        )
        
        # Return ProposalResponse (Pydantic model - JSON serializable)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch all other exceptions and convert to HTTPException
        error_type = type(e).__name__
        error_msg = str(e)  # Convert to string to ensure JSON serializable
        
        # Log error (logger will handle serialization)
        logger.exception(f"Error uploading document: {error_type}: {error_msg}")
        
        # Return HTTPException with string detail (JSON serializable)
        from app.environment import environment
        if environment.ENVIRONMENT == "dev":
            detail = f"{error_type}: {error_msg}"
        else:
            detail = "Failed to upload document. Please check server logs."
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


@router.post(
    "/{proposal_id}/documents",
    response_model=ProposalResponse,
    summary="Attach a document to proposal",
)
async def add_proposal_document(
    proposal_id: UUID,
    payload: ProposalDocumentCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.add_document(proposal_id, payload, current_user)
