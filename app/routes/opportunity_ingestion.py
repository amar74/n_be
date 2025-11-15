from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_request_transaction
from app.dependencies.permissions import get_user_permission
from app.dependencies.user_auth import get_current_user
from app.models.opportunity_source import TempOpportunityStatus
from app.models.user import User
from app.schemas.opportunity import OpportunityResponse
from app.schemas.opportunity_ingestion import (
    OpportunitySourceCreate,
    OpportunitySourceUpdate,
    OpportunitySourceResponse,
    ScrapeHistoryResponse,
    OpportunityTempCreate,
    OpportunityTempResponse,
    OpportunityTempUpdate,
    TempOpportunityPromoteRequest,
    OpportunityAgentCreate,
    OpportunityAgentUpdate,
    OpportunityAgentResponse,
    OpportunityAgentRunResponse,
    TempStatus,
)
from app.schemas.user_permission import UserPermissionResponse
from app.services.opportunity_ingestion import OpportunityIngestionService

router = APIRouter(prefix="/opportunities/ingestion", tags=["Opportunities"])


def _require_org(user: User) -> UUID:
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an organization.",
        )
    return user.org_id


@router.get("/sources", response_model=list[OpportunitySourceResponse])
async def list_sources(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    return await service.list_sources(org_id)


@router.post(
    "/sources",
    response_model=OpportunitySourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_source(
    payload: OpportunitySourceCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    return await service.create_source(org_id, current_user.id, payload)


@router.put("/sources/{source_id}", response_model=OpportunitySourceResponse)
async def update_source(
    source_id: UUID,
    payload: OpportunitySourceUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    updated = await service.update_source(source_id, org_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.")
    return updated


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["delete"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    success = await service.delete_source(source_id, org_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.")


@router.get(
    "/sources/{source_id}/history",
    response_model=list[ScrapeHistoryResponse],
)
async def list_source_history(
    source_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    return await service.list_scrape_history(org_id, source_id, limit)


@router.get(
    "/history",
    response_model=list[ScrapeHistoryResponse],
)
async def list_history(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    return await service.list_scrape_history(org_id, None, limit)


@router.get("/temp", response_model=list[OpportunityTempResponse])
async def list_temp_opportunities(
    status: Optional[TempStatus] = Query(default=None),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    status_enum = TempOpportunityStatus(status.value) if status else None
    return await service.list_temp_opportunities(org_id, status_enum, limit)


@router.post(
    "/temp",
    response_model=OpportunityTempResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_temp_opportunity(
    payload: OpportunityTempCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    return await service.create_temp_opportunity(org_id, payload)


@router.patch("/temp/{temp_id}", response_model=OpportunityTempResponse)
async def update_temp_opportunity(
    temp_id: UUID,
    payload: OpportunityTempUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    updated = await service.update_temp_opportunity(temp_id, org_id, current_user.id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temp opportunity not found.")
    return updated


@router.post("/temp/{temp_id}/refresh", response_model=OpportunityTempResponse)
async def refresh_temp_opportunity(
    temp_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    try:
        refreshed = await service.refresh_temp_opportunity(temp_id, org_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not refreshed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temp opportunity not found.")
    return refreshed


@router.post("/temp/{temp_id}/promote", response_model=OpportunityResponse)
async def promote_temp_opportunity(
    temp_id: UUID,
    payload: Optional[TempOpportunityPromoteRequest] = Body(None),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    account_id = payload.account_id if payload else None
    promoted = await service.promote_temp_opportunity(temp_id, current_user, account_id)
    if not promoted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temp opportunity not found.")
    return promoted


@router.get("/agents", response_model=list[OpportunityAgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    return await service.list_agents(org_id)


@router.post(
    "/agents",
    response_model=OpportunityAgentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent(
    payload: OpportunityAgentCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    return await service.create_agent(org_id, current_user.id, payload)


@router.put("/agents/{agent_id}", response_model=OpportunityAgentResponse)
async def update_agent(
    agent_id: UUID,
    payload: OpportunityAgentUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    updated = await service.update_agent(agent_id, org_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")
    return updated


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["delete"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    success = await service.delete_agent(agent_id, org_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found.")


@router.get(
    "/agents/{agent_id}/runs",
    response_model=list[OpportunityAgentRunResponse],
)
async def list_agent_runs(
    agent_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]})),
):
    service = OpportunityIngestionService(db)
    org_id = _require_org(current_user)
    return await service.list_agent_runs(org_id, agent_id, limit)


