from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.db.session import get_request_transaction, get_session, get_transaction
from app.utils.logger import get_logger

import logging

logger = get_logger(__name__)

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


@router.get("/employees/me", response_model=EmployeeResponse)
async def get_my_employee(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
    """Get current user's employee record"""
    try:
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found"
            )
        
        from app.models.employee import Employee
        from sqlalchemy import select, and_
        
        result = await db.execute(
            select(Employee).where(
                and_(
                    Employee.user_id == current_user.id,
                    Employee.company_id == current_user.org_id
                )
            )
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found for current user"
            )
        
        return EmployeeResponse.model_validate(employee.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch employee: {str(e)}"
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
        logger.info(f"🔍 Activating employee {employee_id} for org {current_user.org_id}")
        
        # Get employee
        employee = await employee_service.get_employee_by_id(employee_id, current_user.org_id)
        if not employee:
            logger.warning(f"❌ Employee {employee_id} not found for org {current_user.org_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        logger.info(f"✅ Found employee: {employee.name}, employee_number={employee.employee_number}, email={employee.email}")
        
        # Validate employee has required fields
        if not employee.employee_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee does not have an employee number. Please ensure the employee record is properly created."
            )
        
        if not employee.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee does not have an email address. Please update the employee record first."
            )
        
        # Use employee_number as username for login (no email conflicts!)
        # Email is stored but only for communication, not authentication
        username = employee.employee_number
        user_email = employee.email  # Keep original email for communication
        
        logger.info(f"Activating employee: username={username}, email={user_email}, name={employee.name}")
        
        # Check if user account already exists with this username in the SAME organization
        # Also check if email is already in use (email must be unique globally)
        # Use the same db session for consistency
        from sqlalchemy import select, and_, or_
        
        # Check for existing user by username in same org OR by email (globally unique)
        existing_user_result = await db.execute(
            select(User).where(
                or_(
                    and_(
                        User.username == username,
                        User.org_id == current_user.org_id
                    ),
                    User.email == user_email  # Email must be globally unique
                )
            )
        )
        existing_user = existing_user_result.scalar_one_or_none()
        
        # If user exists with same email but different org, that's a conflict
        if existing_user and existing_user.email == user_email and existing_user.org_id != current_user.org_id:
            logger.warning(f"Email {user_email} already exists for user {existing_user.id} in org {existing_user.org_id}")
            # This is okay - we use username for login, email can be shared
            # But we should still use the existing user if username matches
            if existing_user.username != username or existing_user.org_id != current_user.org_id:
                existing_user = None  # Don't reuse if username/org doesn't match
        
        if existing_user:
            # User exists in the SAME organization with the same username
            # Re-link and update password
            logger.info(f"User account already exists for username={username}, re-linking to employee {employee_id}")
            user = existing_user
            
            # Update user's password
            if activation_data.temporary_password:
                try:
                    from app.services.auth_service import AuthService
                    user.password_hash = AuthService.get_password_hash(activation_data.temporary_password)
                    await db.flush()
                    logger.info(f"Updated password for existing user {user.id}")
                except Exception as pw_error:
                    logger.error(f"Failed to update password: {pw_error}", exc_info=True)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to update user password: {str(pw_error)}"
                    )
        else:
            # Create new user account with employee_number as username
            # Email can be shared across organizations - username is unique per org
            try:
                from app.services.auth_service import AuthService
                from app.models.user import generate_short_user_id
                
                # Generate unique short_id
                short_id = generate_short_user_id()
                while True:
                    existing_short = await db.execute(select(User).where(User.short_id == short_id))
                    if not existing_short.scalar_one_or_none():
                        break
                    short_id = generate_short_user_id()
                
                # Check if email is already in use (even if username is different)
                email_check = await db.execute(select(User).where(User.email == user_email))
                email_user = email_check.scalar_one_or_none()
                
                if email_user:
                    # Email already exists - we can't create a new user with this email
                    # But if it's in the same org and has the same username, we can reuse
                    if email_user.org_id == current_user.org_id and email_user.username == username:
                        logger.info(f"Reusing existing user with email {user_email} and username {username}")
                        user = email_user
                        # Update password
                        user.password_hash = AuthService.get_password_hash(activation_data.temporary_password)
                        await db.flush()
                        await db.refresh(user)
                    else:
                        # Email conflict - can't create user
                        logger.error(f"Email {user_email} already exists for user {email_user.id} in org {email_user.org_id}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Email {user_email} is already registered. Please use a different email or contact support."
                        )
                else:
                    # Create user in the same transaction
                    user = User(
                        email=user_email,
                        username=username,
                        password_hash=AuthService.get_password_hash(activation_data.temporary_password),
                        role=activation_data.user_role,
                        name=employee.name,
                        org_id=current_user.org_id,
                        short_id=short_id
                    )
                    db.add(user)
                    await db.flush()
                    await db.refresh(user)
                    logger.info(f"✅ Created user account: username={username}, email={user_email}, user_id={user.id}")
            except Exception as create_error:
                logger.error(f"Error creating user account: {create_error}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user account: {str(create_error)}"
                )
        
        # Update employee status to active, link user_id, and set system role
        # Use the existing db session from the request transaction
        from app.models.employee import Employee
        from sqlalchemy import select
        try:
            logger.info(f"🔄 Updating employee {employee_id} with user_id={user.id}")
            
            # Get the employee using the existing db session
            # First try without org check to see if employee exists
            result = await db.execute(
                select(Employee).where(Employee.id == employee_id)
            )
            employee_model = result.scalar_one_or_none()
            
            if not employee_model:
                logger.error(f"❌ Employee {employee_id} not found in database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Employee not found in database"
                )
            
            # Verify it belongs to the same organization (if company_id is set)
            if employee_model.company_id is not None and employee_model.company_id != current_user.org_id:
                logger.error(f"❌ Employee {employee_id} belongs to org {employee_model.company_id}, but user org is {current_user.org_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Employee does not belong to your organization"
                )
            
            # If employee doesn't have company_id, set it now
            if employee_model.company_id is None:
                logger.info(f"Setting company_id for employee {employee_id} to {current_user.org_id}")
                employee_model.company_id = current_user.org_id
            
            logger.info(f"📝 Employee model found: id={employee_model.id}, company_id={employee_model.company_id}, current_user_id={employee_model.user_id}")
            
            # Update employee fields directly
            from app.models.employee import EmployeeStatus
            employee_model.status = EmployeeStatus.ACTIVE.value  # Use enum value
            employee_model.user_id = user.id  # Pass UUID directly
            employee_model.role = activation_data.user_role
            if activation_data.department:
                employee_model.department = activation_data.department
            employee_model.review_notes = f"User account created. Role: {activation_data.user_role}, Department: {activation_data.department or 'Not assigned'}, Password: {activation_data.temporary_password}"
            
            logger.info(f"💾 Flushing employee update: user_id={employee_model.user_id}, status={employee_model.status}")
            
            # Flush changes to the database
            try:
                await db.flush()
                await db.refresh(employee_model)
            except Exception as flush_error:
                logger.error(f"Database flush error: {flush_error}", exc_info=True)
                # Try to get more details about the error
                if hasattr(flush_error, 'orig'):
                    logger.error(f"Original error: {flush_error.orig}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error while updating employee: {str(flush_error)}"
                )
            
            logger.info(f"✅ Employee {employee_id} updated successfully: status=active, user_id={employee_model.user_id}")
        except HTTPException:
            raise
        except Exception as update_error:
            logger.error(f"Error updating employee: {update_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update employee: {str(update_error)}"
            )
        
        # Send welcome email if requested (use the user account email, not employee email)
        email_sent = False
        if activation_data.send_welcome_email:
            try:
                email_sent = send_employee_activation_email(
                    employee_email=user_email,  # Send to login email, not employee record email
                    employee_name=employee.name,
                    temporary_password=activation_data.temporary_password,
                    login_url="http://localhost:5173/login",
                    role=activation_data.user_role
                )
                if email_sent:
                    logger.info(f"Welcome email sent to {user_email}")
                else:
                    logger.warning(f"Failed to send welcome email to {user_email}")
            except Exception as email_error:
                logger.error(f"Error sending welcome email: {email_error}")
        
        # Build activation message with username (employee code) and user ID
        activation_message = f"Employee activated successfully! User ID: {user.id} | Login credentials: Username = {username}, Password = {activation_data.temporary_password}"
        
        return EmployeeActivationResponse(
            user_id=user.id,
            employee_id=employee_id,
            username=username,  # Employee ID for login (SFTAM001)
            email=user_email,  # Email for communication
            role=activation_data.user_role,
            message=activation_message,
            email_sent=email_sent
        )
        
    except HTTPException as http_ex:
        logger.error(f"HTTPException in activate_employee: {http_ex.status_code} - {http_ex.detail}")
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"❌ Unexpected error activating employee {employee_id}: {e}")
        logger.error(f"Full traceback:\n{error_trace}")
        
        # Check for common database errors
        error_str = str(e).lower()
        if "unique constraint" in error_str or "duplicate key" in error_str:
            if "email" in error_str or "users.email" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email is already registered. Please use a different email."
                )
            elif "username" in error_str or "users.username" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Username is already taken. Please contact support."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Database constraint violation: {str(e)}"
                )
        elif "foreign key" in error_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reference: {str(e)}"
            )
        else:
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
async def get_available_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
    
    from app.services.role_service import RoleService
    
    if not current_user.org_id:
        # Return empty if no org_id
        return {"roles": []}
    
    try:
        role_service = RoleService(db)
        # Fetch all roles (both system and custom) from database
        all_roles_db = await role_service.list_roles(current_user.org_id, include_system=True)
        
        # Convert to dict format expected by frontend
        roles = []
        for role in all_roles_db:
            role_dict = role.to_dict()
            # Ensure isSystem field matches frontend expectation (to_dict returns isSystem)
            # The to_dict method already converts is_system to isSystem
            roles.append(role_dict)
        
        return {"roles": roles}
    except Exception as e:
        logger.error(f"Error fetching roles: {e}")
        # Fallback to empty list on error
        return {"roles": []}


