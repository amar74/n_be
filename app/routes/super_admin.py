
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt

from app.schemas.vendor import VendorStatsResponse
from app.services import admin as admin_service
from app.utils.logger import logger
from app.environment import environment, Constants
from app.dependencies.permissions import require_super_admin
from app.models.user import User

router = APIRouter(prefix="/super-admin", tags=["super-admin"])

class SuperAdminLoginRequest(BaseModel):
    
    email: EmailStr
    password: str

class SuperAdminLoginResponse(BaseModel):
    
    message: str
    token: str
    expire_at: str
    user: dict

class SuperAdminDashboardResponse(BaseModel):
    
    message: str
    vendor_stats: VendorStatsResponse

@router.post("/login", response_model=SuperAdminLoginResponse)
async def super_admin_login(request: SuperAdminLoginRequest):
    if request.email not in Constants.SUPER_ADMIN_EMAILS:
        raise HTTPException(status_code=401, detail="invalid credentials")
    
    pwd = getattr(environment, 'SUPER_ADMIN_PASSWORD', 'admin123')
    if request.password != pwd:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = await User.get_by_email(request.email) or await User.create(request.email)
    
    exp = datetime.utcnow() + timedelta(days=30)
    token = jwt.encode(
        {"sub": str(user.id), "email": request.email, "role": "super_admin", "exp": exp},
        environment.JWT_SECRET_KEY,
        algorithm="HS256"
    )
    
    return SuperAdminLoginResponse(
        message="Login successful",
        token=token,
        expire_at=exp.isoformat(),
        user={"id": str(user.id), "email": user.email, "role": "super_admin"}
    )

@router.get("/dashboard", response_model=SuperAdminDashboardResponse)
async def get_super_admin_dashboard(current_user: User = Depends(require_super_admin())):
    stats = await admin_service.get_vendor_stats()
    return SuperAdminDashboardResponse(
        message="success",
        vendor_stats=VendorStatsResponse(**stats)
    )

@router.get("/me")
async def get_super_admin_profile(current_user: User = Depends(require_super_admin())):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": "super_admin",
        "org_id": str(current_user.org_id) if current_user.org_id else None
    }
