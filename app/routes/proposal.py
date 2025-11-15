from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
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
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["edit"]})),
) -> ProposalResponse:
    service = _service(db)
    return await service.create_proposal(payload, current_user)


@router.get(
    "/",
    response_model=ProposalListResponse,
    summary="List proposals with pagination",
)
async def list_proposals(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status_filter: Optional[ProposalStatus] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"proposals": ["view"]})),
) -> ProposalListResponse:
    service = _service(db)
    return await service.list_proposals(
        user=current_user,
        page=page,
        size=size,
        status_filter=status_filter,
        search=search,
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
