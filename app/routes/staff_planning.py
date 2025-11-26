"""
Staff Planning API Routes
Handles staffing plan CRUD operations and cost calculations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from app.db.session import get_request_transaction
from app.models.staff_planning import StaffPlan, StaffAllocation
from app.models.user import User
from app.schemas.staff_planning import (
    StaffPlanCreate,
    StaffPlanUpdate,
    StaffPlanResponse,
    StaffAllocationCreate,
    StaffAllocationUpdate,
    StaffAllocationResponse,
    StaffPlanWithAllocations,
)
from app.dependencies.user_auth import get_current_user
from app.services.gemini_service import GeminiService

router = APIRouter(prefix="/staff-planning", tags=["Staff Planning"])
gemini_service = GeminiService()


def calculate_allocation_total_cost_with_escalation(
    monthly_cost: float,
    start_month: int,
    end_month: int,
    escalation_periods: Optional[List[Dict]] = None,
    escalation_rate: Optional[float] = None,
    escalation_start_month: Optional[int] = None,
) -> float:
    """Calculate the total cost for a single allocation with escalation applied.
    
    This matches the logic in calculate_staff_plan_costs to ensure consistency.
    """
    if monthly_cost <= 0 or end_month < start_month:
        return 0.0
    
    # Parse escalation periods
    import json
    periods = None
    if escalation_periods:
        if isinstance(escalation_periods, str):
            periods = json.loads(escalation_periods)
        else:
            periods = escalation_periods
    elif escalation_rate is not None and escalation_rate > 0:
        # Backward compatibility: convert single rate to periods format
        esc_start = escalation_start_month or start_month
        if esc_start < start_month:
            esc_start = start_month
        periods = [{
            "start_month": esc_start,
            "end_month": end_month,
            "rate": escalation_rate
        }]
    
    # Sort periods by start_month
    if periods:
        periods = sorted(periods, key=lambda p: p.get("start_month", 0))
    
    total_cost = 0.0
    
    # Calculate cost for each month with escalation
    for month in range(start_month, end_month + 1):
        multiplier = 1.0
        
        if periods and len(periods) > 0:
            # Multiple periods: calculate cumulative escalation sequentially
            for period in periods:
                period_start = period.get("start_month", start_month)
                period_end = period.get("end_month", end_month)
                period_rate = period.get("rate", 0.0)
                
                # Skip periods that haven't started yet
                if month < period_start:
                    continue
                
                if period_end < month:
                    # This period is completely in the past, apply full period escalation
                    if period_rate > 0:
                        period_months = period_end - period_start + 1
                        monthly_rate = (1 + (period_rate / 100.0)) ** (1 / 12.0)
                        # Apply compounding for all months in this period
                        multiplier *= monthly_rate ** period_months
                else:
                    # Current month is within this period
                    if period_rate > 0:
                        months_in_period_up_to_month = month - period_start + 1
                        monthly_rate = (1 + (period_rate / 100.0)) ** (1 / 12.0)
                        # Apply compounding for months in this period up to current month
                        multiplier *= monthly_rate ** (months_in_period_up_to_month - 1)
                    # We've reached the current month, no need to process further periods
                    break
        
        monthly_amount = monthly_cost * multiplier
        total_cost += monthly_amount
    
    return round(total_cost, 2)


def calculate_staff_plan_costs(
    staff_allocations: List[StaffAllocation],
    duration_months: int,
    overhead_rate: float,
    profit_margin: float,
    annual_escalation_rate: Optional[float] = None,
):
    """Calculate all costs for a staff plan including yearly breakdown.

    Each allocation must define its own escalation rate. Employee-level escalation rates are required.
    Project-level escalation is deprecated and no longer used as a fallback.
    """

    if duration_months <= 0:
        return {
            "total_labor_cost": 0.0,
            "total_overhead": 0.0,
            "total_cost": 0.0,
            "total_profit": 0.0,
            "total_price": 0.0,
            "yearly_breakdown": [],
        }

    monthly_labor = [0.0 for _ in range(duration_months)]

    for allocation in staff_allocations:
        if allocation.monthly_cost is None or allocation.monthly_cost <= 0:
            continue

        start_month = max(1, allocation.start_month or 1)
        end_month = min(duration_months, allocation.end_month or duration_months)
        if end_month < start_month:
            continue

        # Parse escalation periods (new format) or fall back to single rate (backward compatibility)
        import json
        escalation_periods = None
        if allocation.escalation_periods:
            # New format: multiple escalation periods
            if isinstance(allocation.escalation_periods, str):
                escalation_periods = json.loads(allocation.escalation_periods)
            else:
                escalation_periods = allocation.escalation_periods
        elif allocation.escalation_rate is not None and allocation.escalation_rate > 0:
            # Backward compatibility: convert single rate to periods format
            escalation_start_month = allocation.escalation_start_month or start_month
            if escalation_start_month < start_month:
                escalation_start_month = start_month
            escalation_periods = [{
                "start_month": escalation_start_month,
                "end_month": end_month,
                "rate": allocation.escalation_rate
            }]
        else:
            # No escalation
            escalation_periods = []

        # Sort periods by start_month to ensure correct order
        if escalation_periods:
            escalation_periods = sorted(escalation_periods, key=lambda p: p.get("start_month", 0))
        
        # Calculate cost for each month with multiple escalation periods
        for month in range(start_month, end_month + 1):
            multiplier = 1.0
            
            if escalation_periods and len(escalation_periods) > 0:
                # Multiple periods: calculate cumulative escalation sequentially
                # Process periods chronologically up to the current month
                for period in escalation_periods:
                    period_start = period.get("start_month", start_month)
                    period_end = period.get("end_month", end_month)
                    period_rate = period.get("rate", 0.0)
                    
                    # Skip periods that haven't started yet
                    if month < period_start:
                        continue
                    
                    if period_end < month:
                        # This period is completely in the past, apply full period escalation
                        if period_rate > 0:
                            period_months = period_end - period_start + 1
                            monthly_rate = (1 + (period_rate / 100.0)) ** (1 / 12.0)
                            # Apply compounding for all months in this period
                            multiplier *= monthly_rate ** period_months
                    else:
                        # Current month is within this period
                        if period_rate > 0:
                            months_in_period_up_to_month = month - period_start + 1
                            monthly_rate = (1 + (period_rate / 100.0)) ** (1 / 12.0)
                            # Apply compounding for months in this period up to current month
                            multiplier *= monthly_rate ** (months_in_period_up_to_month - 1)
                        # We've reached the current month, no need to process further periods
                        break
            else:
                # No escalation periods, multiplier stays at 1.0
                multiplier = 1.0
            
            monthly_amount = allocation.monthly_cost * multiplier
            monthly_labor[month - 1] += monthly_amount

    yearly_breakdown = []
    years = max(1, (duration_months + 11) // 12)

    total_labor_cost = sum(monthly_labor)
    total_overhead = 0.0
    total_cost = 0.0
    total_profit = 0.0
    total_price = 0.0

    for year in range(1, years + 1):
        start_index = (year - 1) * 12
        end_index = min(year * 12, duration_months)
        if start_index >= end_index:
            break

        labor_cost = sum(monthly_labor[start_index:end_index])
        overhead = labor_cost * (overhead_rate / 100.0)
        cost = labor_cost + overhead
        profit = cost * (profit_margin / 100.0)
        price = cost + profit

        total_overhead += overhead
        total_cost += cost
        total_profit += profit
        total_price += price

        yearly_breakdown.append(
            {
                "year": year,
                "laborCost": round(labor_cost, 2),
                "overhead": round(overhead, 2),
                "totalCost": round(cost, 2),
                "profit": round(profit, 2),
                "totalPrice": round(price, 2),
            }
        )

    return {
        "total_labor_cost": round(total_labor_cost, 2),
        "total_overhead": round(total_overhead, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2),
        "total_price": round(total_price, 2),
        "yearly_breakdown": yearly_breakdown,
    }


@router.post("/", response_model=StaffPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_plan(
    plan_data: StaffPlanCreate,
    current_user: User = Depends(get_current_user)
):
    
    db: AsyncSession = get_request_transaction()
    
    try:
        # Check if a staff plan already exists for this project
        # If project_id is provided, check by project_id; otherwise check by project_name within org
        existing_plan_query = select(StaffPlan).where(
            StaffPlan.org_id == current_user.org_id
        )
        
        if plan_data.project_id:
            # Check by project_id if provided
            existing_plan_query = existing_plan_query.where(
                StaffPlan.project_id == plan_data.project_id
            )
        else:
            # If no project_id, check by project_name within the same org
            existing_plan_query = existing_plan_query.where(
                StaffPlan.project_name == plan_data.project_name
            )
        
        result = await db.execute(existing_plan_query)
        existing_plan = result.scalar_one_or_none()
        
        if existing_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A staff plan already exists for this project. Please delete the existing plan (ID: {existing_plan.id}) before creating a new one."
            )
        
        # Create new staff plan with organization isolation
        new_plan = StaffPlan(
            project_id=plan_data.project_id,
            project_name=plan_data.project_name,
            project_description=plan_data.project_description,
            project_start_date=plan_data.project_start_date,
            duration_months=plan_data.duration_months,
            overhead_rate=plan_data.overhead_rate,
            profit_margin=plan_data.profit_margin,
            annual_escalation_rate=plan_data.annual_escalation_rate,
            status="draft",
            org_id=current_user.org_id,  # Multi-tenancy: isolate by organization
            created_by=current_user.id
        )
        
        db.add(new_plan)
        await db.flush()
        await db.refresh(new_plan)
        await db.commit()  # CRITICAL: Commit to database!
        
        logger.info(f"✅ Staff plan created: {new_plan.id} - {new_plan.project_name}")
        return new_plan.to_dict()
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to create staff plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create staff plan: {str(e)}"
        )


@router.get("/", response_model=List[StaffPlanResponse])
async def get_staff_plans(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all staff plans with optional filtering"""
    db: AsyncSession = get_request_transaction()
    
    try:
        from sqlalchemy import func
        from app.models.staff_planning import StaffAllocation
        
        # Query plans with allocation counts - FILTERED BY ORGANIZATION
        query = select(
            StaffPlan,
            func.count(StaffAllocation.id).label('team_size')
        ).outerjoin(
            StaffAllocation, StaffPlan.id == StaffAllocation.staff_plan_id
        ).where(
            StaffPlan.org_id == current_user.org_id  # Multi-tenancy: only show plans from user's organization
        ).group_by(StaffPlan.id)
        
        if status_filter:
            query = query.where(StaffPlan.status == status_filter)
        
        query = query.order_by(StaffPlan.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        rows = result.all()
        
        # Build response with team_size included
        response_data = []
        for plan, team_size in rows:
            plan_dict = plan.to_dict()
            plan_dict['team_size'] = team_size
            response_data.append(plan_dict)
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch staff plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch staff plans: {str(e)}"
        )