@router.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
    
    from app.services.role_service import RoleService
    from app.schemas.role import RoleResponse
    
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    # Check if user is admin
    user_role = current_user.role.lower() if current_user.role else ''
    if user_role not in ['admin', 'vendor', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create custom roles"
        )
    
    try:
        role_service = RoleService(db)
        role = await role_service.create_role(
            name=role_data.get('name'),
            org_id=current_user.org_id,
            description=role_data.get('description'),
            permissions=role_data.get('permissions', []),
            color=role_data.get('color'),
        )
        # Flush to ensure the role is persisted
        await db.flush()
        logger.info(f"Successfully created role: {role.name} (ID: {role.id}) for org {current_user.org_id}")
        return role.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


@router.put("/roles/{role_id}")
async def update_role(
    role_id: UUID,
    role_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
    
    from app.services.role_service import RoleService
    
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    # Check if user is admin
    user_role = current_user.role.lower() if current_user.role else ''
    if user_role not in ['admin', 'vendor', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update roles"
        )
    
    role_service = RoleService(db)
    role = await role_service.update_role(
        role_id=role_id,
        org_id=current_user.org_id,
        name=role_data.get('name'),
        description=role_data.get('description'),
        permissions=role_data.get('permissions'),
        color=role_data.get('color'),
    )
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role.to_dict()


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
   
    from app.services.role_service import RoleService
    
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )
    
    # Check if user is admin
    user_role = current_user.role.lower() if current_user.role else ''
    if user_role not in ['admin', 'vendor', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete roles"
        )
    
    role_service = RoleService(db)
    await role_service.delete_role(role_id, current_user.org_id)


