from fastapi import Depends
from app.dependencies.user_auth import get_current_user
from app.environment import Constants
from app.utils.error import MegapolisHTTPException
from app.models.user import User
from app.schemas.auth import AuthUserResponse


def require_role(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise MegapolisHTTPException(
                status_code=403,
                details="You do not have permission to perform this action",
            )
        return current_user

    return role_checker


def require_super_admin():
    """Dependency ensuring the requester is a super admin.

    Logic:
    - Loads the full `User` from DB using the ID from `current_user` (AuthUserResponse)
    - Allows if user's role is 'super_admin'
    - Else allows if user's email is in Constants.SUPER_ADMIN_EMAILS (if configured)
    - Otherwise, raises 403
    """

    async def super_admin_checker(current: AuthUserResponse = Depends(get_current_user)) -> AuthUserResponse:
        # Fetch full user to access email and latest role
        db_user = await User.get_by_id(int(current.id))
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