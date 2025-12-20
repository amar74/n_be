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
        user_role_lower = current_user.role.lower() if current_user.role else ''
        
        # If 'admin' is allowed, also allow 'vendor' role (main owner has admin privileges)
        effective_allowed_roles = allowed_roles.copy()
        if 'admin' in [r.lower() for r in allowed_roles]:
            effective_allowed_roles.append('vendor')
        
        # Normalize roles for comparison
        normalized_allowed = [r.lower() for r in effective_allowed_roles]
        
        if user_role_lower not in normalized_allowed:
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

    async def super_admin_checker(current_user: AuthUserResponse = Depends(get_current_user)) -> User:
        allowed_emails = Constants.SUPER_ADMIN_EMAILS
        if current_user.email not in allowed_emails:
            raise MegapolisHTTPException(
                status_code=403,
                details="You do not have permission to perform this action",
            )
        user = await User.get_by_id(current_user.id)
        if not user:
            raise MegapolisHTTPException(status_code=404, details="User not found")
        return user

    return super_admin_checker

def _get_rbac_role(user: User, employee_record=None) -> str:
    user_role = user.role.lower() if user.role else ''
    
    if user_role in ['admin', 'vendor', 'super_admin', 'platform_admin', 'org_admin']:
        return 'org_admin'
    
    if user_role in ['manager', 'contributor', 'viewer']:
        return user_role
    
    if employee_record:
        job_title = (employee_record.job_title or '').lower()
        department = (employee_record.department or '').lower()
        role = (employee_record.role or '').lower()
        
        if 'manager' in job_title or 'lead' in job_title or 'director' in job_title:
            return 'manager'
        
        if department == 'hr' or 'hr' in job_title:
            return 'contributor'
        
        if department == 'finance' or 'finance' in job_title or 'accountant' in job_title:
            return 'manager' if 'manager' in job_title else 'contributor'
        
        if user_role == 'employee':
            if 'analyst' in job_title or 'viewer' in job_title or 'read-only' in job_title:
                return 'viewer'
            return 'contributor'
        
        if role == 'viewer':
            return 'viewer'
        elif role == 'contributor':
            return 'contributor'
        elif role == 'manager':
            return 'manager'
    
    return 'viewer'

def _get_rbac_permissions(rbac_role: str) -> Dict[str, List[str]]:
    if rbac_role == 'org_admin':
        return {
            'accounts': [Permission.VIEW, Permission.EDIT],
            'opportunities': [Permission.VIEW, Permission.EDIT],
            'proposals': [Permission.VIEW, Permission.EDIT],
            'projects': [Permission.VIEW, Permission.EDIT],
            'resources': [Permission.VIEW, Permission.EDIT],
        }
    elif rbac_role == 'manager':
        return {
            'accounts': [Permission.VIEW, Permission.EDIT],
            'opportunities': [Permission.VIEW, Permission.EDIT],
            'proposals': [Permission.VIEW, Permission.EDIT],
            'projects': [Permission.VIEW, Permission.EDIT],
            'resources': [Permission.VIEW, Permission.EDIT],
        }
    elif rbac_role == 'contributor':
        return {
            'accounts': [Permission.VIEW, Permission.EDIT],
            'opportunities': [Permission.VIEW, Permission.EDIT],
            'proposals': [Permission.VIEW, Permission.EDIT],
            'projects': [Permission.VIEW, Permission.EDIT],
            'resources': [Permission.VIEW, Permission.EDIT],
        }
    elif rbac_role == 'viewer':
        return {
            'accounts': [Permission.VIEW],
            'opportunities': [Permission.VIEW],
            'proposals': [Permission.VIEW],
            'projects': [Permission.VIEW],
            'resources': [Permission.VIEW],
        }
    else:
        return {}

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
            rbac_role = _get_rbac_role(current_user, None)
            rbac_perms = _get_rbac_permissions(rbac_role)
            
            for resource, required_actions in required_permissions.items():
                if not required_actions:
                    continue
                
                rbac_resource_perms = rbac_perms.get(resource, [])
                missing_actions = [action for action in required_actions if action not in rbac_resource_perms]
                
                if missing_actions:
                    raise MegapolisHTTPException(
                        status_code=403,
                        details=f"Insufficient permissions for {resource}. Required: {required_actions}, Missing: {missing_actions}. Your RBAC role ({rbac_role}) provides: {rbac_resource_perms}"
                    )
            
            return UserPermissionResponse(
                userid=current_user.id,
                accounts=rbac_perms.get('accounts', []),
                opportunities=rbac_perms.get('opportunities', []),
                proposals=rbac_perms.get('proposals', [])
            )
        
        for resource, required_actions in required_permissions.items():
            if not required_actions:
                continue
            
            if not hasattr(user_permission, resource):
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