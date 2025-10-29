from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from uuid import UUID

from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.models.survey import SurveyDistribution, Survey
from app.db.session import get_request_transaction
from app.utils.logger import logger
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload


router = APIRouter(prefix="/employee/surveys", tags=["Employee Surveys"])


@router.get("/assigned")
async def get_assigned_surveys(
    current_user: User = Depends(get_current_user)
):
    """Get surveys assigned to the logged-in employee"""
    try:
        db = get_request_transaction()
        
        # Find employee record for current user
        from app.models.employee import Employee
        stmt = select(Employee).where(
            and_(
                Employee.user_id == current_user.id,
                Employee.company_id == current_user.org_id
            )
        )
        result = await db.execute(stmt)
        employee = result.scalar_one_or_none()
        
        if not employee:
            logger.warning(f"No employee record found for user {current_user.id}")
            return []
        
        logger.info(f"Found employee {employee.id} for user {current_user.id}")
        
        # Get survey distributions assigned to this employee
        stmt = (
            select(SurveyDistribution)
            .where(SurveyDistribution.employee_id == employee.id)
            .options(joinedload(SurveyDistribution.survey))
            .order_by(SurveyDistribution.created_at.desc())
        )
        
        result = await db.execute(stmt)
        distributions = list(result.scalars().all())
        
        logger.info(f"Found {len(distributions)} survey distributions for employee {employee.id}")
        
        # Format response
        assigned_surveys = []
        for dist in distributions:
            if dist.survey:
                assigned_surveys.append({
                    "id": str(dist.survey.id),
                    "distribution_id": str(dist.id),
                    "title": dist.survey.title,
                    "description": dist.survey.description,
                    "status": dist.survey.status.value if dist.survey.status else "unknown",
                    "is_completed": dist.is_completed,
                    "survey_link": dist.survey_link or f"/employee/survey/{dist.survey.id}",
                    "created_at": dist.created_at.isoformat() if dist.created_at else None
                })
        
        return assigned_surveys
        
    except Exception as e:
        logger.error(f"Error fetching assigned surveys: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assigned surveys: {str(e)}"
        )


@router.get("/{survey_id}")
async def get_employee_survey(
    survey_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get survey details for authenticated employee"""
    try:
        db = get_request_transaction()
        
        # Verify employee has access to this survey
        from app.models.employee import Employee
        stmt = select(Employee).where(
            and_(
                Employee.user_id == current_user.id,
                Employee.company_id == current_user.org_id
            )
        )
        result = await db.execute(stmt)
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found"
            )
        
        # Check if survey is assigned to this employee
        stmt = select(SurveyDistribution).where(
            and_(
                SurveyDistribution.survey_id == survey_id,
                SurveyDistribution.employee_id == employee.id
            )
        ).options(joinedload(SurveyDistribution.survey))
        
        result = await db.execute(stmt)
        distribution = result.scalar_one_or_none()
        
        if not distribution or not distribution.survey:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this survey"
            )
        
        survey = distribution.survey
        
        return {
            "id": str(survey.id),
            "title": survey.title,
            "description": survey.description,
            "questions": survey.questions or [],
            "is_completed": distribution.is_completed,
            "distribution_id": str(distribution.id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee survey: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch survey: {str(e)}"
        )


@router.post("/{survey_id}/submit")
async def submit_employee_survey(
    survey_id: UUID,
    response_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Submit survey response from authenticated employee"""
    try:
        db = get_request_transaction()
        
        # Get employee
        from app.models.employee import Employee
        stmt = select(Employee).where(
            and_(
                Employee.user_id == current_user.id,
                Employee.company_id == current_user.org_id
            )
        )
        result = await db.execute(stmt)
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found"
            )
        
        # Verify distribution exists
        stmt = select(SurveyDistribution).where(
            and_(
                SurveyDistribution.survey_id == survey_id,
                SurveyDistribution.employee_id == employee.id
            )
        )
        result = await db.execute(stmt)
        distribution = result.scalar_one_or_none()
        
        if not distribution:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Survey not assigned to you"
            )
        
        if distribution.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already completed this survey"
            )
        
        # Create response
        from app.models.survey import SurveyResponse
        import secrets
        
        response_code = f"RESP_{secrets.token_urlsafe(8).upper()}"
        
        survey_response = SurveyResponse(
            response_code=response_code,
            survey_id=survey_id,
            distribution_id=distribution.id,
            employee_id=employee.id,
            account_id=None,
            contact_id=None,
            response_data=response_data.get("responses", {}),
            finished=True,
            meta={
                "employee_name": employee.name,
                "employee_email": employee.email,
                "employee_number": employee.employee_number,
                "submission_type": "authenticated_employee"
            }
        )
        
        db.add(survey_response)
        
        # Mark distribution as completed
        distribution.is_completed = True
        from datetime import datetime
        distribution.completed_at = datetime.utcnow()
        
        await db.flush()
        await db.refresh(survey_response)
        
        logger.info(f"Employee {employee.id} submitted survey {survey_id}")
        
        return {
            "success": True,
            "message": "Thank you for completing the survey!",
            "response_code": response_code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting employee survey: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit survey: {str(e)}"
        )