@router.patch("/users/{user_id}/permissions")
async def update_user_permissions(
    user_id: UUID,
    permissions: PermissionUpdate,
    current_user: User = Depends(get_current_user)
):

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


# ==================== EMPLOYEE ATTENDANCE ====================

@router.get("/employee/attendance")
async def get_attendance_records(
    month: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
    """
    Get attendance records for the current user (employee)
    
    - **month**: Format YYYY-MM (e.g., "2025-12"). If not provided, uses current month
    """
    try:
        from app.models.attendance import Attendance
        from app.models.employee import Employee
        from datetime import datetime
        from sqlalchemy import select, and_, extract
        
        # Get employee record for current user
        employee_result = await db.execute(
            select(Employee).where(
                and_(
                    Employee.user_id == current_user.id,
                    Employee.company_id == current_user.org_id
                )
            )
        )
        employee = employee_result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found for current user"
            )
        
        # Parse month parameter or use current month
        if month:
            try:
                year, month_num = map(int, month.split('-'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid month format. Use YYYY-MM (e.g., '2025-12')"
                )
        else:
            now = datetime.now()
            year = now.year
            month_num = now.month
        
        # Query attendance records for the month
        result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.employee_id == employee.id,
                    extract('year', Attendance.date) == year,
                    extract('month', Attendance.date) == month_num
                )
            ).order_by(Attendance.date)
        )
        records = result.scalars().all()
        
        return {
            "records": [record.to_dict() for record in records]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching attendance records: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch attendance records: {str(e)}"
        )


