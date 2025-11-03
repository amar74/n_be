"""
Account Team Schemas
Schemas for managing employee assignments to accounts
"""
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
import uuid


class AccountTeamCreateRequest(BaseModel):
    """Request to add an employee to an account team"""
    employee_id: uuid.UUID
    role_in_account: Optional[str] = None

    @field_validator("role_in_account")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Role cannot be empty if provided")
        return v.strip() if v is not None else v


class AccountTeamUpdateRequest(BaseModel):
    """Request to update team member's role in account"""
    role_in_account: Optional[str] = None

    @field_validator("role_in_account")
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Role cannot be empty if provided")
        return v.strip() if v is not None else v


class EmployeeBasicInfo(BaseModel):
    """Basic employee information for team display"""
    id: uuid.UUID
    employee_number: str
    name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    bill_rate: Optional[float] = None
    status: str
    experience: Optional[str] = None
    skills: Optional[List[str]] = None

    model_config = {"from_attributes": True}


class AccountTeamResponse(BaseModel):
    """Response for account team member with employee details"""
    id: int
    account_id: uuid.UUID
    employee_id: uuid.UUID
    role_in_account: Optional[str] = None
    assigned_at: datetime
    assigned_by: Optional[uuid.UUID] = None
    # Embedded employee details
    employee: Optional[EmployeeBasicInfo] = None

    model_config = {"from_attributes": True}


class AccountTeamListResponse(BaseModel):
    """List of team members for an account"""
    team_members: List[AccountTeamResponse]
    total_count: int
    account_id: uuid.UUID

    model_config = {"from_attributes": True}


class AccountTeamDeleteResponse(BaseModel):
    """Response after removing a team member"""
    id: int
    message: str
    employee_id: uuid.UUID
    account_id: uuid.UUID

    model_config = {"from_attributes": True}

