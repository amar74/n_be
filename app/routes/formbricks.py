from fastapi import APIRouter, Depends

from app.dependencies.user_auth import get_current_user
from app.models.user import User
from app.schemas.formbricks import FormbricksLoginTokenResponse
from app.services.formbricks import get_formbricks_login_token

router = APIRouter(prefix="/formbricks", tags=["formbricks"])



@router.get("/login-token", operation_id="getFormbricksLoginToken")
async def get_formbricks_login_token_handler(
    current_user: User = Depends(get_current_user),
) -> FormbricksLoginTokenResponse:
    return await get_formbricks_login_token(current_user)