@router.get("/{plan_id}", response_model=StaffPlanResponse)
async def get_staff_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific staff plan by ID"""
    db: AsyncSession = get_request_transaction()
    
    result = await db.execute(
        select(StaffPlan).where(
            and_(
                StaffPlan.id == plan_id,
                StaffPlan.org_id == current_user.org_id  # Multi-tenancy: verify ownership
            )
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff plan {plan_id} not found"
        )
    
    return plan.to_dict()


@router.put("/{plan_id}", response_model=StaffPlanResponse)
async def update_staff_plan(
    plan_id: int,
    plan_data: StaffPlanUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update an existing staff plan"""
    db: AsyncSession = get_request_transaction()
    
    result = await db.execute(
        select(StaffPlan).where(
            and_(
                StaffPlan.id == plan_id,
                StaffPlan.org_id == current_user.org_id  # Multi-tenancy: verify ownership
            )
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff plan {plan_id} not found"
        )
    
    try:
        # Update fields
        update_data = plan_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(plan, key, value)
        
        await db.flush()
        await db.refresh(plan)
        await db.commit()  # CRITICAL: Commit to database!
        
        logger.info(f"✅ Staff plan updated: {plan.id}")
        return plan.to_dict()
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to update staff plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update staff plan: {str(e)}"
        )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a staff plan"""
    db: AsyncSession = get_request_transaction()
    
    result = await db.execute(
        select(StaffPlan).where(
            and_(
                StaffPlan.id == plan_id,
                StaffPlan.org_id == current_user.org_id  # Multi-tenancy: verify ownership
            )
        )
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff plan {plan_id} not found"
        )
    
    try:
        await db.delete(plan)
        await db.flush()
        await db.commit()  # CRITICAL: Commit to database!
        
        logger.info(f"✅ Staff plan deleted: {plan_id}")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to delete staff plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete staff plan: {str(e)}"
        )


# ========== Staff Allocation Routes ==========

@router.post("/{plan_id}/allocations", response_model=StaffAllocationResponse, status_code=status.HTTP_201_CREATED)
async def add_staff_allocation(
    plan_id: int,
    allocation_data: StaffAllocationCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a staff member to a plan"""
    db: AsyncSession = get_request_transaction()
    
    result = await db.execute(select(StaffPlan).where(StaffPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff plan {plan_id} not found"
        )
    
    try:
        # Calculate costs
        weeks_per_month = 4.33
        months_allocated = allocation_data.end_month - allocation_data.start_month + 1
        monthly_cost = allocation_data.hours_per_week * weeks_per_month * allocation_data.hourly_rate
        
        # Handle escalation: prefer escalation_periods, fallback to single rate (backward compatibility)
        escalation_rate = allocation_data.escalation_rate
        escalation_start_month = allocation_data.escalation_start_month or allocation_data.start_month
        if escalation_start_month < allocation_data.start_month:
            escalation_start_month = allocation_data.start_month
        
        # Store escalation_periods as JSON if provided
        import json
        escalation_periods_json = None
        escalation_periods_list = None
        if allocation_data.escalation_periods and len(allocation_data.escalation_periods) > 0:
            # Multiple periods provided
            escalation_periods_list = [period.model_dump() for period in allocation_data.escalation_periods]
            escalation_periods_json = json.dumps(escalation_periods_list)
        elif escalation_rate is not None and escalation_rate > 0:
            # Backward compatibility: convert single rate to periods format
            escalation_periods_list = [{
                "start_month": escalation_start_month,
                "end_month": allocation_data.end_month,
                "rate": escalation_rate
            }]
            escalation_periods_json = json.dumps(escalation_periods_list)
        # If escalation_periods is empty list or None, escalation_periods_json stays None
        
        # Calculate total cost WITH escalation to match plan calculation
        total_cost = calculate_allocation_total_cost_with_escalation(
            monthly_cost=monthly_cost,
            start_month=allocation_data.start_month,
            end_month=allocation_data.end_month,
            escalation_periods=escalation_periods_list,
            escalation_rate=escalation_rate,
            escalation_start_month=escalation_start_month,
        )

        # Create allocation
        new_allocation = StaffAllocation(
            staff_plan_id=plan_id,
            resource_id=allocation_data.resource_id,
            resource_name=allocation_data.resource_name,
            role=allocation_data.role,
            level=allocation_data.level,
            start_month=allocation_data.start_month,
            end_month=allocation_data.end_month,
            hours_per_week=allocation_data.hours_per_week,
            hourly_rate=allocation_data.hourly_rate,
            monthly_cost=round(monthly_cost, 2),
            total_cost=total_cost,  # Now includes escalation
            escalation_rate=escalation_rate,  # Keep for backward compatibility
            escalation_start_month=escalation_start_month,  # Keep for backward compatibility
            escalation_periods=escalation_periods_json,
            status="planned"
        )
        
        db.add(new_allocation)
        await db.flush()  # Flush to get the allocation data
        
        # Recalculate plan costs
        result = await db.execute(
            select(StaffAllocation).where(StaffAllocation.staff_plan_id == plan_id)
        )
        all_allocations = result.scalars().all()
        
        # Recalculate each allocation's total_cost with escalation to match plan calculation
        import json
        for allocation in all_allocations:
            escalation_periods_list = None
            if allocation.escalation_periods:
                if isinstance(allocation.escalation_periods, str):
                    escalation_periods_list = json.loads(allocation.escalation_periods)
                else:
                    escalation_periods_list = allocation.escalation_periods
            
            allocation.total_cost = calculate_allocation_total_cost_with_escalation(
                monthly_cost=allocation.monthly_cost or 0.0,
                start_month=allocation.start_month or 1,
                end_month=allocation.end_month or plan.duration_months,
                escalation_periods=escalation_periods_list,
                escalation_rate=allocation.escalation_rate,
                escalation_start_month=allocation.escalation_start_month,
            )
        
        costs = calculate_staff_plan_costs(
            all_allocations,
            plan.duration_months,
            plan.overhead_rate,
            plan.profit_margin,
            plan.annual_escalation_rate or 0.0
        )
        
        # Update plan with calculated costs
        plan.total_labor_cost = costs["total_labor_cost"]
        plan.total_overhead = costs["total_overhead"]
        plan.total_cost = costs["total_cost"]
        plan.total_profit = costs["total_profit"]
        plan.total_price = costs["total_price"]
        plan.yearly_breakdown = costs["yearly_breakdown"]
        
        await db.flush()
        await db.refresh(new_allocation)
        await db.commit()  # CRITICAL: Commit to database!
        
        logger.info(f"✅ Staff allocation created: {new_allocation.id} for plan {plan_id}")
        return new_allocation.to_dict()
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to add staff allocation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add staff allocation: {str(e)}"
        )


