from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.schemas.opportunity_tabs import *
from app.services.opportunity_tabs import OpportunityTabsService
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.db.session import get_request_transaction
from app.utils.logger import get_logger

logger = get_logger("opportunity_tabs_routes")

router = APIRouter(prefix="/opportunities", tags=["Opportunity Tabs"])

# Overview Tab Routes
@router.get("/{opportunity_id}/overview", response_model=OpportunityOverviewResponse)
async def get_opportunity_overview(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_overview(opportunity_id)

@router.put("/{opportunity_id}/overview", response_model=OpportunityOverviewResponse)
async def update_opportunity_overview(
    opportunity_id: UUID,
    update_data: OpportunityOverviewUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]}))
):
    service = OpportunityTabsService(db)
    return await service.update_overview(opportunity_id, update_data)

# Stakeholders Tab Routes
@router.get("/{opportunity_id}/stakeholders", response_model=List[StakeholderResponse])
async def get_opportunity_stakeholders(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_stakeholders(opportunity_id)

@router.post("/{opportunity_id}/stakeholders", response_model=StakeholderResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity_stakeholder(
    opportunity_id: UUID,
    stakeholder_data: StakeholderCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
):
    service = OpportunityTabsService(db)
    return await service.create_stakeholder(opportunity_id, stakeholder_data)

@router.put("/{opportunity_id}/stakeholders/{stakeholder_id}", response_model=StakeholderResponse)
async def update_opportunity_stakeholder(
    opportunity_id: UUID,
    stakeholder_id: UUID,
    update_data: StakeholderUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]}))
):
    service = OpportunityTabsService(db)
    return await service.update_stakeholder(stakeholder_id, update_data)

@router.delete("/{opportunity_id}/stakeholders/{stakeholder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity_stakeholder(
    opportunity_id: UUID,
    stakeholder_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["delete"]}))
):
    service = OpportunityTabsService(db)
    success = await service.delete_stakeholder(stakeholder_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stakeholder not found"
        )

# Driver Routes
@router.get("/{opportunity_id}/drivers", response_model=List[DriverResponse])
async def get_opportunity_drivers(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_drivers(opportunity_id)

@router.post("/{opportunity_id}/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity_driver(
    opportunity_id: UUID,
    driver_data: DriverCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
):
    service = OpportunityTabsService(db)
    return await service.create_driver(opportunity_id, driver_data)

# Competition Tab Routes
@router.get("/{opportunity_id}/competitors", response_model=List[CompetitorResponse])
async def get_opportunity_competitors(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_competitors(opportunity_id)

@router.post("/{opportunity_id}/competitors", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity_competitor(
    opportunity_id: UUID,
    competitor_data: CompetitorCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
):
    service = OpportunityTabsService(db)
    return await service.create_competitor(opportunity_id, competitor_data)

# Strategy Routes
@router.get("/{opportunity_id}/strategies", response_model=List[StrategyResponse])
async def get_opportunity_strategies(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_strategies(opportunity_id)

@router.post("/{opportunity_id}/strategies", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity_strategy(
    opportunity_id: UUID,
    strategy_data: StrategyCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
):
    service = OpportunityTabsService(db)
    return await service.create_strategy(opportunity_id, strategy_data)

# Delivery Model Tab Routes
@router.get("/{opportunity_id}/delivery-model", response_model=DeliveryModelResponse)
async def get_opportunity_delivery_model(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    delivery_model = await service.get_delivery_model(opportunity_id)
    
    if not delivery_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery model not found"
        )
    
    return delivery_model

@router.put("/{opportunity_id}/delivery-model", response_model=DeliveryModelResponse)
async def update_opportunity_delivery_model(
    opportunity_id: UUID,
    update_data: DeliveryModelUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]}))
):
    service = OpportunityTabsService(db)
    return await service.update_delivery_model(opportunity_id, update_data)

# Team & References Tab Routes
@router.get("/{opportunity_id}/team", response_model=List[TeamMemberResponse])
async def get_opportunity_team_members(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_team_members(opportunity_id)

@router.post("/{opportunity_id}/team", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity_team_member(
    opportunity_id: UUID,
    member_data: TeamMemberCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
):
    service = OpportunityTabsService(db)
    return await service.create_team_member(opportunity_id, member_data)

@router.get("/{opportunity_id}/references", response_model=List[ReferenceResponse])
async def get_opportunity_references(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_references(opportunity_id)

@router.post("/{opportunity_id}/references", response_model=ReferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity_reference(
    opportunity_id: UUID,
    reference_data: ReferenceCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
):
    service = OpportunityTabsService(db)
    return await service.create_reference(opportunity_id, reference_data)

# Financial Summary Tab Routes
@router.get("/{opportunity_id}/financial", response_model=FinancialSummaryResponse)
async def get_opportunity_financial_summary(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    financial = await service.get_financial_summary(opportunity_id)
    
    if not financial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial summary not found"
        )
    
    return financial

@router.put("/{opportunity_id}/financial", response_model=FinancialSummaryResponse)
async def update_opportunity_financial_summary(
    opportunity_id: UUID,
    update_data: FinancialSummaryUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["update"]}))
):
    service = OpportunityTabsService(db)
    return await service.update_financial_summary(opportunity_id, update_data)

# Legal & Risks Tab Routes
@router.get("/{opportunity_id}/risks", response_model=List[RiskResponse])
async def get_opportunity_risks(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_risks(opportunity_id)

@router.post("/{opportunity_id}/risks", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity_risk(
    opportunity_id: UUID,
    risk_data: RiskCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
):
    service = OpportunityTabsService(db)
    return await service.create_risk(opportunity_id, risk_data)

@router.get("/{opportunity_id}/legal-checklist", response_model=List[LegalChecklistItemResponse])
async def get_opportunity_legal_checklist(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    return await service.get_legal_checklist(opportunity_id)

@router.post("/{opportunity_id}/legal-checklist", response_model=LegalChecklistItemResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity_legal_checklist_item(
    opportunity_id: UUID,
    item_data: LegalChecklistItemCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
):
    service = OpportunityTabsService(db)
    return await service.create_legal_checklist_item(opportunity_id, item_data)

# Combined Tab Data Route
@router.get("/{opportunity_id}/all-tabs", response_model=OpportunityTabDataResponse)
async def get_all_opportunity_tab_data(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["read"]}))
):
    service = OpportunityTabsService(db)
    
    # Fetch all tab data concurrently
    overview = await service.get_overview(opportunity_id)
    stakeholders = await service.get_stakeholders(opportunity_id)
    drivers = await service.get_drivers(opportunity_id)
    competitors = await service.get_competitors(opportunity_id)
    strategies = await service.get_strategies(opportunity_id)
    delivery_model = await service.get_delivery_model(opportunity_id)
    team_members = await service.get_team_members(opportunity_id)
    references = await service.get_references(opportunity_id)
    financial = await service.get_financial_summary(opportunity_id)
    risks = await service.get_risks(opportunity_id)
    legal_checklist = await service.get_legal_checklist(opportunity_id)
    
    return OpportunityTabDataResponse(
        overview=overview,
        stakeholders=stakeholders,
        drivers=drivers,
        competitors=competitors,
        strategies=strategies,
        delivery_model=delivery_model,
        team_members=team_members,
        references=references,
        financial=financial,
        risks=risks,
        legal_checklist=legal_checklist
    )