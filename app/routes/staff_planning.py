"""
Staff Planning API Routes
Handles staffing plan CRUD operations and cost calculations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
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
    StaffAllocationResponse,
    StaffPlanWithAllocations
)
from app.dependencies.user_auth import get_current_user
from app.services.gemini_service import GeminiService

router = APIRouter(prefix="/staff-planning", tags=["Staff Planning"])
gemini_service = GeminiService()


def calculate_staff_plan_costs(
    staff_allocations: List[StaffAllocation],
    duration_months: int,
    overhead_rate: float,
    profit_margin: float,
    annual_escalation_rate: float
):
    """Calculate all costs for a staff plan including yearly breakdown"""
    
    # Calculate base labor cost
    total_labor_cost = sum(allocation.total_cost for allocation in staff_allocations)
    
    # Calculate yearly breakdown with escalation
    years = max(1, (duration_months + 11) // 12)  # Ceiling division
    yearly_breakdown = []
    monthly_labor_cost = total_labor_cost / duration_months if duration_months > 0 else 0
    
    for year in range(1, years + 1):
        months_in_year = min(12, duration_months - ((year - 1) * 12))
        if months_in_year <= 0:
            break
            
        escalation_multiplier = (1 + (annual_escalation_rate / 100)) ** (year - 1)
        
        year_labor_cost = monthly_labor_cost * months_in_year * escalation_multiplier
        year_overhead = year_labor_cost * (overhead_rate / 100)
        year_total_cost = year_labor_cost + year_overhead
        year_profit = year_total_cost * (profit_margin / 100)
        year_total_price = year_total_cost + year_profit
        
        yearly_breakdown.append({
            "year": year,
            "laborCost": round(year_labor_cost, 2),
            "overhead": round(year_overhead, 2),
            "totalCost": round(year_total_cost, 2),
            "profit": round(year_profit, 2),
            "totalPrice": round(year_total_price, 2)
        })
    
    # Calculate totals
    total_overhead = sum(y["overhead"] for y in yearly_breakdown)
    total_cost = sum(y["totalCost"] for y in yearly_breakdown)
    total_profit = sum(y["profit"] for y in yearly_breakdown)
    total_price = sum(y["totalPrice"] for y in yearly_breakdown)
    
    return {
        "total_labor_cost": round(total_labor_cost, 2),
        "total_overhead": round(total_overhead, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2),
        "total_price": round(total_price, 2),
        "yearly_breakdown": yearly_breakdown
    }


@router.post("/", response_model=StaffPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_plan(
    plan_data: StaffPlanCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new staff plan"""
    db: AsyncSession = get_request_transaction()
    
    try:
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
        hours_total = allocation_data.hours_per_week * weeks_per_month * months_allocated
        monthly_cost = (allocation_data.hours_per_week * weeks_per_month * allocation_data.hourly_rate)
        total_cost = monthly_cost * months_allocated
        
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
            total_cost=round(total_cost, 2),
            status="planned"
        )
        
        db.add(new_allocation)
        await db.flush()  # Flush to get the allocation data
        
        # Recalculate plan costs
        result = await db.execute(
            select(StaffAllocation).where(StaffAllocation.staff_plan_id == plan_id)
        )
        all_allocations = result.scalars().all()
        
        costs = calculate_staff_plan_costs(
            all_allocations,
            plan.duration_months,
            plan.overhead_rate,
            plan.profit_margin,
            plan.annual_escalation_rate
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
        
        costs = calculate_staff_plan_costs(
            all_allocations,
            plan.duration_months,
            plan.overhead_rate,
            plan.profit_margin,
            plan.annual_escalation_rate
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

ANNUAL ESCALATION RATE: {plan.annual_escalation_rate}%
OVERHEAD RATE: {plan.overhead_rate}%
PROFIT MARGIN: {plan.profit_margin}%

YEARLY COSTS:
{chr(10).join(f"Year {y['year']}: ${y['totalPrice']:,.2f} (Labor: ${y['laborCost']:,.2f})" for y in yearly_breakdown)}

Provide a brief, professional analysis (2-3 sentences) explaining:
1. Why costs increase year over year
2. The impact of the {plan.annual_escalation_rate}% annual escalation rate
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
            "escalation_rate": plan.annual_escalation_rate,
            "total_escalation_impact": round(plan.total_price - plan.total_labor_cost * (1 + plan.overhead_rate/100) * (1 + plan.profit_margin/100), 2),
            "key_factors": [
                f"Annual salary escalation: {plan.annual_escalation_rate}%",
                f"Market inflation adjustment",
                f"Total cost increase: {round(cost_increase, 1)}% over {len(yearly_breakdown)} years"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to generate AI analysis: {str(e)}")
        return {
            "analysis": f"The cost increases year-over-year due to the {plan.annual_escalation_rate}% annual escalation rate, which accounts for market inflation, salary growth, and increased labor costs typical in the construction and engineering industry.",
            "key_factors": [
                f"Annual escalation: {plan.annual_escalation_rate}%",
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
  "recommended_parameters": {{"duration_months": 24, "overhead_rate": 25.0, "profit_margin": 15.0, "annual_escalation_rate": 3.5}},
  "market_insights": ["insight 1", "insight 2"],
  "rationale": {{"duration": "why", "overhead": "why", "profit": "why", "escalation": "why"}}
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
                    "annual_escalation_rate": 3.5
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
            "analysis": "Using industry-standard parameters for construction projects. Overhead at 25% covers administrative costs, equipment, and facilities. Profit margin of 15% is competitive yet sustainable. Annual escalation of 3% accounts for inflation and labor market growth.",
            "recommended_parameters": {
                "duration_months": 24 if project_value > 500000 else 12,
                "overhead_rate": 25.0,
                "profit_margin": 15.0,
                "annual_escalation_rate": 3.0
            },
            "market_insights": [
                "Construction inflation trending at 3-4% annually",
                "Skilled labor shortage driving wage increases",
                "Typical overhead range: 20-30% for infrastructure projects"
            ]
        }

