
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.schemas.vendor import (
    VendorCreateRequest,
    VendorUpdateRequest,
    VendorStatusUpdateRequest,
    VendorResponse,
    VendorListResponse,
    VendorStatsResponse,
    VendorLoginRequest,
)
from app.services import vendor as vendor_service
from app.services.email import send_vendor_invitation_email, send_vendor_welcome_email
from app.utils.logger import logger
from app.environment import environment

router = APIRouter(prefix="/vendors", tags=["vendors"])

@router.post("/login", status_code=status.HTTP_200_OK)
async def vendor_login(request: VendorLoginRequest):
    result = await vendor_service.authenticate_vendor(request.email, request.password)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or inactive account"
        )
    
    return {
        "message": "Login successful",
        "vendor": result["vendor"],
        "token": result["token"],
        "expire_at": result["expire_at"]
    }

@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(request: VendorCreateRequest):
    try:
        result = await vendor_service.create_vendor(request)
        vendor = result["vendor"]
        plain_password = result["password"]
        
        vendor_login_url = getattr(
            environment, 
            'VENDOR_LOGIN_URL', 
            'http://localhost:3000/vendor/login'
        )
        
        # Send invitation email with credentials
        invitation_sent = send_vendor_invitation_email(
            vendor_id=str(vendor.id),
            vendor_name=vendor.vendor_name,
            company_name=vendor.organisation,
            vendor_email=vendor.email,
            password=plain_password,
            login_url=vendor_login_url
        )
        
        if not invitation_sent:
            logger.warning(f"Failed to send invitation email to {vendor.email}")
        
        # Send welcome email
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
async def update_vendor_status(vendor_id: str, request: VendorStatusUpdateRequest):
    vendor = await vendor_service.update_vendor_status(vendor_id, request.status)
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found"
        )
    
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
