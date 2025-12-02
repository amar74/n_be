"""
Notification service for opportunity-related events.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.models.user import User
from app.models.opportunity import Opportunity
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationPreference
from app.services.email import _send_email_via_smtp
from app.utils.logger import get_logger

logger = get_logger("opportunity_notifications")


class OpportunityNotificationService:
    """Service for managing opportunity-related notifications."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def _get_user_preferences(self, user_id: UUID) -> Dict[str, Any]:
        """Get user notification preferences."""
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        result = await self.db.execute(stmt)
        pref = result.scalar_one_or_none()
        if pref:
            return pref.preferences
        return {}
    
    async def _should_send_email(self, user_id: UUID, notification_type: NotificationType) -> bool:
        """Check if email should be sent based on user preferences."""
        prefs = await self._get_user_preferences(user_id)
        type_str = notification_type.value
        if type_str in prefs:
            return prefs[type_str].get("email", True)
        return True  # Default to sending emails
    
    async def _should_send_in_app(self, user_id: UUID, notification_type: NotificationType) -> bool:
        """Check if in-app notification should be sent."""
        prefs = await self._get_user_preferences(user_id)
        type_str = notification_type.value
        if type_str in prefs:
            return prefs[type_str].get("in_app", True)
        return True  # Default to sending in-app
    
    async def _create_notification(
        self,
        org_id: UUID,
        user_id: Optional[UUID],
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.medium,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a notification record."""
        notification = Notification(
            org_id=org_id,
            user_id=user_id,
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            notification_metadata=metadata or {}
        )
        self.db.add(notification)
        await self.db.flush()
        return notification
    
    async def _send_email_notification(
        self,
        user_email: str,
        user_name: Optional[str],
        title: str,
        message: str,
        opportunity_id: Optional[UUID] = None
    ) -> bool:
        """Send email notification."""
        try:
            subject = f"Opportunity Notification: {title}"
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #161950; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 30px; background-color: #161950; color: white; text-decoration: none; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{title}</h1>
                    </div>
                    <div class="content">
                        <p>{message}</p>
                        {f'<p><a href="#" class="button">View Opportunity</a></p>' if opportunity_id else ''}
                    </div>
                </div>
            </body>
            </html>
            """
            text_body = f"{title}\n\n{message}"
            
            return _send_email_via_smtp(user_email, subject, text_body, html_body)
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    async def notify_opportunity_created(
        self,
        opportunity_id: UUID,
        org_id: UUID,
        created_by: UUID
    ) -> None:
        """Send notification when opportunity is created."""
        try:
            opportunity = await Opportunity.get_by_id(opportunity_id, org_id)
            if not opportunity:
                return
            
            # Get creator user
            stmt = select(User).where(User.id == created_by)
            result = await self.db.execute(stmt)
            creator = result.scalar_one_or_none()
            
            if not creator:
                return
            
            title = f"New Opportunity: {opportunity.project_name}"
            message = f"A new opportunity '{opportunity.project_name}' has been created."
            
            # Create in-app notification
            if await self._should_send_in_app(created_by, NotificationType.opportunity_created):
                await self._create_notification(
                    org_id=org_id,
                    user_id=created_by,
                    notification_type=NotificationType.opportunity_created,
                    title=title,
                    message=message,
                    priority=NotificationPriority.medium,
                    related_entity_type="opportunity",
                    related_entity_id=opportunity_id,
                    notification_metadata={"opportunity_name": opportunity.project_name}
                )
            
            # Send email notification
            if await self._should_send_email(created_by, NotificationType.opportunity_created):
                await self._send_email_notification(
                    creator.email,
                    creator.name,
                    title,
                    message,
                    opportunity_id
                )
            
            logger.info(f"Notification sent for opportunity {opportunity_id} creation")
            
        except Exception as e:
            logger.error(f"Error sending opportunity creation notification: {e}")
    
    async def notify_opportunity_stage_changed(
        self,
        opportunity_id: UUID,
        org_id: UUID,
        old_stage: str,
        new_stage: str,
        changed_by: UUID
    ) -> None:
        """Send notification when opportunity stage changes."""
        try:
            opportunity = await Opportunity.get_by_id(opportunity_id, org_id)
            if not opportunity:
                return
            
            # Get all users in org who should be notified
            stmt = select(User).where(User.org_id == org_id)
            result = await self.db.execute(stmt)
            users = result.scalars().all()
            
            title = f"Opportunity Stage Changed: {opportunity.project_name}"
            message = f"Opportunity '{opportunity.project_name}' stage changed from {old_stage} to {new_stage}."
            
            for user in users:
                # Create in-app notification
                if await self._should_send_in_app(user.id, NotificationType.opportunity_stage_changed):
                    await self._create_notification(
                        org_id=org_id,
                        user_id=user.id,
                        notification_type=NotificationType.opportunity_stage_changed,
                        title=title,
                        message=message,
                        priority=NotificationPriority.medium,
                        related_entity_type="opportunity",
                        related_entity_id=opportunity_id,
                        notification_metadata={"old_stage": old_stage, "new_stage": new_stage}
                    )
                
                # Send email
                if await self._should_send_email(user.id, NotificationType.opportunity_stage_changed):
                    await self._send_email_notification(
                        user.email, user.name, title, message, opportunity_id
                    )
            
            logger.info(f"Stage change notifications sent for opportunity {opportunity_id}")
            
        except Exception as e:
            logger.error(f"Error sending stage change notification: {e}")
    
    async def notify_opportunity_promoted(
        self,
        opportunity_id: UUID,
        org_id: UUID,
        promoted_by: UUID
    ) -> None:
        """Send notification when temp opportunity is promoted."""
        try:
            opportunity = await Opportunity.get_by_id(opportunity_id, org_id)
            if not opportunity:
                return
            
            # Get all users in org
            stmt = select(User).where(User.org_id == org_id)
            result = await self.db.execute(stmt)
            users = result.scalars().all()
            
            title = f"New Opportunity Promoted: {opportunity.project_name}"
            message = f"Temp opportunity '{opportunity.project_name}' has been promoted to active pipeline."
            
            for user in users:
                if await self._should_send_in_app(user.id, NotificationType.opportunity_promoted):
                    await self._create_notification(
                        org_id=org_id,
                        user_id=user.id,
                        notification_type=NotificationType.opportunity_promoted,
                        title=title,
                        message=message,
                        priority=NotificationPriority.high,
                        related_entity_type="opportunity",
                        related_entity_id=opportunity_id
                    )
                
                if await self._should_send_email(user.id, NotificationType.opportunity_promoted):
                    await self._send_email_notification(
                        user.email, user.name, title, message, opportunity_id
                    )
            
            logger.info(f"Promotion notifications sent for opportunity {opportunity_id}")
            
        except Exception as e:
            logger.error(f"Error sending promotion notification: {e}")
    
    async def notify_high_value_opportunity(
        self,
        opportunity_id: UUID,
        org_id: UUID,
        project_value: float
    ) -> None:
        """Send notification for high-value opportunities."""
        try:
            HIGH_VALUE_THRESHOLD = 1_000_000.0
            
            if project_value < HIGH_VALUE_THRESHOLD:
                return
            
            opportunity = await Opportunity.get_by_id(opportunity_id, org_id)
            if not opportunity:
                return
            
            # Get org admins for high-value notifications
            stmt = select(User).where(
                User.org_id == org_id,
                User.role.in_(["admin", "Admin"])
            )
            result = await self.db.execute(stmt)
            admins = result.scalars().all()
            
            title = f"High-Value Opportunity: {opportunity.project_name}"
            message = f"High-value opportunity detected: '{opportunity.project_name}' (${project_value:,.0f})"
            
            for admin in admins:
                if await self._should_send_in_app(admin.id, NotificationType.opportunity_high_value):
                    await self._create_notification(
                        org_id=org_id,
                        user_id=admin.id,
                        notification_type=NotificationType.opportunity_high_value,
                        title=title,
                        message=message,
                        priority=NotificationPriority.urgent,
                        related_entity_type="opportunity",
                        related_entity_id=opportunity_id,
                        notification_metadata={"project_value": project_value}
                    )
                
                if await self._should_send_email(admin.id, NotificationType.opportunity_high_value):
                    await self._send_email_notification(
                        admin.email, admin.name, title, message, opportunity_id
                    )
            
            logger.info(f"High-value notifications sent for opportunity {opportunity_id}")
            
        except Exception as e:
            logger.error(f"Error sending high-value notification: {e}")
    
    async def get_opportunity_notifications(
        self,
        user_id: UUID,
        org_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user related to opportunities."""
        try:
            stmt = select(Notification).where(
                Notification.user_id == user_id,
                Notification.org_id == org_id
            )
            
            if unread_only:
                stmt = stmt.where(Notification.is_read == False)
            
            stmt = stmt.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
            
            result = await self.db.execute(stmt)
            notifications = result.scalars().all()
            
            return [
                {
                    "id": str(n.id),
                    "type": n.type.value,
                    "priority": n.priority.value,
                    "title": n.title,
                    "message": n.message,
                    "is_read": n.is_read,
                    "read_at": n.read_at.isoformat() if n.read_at else None,
                    "created_at": n.created_at.isoformat(),
                    "related_entity_type": n.related_entity_type,
                    "related_entity_id": str(n.related_entity_id) if n.related_entity_id else None,
                    "metadata": n.notification_metadata or {}
                }
                for n in notifications
            ]
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    async def mark_notification_read(
        self,
        notification_id: UUID,
        user_id: UUID
    ) -> bool:
        """Mark a notification as read."""
        try:
            stmt = select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
            result = await self.db.execute(stmt)
            notification = result.scalar_one_or_none()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                await self.db.flush()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    async def mark_all_notifications_read(
        self,
        user_id: UUID,
        org_id: UUID
    ) -> int:
        """Mark all notifications as read for a user."""
        try:
            stmt = select(Notification).where(
                Notification.user_id == user_id,
                Notification.org_id == org_id,
                Notification.is_read == False
            )
            result = await self.db.execute(stmt)
            notifications = result.scalars().all()
            
            count = 0
            for notification in notifications:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                count += 1
            
            await self.db.flush()
            return count
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            return 0
    
    async def get_unread_count(
        self,
        user_id: UUID,
        org_id: UUID
    ) -> int:
        """Get count of unread notifications."""
        try:
            stmt = select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.org_id == org_id,
                Notification.is_read == False
            )
            result = await self.db.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0

