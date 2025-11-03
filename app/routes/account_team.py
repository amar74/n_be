"""
Account Team Routes
Endpoints for managing employee assignments to accounts
"""
from fastapi import APIRouter, Depends, Path, HTTPException, status
from typing import Annotated
import uuid

from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.schemas.account_team import (
    AccountTeamCreateRequest,
    AccountTeamUpdateRequest,
    AccountTeamResponse,
    AccountTeamListResponse,
    AccountTeamDeleteResponse,
)
from app.services.account_team import (
    add_team_member,
    list_team_members,
    get_team_member,
    update_team_member,
    remove_team_member,
)
from app.utils.logger import logger


router = APIRouter(prefix="/accounts/{account_id}/team", tags=["account-team"])


@router.post(
    "/",
    response_model=AccountTeamResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="addAccountTeamMember"
)
async def add_account_team_member_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    payload: AccountTeamCreateRequest = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
) -> AccountTeamResponse:
    """
    Add an employee to an account's team
    
    - **account_id**: UUID of the account
    - **employee_id**: UUID of the employee to add
    - **role_in_account**: Optional role/designation for this account
    """
    try:
        return await add_team_member(account_id, payload, current_user)
    except ValueError as e:
        logger.error(f"Validation error adding team member: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding team member to account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add team member: {str(e)}"
        )


@router.get(
    "/",
    response_model=AccountTeamListResponse,
    operation_id="listAccountTeamMembers"
)
async def list_account_team_members_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
) -> AccountTeamListResponse:
    """
    Get all team members assigned to an account
    
    - **account_id**: UUID of the account
    
    Returns list of employees with their details and assignment information
    """
    try:
        return await list_team_members(account_id, current_user)
    except Exception as e:
        logger.error(f"Error listing team members for account {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list team members: {str(e)}"
        )


@router.get(
    "/{team_member_id}",
    response_model=AccountTeamResponse,
    operation_id="getAccountTeamMember"
)
async def get_account_team_member_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    team_member_id: int = Path(..., description="Team Member ID"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view"]}))
) -> AccountTeamResponse:
    """
    Get details of a specific team member assignment
    
    - **account_id**: UUID of the account
    - **team_member_id**: ID of the team member assignment
    """
    try:
        return await get_team_member(account_id, team_member_id, current_user)
    except ValueError as e:
        logger.error(f"Team member not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting team member {team_member_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get team member: {str(e)}"
        )


@router.put(
    "/{team_member_id}",
    response_model=AccountTeamResponse,
    operation_id="updateAccountTeamMember"
)
async def update_account_team_member_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    team_member_id: int = Path(..., description="Team Member ID"),
    payload: AccountTeamUpdateRequest = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit"]}))
) -> AccountTeamResponse:
    """
    Update a team member's role in the account
    
    - **account_id**: UUID of the account
    - **team_member_id**: ID of the team member assignment
    - **role_in_account**: Updated role/designation
    """
    try:
        return await update_team_member(account_id, team_member_id, payload, current_user)
    except ValueError as e:
        logger.error(f"Team member not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating team member {team_member_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update team member: {str(e)}"
        )


@router.delete(
    "/{team_member_id}",
    response_model=AccountTeamDeleteResponse,
    operation_id="removeAccountTeamMember"
)
async def remove_account_team_member_route(
    account_id: uuid.UUID = Path(..., description="Account ID"),
    team_member_id: int = Path(..., description="Team Member ID"),
    current_user: Annotated[User, Depends(get_current_user)] = ...,
    user_permission: UserPermissionResponse = Depends(get_user_permission({"accounts": ["view", "edit", "delete"]}))
) -> AccountTeamDeleteResponse:
    """
    Remove an employee from an account's team
    
    - **account_id**: UUID of the account
    - **team_member_id**: ID of the team member assignment to remove
    """
    try:
        return await remove_team_member(account_id, team_member_id, current_user)
    except ValueError as e:
        logger.error(f"Team member not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error removing team member {team_member_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove team member: {str(e)}"
        )

