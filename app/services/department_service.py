from __future__ import annotations

import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.organization import Organization
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("department_service")


class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_department(
        self,
        name: str,
        org_id: uuid.UUID,
        code: Optional[str] = None,
        description: Optional[str] = None,
        manager_id: Optional[uuid.UUID] = None,
        is_active: bool = True,
    ) -> Department:
        """Create a new department."""
        try:
            # Validate organization exists
            org_result = await self.db.execute(
                select(Organization).where(Organization.id == org_id)
            )
            org = org_result.scalar_one_or_none()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Organization not found"
                )

            # Check if department name already exists for this org
            existing_result = await self.db.execute(
                select(Department).where(
                    and_(
                        Department.org_id == org_id,
                        Department.name == name,
                        Department.is_active == True
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Department '{name}' already exists in this organization"
                )

            # Create department
            department = Department(
                org_id=org_id,
                name=name,
                code=code,
                description=description,
                manager_id=manager_id,
                is_active=is_active,
            )

            self.db.add(department)
            await self.db.flush()
            await self.db.refresh(department)

            logger.info(f"Created department: {name} for org {org_id}")
            return department

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating department: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create department: {str(e)}"
            )

    async def list_departments(
        self,
        org_id: uuid.UUID,
        include_inactive: bool = False,
    ) -> List[Department]:
        """List all departments for an organization."""
        try:
            filters = [Department.org_id == org_id]
            if not include_inactive:
                filters.append(Department.is_active == True)

            result = await self.db.execute(
                select(Department)
                .where(*filters)
                .order_by(Department.name)
            )
            departments = result.scalars().all()
            return list(departments)

        except Exception as e:
            logger.error(f"Error listing departments: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list departments: {str(e)}"
            )

    async def get_department(
        self,
        department_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> Optional[Department]:
        """Get a department by ID."""
        try:
            result = await self.db.execute(
                select(Department).where(
                    and_(
                        Department.id == department_id,
                        Department.org_id == org_id
                    )
                )
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting department: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get department: {str(e)}"
            )

    async def update_department(
        self,
        department_id: uuid.UUID,
        org_id: uuid.UUID,
        name: Optional[str] = None,
        code: Optional[str] = None,
        description: Optional[str] = None,
        manager_id: Optional[uuid.UUID] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Department]:
        """Update a department."""
        try:
            department = await self.get_department(department_id, org_id)
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found"
                )

            # Check name uniqueness if name is being changed
            if name and name != department.name:
                existing_result = await self.db.execute(
                    select(Department).where(
                        and_(
                            Department.org_id == org_id,
                            Department.name == name,
                            Department.id != department_id,
                            Department.is_active == True
                        )
                    )
                )
                existing = existing_result.scalar_one_or_none()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Department '{name}' already exists in this organization"
                    )

            # Update fields
            if name is not None:
                department.name = name
            if code is not None:
                department.code = code
            if description is not None:
                department.description = description
            if manager_id is not None:
                department.manager_id = manager_id
            if is_active is not None:
                department.is_active = is_active

            department.updated_at = datetime.utcnow()

            await self.db.flush()
            await self.db.refresh(department)

            logger.info(f"Updated department: {department_id}")
            return department

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating department: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update department: {str(e)}"
            )

    async def delete_department(
        self,
        department_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> bool:
        """Delete a department (soft delete by setting is_active=False)."""
        try:
            department = await self.get_department(department_id, org_id)
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found"
                )

            # Check if department has employees assigned
            from app.models.employee import Employee
            employees_result = await self.db.execute(
                select(func.count(Employee.id)).where(
                    and_(
                        Employee.company_id == org_id,
                        Employee.department == department.name
                    )
                )
            )
            employee_count = employees_result.scalar() or 0

            if employee_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete department: {employee_count} employee(s) are assigned to this department"
                )

            # Soft delete
            department.is_active = False
            department.updated_at = datetime.utcnow()

            await self.db.flush()

            logger.info(f"Deleted department: {department_id}")
            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting department: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete department: {str(e)}"
            )

