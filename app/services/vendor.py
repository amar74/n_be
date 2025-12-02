"""
Procurement Vendor Service

IMPORTANT: This service is for Procurement vendors (suppliers), NOT Super Admin vendor users.

- Super Admin Vendors: Users who log into the application (created via /admin/create_new_user)
- Procurement Vendors: Supplier records for procurement management (created via /vendors/)

These are TWO COMPLETELY SEPARATE systems. Do NOT mix them.

See: docs/VENDOR_SYSTEMS_DOCUMENTATION.md for full details.
"""

import secrets
import string
import uuid
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import jwt
import bcrypt

from app.models.vendor import Vendor, VendorStatus, VendorQualification

from app.schemas.vendor import (
    VendorCreateRequest,
    VendorUpdateRequest,
    VendorStatsResponse,
    VendorQualificationCreateRequest,
    VendorQualificationUpdateRequest,
    VendorQualificationResponse,
)
from app.environment import environment
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException

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
    # Bcrypt has a 72-byte limit, truncate if necessary
    # Convert to bytes and truncate to 72 bytes max
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Hash using bcrypt directly
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

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
    """
    Create a Procurement vendor (supplier record).
    Note: These are suppliers from which the organization purchases, NOT user accounts.
    They do NOT need passwords or login credentials.
    """
    existing_vendor = await Vendor.get_by_email(request.email)
    if existing_vendor:
        raise ValueError(f"Vendor with email {request.email} already exists")
    
    # Procurement vendors are suppliers, not users - no password needed
    # Create vendor record without password
    vendor = await Vendor.create(
        vendor_name=request.vendor_name,
        organisation=request.organisation,
        email=request.email,
        contact_number=request.contact_number,
        password_hash=None,  # Suppliers don't need passwords
        website=request.website,
        address=getattr(request, 'address', None),
        payment_terms=getattr(request, 'payment_terms', None),
        tax_id=getattr(request, 'tax_id', None),
        notes=getattr(request, 'notes', None),
    )
    
    logger.info(f"Procurement vendor (supplier) created successfully: {vendor.email}")
    
    return {
        "vendor": vendor
    }

async def authenticate_vendor(email: str, password: str) -> Optional[Dict]:
    """
    Authenticate a vendor for login.
    Note: Most Procurement vendors (suppliers) don't have passwords and cannot log in.
    This endpoint is for vendors who have been explicitly given portal access with passwords.
    """
    vendor = await Vendor.get_by_email(email)
    
    if not vendor:
        logger.warning(f"Vendor not found: {email}")
        return None
    
    if not vendor.is_active:
        logger.warning(f"Vendor account is inactive: {email}")
        return None
    
    # Procurement vendors (suppliers) typically don't have passwords
    if not vendor.password_hash:
        logger.warning(f"Vendor does not have login credentials (supplier record only): {email}")
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
    from sqlalchemy import func, select
    from app.db.session import get_session
    
    async with get_session() as session:
        try:
            # Count total vendors
            total_result = await session.execute(select(func.count(Vendor.id)))
            total_vendors = int(total_result.scalar_one())
            
            # Count by status
            approved_result = await session.execute(
                select(func.count(Vendor.id)).where(Vendor.status == VendorStatus.APPROVED.value)
            )
            total_approved = int(approved_result.scalar_one())
            
            pending_result = await session.execute(
                select(func.count(Vendor.id)).where(Vendor.status == VendorStatus.PENDING.value)
            )
            total_pending = int(pending_result.scalar_one())
            
            rejected_result = await session.execute(
                select(func.count(Vendor.id)).where(Vendor.status == VendorStatus.REJECTED.value)
            )
            total_rejected = int(rejected_result.scalar_one())
            
            return VendorStatsResponse(
                total_vendors=total_vendors,
                total_approved=total_approved,
                total_pending=total_pending,
                total_rejected=total_rejected,
            )
        except Exception as ex:
            logger.error(f"Failed to get vendor stats: {str(ex)}")
            raise MegapolisHTTPException(status_code=500, message="Failed to get vendor statistics")

async def get_all_vendors(skip: int = 0, limit: int = 100) -> List[Vendor]:
    from sqlalchemy import select
    from app.db.session import get_session
    
    async with get_session() as session:
        try:
            result = await session.execute(select(Vendor).offset(skip).limit(limit))
            vendors = list(result.scalars().all())
            return vendors
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
            address=getattr(request, 'address', None),
            payment_terms=getattr(request, 'payment_terms', None),
            tax_id=getattr(request, 'tax_id', None),
            notes=getattr(request, 'notes', None),
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


