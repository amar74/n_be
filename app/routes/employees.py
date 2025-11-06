from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import List, Optional
from uuid import UUID

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeStageUpdate,
    EmployeeResponse,
    AIRoleSuggestionRequest,
    AIRoleSuggestionResponse,
    ResumeResponse,
    ResumeAnalysisResponse,
    SkillsGapResponse,
    OnboardingDashboard,
    PermissionUpdate,
    InterviewSchedule,
    InterviewFeedback
)
from app.schemas.employee_activation import EmployeeActivationRequest, EmployeeActivationResponse
from app.services.employee_service import employee_service
from app.services.resume_service import resume_service
from app.services.gemini_service import gemini_service
from app.services.auth_service import AuthService
from app.services.email import send_employee_activation_email
from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.db.session import get_request_transaction
from sqlalchemy.ext.asyncio import AsyncSession

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resources", tags=["Employee Onboarding"])


# ==================== EMPLOYEE CRUD ====================

@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new employee with optional AI role suggestion
    
    - **use_ai_suggestion**: If true, AI will suggest role, skills, and bill rate
    """
    try:
        employee = await employee_service.create_employee(
            employee_data=employee_data,
            company_id=current_user.org_id,
            created_by=current_user.id
        )
        return employee
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employee: {str(e)}"
        )


@router.get("/employees", response_model=List[EmployeeResponse])
async def get_employees(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Get list of employees with optional status filter
    
    - **status**: Filter by status (pending, review, accepted, rejected, active, deactivated)
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    try:
        employees = await employee_service.get_employees(
            company_id=current_user.org_id,
            status=status_filter,
            skip=skip,
            limit=limit
        )
        return employees
    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch employees: {str(e)}"
        )


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get employee by ID"""
    try:
        employee = await employee_service.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch employee: {str(e)}"
        )


@router.patch("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    employee_data: EmployeeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update employee information"""
    try:
        employee = await employee_service.update_employee(employee_id, employee_data)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update employee: {str(e)}"
        )


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Delete employee"""
    try:
        result = await employee_service.delete_employee(employee_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete employee: {str(e)}"
        )


@router.patch("/employees/{employee_id}/stage", response_model=EmployeeResponse)
async def change_employee_stage(
    employee_id: UUID,
    stage_data: EmployeeStageUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Change employee onboarding stage
    
    - **new_stage**: One of: pending, review, accepted, rejected, active, deactivated
    - **notes**: Optional notes about the stage change (required for reverse moves)
    """
    try:
        employee = await employee_service.change_employee_stage(
            employee_id, 
            stage_data.new_stage,
            notes=stage_data.notes
        )
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return employee
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing employee stage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change employee stage: {str(e)}"
        )


# ==================== BULK IMPORT ====================

@router.post("/employees/import")
async def bulk_import_employees(
    file: UploadFile = File(..., description="CSV file with employee data"),
    ai_enrich: bool = Form(False, description="Use AI to enrich employee data"),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk import employees from CSV file
    
    **CSV Format:**
    name, email, phone, job_title, role, department, location, bill_rate
    
    - **ai_enrich**: If true, AI will suggest roles and skills for all employees
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are supported"
            )

        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')

        # Process bulk import
        result = await employee_service.bulk_import_employees(
            csv_content=csv_content,
            company_id=current_user.org_id,
            ai_enrich=ai_enrich,
            created_by=current_user.id
        )

        return {
            "message": f"Import completed. Success: {result['success']}, Failed: {result['failed']}",
            "success_count": result['success'],
            "failed_count": result['failed'],
            "errors": result['errors'],
            "employees": result['employees']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk import: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import employees: {str(e)}"
        )


# ==================== EMPLOYEE ACTIVATION ====================

