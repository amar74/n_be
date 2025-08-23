from fastapi import Depends, HTTPException, status
from app.constant.get_current_user import current_user
from app.utils.error import MegapolisHTTPException
from app.models.user import User


def require_role(allowed_roles: list[str]):
    def role_checker(current_user: User = Depends(current_user)):
        if current_user.role not in allowed_roles:
            raise MegapolisHTTPException(
                status_code=403,
                details="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
