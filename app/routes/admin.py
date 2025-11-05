from fastapi import APIRouter, Depends, Query
from app.dependencies.permissions import require_role, require_super_admin
from app.schemas.admin import (
    AdminCreateUserRequest,
    AdminCreateUserResponse,
    AdminUserListResponse,
    AdminUser,
)
from app.schemas.auth import AuthUserResponse
from app.services.admin import count_users, admin_create_user, list_users
from app.schemas.user import Roles
from app.services.email import send_vendor_creation_email
from app.environment import environment
from app.utils.logger import logger

router = APIRouter(prefix="/admin", tags=[Roles.ADMIN])

@router.get("/user_list", response_model=AdminUserListResponse, operation_id="userList")
async def admin_user_list(
    _: str = Depends(require_super_admin()),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    
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
    
    user = await admin_create_user(
        email=payload.email,
        password=payload.password,
        role=payload.role or Roles.VENDOR,
        contact_number=payload.contact_number,
        name=payload.name
    )
    
    # Send email to vendor if role is VENDOR
    if user.role == Roles.VENDOR:
        login_url = getattr(
            environment,
            'VENDOR_LOGIN_URL',
            'http://localhost:5173/auth/login'
        )
        
        # Get organization name if provided in payload
        organization_name = getattr(payload, 'organization_name', None)
        
        email_sent = send_vendor_creation_email(
            vendor_email=user.email,
            vendor_name=user.name or user.email.split('@')[0],
            password=payload.password,  # Send plain password from request
            login_url=login_url,
            organization_name=organization_name
        )
        
        if email_sent:
            logger.info(f"✅ Vendor creation email sent successfully to {user.email}")
        else:
            logger.warning(f"⚠️ Failed to send vendor creation email to {user.email}")
    
    return AdminCreateUserResponse(
        message=f"User created successfully with role '{user.role}'",
        user=AuthUserResponse.model_validate(user),
    )

