"""
Account Audit Trail Service
Tracks all changes to account records
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from fastapi import Request

from app.models.account_audit import AccountAuditLog
from app.models.account import Account
from app.utils.logger import logger

class AccountAuditService:
    """Service for tracking account changes"""
    
    @staticmethod
    async def log_account_change(
        db: AsyncSession,
        account_id: UUID,
        action: str,
        user_id: Optional[UUID],
        changes: Optional[Dict[str, Any]] = None,
        summary: Optional[str] = None,
        request: Optional[Request] = None
    ) -> AccountAuditLog:
        """
        Log a change to an account
        
        Args:
            db: Database session
            account_id: ID of the account being changed
            action: Action type ('create', 'update', 'delete', 'approve', 'decline')
            user_id: ID of user making the change
            changes: Dictionary of field changes {field: {old_value, new_value}}
            summary: Human-readable summary of the change
            request: FastAPI request object (for IP/UA)
        """
        try:
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent", None)
            
            audit_log = AccountAuditLog(
                account_id=account_id,
                action=action,
                user_id=user_id,
                changes=changes,
                summary=summary,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(audit_log)
            await db.flush()
            
            logger.info(f"Audit log created for account {account_id}: {action} by user {user_id}")
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            # Don't fail the main operation if audit logging fails
            raise
    
    @staticmethod
    async def get_account_audit_history(
        db: AsyncSession,
        account_id: UUID,
        limit: int = 50,
        action_filter: Optional[str] = None
    ) -> List[AccountAuditLog]:
        """
        Get audit history for an account
        
        Args:
            db: Database session
            account_id: ID of the account
            limit: Maximum number of records to return
            action_filter: Optional filter by action type
        """
        try:
            stmt = select(AccountAuditLog).where(
                AccountAuditLog.account_id == account_id
            )
            
            if action_filter:
                stmt = stmt.where(AccountAuditLog.action == action_filter)
            
            stmt = stmt.order_by(desc(AccountAuditLog.created_at)).limit(limit)
            
            result = await db.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error fetching audit history: {e}")
            return []
    
    @staticmethod
    def compute_field_changes(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute field-level changes between old and new account data
        
        Args:
            old_data: Previous account state
            new_data: New account state
            
        Returns:
            Dictionary of changes {field_name: {old_value, new_value}}
        """
        changes = {}
        
        # Fields to track
        tracked_fields = [
            'client_name', 'client_type', 'market_sector', 'company_website',
            'hosting_area', 'msa_in_place', 'account_approver', 'approval_status',
            'notes', 'total_value', 'ai_health_score', 'risk_level'
        ]
        
        for field in tracked_fields:
            old_value = old_data.get(field)
            new_value = new_data.get(field)
            
            # Handle nested fields (like client_address)
            if field == 'client_address' and isinstance(old_value, dict) and isinstance(new_value, dict):
                address_changes = {}
                address_fields = ['line1', 'line2', 'city', 'state', 'pincode']
                for addr_field in address_fields:
                    old_addr_val = old_value.get(addr_field)
                    new_addr_val = new_value.get(addr_field)
                    if old_addr_val != new_addr_val:
                        address_changes[addr_field] = {
                            'old_value': old_addr_val,
                            'new_value': new_addr_val
                        }
                if address_changes:
                    changes['client_address'] = address_changes
            elif old_value != new_value:
                changes[field] = {
                    'old_value': old_value,
                    'new_value': new_value
                }
        
        return changes
    
    @staticmethod
    def generate_summary(action: str, changes: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a human-readable summary of the change
        
        Args:
            action: Action type
            changes: Dictionary of field changes
        """
        if action == 'create':
            return "Account created"
        elif action == 'delete':
            return "Account deleted"
        elif action == 'approve':
            return "Account approved"
        elif action == 'decline':
            return "Account declined"
        elif action == 'update' and changes:
            changed_fields = list(changes.keys())
            if len(changed_fields) == 1:
                return f"Updated {changed_fields[0].replace('_', ' ')}"
            else:
                return f"Updated {len(changed_fields)} fields: {', '.join([f.replace('_', ' ') for f in changed_fields[:3]])}"
        else:
            return f"Account {action}"

account_audit_service = AccountAuditService()

