"""
Account Team Service
Business logic for managing employee assignments to accounts
"""
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.account_team import AccountTeam
from app.models.account import Account
from app.models.employee import Employee
from app.models.user import User
from app.schemas.account_team import (
    AccountTeamCreateRequest,
    AccountTeamUpdateRequest,
    AccountTeamResponse,
    AccountTeamListResponse,
    AccountTeamDeleteResponse,
    EmployeeBasicInfo,
)
from app.db.session import get_session
from app.utils.logger import logger


async def add_team_member(
    account_id: uuid.UUID,
    payload: AccountTeamCreateRequest,
    current_user: User
) -> AccountTeamResponse:
    """
    Add an employee to an account's team
    
    Args:
        account_id: UUID of the account
        payload: Team member creation data
        current_user: Currently authenticated user
        
    Returns:
        AccountTeamResponse with employee details
        
    Raises:
        ValueError: If account or employee not found, or if already assigned
    """
    async with get_session() as session:
        # Verify account exists and belongs to user's organization
        account_query = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id
        )
        account_result = await session.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"Account {account_id} not found or access denied")
        
        # Verify employee exists and belongs to same organization
        employee_query = select(Employee).where(
            Employee.id == payload.employee_id,
            Employee.company_id == current_user.org_id
        )
        employee_result = await session.execute(employee_query)
        employee = employee_result.scalar_one_or_none()
        
        if not employee:
            raise ValueError(f"Employee {payload.employee_id} not found or access denied")
        
        # Check if already assigned
        existing_query = select(AccountTeam).where(
            AccountTeam.account_id == account_id,
            AccountTeam.employee_id == payload.employee_id,
            AccountTeam.removed_at.is_(None)
        )
        existing_result = await session.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Employee {employee.name} is already assigned to this account")
        
        # Create team member assignment
        team_member = AccountTeam(
            account_id=account_id,
            employee_id=payload.employee_id,
            role_in_account=payload.role_in_account,
            assigned_by=current_user.id
        )
        
        session.add(team_member)
        await session.commit()
        await session.refresh(team_member)
        
        # Fetch with employee details
        result_query = select(AccountTeam).options(
            selectinload(AccountTeam.employee)
        ).where(AccountTeam.id == team_member.id)
        result = await session.execute(result_query)
        team_member_with_employee = result.scalar_one()
        
        logger.info(f"Added employee {employee.name} to account {account.client_name}")
        
        # Build response with employee details
        response_data = team_member_with_employee.to_dict()
        if team_member_with_employee.employee:
            response_data["employee"] = EmployeeBasicInfo.model_validate(
                team_member_with_employee.employee.to_dict()
            )
        
        return AccountTeamResponse.model_validate(response_data)


async def list_team_members(
    account_id: uuid.UUID,
    current_user: User
) -> AccountTeamListResponse:
    """
    Get all team members for an account
    
    Args:
        account_id: UUID of the account
        current_user: Currently authenticated user
        
    Returns:
        AccountTeamListResponse with all team members and their details
    """
    async with get_session() as session:
        # Verify account access
        account_query = select(Account).where(
            Account.account_id == account_id,
            Account.org_id == current_user.org_id
        )
        account_result = await session.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"Account {account_id} not found or access denied")
        
        # Get all active team members with employee details
        query = select(AccountTeam).options(
            selectinload(AccountTeam.employee)
        ).where(
            AccountTeam.account_id == account_id,
            AccountTeam.removed_at.is_(None)
        ).order_by(AccountTeam.assigned_at.desc())
        
        result = await session.execute(query)
        team_members = result.scalars().all()
        
        # Build response with employee details
        team_member_responses = []
        for tm in team_members:
            tm_data = tm.to_dict()
            if tm.employee:
                tm_data["employee"] = EmployeeBasicInfo.model_validate(tm.employee.to_dict())
            team_member_responses.append(AccountTeamResponse.model_validate(tm_data))
        
        return AccountTeamListResponse(
            team_members=team_member_responses,
            total_count=len(team_member_responses),
            account_id=account_id
        )


