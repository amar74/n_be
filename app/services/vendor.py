
import secrets
import string
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from app.models.vendor import Vendor, VendorStatus
from app.schemas.vendor import (
    VendorCreateRequest,
    VendorUpdateRequest,
    VendorStatsResponse,
)
from app.environment import environment
from app.utils.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password(length: int = 12) -> str:

    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]
    password += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

def hash_password(password: str) -> str:

    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)

def create_vendor_token(vendor_id: str, email: str) -> Dict[str, str]:

    token_expiry = datetime.utcnow() + timedelta(days=30)
    payload = {
        "sub": vendor_id,
        "email": email,
        "role": "vendor",
        "exp": token_expiry
    }
    
    secret_key = environment.JWT_SECRET_KEY
    if not secret_key:
        raise ValueError("JWT_SECRET_KEY is not set in the environment")
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    
    return {
        "token": token,
        "expire_at": token_expiry.isoformat()
    }

async def create_vendor(request: VendorCreateRequest) -> Dict[str, any]:

    existing_vendor = await Vendor.get_by_email(request.email)
    if existing_vendor:
        raise ValueError(f"Vendor with email {request.email} already exists")
    
    plain_password = request.password if request.password else generate_password()
    
    password_hash = hash_password(plain_password)
    
    vendor = await Vendor.create(
        vendor_name=request.vendor_name,
        organisation=request.organisation,
        email=request.email,
        contact_number=request.contact_number,
        password_hash=password_hash,
        website=request.website,
    )
    
    logger.info(f"Vendor created successfully: {vendor.email}")
    
    return {
        "vendor": vendor,
        "password": plain_password  # Return plain password for email
    }

async def authenticate_vendor(email: str, password: str) -> Optional[Dict]:

    vendor = await Vendor.get_by_email(email)
    
    if not vendor:
        logger.warning(f"Vendor not found: {email}")
        return None
    
    if not vendor.is_active:
        logger.warning(f"Vendor account is inactive: {email}")
        return None
    
    if not verify_password(password, vendor.password_hash):
        logger.warning(f"Invalid password for vendor: {email}")
        return None
    
    token_data = create_vendor_token(str(vendor.id), vendor.email)
    
    logger.info(f"Vendor authenticated sucessfully: {email}")
    
    return {
        "vendor": vendor.to_dict(),
        "token": token_data["token"],
        "expire_at": token_data["expire_at"]
    }

async def get_vendor_stats() -> VendorStatsResponse:
    from app.models.user import User
    from app.schemas.user import Roles
    from sqlalchemy import select, func
    from app.db.session import get_session

    async with get_session() as session:
        try:
            # Count total vendors (users with vendor role)
            total_result = await session.execute(
                select(func.count()).select_from(User).where(User.role == Roles.VENDOR)
            )
            total_vendors = int(total_result.scalar_one())
            
            # For now, all vendors are considered approved since there's no status field in users table
            # In the future, you might want to add a status field to the users table
            return VendorStatsResponse(
                total_vendors=total_vendors,
                total_approved=total_vendors,  # All are considered approved
                total_pending=0,  # No pending status in users table
                total_rejected=0,  # No rejected status in users table
            )
        except Exception as ex:
            logger.error(f"Failed to get vendor stats: {str(ex)}")
            raise MegapolisHTTPException(status_code=500, message="Failed to get vendor statistics")

async def get_all_vendors(skip: int = 0, limit: int = 100) -> List["User"]:
    from app.models.user import User
    from app.schemas.user import Roles
    from sqlalchemy import select
    from app.db.session import get_session

    async with get_session() as session:
        try:
            result = await session.execute(
                select(User).where(User.role == Roles.VENDOR).offset(skip).limit(limit)
            )
            return list(result.scalars().all())
        except Exception as ex:
            logger.error(f"Failed to get all vendors: {str(ex)}")
            raise MegapolisHTTPException(status_code=500, message="Failed to get vendors list")

async def get_vendor_by_id(vendor_id: str) -> Optional[Vendor]:

    from uuid import UUID
    try:
        uuid_id = UUID(vendor_id)
        return await Vendor.get_by_id(uuid_id)
    except ValueError:
        return None

async def update_vendor(
    vendor_id: str,
    request: VendorUpdateRequest
) -> Optional[Vendor]:

    from uuid import UUID
    try:
        uuid_id = UUID(vendor_id)
        return await Vendor.update(
            vendor_id=uuid_id,
            vendor_name=request.vendor_name,
            organisation=request.organisation,
            website=request.website,
            contact_number=request.contact_number,
        )
    except ValueError:
        return None

async def update_vendor_status(vendor_id: str, status: str) -> Optional[Vendor]:

    from uuid import UUID
    try:
        uuid_id = UUID(vendor_id)
        return await Vendor.update_status(uuid_id, status)
    except ValueError:
        return None

async def delete_vendor(vendor_id: str) -> bool:

    from uuid import UUID
    try:
        uuid_id = UUID(vendor_id)
        return await Vendor.delete(uuid_id)
    except ValueError:
        return False