# Vendor Qualification Service Methods
async def create_vendor_qualification(
    request: VendorQualificationCreateRequest,
    assessed_by: str
) -> VendorQualificationResponse:
    """Create or update vendor qualification"""
    from uuid import UUID
    from sqlalchemy import select
    from app.db.session import get_session
    
    try:
        vendor_id = UUID(request.vendor_id)
        assessor_id = UUID(assessed_by)
    except ValueError as e:
        logger.error(f"Invalid UUID format: {e}")
        raise MegapolisHTTPException(status_code=400, message=f"Invalid UUID format: {str(e)}")
    
    async with get_session() as session:
        # Check if vendor exists
        vendor_result = await session.execute(select(Vendor).where(Vendor.id == vendor_id))
        vendor = vendor_result.scalar_one_or_none()
        if not vendor:
            raise MegapolisHTTPException(status_code=404, message="Vendor not found")
        
        # Deactivate all existing qualifications for this vendor (mark previous ones as inactive)
        existing_quals_result = await session.execute(
            select(VendorQualification).where(
                VendorQualification.vendor_id == vendor_id,
                VendorQualification.is_active == True
            )
        )
        existing_quals = existing_quals_result.scalars().all()
        for existing_qual in existing_quals:
            existing_qual.is_active = False
            existing_qual.updated_at = datetime.utcnow()
        
        # Create new qualification (always create new, never update existing)
        qualification = VendorQualification(
            id=uuid.uuid4(),
            vendor_id=vendor_id,
            financial_stability=request.financial_stability,
            credentials_verified=request.credentials_verified or False,
            certifications=request.certifications or [],
            qualification_score=str(request.qualification_score) if request.qualification_score else None,
            risk_level=request.risk_level,
            notes=request.notes,
            is_active=True,  # New qualification is always active
            assessment_type=request.assessment_type or "manual",  # Default to manual if not specified
            assessed_by=assessor_id,
            last_assessed=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(qualification)
        
        try:
            await session.commit()
            await session.refresh(qualification)
        except Exception as e:
            logger.error(f"Error committing qualification: {e}")
            await session.rollback()
            raise MegapolisHTTPException(status_code=500, message=f"Failed to save qualification: {str(e)}")
        
        try:
            return VendorQualificationResponse(
                id=str(qualification.id),
                vendor_id=str(qualification.vendor_id),
                vendor_name=vendor.vendor_name,
                financial_stability=qualification.financial_stability,
                credentials_verified=qualification.credentials_verified,
                certifications=qualification.certifications or [],
                qualification_score=float(qualification.qualification_score) if qualification.qualification_score else None,
                risk_level=qualification.risk_level,
                notes=qualification.notes,
                is_active=qualification.is_active,
                assessment_type=qualification.assessment_type,
                assessed_by=str(qualification.assessed_by) if qualification.assessed_by else None,
                last_assessed=qualification.last_assessed.isoformat() if qualification.last_assessed else None,
                created_at=qualification.created_at.isoformat(),
                updated_at=qualification.updated_at.isoformat(),
            )
        except Exception as e:
            logger.error(f"Error creating response: {e}")
            raise MegapolisHTTPException(status_code=500, message=f"Failed to create response: {str(e)}")


async def get_vendor_qualification(vendor_id: str, active_only: bool = True) -> Optional[VendorQualificationResponse]:
    """Get vendor qualification by vendor ID (returns active one by default, or latest if none active)"""
    from uuid import UUID
    from sqlalchemy import select
    from app.db.session import get_session
    
    try:
        uuid_id = UUID(vendor_id)
    except ValueError:
        return None
    
    async with get_session() as session:
        try:
            if active_only:
                # Get active qualification
                result = await session.execute(
                    select(VendorQualification)
                    .where(VendorQualification.vendor_id == uuid_id, VendorQualification.is_active == True)
                    .order_by(VendorQualification.created_at.desc())
                )
            else:
                # Get latest qualification (even if inactive)
                result = await session.execute(
                    select(VendorQualification)
                    .where(VendorQualification.vendor_id == uuid_id)
                    .order_by(VendorQualification.created_at.desc())
                )
            qualification = result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error querying qualification: {e}", exc_info=True)
            return None
        
        if not qualification:
            return None
        
        # Get vendor name
        vendor_result = await session.execute(select(Vendor).where(Vendor.id == uuid_id))
        vendor = vendor_result.scalar_one_or_none()
        
        try:
            return VendorQualificationResponse(
                id=str(qualification.id),
                vendor_id=str(qualification.vendor_id),
                vendor_name=vendor.vendor_name if vendor else "Unknown",
                financial_stability=qualification.financial_stability,
                credentials_verified=qualification.credentials_verified,
                certifications=qualification.certifications or [],
                qualification_score=float(qualification.qualification_score) if qualification.qualification_score else None,
                risk_level=qualification.risk_level,
                notes=qualification.notes,
                is_active=getattr(qualification, 'is_active', True),  # Default to True if attribute doesn't exist
                assessment_type=getattr(qualification, 'assessment_type', None),
                assessed_by=str(qualification.assessed_by) if qualification.assessed_by else None,
                last_assessed=qualification.last_assessed.isoformat() if qualification.last_assessed else None,
                created_at=qualification.created_at.isoformat(),
                updated_at=qualification.updated_at.isoformat(),
            )
        except Exception as e:
            logger.error(f"Error creating qualification response: {e}", exc_info=True)
            raise


async def get_vendor_qualification_history(vendor_id: str, limit: int = 10) -> List[VendorQualificationResponse]:
    """Get qualification history for a vendor (all qualifications, ordered by date)"""
    from uuid import UUID
    from sqlalchemy import select
    from app.db.session import get_session
    
    try:
        uuid_id = UUID(vendor_id)
    except ValueError:
        return []
    
    async with get_session() as session:
        result = await session.execute(
            select(VendorQualification)
            .where(VendorQualification.vendor_id == uuid_id)
            .order_by(VendorQualification.created_at.desc())
            .limit(limit)
        )
        qualifications = list(result.scalars().all())
        
        # Get vendor name
        vendor_result = await session.execute(select(Vendor).where(Vendor.id == uuid_id))
        vendor = vendor_result.scalar_one_or_none()
        vendor_name = vendor.vendor_name if vendor else "Unknown"
        
        responses = []
        for qual in qualifications:
            responses.append(VendorQualificationResponse(
                id=str(qual.id),
                vendor_id=str(qual.vendor_id),
                vendor_name=vendor_name,
                financial_stability=qual.financial_stability,
                credentials_verified=qual.credentials_verified,
                certifications=qual.certifications or [],
                qualification_score=float(qual.qualification_score) if qual.qualification_score else None,
                risk_level=qual.risk_level,
                notes=qual.notes,
                is_active=getattr(qual, 'is_active', True),  # Default to True if attribute doesn't exist
                assessment_type=getattr(qual, 'assessment_type', None),
                assessed_by=str(qual.assessed_by) if qual.assessed_by else None,
                last_assessed=qual.last_assessed.isoformat() if qual.last_assessed else None,
                created_at=qual.created_at.isoformat(),
                updated_at=qual.updated_at.isoformat(),
            ))
        
        return responses


async def get_all_vendor_qualifications(skip: int = 0, limit: int = 100, active_only: bool = True) -> List[VendorQualificationResponse]:
    """Get all vendor qualifications (returns active ones by default)"""
    from sqlalchemy import select
    from app.db.session import get_session
    
    async with get_session() as session:
        query = select(VendorQualification)
        if active_only:
            query = query.where(VendorQualification.is_active == True)
        query = query.order_by(VendorQualification.created_at.desc()).offset(skip).limit(limit)
        
        result = await session.execute(query)
        qualifications = list(result.scalars().all())
        
        responses = []
        for qual in qualifications:
            vendor_result = await session.execute(select(Vendor).where(Vendor.id == qual.vendor_id))
            vendor = vendor_result.scalar_one_or_none()
            
            responses.append(VendorQualificationResponse(
                id=str(qual.id),
                vendor_id=str(qual.vendor_id),
                vendor_name=vendor.vendor_name if vendor else "Unknown",
                financial_stability=qual.financial_stability,
                credentials_verified=qual.credentials_verified,
                certifications=qual.certifications or [],
                qualification_score=float(qual.qualification_score) if qual.qualification_score else None,
                risk_level=qual.risk_level,
                notes=qual.notes,
                is_active=getattr(qual, 'is_active', True),  # Default to True if attribute doesn't exist
                assessment_type=getattr(qual, 'assessment_type', None),
                assessed_by=str(qual.assessed_by) if qual.assessed_by else None,
                last_assessed=qual.last_assessed.isoformat() if qual.last_assessed else None,
                created_at=qual.created_at.isoformat(),
                updated_at=qual.updated_at.isoformat(),
            ))
        
        return responses


async def get_vendor_performance(vendor_id: str) -> Optional[Dict]:
    """Calculate vendor performance from real data (orders, invoices, delivery times)"""
    from uuid import UUID
    from sqlalchemy import select, func
    from app.db.session import get_session
    from app.models.procurement import PurchaseOrder, VendorInvoice, DeliveryMilestone
    from decimal import Decimal
    
    try:
        uuid_id = UUID(vendor_id)
    except ValueError:
        return None
    
    async with get_session() as session:
        # Get vendor
        vendor_result = await session.execute(select(Vendor).where(Vendor.id == uuid_id))
        vendor = vendor_result.scalar_one_or_none()
        if not vendor:
            return None
        
        # Count total orders
        orders_result = await session.execute(
            select(func.count(PurchaseOrder.id)).where(PurchaseOrder.vendor_id == uuid_id)
        )
        total_orders = int(orders_result.scalar_one() or 0)
        
        # Calculate total spend from purchase orders (primary source - committed spend)
        orders_spend_result = await session.execute(
            select(func.sum(PurchaseOrder.amount)).where(PurchaseOrder.vendor_id == uuid_id)
        )
        orders_spend = float(orders_spend_result.scalar_one() or 0)
        
        # Calculate total spend from invoices (actual invoiced amount)
        invoices_result = await session.execute(
            select(func.sum(VendorInvoice.amount)).where(VendorInvoice.vendor_id == uuid_id)
        )
        invoices_spend = float(invoices_result.scalar_one() or 0)
        
        # Use purchase orders spend as primary (committed spend), fallback to invoices if no orders
        total_spend = orders_spend if orders_spend > 0 else invoices_spend
        
        # Calculate on-time delivery rate from milestones
        milestones_result = await session.execute(
            select(DeliveryMilestone)
            .join(PurchaseOrder)
            .where(PurchaseOrder.vendor_id == uuid_id)
        )
        milestones = list(milestones_result.scalars().all())
        
        on_time_count = 0
        total_milestones = len(milestones)
        delivery_times = []
        
        for milestone in milestones:
            if milestone.completed_date and milestone.due_date:
                delivery_times.append((milestone.completed_date - milestone.due_date).days)
                if milestone.completed_date <= milestone.due_date:
                    on_time_count += 1
        
        on_time_delivery_rate = (on_time_count / total_milestones * 100) if total_milestones > 0 else 0.0
        average_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0.0
        
        # Get last order date
        last_order_result = await session.execute(
            select(PurchaseOrder.created_at)
            .where(PurchaseOrder.vendor_id == uuid_id)
            .order_by(PurchaseOrder.created_at.desc())
            .limit(1)
        )
        last_order_date = last_order_result.scalar_one_or_none()
        
        # Calculate quality rating (placeholder - can be enhanced with actual ratings)
        quality_rating = 4.5 if total_orders > 0 else 0.0
        communication_rating = 4.3 if total_orders > 0 else 0.0
        overall_rating = (quality_rating + communication_rating) / 2
        
        # Determine performance trend based on actual data
        if total_orders == 0:
            performance_trend = "new"
        elif total_orders == 1:
            # For single order, default to stable (not enough data to determine trend)
            performance_trend = "stable"
        elif total_orders >= 5:
            if on_time_delivery_rate >= 90:
                performance_trend = "improving"
            elif on_time_delivery_rate >= 70:
                performance_trend = "stable"
            else:
                performance_trend = "declining"
        elif total_orders >= 3:
            if on_time_delivery_rate >= 80:
                performance_trend = "stable"
            else:
                performance_trend = "declining"
        else:
            # 2 orders - default to stable
            performance_trend = "stable"
        
        from decimal import Decimal
        
        return {
            "vendor_id": str(vendor.id),
            "vendor_name": vendor.vendor_name,
            "total_orders": total_orders,
            "total_spend": Decimal(str(total_spend)),
            "average_delivery_time": average_delivery_time,
            "on_time_delivery_rate": on_time_delivery_rate,
            "quality_rating": quality_rating,
            "communication_rating": communication_rating,
            "overall_rating": overall_rating,
            "performance_trend": performance_trend,
            "last_order_date": last_order_date.isoformat() if last_order_date else None,
        }
