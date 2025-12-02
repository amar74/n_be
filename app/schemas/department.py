from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Department name")
    code: Optional[str] = Field(None, max_length=20, description="Department code (e.g., 'ENG', 'SALES')")
    description: Optional[str] = Field(None, description="Department description")
    manager_id: Optional[UUID] = Field(None, description="Department manager employee ID")
    is_active: bool = Field(True, description="Whether the department is active")


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    manager_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class DepartmentResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    code: Optional[str]
    description: Optional[str]
    manager_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