@router.get("/{plan_id}/allocations", response_model=List[StaffAllocationResponse])
async def get_staff_allocations(
    plan_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get all staff allocations for a plan"""
    db: AsyncSession = get_request_transaction()
    
    result = await db.execute(select(StaffPlan).where(StaffPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff plan {plan_id} not found"
        )
    
    result = await db.execute(
        select(StaffAllocation).where(StaffAllocation.staff_plan_id == plan_id)
    )
    allocations = result.scalars().all()
    
    return [allocation.to_dict() for allocation in allocations]


@router.patch(
    "/{plan_id}/allocations/{allocation_id}",
    response_model=StaffAllocationResponse,
)
async def update_staff_allocation(
    plan_id: int,
    allocation_id: int,
    allocation_update: StaffAllocationUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update an existing staff allocation and refresh plan financials."""
    db: AsyncSession = get_request_transaction()

    plan_result = await db.execute(
        select(StaffPlan).where(
            and_(
                StaffPlan.id == plan_id,
                StaffPlan.org_id == current_user.org_id,
            )
        )
    )
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff plan {plan_id} not found",
        )

    allocation_result = await db.execute(
        select(StaffAllocation).where(
            and_(
                StaffAllocation.id == allocation_id,
                StaffAllocation.staff_plan_id == plan_id,
            )
        )
    )
    allocation = allocation_result.scalar_one_or_none()
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allocation {allocation_id} not found",
        )

    update_data = allocation_update.model_dump(exclude_unset=True)
    if not update_data:
        return allocation.to_dict()

    try:
        # Handle escalation_periods separately (needs JSON conversion)
        import json
        if "escalation_periods" in update_data:
            escalation_periods = update_data.pop("escalation_periods")
            if escalation_periods and len(escalation_periods) > 0:
                allocation.escalation_periods = json.dumps([period.model_dump() if hasattr(period, 'model_dump') else period for period in escalation_periods])
            else:
                allocation.escalation_periods = None
        elif "escalation_rate" in update_data or "escalation_start_month" in update_data:
            # Backward compatibility: convert single rate to periods if needed
            escalation_rate = update_data.get("escalation_rate", allocation.escalation_rate)
            escalation_start_month = update_data.get("escalation_start_month", allocation.escalation_start_month or allocation.start_month)
            end_month = allocation.end_month
            
            if escalation_rate is not None and escalation_rate > 0:
                allocation.escalation_periods = json.dumps([{
                    "start_month": escalation_start_month,
                    "end_month": end_month,
                    "rate": escalation_rate
                }])
        
        for key, value in update_data.items():
            setattr(allocation, key, value)

        # Ensure escalation start month is set correctly (for backward compatibility)
        if allocation.escalation_start_month is None:
            allocation.escalation_start_month = allocation.start_month
        elif allocation.escalation_start_month < allocation.start_month:
            allocation.escalation_start_month = allocation.start_month

        # Recalculate cost figures when timing or rates change
        if any(
            field in update_data
            for field in ("start_month", "end_month", "hours_per_week", "hourly_rate", "escalation_rate", "escalation_start_month", "escalation_periods")
        ):
            weeks_per_month = 4.33
            months_allocated = max(1, allocation.end_month - allocation.start_month + 1)
            monthly_cost = allocation.hours_per_week * weeks_per_month * allocation.hourly_rate
            allocation.monthly_cost = round(monthly_cost, 2)
            
            # Calculate total cost WITH escalation to match plan calculation
            import json
            escalation_periods_list = None
            if allocation.escalation_periods:
                if isinstance(allocation.escalation_periods, str):
                    escalation_periods_list = json.loads(allocation.escalation_periods)
                else:
                    escalation_periods_list = allocation.escalation_periods
            
            allocation.total_cost = calculate_allocation_total_cost_with_escalation(
                monthly_cost=monthly_cost,
                start_month=allocation.start_month,
                end_month=allocation.end_month,
                escalation_periods=escalation_periods_list,
                escalation_rate=allocation.escalation_rate,
                escalation_start_month=allocation.escalation_start_month,
            )

        await db.flush()

        result = await db.execute(
            select(StaffAllocation).where(StaffAllocation.staff_plan_id == plan_id)
        )
        all_allocations = result.scalars().all()
        
        # Recalculate each allocation's total_cost with escalation to match plan calculation
        import json
        for allocation in all_allocations:
            escalation_periods_list = None
            if allocation.escalation_periods:
                if isinstance(allocation.escalation_periods, str):
                    escalation_periods_list = json.loads(allocation.escalation_periods)
                else:
                    escalation_periods_list = allocation.escalation_periods
            
            allocation.total_cost = calculate_allocation_total_cost_with_escalation(
                monthly_cost=allocation.monthly_cost or 0.0,
                start_month=allocation.start_month or 1,
                end_month=allocation.end_month or plan.duration_months,
                escalation_periods=escalation_periods_list,
                escalation_rate=allocation.escalation_rate,
                escalation_start_month=allocation.escalation_start_month,
            )

        costs = calculate_staff_plan_costs(
            all_allocations,
            plan.duration_months,
            plan.overhead_rate,
            plan.profit_margin,
            plan.annual_escalation_rate or 0.0,
        )

        plan.total_labor_cost = costs["total_labor_cost"]
        plan.total_overhead = costs["total_overhead"]
        plan.total_cost = costs["total_cost"]
        plan.total_profit = costs["total_profit"]
        plan.total_price = costs["total_price"]
        plan.yearly_breakdown = costs["yearly_breakdown"]

        await db.flush()
        await db.commit()
        await db.refresh(allocation)

        logger.info(
            "✅ Staff allocation updated: %s for plan %s", allocation_id, plan_id
        )
        return allocation.to_dict()
    except Exception as exc:
        await db.rollback()
        logger.error("❌ Failed to update staff allocation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update staff allocation: {exc}",
        )


