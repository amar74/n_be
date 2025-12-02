"""
Notification API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.models.user import User
from app.schemas.user_permission import UserPermissionResponse
from app.db.session import get_request_transaction
from app.services.opportunity_notifications import OpportunityNotificationService
from app.utils.logger import get_logger

logger = get_logger("notification_routes")

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def get_notifications(
    unread_only: bool = Query(False, description="Filter unread notifications only"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"notifications": ["view"]}))
) -> List[dict]:
    """Get notifications for current user."""
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    service = OpportunityNotificationService(db)
    notifications = await service.get_opportunity_notifications(
        user_id=current_user.id,
        org_id=current_user.org_id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    return notifications


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"notifications": ["view"]}))
) -> dict:
    """Get count of unread notifications."""
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    service = OpportunityNotificationService(db)
    count = await service.get_unread_count(
        user_id=current_user.id,
        org_id=current_user.org_id
    )
    
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"notifications": ["edit"]}))
) -> dict:
    """Mark a notification as read."""
    service = OpportunityNotificationService(db)
    success = await service.mark_notification_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True, "message": "Notification marked as read"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"notifications": ["edit"]}))
) -> dict:
    """Mark all notifications as read for current user."""
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="User must belong to an organization")
    
    service = OpportunityNotificationService(db)
    count = await service.mark_all_notifications_read(
        user_id=current_user.id,
        org_id=current_user.org_id
    )
    
    return {"success": True, "count": count, "message": f"{count} notifications marked as read"}

