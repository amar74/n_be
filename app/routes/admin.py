from fastapi import APIRouter, Depends, Query
from app.rbac.permissions import require_role, require_super_admin
from app.utils.logger import logger
from app.schemas.admin import (
    AdminCreateUserRequest,
    AdminCreateUserResponse,
    AdminUserListResponse,
    AdminUser,
)
from app.schemas.auth import AuthUserResponse
from app.services.admin import count_users, admin_create_user, list_users


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/user_list", response_model=AdminUserListResponse, operation_id="userList")
async def admin_user_list(
    _: str = Depends(require_super_admin()),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    """Return total number of users and a paginated list of users."""
    total, users = await list_users(skip=skip, limit=limit)
    return AdminUserListResponse(
        total_users=total,
        users=[AdminUser.model_validate(u) for u in users],
    )


@router.post(
    "/create_new_user",
    response_model=AdminCreateUserResponse,
    status_code=201,
    operation_id="createNewUser",
)
async def admin_create_new_user(
    payload: AdminCreateUserRequest,
    _: str = Depends(require_super_admin())
):
    """Create a new user using Supabase SDK and mirror in local DB."""
    user = await admin_create_user(payload.email, payload.password)
    return AdminCreateUserResponse(
        message="User created successfully",
        user=AuthUserResponse.model_validate(user),
    )


