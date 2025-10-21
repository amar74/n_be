from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta, datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict
    expire_at: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    org_id: Optional[str] = None

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "admin"

class SignupResponse(BaseModel):
    message: str
    user: dict

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Direct database query to avoid SQLAlchemy relationship issues
    import asyncpg
    from app.environment import environment
    # Convert SQLAlchemy URL to asyncpg format
    db_url = environment.DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')
    conn = await asyncpg.connect(db_url)
    try:
        user_row = await conn.fetchrow(
            'SELECT id, email, org_id, role FROM users WHERE id = $1',
            user_id
        )
        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create a simple user object
        user = User()
        user.id = user_row['id']
        user.email = user_row['email']
        user.org_id = user_row['org_id']
        user.role = user_row['role']
        return user
    finally:
        await conn.close()

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = await AuthService.authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "org_id": str(user.org_id) if user.org_id else None,
        },
        expire_at=(datetime.utcnow() + access_token_expires).isoformat()
    )

@router.post("/super-admin/login", response_model=LoginResponse)
async def super_admin_login(request: LoginRequest):
    user = await AuthService.authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is super admin
    if user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Super admin role required.",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "org_id": str(user.org_id) if user.org_id else None,
        },
        expire_at=(datetime.utcnow() + access_token_expires).isoformat()
    )

@router.post("/signup", response_model=SignupResponse)
async def signup(request: SignupRequest):
    # Check if user already exists
    existing_user = await AuthService.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = await AuthService.create_user(
        email=request.email,
        password=request.password,
        role=request.role
    )
    
    return SignupResponse(
        message="User created successfully",
        user={
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        org_id=str(current_user.org_id) if current_user.org_id else None
    )

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user)
):
    # Verify current password
    if not AuthService.verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    success = await AuthService.update_user_password(str(current_user.id), new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"message": "Password updated successfully"}