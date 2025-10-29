from fastapi import Depends
from app.dependencies.user_auth import get_current_user
from app.environment import Constants
from app.models.organization import Organization
from app.utils.error import MegapolisHTTPException
from app.models.user import User
from app.models.user_permission import UserPermission
from app.schemas.auth import AuthUserResponse
from app.schemas.user_permission import Permission, UserPermissionResponse
from typing import Dict, List

def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: AuthUserResponse = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise MegapolisHTTPException(
                status_code=403,
                details="You do not have permission to perform this action",
            )
        user = await User.get_by_id(current_user.id)
        if not user:
            raise MegapolisHTTPException(status_code=404, details="User not found")
        return user

    return role_checker

def require_super_admin():

    async def super_admin_checker(current_user: AuthUserResponse = Depends(get_current_user)) -> str:
        allowed_emails = Constants.SUPER_ADMIN_EMAILS
        if current_user.email not in allowed_emails:
            raise MegapolisHTTPException(
                status_code=403,
                details="You do not have permission to perform this action",
            )
        return current_user.id

    return super_admin_checker

def get_user_permission(required_permissions: Dict[str, List[str]]):

    async def permission_checker(current_user: User = Depends(get_current_user)) -> UserPermissionResponse:

        user_permission = await UserPermission.get_by_userid(current_user.id)
        organization = await Organization.get_by_id(current_user.org_id)
        
        if not organization:
            raise MegapolisHTTPException(
                status_code=404,
                details="Organization not found"
            )
        
        if organization.owner_id == current_user.id:
            return UserPermissionResponse(
                userid=current_user.id,
                accounts=[Permission.VIEW, Permission.EDIT],
                opportunities=[Permission.VIEW, Permission.EDIT],
                proposals=[Permission.VIEW, Permission.EDIT]
            )
        
        if not user_permission:
            for resource, required_actions in required_permissions.items():
                if required_actions:  # If any actions are required
                    raise MegapolisHTTPException(
                        status_code=403,
                        details=f"Insufficient permissions for {resource}. Required: {required_actions}"
                    )
            return UserPermissionResponse(
                userid=current_user.id,
                accounts=[],
                opportunities=[],
                proposals=[]
            )
        
        for resource, required_actions in required_permissions.items():
            if not required_actions:  # Skip if no actions required
                continue
                
            user_resource_permissions = getattr(user_permission, resource, [])
            
            missing_actions = [action for action in required_actions if action not in user_resource_permissions]
            
            if missing_actions:
                raise MegapolisHTTPException(
                    status_code=403,
                    details=f"Insufficient permissions for {resource}. Required: {required_actions}, Missing: {missing_actions}"
                )
        
        return UserPermissionResponse.model_validate(user_permission)
    
    return permission_checker