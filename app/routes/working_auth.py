"""
Working authentication routes that bypass complex model loading.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta, datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
from app.environment import environment

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
    created_at: Optional[str] = None

# Hardcoded users for now (will be replaced with database later)
USERS = {
    "admin@megapolis.com": {
        "id": "1",
        "email": "admin@megapolis.com",
        "password": "Amar77492$#@",
        "role": "super_admin"
    },
    "amar74.soft@gmail.com": {
        "id": "2", 
        "email": "amar74.soft@gmail.com",
        "password": "Amar77492#@$",
        "role": "admin"
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, environment.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, environment.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.JWTError:
        return None

# Authentication endpoints
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = USERS.get(request.email)
    
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        token=access_token,
        user={
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "created_at": datetime.utcnow().isoformat()
        },
        expire_at=(datetime.utcnow() + access_token_expires).isoformat()
    )

@router.post("/super-admin/login", response_model=LoginResponse)
async def super_admin_login(request: LoginRequest):
    user = USERS.get(request.email)
    
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is super admin
    if user["role"] != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Super admin role required.",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        token=access_token,
        user={
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "created_at": datetime.utcnow().isoformat()
        },
        expire_at=(datetime.utcnow() + access_token_expires).isoformat()
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info():
    # For now, return a dummy user - you can implement JWT verification later
    return UserResponse(
        id="1",
        email="admin@megapolis.com",
        role="super_admin",
        created_at=datetime.utcnow().isoformat()
    )

# Add minimal orgs endpoint
@router.get("/orgs/me")
async def get_my_org():
    return {
        "id": "1",
        "name": "Megapolis Advisory",
        "owner_id": "1",
        "created_at": datetime.utcnow().isoformat()
    }

# Add minimal opportunities endpoint
@router.get("/opportunities/")
async def get_opportunities():
    return {
        "opportunities": [],
        "total": 0,
        "page": 1,
        "per_page": 10
    }

# Add minimal accounts endpoint  
@router.get("/accounts/")
async def get_accounts():
    return {
        "accounts": [],
        "total": 0,
        "page": 1,
        "per_page": 10
    }