@router.post("/employee/attendance/punch-in")
async def punch_in(
    punch_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
    """
    Record employee punch-in time
    
    - **date**: Format YYYY-MM-DD (e.g., "2025-12-06")
    - **time**: Format HH:mm:ss (e.g., "09:00:00")
    """
    try:
        from app.models.attendance import Attendance
        from app.models.employee import Employee
        from datetime import datetime, date
        from sqlalchemy import select, and_
        
        # Get employee record
        employee_result = await db.execute(
            select(Employee).where(
                and_(
                    Employee.user_id == current_user.id,
                    Employee.company_id == current_user.org_id
                )
            )
        )
        employee = employee_result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found for current user"
            )
        
        # Parse date and time
        date_str = punch_data.get('date')
        time_str = punch_data.get('time')
        
        if not date_str or not time_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both 'date' and 'time' are required"
            )
        
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            punch_in_datetime = f"{date_str} {time_str}"
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date or time format: {str(e)}"
            )
        
        # Check if attendance record exists for today
        existing_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.employee_id == employee.id,
                    Attendance.date == attendance_date
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            if existing.punch_in:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already punched in for this date"
                )
            # Update existing record
            existing.punch_in = punch_in_datetime
            await db.flush()
            await db.refresh(existing)
            return existing.to_dict()
        else:
            # Create new record
            attendance = Attendance(
                employee_id=employee.id,
                user_id=current_user.id,
                date=attendance_date,
                punch_in=punch_in_datetime,
                work_hours=0.0
            )
            db.add(attendance)
            await db.flush()
            await db.refresh(attendance)
            return attendance.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error punching in: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to punch in: {str(e)}"
        )


@router.post("/employee/attendance/punch-out")
async def punch_out(
    punch_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_request_transaction)
):
    """
    Record employee punch-out time and calculate work hours
    
    - **date**: Format YYYY-MM-DD (e.g., "2025-12-06")
    - **time**: Format HH:mm:ss (e.g., "17:00:00")
    - Maximum 8 hours per day (even if worked more)
    """
    try:
        from app.models.attendance import Attendance
        from app.models.employee import Employee
        from datetime import datetime, date
        from sqlalchemy import select, and_
        
        # Get employee record
        employee_result = await db.execute(
            select(Employee).where(
                and_(
                    Employee.user_id == current_user.id,
                    Employee.company_id == current_user.org_id
                )
            )
        )
        employee = employee_result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found for current user"
            )
        
        # Parse date and time
        date_str = punch_data.get('date')
        time_str = punch_data.get('time')
        
        if not date_str or not time_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both 'date' and 'time' are required"
            )
        
        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            punch_out_datetime = f"{date_str} {time_str}"
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date or time format: {str(e)}"
            )
        
        # Get existing attendance record
        existing_result = await db.execute(
            select(Attendance).where(
                and_(
                    Attendance.employee_id == employee.id,
                    Attendance.date == attendance_date
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if not existing or not existing.punch_in:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must punch in before punching out"
            )
        
        if existing.punch_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already punched out for this date"
            )
        
        # Update punch-out time
        existing.punch_out = punch_out_datetime
        
        # Calculate work hours (max 8 hours)
        try:
            punch_in_dt = datetime.strptime(existing.punch_in, '%Y-%m-%d %H:%M:%S')
            punch_out_dt = datetime.strptime(punch_out_datetime, '%Y-%m-%d %H:%M:%S')
            diff_seconds = (punch_out_dt - punch_in_dt).total_seconds()
            diff_hours = diff_seconds / 3600.0
            
            # Maximum 8 hours per day
            MAX_HOURS = 8.0
            work_hours = min(diff_hours, MAX_HOURS)
            
            existing.work_hours = work_hours
        except Exception as calc_error:
            logger.error(f"Error calculating work hours: {calc_error}")
            existing.work_hours = 0.0
        
        await db.flush()
        await db.refresh(existing)
        return existing.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error punching out: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to punch out: {str(e)}"
        )