@router.delete("/{plan_id}/allocations/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_staff_allocation(
    plan_id: int,
    allocation_id: int,
    current_user: User = Depends(get_current_user)
):
    """Remove a staff allocation from a plan"""
    db: AsyncSession = get_request_transaction()
    
    result = await db.execute(
        select(StaffAllocation).where(
            and_(
                StaffAllocation.id == allocation_id,
                StaffAllocation.staff_plan_id == plan_id
            )
        )
    )
    allocation = result.scalar_one_or_none()
    
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allocation {allocation_id} not found"
        )
    
    try:
        await db.delete(allocation)
        
        # Recalculate plan costs
        result = await db.execute(select(StaffPlan).where(StaffPlan.id == plan_id))
        plan = result.scalar_one_or_none()
        
        result = await db.execute(
            select(StaffAllocation).where(StaffAllocation.staff_plan_id == plan_id)
        )
        all_allocations = result.scalars().all()
        
        # Recalculate each allocation's total_cost with escalation to match plan calculation
        import json
        for allocation in all_allocations:
            escalation_periods_list = None
            if allocation.escalation_periods:
                if isinstance(allocation.escalation_periods, str):
                    escalation_periods_list = json.loads(allocation.escalation_periods)
                else:
                    escalation_periods_list = allocation.escalation_periods
            
            allocation.total_cost = calculate_allocation_total_cost_with_escalation(
                monthly_cost=allocation.monthly_cost or 0.0,
                start_month=allocation.start_month or 1,
                end_month=allocation.end_month or plan.duration_months,
                escalation_periods=escalation_periods_list,
                escalation_rate=allocation.escalation_rate,
                escalation_start_month=allocation.escalation_start_month,
            )
        
        costs = calculate_staff_plan_costs(
            all_allocations,
            plan.duration_months,
            plan.overhead_rate,
            plan.profit_margin,
            plan.annual_escalation_rate or 0.0
        )
        
        # Update plan costs
        plan.total_labor_cost = costs["total_labor_cost"]
        plan.total_overhead = costs["total_overhead"]
        plan.total_cost = costs["total_cost"]
        plan.total_profit = costs["total_profit"]
        plan.total_price = costs["total_price"]
        plan.yearly_breakdown = costs["yearly_breakdown"]
        
        await db.flush()
        await db.commit()  # CRITICAL: Commit to database!
        
        logger.info(f"✅ Staff allocation removed: {allocation_id} from plan {plan_id}")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Failed to remove staff allocation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove staff allocation: {str(e)}"
        )


