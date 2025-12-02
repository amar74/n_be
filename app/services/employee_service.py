import logging
import csv
import io
import asyncio
import json
import re
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import secrets

from app.models.employee import Employee, Resume, EmployeeStatus, ResumeStatus
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    AIRoleSuggestionRequest,
    ResumeAnalysisResponse,
    SkillsGapResponse,
    SkillGapAnalysis,
    OnboardingDashboard,
    EmployeeCSVRow
)
from app.services.gemini_service import gemini_service
from app.services.ai_analysis_service import ai_analysis_service

logger = logging.getLogger(__name__)


class EmployeeService:
    """Service for employee management with AI integration"""

    @staticmethod
    async def create_employee(
        employee_data: EmployeeCreate,
        company_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None
    ) -> EmployeeResponse:
        """
        Create a new employee with optional AI enrichment
        
        Validates:
        - No duplicate emails within the same organization
        - Same email CAN exist in different organizations (multi-org support)
        """
        try:
            logger.info(f"Creating employee: {employee_data.name} ({employee_data.email})")
            
            # Check for duplicate email within the SAME organization
            from sqlalchemy import select
            from app.db.session import get_session
            
            async with get_session() as db:
                existing_employee = await db.execute(
                    select(Employee).where(
                        Employee.email == employee_data.email,
                        Employee.company_id == company_id
                    )
                )
                existing = existing_employee.scalar_one_or_none()
                
                if existing:
                    from fastapi import HTTPException
                    raise HTTPException(
                        status_code=400,
                        detail=f"Employee with email {employee_data.email} already exists in your organization (Status: {existing.status})"
                    )
            
            # If AI suggestion is requested, get AI recommendations
            if employee_data.use_ai_suggestion and employee_data.job_title:
                logger.info(f"Requesting AI suggestion for {employee_data.name}")
                try:
                    ai_suggestion = await gemini_service.suggest_role_and_skills(
                        name=employee_data.name,
                        job_title=employee_data.job_title,
                        department=employee_data.department,
                    )
                    
                    # Use AI suggestions if not provided
                    if not employee_data.role:
                        employee_data.role = ai_suggestion.suggested_role
                    if not employee_data.department:
                        employee_data.department = ai_suggestion.suggested_department
                    if not employee_data.skills:
                        employee_data.skills = ai_suggestion.suggested_skills
                    if not employee_data.bill_rate:
                        employee_data.bill_rate = ai_suggestion.bill_rate_suggestion
                    logger.info(f"AI suggestion completed for {employee_data.name}")
                except Exception as ai_error:
                    logger.error(f"AI suggestion failed, continuing without it: {ai_error}")
                    # Continue without AI if it fails

            logger.info(f"Creating employee record in database...")
            # Create employee
            employee = await Employee.create(
                name=employee_data.name,
                email=employee_data.email,
                company_id=company_id,
                phone=employee_data.phone,
                job_title=employee_data.job_title,
                role=employee_data.role,
                department=employee_data.department,
                location=employee_data.location,
                bill_rate=employee_data.bill_rate,
                experience=employee_data.experience,
                skills=employee_data.skills,
                status=EmployeeStatus.PENDING.value,
                created_by=created_by,
                invite_token=secrets.token_urlsafe(32),
                invite_sent_at=datetime.utcnow()
            )

            logger.info(f"✅ Employee created successfully: {employee.email} with ID: {employee.id}")
            
            # DISABLED: Background AI analysis was causing 30s delays
            # Will be triggered later via separate endpoint or webhook
            # asyncio.create_task(ai_analysis_service.deep_profile_analysis(employee.id))
            # logger.info(f"🚀 Background AI analysis queued for {employee.id}")
            
            return EmployeeResponse.model_validate(employee.to_dict())

        except Exception as e:
            logger.error(f"❌ Error creating employee: {e}", exc_info=True)
            raise

    @staticmethod
    async def get_employees(
        company_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeResponse]:
        """Get list of employees with filters"""
        try:
            employees = await Employee.get_all(
                company_id=company_id,
                status=status,
                skip=skip,
                limit=limit
            )
            return [EmployeeResponse.model_validate(emp.to_dict()) for emp in employees]
        except Exception as e:
            logger.error(f"Error fetching employees: {e}")
            raise

    @staticmethod
    async def get_employee_by_id(employee_id: UUID, company_id: Optional[UUID] = None) -> Optional[EmployeeResponse]:
        """Get employee by ID with optional company_id validation"""
        try:
            employee = await Employee.get_by_id(employee_id)
            if employee:
                # Validate company_id if provided (security check)
                if company_id and employee.company_id != company_id:
                    logger.warning(f"Employee {employee_id} does not belong to company {company_id}")
                    return None
                return EmployeeResponse.model_validate(employee.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error fetching employee {employee_id}: {e}")
            raise

    @staticmethod
    async def update_employee(
        employee_id: UUID,
        employee_data: EmployeeUpdate
    ) -> Optional[EmployeeResponse]:
        """Update employee information"""
        try:
            update_dict = employee_data.model_dump(exclude_unset=True)
            employee = await Employee.update(employee_id, **update_dict)
            
            if employee:
                logger.info(f"Employee updated: {employee.email}")
                return EmployeeResponse.model_validate(employee.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error updating employee {employee_id}: {e}")
            raise

    @staticmethod
    async def delete_employee(employee_id: UUID) -> bool:
        """Delete employee"""
        try:
            result = await Employee.delete(employee_id)
            if result:
                logger.info(f"Employee deleted: {employee_id}")
            return result
        except Exception as e:
            logger.error(f"Error deleting employee {employee_id}: {e}")
            raise

    @staticmethod
    async def change_employee_stage(
        employee_id: UUID,
        new_stage: str,
        notes: Optional[str] = None
    ) -> Optional[EmployeeResponse]:
        """Change employee onboarding stage with optional notes"""
        try:
            # Update both status and review notes if provided
            update_data = {"status": new_stage}
            if notes:
                update_data["review_notes"] = notes
                logger.info(f"Stage change notes: {notes[:100]}...")  # Log first 100 chars
            
            employee = await Employee.update(employee_id, **update_data)
            if employee:
                logger.info(f"Employee {employee.email} moved to stage: {new_stage}")
                
                # If accepted, mark onboarding as potentially complete
                if new_stage == EmployeeStatus.ACCEPTED.value:
                    await Employee.update(employee_id, onboarding_complete=True)
                
                return EmployeeResponse.model_validate(employee.to_dict())
            return None
        except Exception as e:
            logger.error(f"Error changing employee stage: {e}")
            raise

    @staticmethod
    async def bulk_import_employees(
        csv_content: str,
        company_id: Optional[UUID] = None,
        ai_enrich: bool = False,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Bulk import employees from CSV content
        Returns: {"success": count, "failed": count, "errors": [...]}
        """
        try:
            # Parse CSV
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            success_count = 0
            failed_count = 0
            errors = []
            created_employees = []

            for idx, row in enumerate(reader, start=2):  # Start from 2 (1 is header)
                try:
                    # Validate row data
                    employee_row = EmployeeCSVRow(
                        name=row.get('name', row.get('Name', '')),
                        email=row.get('email', row.get('Email', '')),
                        phone=row.get('phone', row.get('Phone')),
                        job_title=row.get('job_title', row.get('Job Title')),
                        role=row.get('role', row.get('Role')),
                        department=row.get('department', row.get('Department')),
                        location=row.get('location', row.get('Location')),
                        bill_rate=float(row.get('bill_rate', row.get('Bill Rate', 0))) if row.get('bill_rate') or row.get('Bill Rate') else None,
                    )

                    # Create employee WITHOUT AI (to avoid blocking)
                    # AI enrichment will happen in background after all imports complete
                    employee_create = EmployeeCreate(
                        name=employee_row.name,
                        email=employee_row.email,
                        phone=employee_row.phone,
                        job_title=employee_row.job_title,
                        role=employee_row.role,
                        department=employee_row.department,
                        location=employee_row.location,
                        bill_rate=employee_row.bill_rate,
                        use_ai_suggestion=False  # Disable AI during bulk import to avoid timeout
                    )

                    employee = await EmployeeService.create_employee(
                        employee_create,
                        company_id=company_id,
                        created_by=created_by
                    )
                    created_employees.append(employee)
                    success_count += 1
                    logger.info(f"✅ Imported employee: {employee.email}")

                except Exception as e:
                    failed_count += 1
                    error_msg = f"Row {idx}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            # Queue AI enrichment for all created employees in background
            if created_employees and ai_enrich:
                logger.info(f"🚀 Queueing AI enrichment for {len(created_employees)} employees in background...")
                
                # Run AI enrichment in background (non-blocking)
                async def enrich_employees_background():
                    for emp in created_employees:
                        try:
                            # emp.id is already a UUID or string from EmployeeResponse
                            emp_id = UUID(str(emp.id)) if not isinstance(emp.id, UUID) else emp.id
                            logger.info(f"🤖 AI enriching employee: {emp.email}")
                            
                            # Get AI suggestions
                            ai_suggestion = await gemini_service.suggest_role_and_skills(
                                name=emp.name,
                                job_title=emp.job_title or '',
                                department=emp.department or ''
                            )
                            
                            # Update employee with AI suggestions
                            update_data = EmployeeUpdate(
                                role=ai_suggestion.suggested_role if not emp.role else emp.role,
                                department=ai_suggestion.suggested_department if not emp.department else emp.department,
                                skills=ai_suggestion.suggested_skills if not emp.skills else emp.skills,
                                bill_rate=ai_suggestion.bill_rate_suggestion if not emp.bill_rate else emp.bill_rate,
                            )
                            
                            await EmployeeService.update_employee(emp_id, update_data)
                            logger.info(f"✅ AI enrichment completed for {emp.email}")
                            
                        except Exception as e:
                            logger.error(f"❌ AI enrichment failed for {emp.email}: {e}")
                
                # Fire and forget - don't wait for completion
                asyncio.create_task(enrich_employees_background())
                logger.info(f"🎯 AI enrichment started in background for {len(created_employees)} employees")

            return {
                "success": success_count,
                "failed": failed_count,
                "errors": errors,
                "employees": created_employees,
                "ai_analysis_queued": success_count if ai_enrich else 0
            }

        except Exception as e:
            logger.error(f"Error in bulk import: {e}")
            raise

    @staticmethod
    async def get_ai_role_suggestion(
        request: AIRoleSuggestionRequest
    ) -> Dict[str, Any]:
        """Get AI role and skills suggestion"""
        try:
            suggestion = await gemini_service.suggest_role_and_skills(
                name=request.name,
                job_title=request.job_title,
                department=request.department,
                company_industry=request.company_industry
            )
            return suggestion.model_dump()
        except Exception as e:
            logger.error(f"Error getting AI suggestion: {e}")
            raise

    @staticmethod
    async def analyze_skills_gap(
        company_id: Optional[UUID] = None
    ) -> SkillsGapResponse:
        """
        AI-powered skills gap analysis based on actual opportunities and projects
        Analyzes opportunities/projects to determine required skills, then compares with available team skills
        """
        try:
            # Get all accepted/active employees
            employees = await Employee.get_all(
                company_id=company_id,
                status=EmployeeStatus.ACCEPTED.value
            )

            # Count current team skills
            skill_counts: Dict[str, int] = {}
            all_team_skills = []
            for emp in employees:
                if emp.skills:
                    for skill in emp.skills:
                        skill_counts[skill] = skill_counts.get(skill, 0) + 1
                        all_team_skills.append(skill)

            # Get active opportunities and projects to analyze skill requirements
            from app.models.opportunity import Opportunity, OpportunityStage
            from sqlalchemy import select, and_, or_
            from app.db.session import get_session
            
            async with get_session() as db:
                # Get active opportunities (won, negotiation, shortlisted, proposal_development)
                active_opportunities_result = await db.execute(
                    select(Opportunity).where(
                        and_(
                            Opportunity.org_id == company_id,
                            or_(
                                Opportunity.stage == OpportunityStage.won,
                                Opportunity.stage == OpportunityStage.negotiation,
                                Opportunity.stage == OpportunityStage.shortlisted,
                                Opportunity.stage == OpportunityStage.proposal_development,
                            )
                        )
                    ).limit(20)
                )
                active_opportunities = active_opportunities_result.scalars().all()

            # Build context for AI analysis
            opportunities_context = []
            for opp in active_opportunities:
                opp_data = {
                    "project_name": opp.project_name,
                    "description": opp.description or "",
                    "market_sector": opp.market_sector or "",
                    "team_size": opp.team_size or 0,
                    "project_value": float(opp.project_value) if opp.project_value else 0,
                    "stage": opp.stage.value if opp.stage else "",
                }
                opportunities_context.append(opp_data)

            # Use AI to analyze opportunities and suggest required skills
            project_demands = {}
            if opportunities_context and gemini_service.enabled:
                try:
                    # Build AI prompt to analyze opportunities and suggest skills
                    opportunities_text = "\n".join([
                        f"Project: {o['project_name']} | Sector: {o['market_sector']} | "
                        f"Team Size: {o['team_size']} | Value: ${o['project_value']:,.0f} | "
                        f"Description: {o['description'][:200]}"
                        for o in opportunities_context[:10]  # Limit to 10 for prompt size
                    ])
                    
                    current_skills_summary = ", ".join(set(all_team_skills[:20]))  # Top 20 unique skills
                    
                    prompt = f"""You are an AI workforce planning analyst for a contractor/construction company (builders, interior designers, material suppliers).

Analyze these active opportunities/projects and suggest the skills needed to fulfill them:

ACTIVE OPPORTUNITIES/PROJECTS:
{opportunities_text}

CURRENT TEAM SKILLS:
{current_skills_summary if current_skills_summary else "No skills data yet"}

Based on the opportunities above, analyze what contractor-specific skills are needed. Consider:
- Construction & Building: General Construction, Residential/Commercial Construction, Framing & Carpentry, Electrical/Plumbing/HVAC Installation, Flooring, Painting, etc.
- Interior Design: Interior Design, Space Planning, Kitchen/Bathroom Design, CAD Design, Material Selection, etc.
- Material Supply: Material Procurement, Supply Chain Management, Vendor Relations, Cost Estimation, etc.
- Project Management: Project Management, Site Supervision, Quality Assurance, Safety Management, etc.

Return ONLY a JSON object with this exact format:
{{
  "required_skills": {{
    "Skill Name 1": <number of people needed>,
    "Skill Name 2": <number of people needed>,
    ...
  }},
  "analysis_summary": "Brief explanation of why these skills are needed"
}}

Focus on contractor-specific skills only. Return maximum 10-15 most critical skills. Prioritize skills with highest gaps.
Return ONLY valid JSON, no markdown or explanation."""

                    # Call Gemini AI
                    response = await asyncio.to_thread(
                        gemini_service.model.generate_content,
                        prompt
                    )
                    response_text = response.text.strip()
                    
                    # Parse JSON from response
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', response_text)
                    if json_match:
                        ai_result = json.loads(json_match.group())
                        project_demands = ai_result.get("required_skills", {})
                        logger.info(f"✅ AI suggested {len(project_demands)} skills based on {len(opportunities_context)} opportunities")
                    else:
                        logger.warning("Failed to parse AI response, using fallback")
                        project_demands = {}
                        
                except Exception as ai_error:
                    logger.error(f"AI analysis failed: {ai_error}, using fallback")
                    project_demands = {}
            
            # Fallback: If no opportunities or AI fails, use contractor industry standards
            if not project_demands:
                logger.info("Using fallback contractor industry standard demands")
                project_demands = {
                    "General Construction": 6,
                    "Project Management": 4,
                    "Interior Design": 3,
                    "Material Procurement": 3,
                    "Site Supervision": 3,
                }

            # Calculate gaps - only show skills with actual gaps or high demand
            gaps = []
            for skill, required in project_demands.items():
                available = skill_counts.get(skill, 0)
                gap = max(0, required - available)
                
                # Only include skills that have gaps OR are in high demand (required >= 3)
                if gap > 0 or required >= 3:
                    priority = "high" if gap >= 2 else "medium" if gap == 1 else "low"
                    
                    gaps.append(SkillGapAnalysis(
                        skill=skill,
                        required=required,
                        available=available,
                        gap=gap,
                        priority=priority
                    ))
            
            # Sort by gap (highest first), then by priority, limit to top 10-12 most critical
            gaps.sort(key=lambda x: (x.gap, 1 if x.priority == "high" else 2 if x.priority == "medium" else 3), reverse=True)
            gaps = gaps[:12]  # Only show top 12 most critical skills

            total_gap = sum(g.gap for g in gaps)
            critical_gaps = sum(1 for g in gaps if g.priority == "high")

            return SkillsGapResponse(
                total_employees=len(employees),
                accepted_employees=len(employees),
                total_gap=total_gap,
                critical_gaps=critical_gaps,
                skill_gaps=gaps
            )

        except Exception as e:
            logger.error(f"Error analyzing skills gap: {e}", exc_info=True)
            raise

    @staticmethod
    async def get_onboarding_dashboard(
        company_id: Optional[UUID] = None
    ) -> OnboardingDashboard:
        """Get onboarding dashboard statistics"""
        try:
            # Get all employees
            all_employees = await Employee.get_all(company_id=company_id, limit=1000)

            # Count by status
            pending = sum(1 for e in all_employees if e.status == EmployeeStatus.PENDING.value)
            review = sum(1 for e in all_employees if e.status == EmployeeStatus.REVIEW.value)
            accepted = sum(1 for e in all_employees if e.status == EmployeeStatus.ACCEPTED.value)
            rejected = sum(1 for e in all_employees if e.status == EmployeeStatus.REJECTED.value)
            active = sum(1 for e in all_employees if e.status == EmployeeStatus.ACTIVE.value)
            
            # Pending invites (pending status with invite sent)
            pending_invites = sum(
                1 for e in all_employees 
                if e.status == EmployeeStatus.PENDING.value and e.invite_sent_at
            )
            
            # Onboarding complete
            onboarding_complete_count = sum(1 for e in all_employees if e.onboarding_complete)

            # Recent hires (last 10 accepted)
            recent = [e for e in all_employees if e.status == EmployeeStatus.ACCEPTED.value]
            recent.sort(key=lambda x: x.created_at, reverse=True)
            recent_hires = [EmployeeResponse.model_validate(e.to_dict()) for e in recent[:10]]

            return OnboardingDashboard(
                total_employees=len(all_employees),
                pending_count=pending,
                review_count=review,
                accepted_count=accepted,
                rejected_count=rejected,
                active_count=active,
                pending_invites=pending_invites,
                onboarding_complete=onboarding_complete_count,
                recent_hires=recent_hires
            )

        except Exception as e:
            logger.error(f"Error getting onboarding dashboard: {e}")
            raise


# Global instance
employee_service = EmployeeService()

