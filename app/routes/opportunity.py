from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional, List

from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityResponse,
    OpportunityListResponse,
    OpportunityStageUpdate,
    OpportunitySearchRequest,
    OpportunitySearchResult,
    OpportunitySearchResponse,
    OpportunityAnalytics,
    OpportunityInsightsResponse,
    OpportunityPipelineResponse,
    OpportunityForecastResponse
)
from app.services.opportunity import OpportunityService
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.models.opportunity import Opportunity
from app.schemas.user_permission import UserPermissionResponse
from app.db.session import get_request_transaction
from app.utils.logger import get_logger

logger = get_logger("opportunity_routes")

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["create"]}))
) -> OpportunityResponse:
    
    service = OpportunityService(db)
    return await service.create_opportunity(opportunity_data, current_user)

@router.get("/", response_model=OpportunityListResponse)
async def list_opportunities(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    stage: Optional[str] = Query(None, description="Filter by stage"),
    search: Optional[str] = Query(None, description="Search query"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityListResponse:
    
    stage_enum = None
    if stage:
        try:
            from app.models.opportunity import OpportunityStage
            stage_enum = OpportunityStage(stage)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stage: {stage}"
            )
    
    service = OpportunityService(db)
    return await service.list_opportunities(
        user=current_user,
        page=page,
        size=size,
        stage=stage_enum,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: str = Path(..., description="Opportunity ID (UUID or custom ID like OPP-NY0001)"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityResponse:
    
    service = OpportunityService(db)
    
    if opportunity_id.startswith('OPP-NY'):
        opportunity = await service.get_opportunity_by_custom_id(opportunity_id, current_user)
    else:
        try:
            uuid_id = UUID(opportunity_id)
            opportunity = await service.get_opportunity_by_id(uuid_id, current_user)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid opportunity ID format"
            )
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity

@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: UUID = Path(..., description="Opportunity ID"),
    opportunity_data: OpportunityUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["edit"]}))
) -> OpportunityResponse:
    
    service = OpportunityService(db)
    opportunity = await service.update_opportunity(opportunity_id, opportunity_data, current_user)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity

@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: UUID = Path(..., description="Opportunity ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["delete"]}))
) -> None:
    
    service = OpportunityService(db)
    success = await service.delete_opportunity(opportunity_id, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

@router.put("/{opportunity_id}/stage", response_model=OpportunityResponse)
async def update_opportunity_stage(
    opportunity_id: UUID = Path(..., description="Opportunity ID"),
    stage_data: OpportunityStageUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["edit"]}))
) -> OpportunityResponse:
    
    service = OpportunityService(db)
    opportunity = await service.update_opportunity_stage(opportunity_id, stage_data, current_user)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity

@router.get("/analytics/dashboard", response_model=OpportunityAnalytics)
async def get_opportunity_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityAnalytics:
    
    service = OpportunityService(db)
    return await service.get_opportunity_analytics(current_user, days)

@router.get("/pipeline/view", response_model=OpportunityPipelineResponse)
async def get_opportunity_pipeline(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityPipelineResponse:
    
    service = OpportunityService(db)
    return await service.get_opportunity_pipeline(current_user)

@router.post("/search/ai", response_model=List[OpportunitySearchResult])
async def search_opportunities_ai(
    search_request: OpportunitySearchRequest,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> List[OpportunitySearchResult]:
    
    service = OpportunityService(db)
    results = await service.search_opportunities_ai(search_request, current_user)
    
    return results

@router.get("/{opportunity_id}/insights", response_model=OpportunityInsightsResponse)
async def get_opportunity_insights(
    opportunity_id: UUID = Path(..., description="Opportunity ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityInsightsResponse:
    
    service = OpportunityService(db)
    return await service.generate_opportunity_insights(opportunity_id, current_user)

@router.get("/{opportunity_id}/forecast", response_model=OpportunityForecastResponse)
async def get_opportunity_forecast(
    opportunity_id: UUID = Path(..., description="Opportunity ID"),
    period: str = Query("quarterly", pattern="^(monthly|quarterly|yearly)$", description="Forecast period"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityForecastResponse:
    
    from app.schemas.opportunity import OpportunityForecast
    from datetime import datetime, timedelta
    
    forecast = OpportunityForecast(
        period=period,
        forecasted_revenue=100000.0,  # Placeholder
        confidence_level=75.0,  # Placeholder
        scenarios={
            "best_case": 150000.0,
            "worst_case": 75000.0,
            "most_likely": 100000.0
        },
        factors=[
            "Market conditions",
            "Competition level",
            "Client budget",
            "Timeline constraints"
        ]
    )
    
    return OpportunityForecastResponse(
        opportunities=[opportunity_id],
        forecast=forecast,
        generated_at=datetime.utcnow(),
        next_review_date=datetime.utcnow() + timedelta(days=30)
    )

@router.get("/export/csv")
async def export_opportunities_csv(
    stage: Optional[str] = Query(None, description="Filter by stage"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
):
    
    service = OpportunityService(db)
    
    opportunities_list = await service.list_opportunities(
        user=current_user,
        page=1,
        size=1000,  # Large number to get all
        stage=stage
    )
    
    return {
        "message": f"Export initiated for {opportunities_list.total} opportunities",
        "download_url": f"/api/v1/opportunities/download/{current_user.id}/export.csv",
        "expires_at": "2024-12-31T23:59:59Z"
    }

@router.get("/by-account/{account_id}", response_model=OpportunityListResponse)
async def list_opportunities_by_account(
    account_id: UUID = Path(..., description="Account ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    stage: Optional[str] = Query(None, description="Filter by stage"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"opportunities": ["view"]}))
) -> OpportunityListResponse:
    
    stage_enum = None
    if stage:
        try:
            from app.models.opportunity import OpportunityStage
            stage_enum = OpportunityStage(stage)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stage: {stage}"
            )
    
    offset = (page - 1) * size
    
    from sqlalchemy import select, func
    query = select(Opportunity).where(
        Opportunity.org_id == current_user.org_id,
        Opportunity.account_id == account_id
    )
    
    if stage_enum:
        query = query.where(Opportunity.stage == stage_enum)
    
    query = query.order_by(Opportunity.created_at.desc()).limit(size).offset(offset)
    result = await db.execute(query)
    opportunities = result.scalars().all()
    
    total_stmt = select(func.count(Opportunity.id)).where(
        Opportunity.org_id == current_user.org_id,
        Opportunity.account_id == account_id
    )
    
    if stage_enum:
        total_stmt = total_stmt.where(Opportunity.stage == stage_enum)
    
    total_result = await db.execute(total_stmt)
    total = total_result.scalar() or 0
    
    opportunity_responses = [OpportunityResponse.model_validate(opp) for opp in opportunities]
    
    return OpportunityListResponse(
        opportunities=opportunity_responses,
        total=total,
        page=page,
        size=size,
        total_pages=(total + size - 1) // size if total > 0 else 0
    )

@router.get("/health/check")
async def health_check():
    
    return {
        "status": "healthy",
        "module": "opportunities",
        "timestamp": "2024-01-01T00:00:00Z"
    }