@router.get("/{plan_id}/with-allocations", response_model=StaffPlanWithAllocations)
async def get_staff_plan_with_allocations(
    plan_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a staff plan with all its allocations"""
    db: AsyncSession = get_request_transaction()
    
    result = await db.execute(select(StaffPlan).where(StaffPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff plan {plan_id} not found"
        )
    
    result = await db.execute(
        select(StaffAllocation).where(StaffAllocation.staff_plan_id == plan_id)
    )
    allocations = result.scalars().all()
    
    # Recalculate each allocation's total_cost with escalation to match plan calculation
    import json
    for allocation in allocations:
        escalation_periods_list = None
        if allocation.escalation_periods:
            if isinstance(allocation.escalation_periods, str):
                escalation_periods_list = json.loads(allocation.escalation_periods)
            else:
                escalation_periods_list = allocation.escalation_periods
        
        allocation.total_cost = calculate_allocation_total_cost_with_escalation(
            monthly_cost=allocation.monthly_cost or 0.0,
            start_month=allocation.start_month or 1,
            end_month=allocation.end_month or plan.duration_months,
            escalation_periods=escalation_periods_list,
            escalation_rate=allocation.escalation_rate,
            escalation_start_month=allocation.escalation_start_month,
        )
    
    return {
        **plan.to_dict(),
        "allocations": [allocation.to_dict() for allocation in allocations]
    }


@router.post("/{plan_id}/ai-cost-analysis")
async def get_ai_cost_analysis(
    plan_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered explanation of cost escalation"""
    db: AsyncSession = get_request_transaction()
    
    result = await db.execute(select(StaffPlan).where(StaffPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff plan {plan_id} not found"
        )
    
    if not gemini_service.enabled:
        return {
            "analysis": "AI analysis is not available. Please configure GEMINI_API_KEY.",
            "key_factors": [],
            "recommendations": []
        }
    
    try:
        # Get allocations
        result = await db.execute(
            select(StaffAllocation).where(StaffAllocation.staff_plan_id == plan_id)
        )
        allocations = result.scalars().all()
        
        # Prepare data for AI
        yearly_breakdown = plan.yearly_breakdown or []
        team_composition = {}
        for alloc in allocations:
            level = alloc.level or 'General'
            team_composition[level] = team_composition.get(level, 0) + 1
        
        prompt = f"""
You are a financial analyst expert in construction and engineering project staffing costs.

Analyze this multi-year staffing plan and provide a professional explanation:

PROJECT: {plan.project_name}
DURATION: {plan.duration_months} months ({len(yearly_breakdown)} years)
TEAM SIZE: {len(allocations)} members
TEAM COMPOSITION: {', '.join(f'{count} {level}' for level, count in team_composition.items())}

ESCALATION: Employee-level rates applied
OVERHEAD RATE: {plan.overhead_rate}%
PROFIT MARGIN: {plan.profit_margin}%

YEARLY COSTS:
{chr(10).join(f"Year {y['year']}: ${y['totalPrice']:,.2f} (Labor: ${y['laborCost']:,.2f})" for y in yearly_breakdown)}

Provide a brief, professional analysis (2-3 sentences) explaining:
1. Why costs increase year over year
2. The impact of employee-level escalation rates on costs
3. Market factors (inflation, salary growth, market demand)

Keep it concise and business-focused. Start directly with the analysis.
"""

        response = gemini_service.model.generate_content(prompt)
        analysis_text = response.text.strip()
        
        # Extract key insights
        cost_increase = ((yearly_breakdown[-1]['totalPrice'] - yearly_breakdown[0]['totalPrice']) 
                        / yearly_breakdown[0]['totalPrice'] * 100) if len(yearly_breakdown) > 1 else 0
        
        return {
            "analysis": analysis_text,
            "cost_increase_percentage": round(cost_increase, 2),
            "escalation_rate": "Employee-level rates",
            "total_escalation_impact": round(plan.total_price - plan.total_labor_cost * (1 + plan.overhead_rate/100) * (1 + plan.profit_margin/100), 2),
            "key_factors": [
                "Employee-level escalation rates applied",
                "Market inflation adjustment",
                f"Total cost increase: {round(cost_increase, 1)}% over {len(yearly_breakdown)} years"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to generate AI analysis: {str(e)}")
        return {
            "analysis": "The cost increases year-over-year due to employee-level escalation rates, which account for market inflation, salary growth, and increased labor costs typical in the construction and engineering industry.",
            "key_factors": [
                "Employee-level escalation rates applied",
                "Market inflation adjustment",
                "Salary and benefit increases"
            ],
            "recommendations": []
        }


@router.post("/ai-staff-recommendations")
async def get_ai_staff_recommendations(
    request_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered staff recommendations based on project requirements
    Analyzes project details and suggests optimal team composition
    """
    db: AsyncSession = get_request_transaction()
    
    project_name = request_data.get('project_name', '')
    project_description = request_data.get('project_description', '')
    duration_months = request_data.get('duration_months', 12)
    project_id = request_data.get('project_id')
    
    # Quick check - if Gemini not enabled, return instant recommendations
    if not gemini_service.enabled:
        logger.info("Gemini AI not enabled - using instant smart recommendations")
        db: AsyncSession = get_request_transaction()
        
        # Get available employees quickly
        from app.models.employee import Employee
        result = await db.execute(
            select(Employee).where(Employee.status == 'accepted').limit(50)
        )
        available_employees = result.scalars().all()
        
        # Smart fallback based on available employees
        recommended = []
        for emp in available_employees[:5]:  # Top 5
            recommended.append({
                "employee_id": str(emp.id),
                "name": emp.name,
                "role": emp.job_title or "Staff Member",
                "reason": f"Experienced in {emp.job_title or 'project work'} with relevant skills",
                "match_score": 75
            })
        
        return {
            "analysis": f"Based on project requirements and available talent pool, we recommend a balanced team. {len(available_employees)} employees are available for allocation.",
            "recommended_employees": recommended,
            "suggested_new_roles": [
                {
                    "role": "Project Manager",
                    "level": "Senior",
                    "skills_required": ["Project Management", "Leadership"],
                    "reason": "Critical for multi-month project coordination",
                    "priority": "High"
                }
            ] if len(available_employees) == 0 else [],
            "team_composition": f"Recommended: {len(recommended)} team members from available pool",
            "available_employees_count": len(available_employees)
        }
    
    try:
        # Fetch opportunity details if project_id is provided
        opportunity_context = ""
        if project_id:
            from app.models.opportunity import Opportunity
            result = await db.execute(select(Opportunity).where(Opportunity.id == project_id))
            opportunity = result.scalar_one_or_none()
            
            if opportunity:
                opportunity_context = f"""
OPPORTUNITY DETAILS:
- Client: {opportunity.client_name}
- Project Type: {opportunity.project_type or 'Not specified'}
- Value: ${opportunity.project_value or 0:,.0f}
- Location: {opportunity.state or 'Not specified'}
- Sectors: {opportunity.sectors or 'Not specified'}
- Services: {opportunity.services or 'Not specified'}
"""
        
        # Get all accepted employees
        from app.models.employee import Employee
        result = await db.execute(
            select(Employee).where(Employee.status == 'accepted').limit(50)
        )
        available_employees = result.scalars().all()
        
        employees_context = "\n".join([
            f"- {emp.name}: {emp.job_title or 'Staff'} | Skills: {', '.join(emp.skills[:3]) if emp.skills else 'General'} | Experience: {emp.experience or 'N/A'}"
            for emp in available_employees[:10]  # Limit to 10 for context
        ])
        
        # Quick analysis with concise prompt
        prompt = f"""
Project: {project_name} ({duration_months} months)
Available: {len(available_employees)} employees

Recommend team composition in JSON (be concise):
{{
  "analysis": "1 sentence why",
  "recommended_employees": [{{"name": "Name", "role": "Role", "reason": "Why", "match_score": 85}}],
  "suggested_new_roles": [{{"role": "Role", "level": "Senior", "priority": "High", "reason": "Why"}}],
  "team_composition": "Brief structure"
}}
"""

        # Use generate_content with timeout
        import asyncio
        response = await asyncio.wait_for(
            asyncio.to_thread(gemini_service.model.generate_content, prompt),
            timeout=5.0  # 5 second timeout
        )
        analysis_text = response.text.strip()
        
        # Try to parse JSON response
        import json
        import re
        
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
        if json_match:
            analysis_text = json_match.group(1)
        
        try:
            ai_response = json.loads(analysis_text)
        except:
            # Fallback if JSON parsing fails
            ai_response = {
                "analysis": analysis_text[:500],
                "recommended_employees": [],
                "suggested_new_roles": [],
                "team_composition": "Review AI analysis above"
            }
        
        # Enhance with actual employee data
        if available_employees and ai_response.get('recommended_employees'):
            for rec in ai_response['recommended_employees']:
                if rec.get('employee_id') and rec['employee_id'] != 'NEW':
                    # Find employee in our list
                    emp = next((e for e in available_employees if str(e.id) == rec['employee_id']), None)
                    if emp:
                        rec['actual_rate'] = f"${100 + hash(emp.id) % 100}/hr"  # Mock rate for demo
                        rec['availability'] = 'Available'
        
        return {
            **ai_response,
            "available_employees_count": len(available_employees),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except asyncio.TimeoutError:
        logger.warning("Gemini AI timeout - using fallback recommendations")
        # Quick fallback without waiting
        return {
            "analysis": f"For {duration_months}-month projects, we recommend a balanced team. Available employees should be matched based on project requirements and skill alignment.",
            "recommended_employees": [],
            "suggested_new_roles": [
                {
                    "role": "Project Manager",
                    "level": "Senior",
                    "skills_required": ["Project Management", "Leadership"],
                    "reason": "Essential for project coordination",
                    "priority": "High"
                }
            ],
            "team_composition": "Balanced team with PM + specialists",
            "available_employees_count": len(available_employees) if 'available_employees' in locals() else 0
        }
    except Exception as e:
        logger.error(f"Failed to generate AI staff recommendations: {str(e)}")
        return {
            "analysis": f"Based on the project scope and {duration_months}-month duration, we recommend assembling a balanced team with project management, technical engineering, and quality assurance capabilities. Consider senior leadership for complex projects and mid-level specialists for execution.",
            "recommended_employees": [],
            "suggested_new_roles": [
                {
                    "role": "Project Manager",
                    "level": "Senior",
                    "skills_required": ["Project Management", "Leadership", "Budget Planning"],
                    "reason": "Essential for coordinating multi-year projects",
                    "priority": "High"
                },
                {
                    "role": "Technical Lead",
                    "level": "Senior",
                    "skills_required": ["Technical Engineering", "Quality Control"],
                    "reason": "Ensures technical standards and quality",
                    "priority": "High"
                }
            ],
            "team_composition": "Recommended: 1 Senior PM + Technical specialists based on project scope",
            "available_employees_count": len(available_employees) if 'available_employees' in locals() else 0
        }


@router.post("/ai-project-parameters")
async def get_ai_project_parameters(
    request_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered recommendations for project parameters
    Suggests optimal Duration, Overhead, Profit Margin, and Escalation Rate
    """
    project_name = request_data.get('project_name', '')
    project_description = request_data.get('project_description', '')
    project_type = request_data.get('project_type', 'Infrastructure')
    project_value = request_data.get('project_value', 0)
    
    if not gemini_service.enabled:
        return {
            "analysis": "AI recommendations are not available. Using industry standards.",
            "recommended_parameters": {
                "duration_months": 12,
                "overhead_rate": 25.0,
                "profit_margin": 15.0,
                "annual_escalation_rate": 3.0
            }
        }
    
    try:
        # Concise prompt for faster response
        prompt = f"""
Project: {project_name}, Value: ${project_value:,.0f}, Type: {project_type}

Recommend financial parameters in JSON (concise):
{{
  "analysis": "1-2 sentences",
  "recommended_parameters": {{"duration_months": 24, "overhead_rate": 25.0, "profit_margin": 15.0}},
  "market_insights": ["insight 1", "insight 2"],
  "rationale": {{"duration": "why", "overhead": "why", "profit": "why"}}
}}
"""

        # Use timeout for faster response
        import asyncio
        response = await asyncio.wait_for(
            asyncio.to_thread(gemini_service.model.generate_content, prompt),
            timeout=5.0  # 5 second timeout
        )
        analysis_text = response.text.strip()
        
        # Parse JSON response
        import json
        import re
        
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
        if json_match:
            analysis_text = json_match.group(1)
        
        try:
            ai_response = json.loads(analysis_text)
        except:
            # Fallback with sensible defaults
            ai_response = {
                "analysis": "Based on industry standards for construction and engineering projects, the recommended parameters balance competitive pricing with sustainable profit margins while accounting for market inflation.",
                "recommended_parameters": {
                    "duration_months": 24 if project_value > 500000 else 12,
                    "overhead_rate": 25.0,
                    "profit_margin": 15.0,
                },
                "market_insights": [
                    "2025 construction inflation: ~3-4%",
                    "Labor costs rising due to skilled worker shortage",
                    "Industry standard overhead: 20-30%"
                ]
            }
        
        return ai_response
        
    except asyncio.TimeoutError:
        logger.warning("Gemini AI timeout - using industry standards")
        return {
            "analysis": "Using industry-standard parameters for construction projects based on typical market conditions.",
            "recommended_parameters": {
                "duration_months": 24 if project_value > 500000 else 12,
                "overhead_rate": 25.0,
                "profit_margin": 15.0,
                "annual_escalation_rate": 3.0
            },
            "market_insights": [
                "Construction inflation: 3-4% annually",
                "Standard overhead: 20-30%",
                "Typical profit margin: 10-20%"
            ]
        }
    except Exception as e:
        logger.error(f"Failed to generate AI project parameters: {str(e)}")
        return {
            "analysis": "Using industry-standard parameters for construction projects. Overhead at 25% covers administrative costs, equipment, and facilities. Profit margin of 15% is competitive yet sustainable. Escalation rates should be set per employee based on their role and market conditions.",
            "recommended_parameters": {
                "duration_months": 24 if project_value > 500000 else 12,
                "overhead_rate": 25.0,
                "profit_margin": 15.0
            },
            "market_insights": [
                "Construction inflation trending at 3-4% annually",
                "Skilled labor shortage driving wage increases",
                "Typical overhead range: 20-30% for infrastructure projects"
            ]
        }

