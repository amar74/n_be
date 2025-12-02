from __future__ import annotations

import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.organization import Organization
from app.utils.logger import get_logger

logger = get_logger("role_service")


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(
        self,
        name: str,
        org_id: uuid.UUID,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        color: Optional[str] = None,
    ) -> Role:
        """Create a new custom role."""
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

            # Check if role name already exists for this org (case-insensitive)
            existing_result = await self.db.execute(
                select(Role).where(
                    and_(
                        Role.org_id == org_id,
                        func.lower(Role.name) == func.lower(name)
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role '{name}' already exists in this organization (case-insensitive match with '{existing.name}')"
                )

            # Create role
            role = Role(
                org_id=org_id,
                name=name,
                description=description,
                permissions=permissions or [],
                color=color,
                is_system=False,
            )

            self.db.add(role)
            await self.db.flush()
            await self.db.refresh(role)

            logger.info(f"Created role: {name} (ID: {role.id}) for org {org_id}")
            return role

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create role: {str(e)}"
            )

    async def list_roles(
        self,
        org_id: uuid.UUID,
        include_system: bool = False,
    ) -> List[Role]:
        """List all roles for an organization."""
        try:
            filters = [Role.org_id == org_id]
            if not include_system:
                filters.append(Role.is_system == False)

            result = await self.db.execute(
                select(Role)
                .where(*filters)
                .order_by(Role.name)
            )
            roles = result.scalars().all()
            return list(roles)

        except Exception as e:
            logger.error(f"Error listing roles: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list roles: {str(e)}"
            )

    async def get_role(
        self,
        role_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> Optional[Role]:
        """Get a role by ID."""
        try:
            result = await self.db.execute(
                select(Role).where(
                    and_(
                        Role.id == role_id,
                        Role.org_id == org_id
                    )
                )
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get role: {str(e)}"
            )

    async def update_role(
        self,
        role_id: uuid.UUID,
        org_id: uuid.UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        color: Optional[str] = None,
    ) -> Optional[Role]:
        """Update a role (only custom roles can be updated)."""
        try:
            role = await self.get_role(role_id, org_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )

            if role.is_system:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="System roles cannot be modified"
                )

            # Check name uniqueness if name is being changed
            if name and name != role.name:
                existing_result = await self.db.execute(
                    select(Role).where(
                        and_(
                            Role.org_id == org_id,
                            Role.name == name,
                            Role.id != role_id
                        )
                    )
                )
                existing = existing_result.scalar_one_or_none()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Role '{name}' already exists in this organization"
                    )

            # Update fields
            if name is not None:
                role.name = name
            if description is not None:
                role.description = description
            if permissions is not None:
                role.permissions = permissions
            if color is not None:
                role.color = color

            role.updated_at = datetime.utcnow()

            await self.db.flush()
            await self.db.refresh(role)

            logger.info(f"Updated role: {role_id}")
            return role

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update role: {str(e)}"
            )

    async def delete_role(
        self,
        role_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> bool:
        """Delete a role (only custom roles can be deleted)."""
        try:
            role = await self.get_role(role_id, org_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found"
                )

            if role.is_system:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="System roles cannot be deleted"
                )

            # Check if role is assigned to any users
            from app.models.user import User
            users_result = await self.db.execute(
                select(func.count(User.id)).where(
                    and_(
                        User.org_id == org_id,
                        User.role == role.name
                    )
                )
            )
            user_count = users_result.scalar() or 0

            if user_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete role: {user_count} user(s) are assigned to this role"
                )

            await self.db.delete(role)
            await self.db.flush()

            logger.info(f"Deleted role: {role_id}")
            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete role: {str(e)}"
            )

