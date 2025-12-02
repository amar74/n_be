from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_request_transaction
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])


def _service(db: AsyncSession) -> DepartmentService:
    return DepartmentService(db)


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new department",
)
async def create_department(
    payload: DepartmentCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"settings": ["edit"]})),
) -> DepartmentResponse:
    """Create a new department for the organization."""
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )

    service = _service(db)
    department = await service.create_department(
        name=payload.name,
        org_id=current_user.org_id,
        code=payload.code,
        description=payload.description,
        manager_id=payload.manager_id,
        is_active=payload.is_active,
    )
    return DepartmentResponse.model_validate(department)


@router.get(
    "/",
    response_model=List[DepartmentResponse],
    summary="List all departments for the organization",
)
async def list_departments(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"settings": ["view"]})),
) -> List[DepartmentResponse]:
    """List all departments for the current user's organization."""
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )

    service = _service(db)
    departments = await service.list_departments(
        org_id=current_user.org_id,
        include_inactive=include_inactive,
    )
    return [DepartmentResponse.model_validate(dept) for dept in departments]


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Get department by ID",
)
async def get_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"settings": ["view"]})),
) -> DepartmentResponse:
    """Get a department by ID."""
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )

    service = _service(db)
    department = await service.get_department(department_id, current_user.org_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return DepartmentResponse.model_validate(department)


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Update a department",
)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"settings": ["edit"]})),
) -> DepartmentResponse:
    """Update a department."""
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )

    service = _service(db)
    department = await service.update_department(
        department_id=department_id,
        org_id=current_user.org_id,
        name=payload.name,
        code=payload.code,
        description=payload.description,
        manager_id=payload.manager_id,
        is_active=payload.is_active,
    )
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return DepartmentResponse.model_validate(department)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a department",
)
async def delete_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    _: UserPermissionResponse = Depends(get_user_permission({"settings": ["edit"]})),
):
    """Delete a department (soft delete)."""
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to an organization"
        )

    service = _service(db)
    await service.delete_department(department_id, current_user.org_id)

