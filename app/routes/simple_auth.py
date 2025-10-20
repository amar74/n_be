from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta, datetime
from app.services.local_auth import authenticate_user, create_access_token, get_user_by_email
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict
    expire_at: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    created_at: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Simple login endpoint."""
    user = await authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        expire_at=(datetime.utcnow() + access_token_expires).isoformat()
    )

@router.post("/super-admin/login", response_model=LoginResponse)
async def super_admin_login(request: LoginRequest):
    """Super admin login endpoint."""
    user = await authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user is super admin
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Access denied. Super admin role required.")
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        expire_at=(datetime.utcnow() + access_token_expires).isoformat()
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information."""
    try:
        from jose import jwt
        from app.environment import environment
        
        token = credentials.credentials
        payload = jwt.decode(token, environment.JWT_SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await get_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")