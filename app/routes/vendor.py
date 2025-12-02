"""
Procurement Vendor Routes

IMPORTANT: These routes are for Procurement vendors (suppliers), NOT Super Admin vendor users.

- Super Admin Vendors: Users who log into the application (created via /admin/create_new_user)
- Procurement Vendors: Supplier records for procurement management (created via /vendors/)

These are TWO COMPLETELY SEPARATE systems. Do NOT mix them.

See: docs/VENDOR_SYSTEMS_DOCUMENTATION.md for full details.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from app.schemas.vendor import (
    VendorCreateRequest,
    VendorUpdateRequest,
    VendorStatusUpdateRequest,
    VendorResponse,
    VendorListResponse,
    VendorStatsResponse,
    VendorQualificationCreateRequest,
    VendorQualificationUpdateRequest,
    VendorQualificationResponse,
)
from app.schemas.auth import AuthUserResponse
from app.dependencies.user_auth import get_current_user
from app.services import vendor as vendor_service
from app.services.email import send_vendor_invitation_email, send_vendor_welcome_email
from app.services.vendor_risk_assessment import VendorRiskAssessmentService
from app.utils.logger import logger
from app.environment import environment
from uuid import UUID

router = APIRouter(prefix="/vendors", tags=["vendors"])

@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(request: VendorCreateRequest):
    """
    Create a Procurement vendor (supplier record).
    Note: These are suppliers from which the organization purchases, NOT user accounts.
    They do NOT receive login credentials.
    """
    try:
        result = await vendor_service.create_vendor(request)
        vendor = result["vendor"]
        
        # Send welcome email (suppliers don't need login credentials)
        welcome_sent = send_vendor_welcome_email(
            vendor_name=vendor.vendor_name,
            company_name=vendor.organisation,
            vendor_email=vendor.email
        )
        
        if not welcome_sent:
            logger.warning(f"Failed to send welcome email to {vendor.email}")
        
        return VendorResponse(**vendor.to_dict())
        
    except ValueError as e:
        logger.error(f"Error creating vendor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error creating vendor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error"
        )

@router.get("/stats", response_model=VendorStatsResponse)
async def get_vendor_statistics():
    try:
        stats = await vendor_service.get_vendor_stats()
        return stats
    except Exception as e:
        logger.exception(f"Error fetching vendor stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error"
        )

@router.get("/", response_model=VendorListResponse)
async def get_all_vendors(skip: int = 0, limit: int = 100):
    try:
        vendors = await vendor_service.get_all_vendors(skip=skip, limit=limit)
        total = await vendor_service.get_vendor_stats()
        
        return VendorListResponse(
            vendors=[VendorResponse(**v.to_dict()) for v in vendors],
            total=total.total_vendors,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.exception(f"Error fetching vendors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error"
        )

# Vendor Qualification Endpoints (MUST come before /{vendor_id} route to avoid route conflicts)
@router.post("/qualifications", response_model=VendorQualificationResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor_qualification(
    request: VendorQualificationCreateRequest,
    current_user: AuthUserResponse = Depends(get_current_user)
):
    """
    Create or update vendor qualification.
    Only admin, manager, vendor (main owner), or organization owners can create qualifications.
    """
    from app.models.organization import Organization
    
    # Check permissions (same as vendor approval)
    user_role_lower = current_user.role.lower() if current_user.role else ''
    has_admin_role = user_role_lower in ['admin', 'manager', 'vendor']
    
    is_org_owner = False
    if current_user.org_id:
        try:
            from uuid import UUID
            org_id_uuid = UUID(current_user.org_id) if isinstance(current_user.org_id, str) else current_user.org_id
            org = await Organization.get_by_id(org_id_uuid)
            if org and org.owner_id:
                owner_id_str = str(org.owner_id)
                user_id_str = str(current_user.id)
                if owner_id_str == user_id_str:
                    is_org_owner = True
        except Exception as e:
            logger.warning(f"Error checking organization owner: {str(e)}")
    
    if not has_admin_role and not is_org_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, manager, vendor (main owner), or organization owners can create vendor qualifications"
        )
    
    try:
        qualification = await vendor_service.create_vendor_qualification(request, str(current_user.id))
        return qualification
    except Exception as e:
        logger.error(f"Error creating vendor qualification: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vendor qualification: {str(e)}"
        )


@router.get("/qualifications", response_model=List[VendorQualificationResponse])
async def get_all_vendor_qualifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(True, description="Return only active qualifications"),
    current_user: AuthUserResponse = Depends(get_current_user)
):
    """Get all vendor qualifications (active ones by default)"""
    try:
        qualifications = await vendor_service.get_all_vendor_qualifications(skip, limit, active_only)
        return qualifications
    except Exception as e:
        logger.error(f"Error fetching vendor qualifications: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch vendor qualifications: {str(e)}"
        )


@router.get("/qualifications/{vendor_id}", response_model=VendorQualificationResponse)
async def get_vendor_qualification(
    vendor_id: str,
    active_only: bool = Query(True, description="Return only active qualification"),
    current_user: AuthUserResponse = Depends(get_current_user)
):
    """Get vendor qualification by vendor ID (returns active one by default)"""
    qualification = await vendor_service.get_vendor_qualification(vendor_id, active_only)
    if not qualification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Qualification not found for vendor {vendor_id}"
        )
    return qualification


@router.get("/qualifications/{vendor_id}/history", response_model=List[VendorQualificationResponse])
async def get_vendor_qualification_history(
    vendor_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of historical qualifications to return"),
    current_user: AuthUserResponse = Depends(get_current_user)
):
    """Get qualification history for a vendor (all qualifications, ordered by date)"""
    try:
        history = await vendor_service.get_vendor_qualification_history(vendor_id, limit)
        return history
    except Exception as e:
        logger.error(f"Error fetching vendor qualification history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch qualification history: {str(e)}"
        )


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: str):
    vendor = await vendor_service.get_vendor_by_id(vendor_id)
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )
    
    return VendorResponse(**vendor.to_dict())

@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(vendor_id: str, request: VendorUpdateRequest):
    vendor = await vendor_service.update_vendor(vendor_id, request)
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )
    
    return VendorResponse(**vendor.to_dict())

@router.patch("/{vendor_id}/status", response_model=VendorResponse)
async def update_vendor_status(
    vendor_id: str, 
    request: VendorStatusUpdateRequest,
    current_user: AuthUserResponse = Depends(get_current_user)
):
    """
    Update vendor status (approve/reject).
    Only admin, manager, vendor (main owner of subscribed app), or organization owners can approve/reject vendors.
    
    NOTE: "vendor" role = main owner/admin of subscribed application with full admin privileges.
    This applies to all modules - vendor role users can manage all features.
    """
    from app.models.organization import Organization
    
    # IMPORTANT: "vendor" role = main owner/admin of subscribed application (full admin privileges)
    # Check if user has admin, manager, or vendor role
    user_role_lower = current_user.role.lower() if current_user.role else ''
    has_admin_role = user_role_lower in ['admin', 'manager', 'vendor']
    
    # Also check if user is organization owner
    is_org_owner = False
    if current_user.org_id:
        try:
            from uuid import UUID
            org_id_uuid = UUID(current_user.org_id) if isinstance(current_user.org_id, str) else current_user.org_id
            org = await Organization.get_by_id(org_id_uuid)
            if org and org.owner_id:
                # Compare owner_id (UUID) with current_user.id (string)
                owner_id_str = str(org.owner_id)
                user_id_str = str(current_user.id)
                if owner_id_str == user_id_str:
                    is_org_owner = True
                    logger.info(f"User {current_user.email} is organization owner for org {current_user.org_id}")
        except Exception as e:
            logger.warning(f"Error checking organization owner: {str(e)}")
            import traceback
            logger.warning(traceback.format_exc())
    
    # Allow if user is admin, manager, vendor (main owner), or organization owner
    if not has_admin_role and not is_org_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only admin, manager, vendor (main owner), or organization owners can approve or reject vendors. Your role: {current_user.role}"
        )
    
    vendor = await vendor_service.update_vendor_status(vendor_id, request.status)
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )
    
    logger.info(f"Vendor {vendor_id} status updated to {request.status} by {current_user.email} (role: {current_user.role}, is_owner: {is_org_owner})")
    
    return VendorResponse(**vendor.to_dict())

@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(vendor_id: str):
    success = await vendor_service.delete_vendor(vendor_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )
    
    return None


# Risk Assessment Endpoints (MUST come before /{vendor_id} route)
@router.get("/risk-assessment")
async def get_all_vendor_risk_assessments(
    current_user: AuthUserResponse = Depends(get_current_user)
):
    """Get AI-powered risk assessments for all vendors"""
    from app.services.vendor_risk_assessment import VendorRiskAssessmentService
    
    risk_service = VendorRiskAssessmentService()
    try:
        assessments = await risk_service.assess_all_vendors()
        return assessments
    except Exception as e:
        logger.error(f"Error assessing all vendors: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assess vendors: {str(e)}"
        )


@router.get("/risk-assessment/{vendor_id}")
async def get_vendor_risk_assessment(
    vendor_id: str,
    current_user: AuthUserResponse = Depends(get_current_user)
):
    """Get AI-powered risk assessment for a vendor"""
    from app.services.vendor_risk_assessment import VendorRiskAssessmentService
    
    risk_service = VendorRiskAssessmentService()
    try:
        assessment = await risk_service.assess_vendor_risk(vendor_id)
        return assessment
    except Exception as e:
        logger.error(f"Error assessing vendor risk: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assess vendor risk: {str(e)}"
        )


@router.get("/{vendor_id}/performance")
async def get_vendor_performance(
    vendor_id: str,
    current_user: AuthUserResponse = Depends(get_current_user)
):
    """Get vendor performance metrics calculated from real data"""
    from app.schemas.procurement import VendorPerformanceResponse
    
    performance = await vendor_service.get_vendor_performance(vendor_id)
    if not performance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance data not found for vendor {vendor_id}"
        )
    
    return VendorPerformanceResponse(**performance)
