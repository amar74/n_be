from fastapi import APIRouter, Request, Depends
import jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.services.supabase import verify_user_token
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.schemas.auth import (
    OnSignUpRequest,
    OnSignupSuccessResponse,
    OnSignupErrorResponse,
    AuthUserResponse,
    VerifySupabaseTokenResponse,
    CurrentUserResponse,
)
from app.environment import environment
from app.dependencies.user_auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/onsignup",
    responses={
        200: {"model": OnSignupSuccessResponse},
        400: {"model": OnSignupErrorResponse},
    },
)
async def onsignup(request: OnSignUpRequest):
    if not request.email:
        return OnSignupErrorResponse(message="Signup failed", error="Email is required")

    user = await User.get_by_email(request.email)
    if not user:
        user = await User.create(request.email)
        return OnSignupSuccessResponse(
            message="User created",
            user=AuthUserResponse.model_validate(user)
        )
    
    return OnSignupSuccessResponse(
        message="User exists",
        user=AuthUserResponse.model_validate(user)
    )

@router.get("/verify_supabase_token")
async def verify_supabase_token(request: Request):
    auth_header = request.headers.get("Authorization")
    sb_header = request.headers.get("sb-mzdvwfoepfagypseyvfh-auth-token")

    if not (auth_header or sb_header):
        raise MegapolisHTTPException(status_code=401, details="No token")

    token = sb_header if sb_header else auth_header.replace("Bearer ", "")

    user_data = verify_user_token(token)
    
    if user_data:
        email = user_data.get("email")
    else:
        decoded = jwt.decode(token, options={"verify_signature": False})
        email = decoded.get("email") or decoded.get("user_metadata", {}).get("email")
        if not email:
            raise MegapolisHTTPException(status_code=401, details="Invalid token")

    user = await User.get_by_email(email) or await User.create(email)

    exp = datetime.utcnow() + timedelta(days=30)
    new_token = jwt.encode(
        {"sub": str(user.id), "email": email, "exp": exp},
        environment.JWT_SECRET_KEY,
        algorithm="HS256"
    )

    return VerifySupabaseTokenResponse(
        message="Verified",
        token=new_token,
        user=AuthUserResponse.model_validate(user),
        expire_at=exp.isoformat()
    )

@router.get("/me", response_model=CurrentUserResponse, operation_id="getCurrentUser")
async def get_current_user(current_user: User = Depends(get_current_user)):
    return CurrentUserResponse(user=current_user)