async def get_team_member(
    account_id: uuid.UUID,
    team_member_id: int,
    current_user: User
) -> AccountTeamResponse:
    """
    Get a specific team member assignment
    
    Args:
        account_id: UUID of the account
        team_member_id: ID of the team member assignment
        current_user: Currently authenticated user
        
    Returns:
        AccountTeamResponse with employee details
        
    Raises:
        ValueError: If team member not found
    """
    async with get_session() as session:
        query = select(AccountTeam).options(
            selectinload(AccountTeam.employee),
            selectinload(AccountTeam.account)
        ).where(
            AccountTeam.id == team_member_id,
            AccountTeam.account_id == account_id
        )
        
        result = await session.execute(query)
        team_member = result.scalar_one_or_none()
        
        if not team_member:
            raise ValueError(f"Team member {team_member_id} not found")
        
        # Verify organization access
        if team_member.account.org_id != current_user.org_id:
            raise ValueError("Access denied")
        
        # Build response with employee details
        tm_data = team_member.to_dict()
        if team_member.employee:
            tm_data["employee"] = EmployeeBasicInfo.model_validate(team_member.employee.to_dict())
        
        return AccountTeamResponse.model_validate(tm_data)


async def update_team_member(
    account_id: uuid.UUID,
    team_member_id: int,
    payload: AccountTeamUpdateRequest,
    current_user: User
) -> AccountTeamResponse:
    """
    Update a team member's role in the account
    
    Args:
        account_id: UUID of the account
        team_member_id: ID of the team member assignment
        payload: Update data
        current_user: Currently authenticated user
        
    Returns:
        Updated AccountTeamResponse
        
    Raises:
        ValueError: If team member not found
    """
    async with get_session() as session:
        query = select(AccountTeam).options(
            selectinload(AccountTeam.employee),
            selectinload(AccountTeam.account)
        ).where(
            AccountTeam.id == team_member_id,
            AccountTeam.account_id == account_id
        )
        
        result = await session.execute(query)
        team_member = result.scalar_one_or_none()
        
        if not team_member:
            raise ValueError(f"Team member {team_member_id} not found")
        
        # Verify organization access
        if team_member.account.org_id != current_user.org_id:
            raise ValueError("Access denied")
        
        # Update fields
        if payload.role_in_account is not None:
            team_member.role_in_account = payload.role_in_account
        
        await session.commit()
        await session.refresh(team_member)
        
        logger.info(f"Updated team member {team_member_id} for account {account_id}")
        
        # Build response with employee details
        tm_data = team_member.to_dict()
        if team_member.employee:
            tm_data["employee"] = EmployeeBasicInfo.model_validate(team_member.employee.to_dict())
        
        return AccountTeamResponse.model_validate(tm_data)


async def remove_team_member(
    account_id: uuid.UUID,
    team_member_id: int,
    current_user: User
) -> AccountTeamDeleteResponse:
    """
    Remove an employee from an account's team
    
    Args:
        account_id: UUID of the account
        team_member_id: ID of the team member assignment
        current_user: Currently authenticated user
        
    Returns:
        AccountTeamDeleteResponse
        
    Raises:
        ValueError: If team member not found
    """
    async with get_session() as session:
        query = select(AccountTeam).options(
            selectinload(AccountTeam.account)
        ).where(
            AccountTeam.id == team_member_id,
            AccountTeam.account_id == account_id
        )
        
        result = await session.execute(query)
        team_member = result.scalar_one_or_none()
        
        if not team_member:
            raise ValueError(f"Team member {team_member_id} not found")
        
        # Verify organization access
        if team_member.account.org_id != current_user.org_id:
            raise ValueError("Access denied")
        
        employee_id = team_member.employee_id
        
        # Delete the assignment
        await session.delete(team_member)
        await session.commit()
        
        logger.info(f"Removed team member {team_member_id} from account {account_id}")
        
        return AccountTeamDeleteResponse(
            id=team_member_id,
            message="Team member removed successfully",
            employee_id=employee_id,
            account_id=account_id
        )

