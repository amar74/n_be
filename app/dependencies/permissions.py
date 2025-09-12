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


def require_role(allowed_roles: list[str]):
    async def role_checker(current_user: AuthUserResponse = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise MegapolisHTTPException(
                status_code=403,
                details="You do not have permission to perform this action",
            )
        # Convert AuthUserResponse to User for full access
        user = await User.get_by_id(current_user.id)
        if not user:
            raise MegapolisHTTPException(status_code=404, details="User not found")
        return user

    return role_checker


def require_super_admin():
    """Dependency ensuring the requester is a super admin.

    Logic:
    - Loads the full `User` from DB using the ID from `current_user` (AuthUserResponse)
    - Allows if user's role is 'super_admin'
    - Else allows if user's email is in Constants.SUPER_ADMIN_EMAILS (if configured)
    - Otherwise, raises 403
    """

    async def super_admin_checker(current: User = Depends(get_current_user)) -> User:
        # Fetch full user to access email and latest role
        db_user = await User.get_by_id(current.id)
        if not db_user:
            raise MegapolisHTTPException(status_code=404, details="User not found")

        # # Check role first
        # if getattr(db_user, "role", None) == "super_admin":
        #     return current

        # Fallback to configured emails list
        allowed_emails = Constants.SUPER_ADMIN_EMAILS
        if db_user.email not in allowed_emails:
            raise MegapolisHTTPException(
                status_code=403,
                details="You do not have permission to perform this action",
            )
        return db_user


    return super_admin_checker


def get_user_permission(required_permissions: Dict[str, List[str]]):
    """
    Dependency factory that creates a permission checker for specific resource permissions.
    
    Args:
        required_permissions: Dictionary mapping resource names to required permission actions
        Example: {"opportunities": ["view", "edit"], "accounts": ["view"]}
    
    Returns:
        Dependency function that validates user permissions and returns UserPermissionResponse
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> UserPermissionResponse:
        """
        Check if the current user has the required permissions for the specified resources.
        
        Args:
            current_user: The authenticated user from get_current_user dependency
            
        Returns:
            UserPermissionResponse: The user's permission data
            
        Raises:
            MegapolisHTTPException: 403 if user doesn't have required permissions
        """
        # Get user permissions from database
        user_permission = await UserPermission.get_by_userid(current_user.id)
        organization = await Organization.get_by_id(current_user.org_id)
        if organization.owner_id == current_user.id:
            return UserPermissionResponse(
                userid=current_user.id,
                accounts=[Permission.VIEW, Permission.EDIT],
                opportunities=[Permission.VIEW, Permission.EDIT],
                proposals=[Permission.VIEW, Permission.EDIT]
            )
        
        # If no permissions found, user has no permissions (empty lists)
        if not user_permission:
            # Check if any permissions are required
            for resource, required_actions in required_permissions.items():
                if required_actions:  # If any actions are required
                    raise MegapolisHTTPException(
                        status_code=403,
                        details=f"Insufficient permissions for {resource}. Required: {required_actions}"
                    )
            # Return empty permissions if no requirements
            return UserPermissionResponse(
                userid=current_user.id,
                accounts=[],
                opportunities=[],
                proposals=[]
            )
        
        # Check each required resource and its actions
        for resource, required_actions in required_permissions.items():
            if not required_actions:  # Skip if no actions required
                continue
                
            # Get user's permissions for this resource
            user_resource_permissions = getattr(user_permission, resource, [])
            
            # Check if user has all required actions for this resource
            missing_actions = [action for action in required_actions if action not in user_resource_permissions]
            
            if missing_actions:
                raise MegapolisHTTPException(
                    status_code=403,
                    details=f"Insufficient permissions for {resource}. Required: {required_actions}, Missing: {missing_actions}"
                )
        
        # Return the user's permission data
        return UserPermissionResponse.model_validate(user_permission)
    
    return permission_checker