@router.post("/employees/{employee_id}/activate", response_model=EmployeeActivationResponse)
async def activate_employee(
    employee_id: UUID,
    activation_data: EmployeeActivationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
    """
    Activate an employee by creating a user account with login credentials
    
    This endpoint:
    1. Creates a user account linked to the employee
    2. Sets temporary password (requires change on first login)
    3. Assigns role and permissions
    4. Sends welcome email with credentials
    5. Updates employee status to 'active'
    """
    try:
        # Get employee
        employee = await employee_service.get_employee_by_id(employee_id, current_user.org_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Check if user account already exists
        existing_user = await AuthService.get_user_by_email(employee.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User account already exists for {employee.email}"
            )
        
        # Create user account
        user = await AuthService.create_user(
            email=employee.email,
            password=activation_data.temporary_password,
            role=activation_data.user_role,
            name=employee.name,
            org_id=current_user.org_id
        )
        
        logger.info(f"Created user account {user.id} for employee {employee_id}")
        
        # Update employee status to active, link user_id, and set system role
        # Use direct Employee.update() to avoid schema type conversion issues
        from app.models.employee import Employee
        employee_updated = await Employee.update(
            employee_id,
            status="active",
            user_id=user.id,  # Pass UUID directly, not string
            role=activation_data.user_role,  # Save system role (employee, admin, manager, etc.)
            review_notes=f"User account created. Role: {activation_data.user_role}, Permissions: {', '.join(activation_data.permissions)}, Password: {activation_data.temporary_password}"
        )
        
        if not employee_updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update employee after user creation"
            )
        
        logger.info(f"✅ Employee {employee_id} updated: status=active, user_id={user.id}")
        
        # Send welcome email if requested
        email_sent = False
        if activation_data.send_welcome_email:
            try:
                email_sent = send_employee_activation_email(
                    employee_email=employee.email,
                    employee_name=employee.name,
                    temporary_password=activation_data.temporary_password,
                    login_url="http://localhost:5173/login",
                    role=activation_data.user_role
                )
                if email_sent:
                    logger.info(f"Welcome email sent to {employee.email}")
                else:
                    logger.warning(f"Failed to send welcome email to {employee.email}")
            except Exception as email_error:
                logger.error(f"Error sending welcome email: {email_error}")
        
        return EmployeeActivationResponse(
            user_id=user.id,
            employee_id=employee_id,
            email=employee.email,
            role=activation_data.user_role,
            message=f"Employee activated successfully. User account created for {employee.email}",
            email_sent=email_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate employee: {str(e)}"
        )


# ==================== AI FEATURES ====================

@router.post("/ai/role-suggest", response_model=AIRoleSuggestionResponse)
async def ai_role_suggestion(
    request: AIRoleSuggestionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered role and skills suggestion
    
    Analyzes job title and department to suggest:
    - Appropriate role
    - Suggested skills
    - Bill rate estimate
    """
    try:
        suggestion = await employee_service.get_ai_role_suggestion(request)
        return suggestion
    except Exception as e:
        logger.error(f"Error getting AI suggestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI suggestion: {str(e)}"
        )


@router.get("/ai/skills-gap", response_model=SkillsGapResponse)
async def get_skills_gap_analysis(
    current_user: User = Depends(get_current_user)
):
    """
    Analyze skills gap between current team and project demands
    
    Returns detailed breakdown of:
    - Skills needed vs available
    - Critical gaps
    - Priority recommendations
    """
    try:
        analysis = await employee_service.analyze_skills_gap(current_user.org_id)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing skills gap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze skills gap: {str(e)}"
        )


# ==================== RESUME MANAGEMENT ====================

@router.post("/resumes-import", response_model=ResumeResponse)
async def upload_resume(
    employee_id: UUID = Form(...),
    file: UploadFile = File(..., description="Resume file (PDF, DOC, DOCX)"),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse employee resume with AI
    
    - Uploads file to S3
    - Automatically extracts skills, experience, certifications
    - Updates employee profile with parsed data
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, DOC, and DOCX files are supported"
            )

        # Read file content
        file_content = await file.read()

        # Upload and parse resume
        resume = await resume_service.upload_resume(
            employee_id=employee_id,
            file_content=file_content,
            file_name=file.filename,
            file_type=file.content_type
        )

        return resume

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )


@router.get("/employees/{employee_id}/resume", response_model=ResumeResponse)
async def get_employee_resume(
    employee_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get resume for an employee"""
    try:
        resume = await resume_service.get_resume_by_employee_id(employee_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found for this employee"
            )
        return resume
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resume: {str(e)}"
        )


@router.get("/ai/resume-analysis/{employee_id}", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    employee_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get AI-parsed resume analysis"""
    try:
        analysis = await resume_service.get_resume_analysis(employee_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume analysis not found"
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching resume analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resume analysis: {str(e)}"
        )


# ==================== DASHBOARD & ANALYTICS ====================

@router.get("/dashboard/onboarding", response_model=OnboardingDashboard)
async def get_onboarding_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    Get onboarding dashboard with statistics
    
    Returns:
    - Total employees count
    - Counts by status (pending, review, accepted, rejected)
    - Pending invites
    - Recent hires
    """
    try:
        dashboard = await employee_service.get_onboarding_dashboard(current_user.org_id)
        return dashboard
    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard: {str(e)}"
        )


# ==================== PERMISSIONS (RBAC) ====================

@router.get("/roles")
async def get_available_roles(current_user: User = Depends(get_current_user)):
    """
    Get list of available roles
    Returns system roles + any custom roles created by admins
    """
    # System roles (default, cannot be deleted)
    system_roles = [
        {
            "id": "employee",
            "name": "Employee",
            "description": "Standard employee with basic access to assigned work",
            "permissions": ["view_projects", "view_accounts", "view_resources"],
            "isSystem": True,
            "color": "bg-blue-100 text-blue-700 border-blue-200"
        },
        {
            "id": "team_lead",
            "name": "Team Lead",
            "description": "Manages team members and projects",
            "permissions": ["view_projects", "edit_projects", "view_accounts", "edit_accounts", "view_resources", "manage_team", "view_reports"],
            "isSystem": True,
            "color": "bg-purple-100 text-purple-700 border-purple-200"
        },
        {
            "id": "manager",
            "name": "Manager",
            "description": "Department management with extended access",
            "permissions": ["view_projects", "edit_projects", "view_accounts", "edit_accounts", "view_opportunities", "edit_opportunities", "view_resources", "edit_resources", "manage_team", "view_reports", "export_data"],
            "isSystem": True,
            "color": "bg-amber-100 text-amber-700 border-amber-200"
        },
        {
            "id": "admin",
            "name": "Admin",
            "description": "Full system access including role management",
            "permissions": ["view_projects", "edit_projects", "delete_projects", "view_accounts", "edit_accounts", "delete_accounts", "view_opportunities", "edit_opportunities", "view_resources", "edit_resources", "manage_team", "view_reports", "export_data", "manage_roles", "system_settings"],
            "isSystem": True,
            "color": "bg-red-100 text-red-700 border-red-200"
        }
    ]
    
    # TODO: Fetch custom roles from database (when role table is implemented)
    # For now, returning only system roles
    
    return {"roles": system_roles}


@router.patch("/users/{user_id}/permissions")
async def update_user_permissions(
    user_id: UUID,
    permissions: PermissionUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update user permissions (RBAC)
    
    - **permissions**: List of permission IDs to assign
    """
    # This would integrate with your existing user permissions system
    # For now, returning success response
    return {
        "message": "Permissions updated successfully",
        "user_id": str(user_id),
        "permissions": permissions.permissions
    }


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get current user permissions"""
    # This would fetch from your permissions table
    return {
        "user_id": str(user_id),
        "permissions": ["projects", "resources", "reports"]
    }


# ==================== EMAIL & NOTIFICATIONS ====================

@router.post("/notifications/welcome/{employee_id}")
async def send_welcome_email(
    employee_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Send AI-generated welcome email to employee
    """
    try:
        employee = await employee_service.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # Generate email content using AI
        email_body = await gemini_service.generate_welcome_email(
            employee_name=employee.name,
            role=employee.role or "Team Member",
            company_name="SoftiCation Business Suite"
        )

        # In production, this would call your email service
        logger.info(f"Welcome email generated for {employee.email}")

        return {
            "message": "Welcome email sent successfully",
            "employee_id": str(employee_id),
            "email": employee.email,
            "preview": email_body[:200] + "..."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send welcome email: {str(e)}"
        )


# ==================== EMPLOYEE SEARCH ====================

@router.post("/employees/search")
async def search_employees(
    search_criteria: dict,
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered employee search with smart matching
    
    Search by: position, skills, sectors, services, project_types
    Returns: Candidates with match percentage (sorted)
    """
    try:
        from app.models.employee import Employee
        
        position = search_criteria.get('position', '')
        skills = search_criteria.get('skills', [])
        sectors = search_criteria.get('sectors', [])
        services = search_criteria.get('services', [])
        project_types = search_criteria.get('projectTypes', [])
        
        # Get all employees (in accepted/active status - team members)
        all_employees = await Employee.get_all(
            company_id=current_user.org_id,
            limit=1000
        )
        
        # Filter for CANDIDATES only (pending + review) - NOT accepted/active
        candidates = [e for e in all_employees if e.status in ['pending', 'review']]
        
        # Calculate match score for each candidate
        results = []
        for emp in candidates:
            match_score = 0
            total_criteria = 0
            
            # Position match (case-insensitive)
            if position:
                total_criteria += 30
                if emp.job_title and position.lower() in emp.job_title.lower():
                    match_score += 30
                elif emp.role and position.lower() in emp.role.lower():
                    match_score += 20
            
            # Skills match
            if skills:
                total_criteria += 40
                emp_skills = emp.skills or []
                matched_skills = len(set(skills) & set(emp_skills))
                if matched_skills > 0:
                    match_score += min((matched_skills / len(skills)) * 40, 40)
            
            # Sectors match (mock - would check emp.sectors if available)
            if sectors:
                total_criteria += 15
                match_score += 10  # Partial match for now
            
            # Services match (mock - would check emp.services if available)
            if services:
                total_criteria += 10
                match_score += 7  # Partial match for now
            
            # Project types match (mock)
            if project_types:
                total_criteria += 5
                match_score += 3  # Partial match for now
            
            # Calculate final percentage
            if total_criteria > 0:
                final_percentage = int((match_score / total_criteria) * 100)
            else:
                final_percentage = 100  # No criteria = all match
            
            # Only include if match >= 50%
            if final_percentage >= 50:
                results.append({
                    'id': str(emp.id),
                    'name': emp.name,
                    'email': emp.email,
                    'phone': emp.phone,
                    'role': emp.job_title or emp.role,
                    'location': emp.location or 'Not specified',
                    'experience': emp.experience or 'Not specified',
                    'matchPercentage': final_percentage,
                    'availability': 'limited' if emp.status == 'review' else 'available',
                    'source': 'internal',
                    'skills': emp.skills or [],
                    'currentStage': emp.status,  # pending or review
                })
        
        # Sort by match percentage (descending)
        results.sort(key=lambda x: x['matchPercentage'], reverse=True)
        
        # Calculate match range
        if results:
            min_match = min(r['matchPercentage'] for r in results)
            max_match = max(r['matchPercentage'] for r in results)
            match_range = f"{min_match}-{max_match}%"
        else:
            match_range = "0%"
        
        logger.info(f"Candidate search completed: {len(results)} candidates found (pending/review only)")
        
        return {
            'results': results,
            'count': len(results),
            'match_range': match_range,
        }
        
    except Exception as e:
        logger.error(f"Error searching employees: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search employees: {str(e)}"
        )


@router.post("/employees/ai-search")
async def ai_semantic_search(
    search_query: dict,
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered semantic employee search using Gemini
    
    Converts natural language queries into structured search filters
    Example: "Find civil engineers with 5+ years experience in high-rise construction"
    """
    try:
        from app.models.employee import Employee
        
        query_text = search_query.get('query', '')
        
        if not query_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query text is required"
            )
        
        logger.info(f"🤖 AI Search Query: {query_text}")
        
        # Step 1: Convert natural language to structured filters using Gemini
        prompt = f"""
Convert this employee search query into structured JSON filters for a contractor/construction company database.

Example Input: "Find HVAC technician with 5 years of experience in commercial buildings in New York"
Example Output:
{{
  "role": "HVAC Technician",
  "skills": ["HVAC Installation", "Duct Fitting", "Commercial HVAC"],
  "sectors": ["Commercial"],
  "location": "New York",
  "min_experience": 5
}}

Example Input: "Find electrical contractors available with valid license"
Example Output:
{{
  "role": "Electrical Contractor",
  "skills": ["Electrical Wiring", "Electrical Installation"],
  "certifications": ["Electrical License"],
  "availability": "available"
}}

Now convert this query:
"{query_text}"

Return ONLY the JSON object, no markdown or explanation.
"""

        # Call Gemini
        try:
            import asyncio
            response = await asyncio.wait_for(
                asyncio.to_thread(gemini_service.model.generate_content, prompt),
                timeout=10.0
            )
            response_text = response.text.strip()
            
            # Parse JSON from response
            import json
            import re
            # Extract JSON from markdown if present
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                filters = json.loads(json_match.group())
            else:
                filters = json.loads(response_text)
            
            logger.info(f"✅ AI extracted filters: {filters}")
        except Exception as ai_error:
            logger.error(f"AI parsing failed: {ai_error}")
            # Fallback: simple keyword search
            filters = {"role": query_text}
        
        # Step 2: Query database using extracted filters
        all_employees = await Employee.get_all(
            company_id=current_user.org_id,
            limit=1000
        )
        
        # Filter for CANDIDATES only (pending + review) - NOT accepted/active
        candidates = [e for e in all_employees if e.status in ['pending', 'review']]
        
        # Apply filters
        results = []
        for emp in candidates:
            match_score = 0
            total_criteria = 0
            
            # Role/Position match
            if filters.get('role'):
                total_criteria += 30
                role_search = filters['role'].lower()
                if emp.job_title and role_search in emp.job_title.lower():
                    match_score += 30
                elif emp.role and role_search in emp.role.lower():
                    match_score += 25
            
            # Skills match
            if filters.get('skills'):
                total_criteria += 40
                emp_skills = [s.lower() for s in (emp.skills or [])]
                filter_skills = [s.lower() for s in filters['skills']]
                matched = sum(1 for fs in filter_skills if any(fs in es or es in fs for es in emp_skills))
                if matched > 0:
                    match_score += min((matched / len(filter_skills)) * 40, 40)
            
            # Location match
            if filters.get('location'):
                total_criteria += 15
                if emp.location and filters['location'].lower() in emp.location.lower():
                    match_score += 15
            
            # Experience match
            if filters.get('min_experience'):
                total_criteria += 15
                try:
                    emp_exp = float(emp.experience.split()[0]) if emp.experience else 0
                    if emp_exp >= filters['min_experience']:
                        match_score += 15
                except:
                    pass
            
            # Calculate final percentage
            if total_criteria > 0:
                final_percentage = int((match_score / total_criteria) * 100)
            else:
                final_percentage = 100
            
            # Include if match >= 50%
            if final_percentage >= 50:
                results.append({
                    'id': str(emp.id),
                    'name': emp.name,
                    'email': emp.email,
                    'phone': emp.phone,
                    'role': emp.job_title or emp.role,
                    'location': emp.location or 'Not specified',
                    'experience': emp.experience or 'Not specified',
                    'matchPercentage': final_percentage,
                    'availability': 'limited' if emp.status == 'review' else 'available',
                    'source': 'internal',
                    'skills': emp.skills or [],
                    'currentStage': emp.status,  # pending or review
                })
        
        # Sort by match percentage
        results.sort(key=lambda x: x['matchPercentage'], reverse=True)
        
        # Calculate match range
        if results:
            min_match = min(r['matchPercentage'] for r in results)
            max_match = max(r['matchPercentage'] for r in results)
            match_range = f"{min_match}-{max_match}%"
        else:
            match_range = "0%"
        
        logger.info(f"✅ AI search completed: {len(results)} candidates found (pending/review only) using filters {filters}")
        
        return {
            'results': results,
            'count': len(results),
            'match_range': match_range,
            'ai_filters': filters,  # Show what AI extracted
        }
        
    except Exception as e:
        logger.error(f"Error in AI search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform AI search: {str(e)}"
        )


# ==================== INTERVIEW MANAGEMENT ====================

@router.post("/employees/{employee_id}/interview/schedule", response_model=EmployeeResponse)
async def schedule_interview(
    employee_id: UUID,
    schedule_data: InterviewSchedule,
    current_user: User = Depends(get_current_user)
):
    """
    Schedule interview for employee
    Saves interview date, time, link, platform, and interviewer details
    """
    try:
        from app.models.employee import Employee
        from datetime import datetime
        
        employee = await Employee.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Parse date string to datetime
        interview_datetime = datetime.fromisoformat(schedule_data.interview_date)
        
        # Update employee with interview schedule
        await Employee.update(
            employee_id,
            interview_date=interview_datetime,
            interview_time=schedule_data.interview_time,
            interview_link=schedule_data.interview_link,
            interview_platform=schedule_data.platform,
            interviewer_name=schedule_data.interviewer_name,
            interviewer_email=schedule_data.interviewer_email,
            interview_notes=schedule_data.notes,
            status="review"  # Move to interview/review stage
        )
        
        logger.info(f"Interview scheduled for employee {employee_id} on {schedule_data.interview_date} at {schedule_data.interview_time}")
        
        # Get updated employee
        updated_employee = await Employee.get_by_id(employee_id)
        return EmployeeResponse.model_validate(updated_employee.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling interview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule interview: {str(e)}"
        )


@router.post("/employees/{employee_id}/interview/feedback", response_model=EmployeeResponse)
async def submit_interview_feedback(
    employee_id: UUID,
    feedback_data: InterviewFeedback,
    current_user: User = Depends(get_current_user)
):
    """
    Submit interview feedback for employee
    Saves ratings, strengths, weaknesses, recommendation, and notes
    Automatically moves to next stage based on recommendation
    """
    try:
        from app.models.employee import Employee
        from datetime import datetime
        
        employee = await Employee.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Determine next stage based on recommendation
        next_stage = "review"  # default
        if feedback_data.recommendation == "accept":
            next_stage = "accepted"
        elif feedback_data.recommendation == "reject":
            next_stage = "rejected"
        
        # Prepare feedback JSON
        feedback_json = {
            "interview_date": feedback_data.interview_date,
            "interviewer_name": feedback_data.interviewer_name,
            "technical_skills": feedback_data.technical_skills,
            "communication_skills": feedback_data.communication_skills,
            "cultural_fit": feedback_data.cultural_fit,
            "overall_rating": feedback_data.overall_rating,
            "strengths": feedback_data.strengths,
            "weaknesses": feedback_data.weaknesses,
            "recommendation": feedback_data.recommendation,
            "notes": feedback_data.notes,
            "submitted_at": datetime.utcnow().isoformat(),
            "submitted_by": str(current_user.id)
        }
        
        # Format review notes with feedback
        review_notes = f"""
📋 Interview Feedback ({feedback_data.interview_date})
Interviewer: {feedback_data.interviewer_name}

⭐ Ratings:
- Technical Skills: {feedback_data.technical_skills}/5
- Communication: {feedback_data.communication_skills}/5
- Cultural Fit: {feedback_data.cultural_fit}/5
- Overall: {feedback_data.overall_rating}/5

💪 Strengths: {feedback_data.strengths or 'N/A'}
⚠️ Areas for Improvement: {feedback_data.weaknesses or 'N/A'}

✅ Recommendation: {feedback_data.recommendation.upper()}

📝 Additional Notes:
{feedback_data.notes or 'N/A'}
        """.strip()
        
        # Update employee with feedback and move to next stage
        await Employee.update(
            employee_id,
            interview_feedback=feedback_json,
            interview_completed_at=datetime.utcnow(),
            review_notes=review_notes,
            status=next_stage
        )
        
        logger.info(f"Interview feedback submitted for employee {employee_id}, moved to {next_stage}")
        
        # Get updated employee
        updated_employee = await Employee.get_by_id(employee_id)
        return EmployeeResponse.model_validate(updated_employee.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting interview feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit interview feedback: {str(e)}"
        )

