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
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    role: str
    org_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None

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
    
    # Open and close connection immediately after getting user
    user = await AuthService.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = await AuthService.authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Update last_login timestamp with direct SQL to avoid session conflicts
    from app.db.session import get_session
    from sqlalchemy import update
    async with get_session() as db:
        await db.execute(
            update(User).where(User.id == user.id).values(last_login=datetime.utcnow())
        )
        await db.commit()
    
    # Create JWT token
    access_token_expires = timedelta(minutes=30)
    expire_at = datetime.utcnow() + access_token_expires
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    
    return LoginResponse(
        token=access_token,
        expire_at=expire_at.isoformat(),
        user={
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
            "org_id": str(user.org_id) if user.org_id else None,
        }
    )

@router.post("/signup", response_model=SignupResponse)
async def signup(request: SignupRequest):
    # Check if user already exists
    existing_user = await AuthService.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user = await AuthService.create_user(
        email=request.email,
        password=request.password,
        role=request.role,
    )
    
    return SignupResponse(
        message="User created successfully",
        user={
            "id": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )

class CurrentUserResponse(BaseModel):
    user: UserResponse

@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    user_data = UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,  # Employee code for employees
        name=current_user.name,
        phone=current_user.phone,
        bio=current_user.bio,
        address=current_user.address,
        city=current_user.city,
        state=current_user.state,
        zip_code=current_user.zip_code,
        country=current_user.country,
        timezone=current_user.timezone,
        language=current_user.language,
        role=current_user.role,
        org_id=str(current_user.org_id) if current_user.org_id else None,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
        updated_at=current_user.updated_at.isoformat() if current_user.updated_at else None,
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )
    return CurrentUserResponse(user=user_data)

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update the current user's profile information"""
    try:
        # Update user profile in database
        success = await AuthService.update_user_profile(
            str(current_user.id),
            name=profile_data.name,
            phone=profile_data.phone,
            bio=profile_data.bio,
            address=profile_data.address,
            city=profile_data.city,
            state=profile_data.state,
            zip_code=profile_data.zip_code,
            country=profile_data.country,
            timezone=profile_data.timezone,
            language=profile_data.language
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile"
            )
        
        # Fetch updated user
        updated_user = await User.get_by_id(str(current_user.id))
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=str(updated_user.id),
            email=updated_user.email,
            username=updated_user.username,  # Employee code for employees
            name=updated_user.name,
            phone=updated_user.phone,
            bio=updated_user.bio,
            address=updated_user.address,
            city=updated_user.city,
            state=updated_user.state,
            zip_code=updated_user.zip_code,
            country=updated_user.country,
            timezone=updated_user.timezone,
            language=updated_user.language,
            role=updated_user.role,
            org_id=str(updated_user.org_id) if updated_user.org_id else None,
            created_at=updated_user.created_at.isoformat() if updated_user.created_at else None,
            updated_at=updated_user.updated_at.isoformat() if updated_user.updated_at else None,
            last_login=updated_user.last_login.isoformat() if updated_user.last_login else None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
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
