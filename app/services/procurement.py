from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
import os
import boto3
from botocore.exceptions import ClientError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.environment import environment

from app.models.procurement import (
    PurchaseRequisition,
    PurchaseOrder,
    RFQ,
    RFQResponse as RFQResponseModel,
    EmployeeExpense,
    VendorInvoice,
    GRN,
    DeliveryMilestone,
    RequisitionStatus,
    PurchaseOrderStatus,
    RFQStatus,
    ExpenseStatus,
    InvoiceStatus,
    MatchingStatus,
    GRNStatus,
    DeliveryMilestoneStatus,
)
from app.models.user import User
from app.schemas.procurement import (
    PurchaseRequisitionCreate,
    PurchaseRequisitionUpdate,
    PurchaseRequisitionResponse,
    PurchaseRequisitionListResponse,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
    PurchaseOrderResponse,
    PurchaseOrderListResponse,
    RFQCreate,
    RFQUpdate,
    RFQResponse as RFQResponseSchema,
    RFQListResponse,
    RFQResponseCreate as RFQResponseCreateSchema,
    RFQResponseResponse,
    EmployeeExpenseCreate,
    EmployeeExpenseUpdate,
    EmployeeExpenseResponse,
    EmployeeExpenseListResponse,
    VendorInvoiceCreate,
    VendorInvoiceUpdate,
    VendorInvoiceResponse,
    VendorInvoiceListResponse,
    GRNCreate,
    GRNUpdate,
    GRNResponse,
    GRNListResponse,
    DeliveryMilestoneCreate,
    DeliveryMilestoneUpdate,
    DeliveryMilestoneResponse,
    DeliveryMilestoneListResponse,
    RequisitionApprovalRequest,
    ExpenseApprovalRequest,
    ProcurementDashboardStats,
)
from app.utils.logger import get_logger
from app.services.file_extractor import FileExtractor
from app.services.gemini_service import gemini_service
import json
import re
from decimal import Decimal

logger = get_logger("procurement_service")

class ProcurementService:
    """Service for Procurement Management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user_name(self, user_id: UUID) -> Optional[str]:
        """Helper method to get user name by ID"""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                return user.name or user.email or None
            return None
        except Exception as e:
            logger.warning(f"Error fetching user name for {user_id}: {e}")
            return None

    # Purchase Requisition Methods
    async def create_requisition(
        self,
        requisition_data: PurchaseRequisitionCreate,
        user: User
    ) -> PurchaseRequisitionResponse:
        """Create a new purchase requisition"""
        try:
            if not user.org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must be associated with an organization"
                )

            from app.services.id_generator import IDGenerator
            custom_id = await IDGenerator.generate_requisition_id(str(user.org_id), self.db)

            requisition = PurchaseRequisition(
                custom_id=custom_id,
                org_id=user.org_id,
                requested_by=user.id,
                purchase_type=requisition_data.purchase_type,
                description=requisition_data.description,
                category=requisition_data.category,
                estimated_cost=requisition_data.estimated_cost,
                vendor=requisition_data.vendor,
                justification=requisition_data.justification,
                department=requisition_data.department,
                project_code=requisition_data.project_code,
                urgency=requisition_data.urgency,
                needed_by=requisition_data.needed_by,
                status=RequisitionStatus.DRAFT,
            )

            self.db.add(requisition)
            await self.db.flush()
            await self.db.refresh(requisition)

            logger.info(f"Created requisition {requisition.id}")
            return PurchaseRequisitionResponse.model_validate(requisition)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating requisition: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create requisition"
            )

    async def get_requisition(
        self,
        requisition_id: UUID,
        user: User
    ) -> Optional[PurchaseRequisitionResponse]:
        """Get requisition by ID"""
        try:
            result = await self.db.execute(
                select(PurchaseRequisition)
                .where(
                    and_(
                        PurchaseRequisition.id == requisition_id,
                        PurchaseRequisition.org_id == user.org_id
                    )
                )
            )
            requisition = result.scalar_one_or_none()
            if not requisition:
                return None
            
            # Get user name
            requested_by_name = await self._get_user_name(requisition.requested_by)
            
            response = PurchaseRequisitionResponse.model_validate(requisition)
            response.requested_by_name = requested_by_name
            return response
        except Exception as e:
            logger.error(f"Error getting requisition {requisition_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve requisition"
            )

    async def list_requisitions(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> PurchaseRequisitionListResponse:
        """List requisitions with pagination and filters"""
        try:
            offset = (page - 1) * size
            query = select(PurchaseRequisition).where(
                PurchaseRequisition.org_id == user.org_id
            )

            if status_filter:
                query = query.where(PurchaseRequisition.status == status_filter)

            if search:
                query = query.where(
                    or_(
                        PurchaseRequisition.description.ilike(f"%{search}%"),
                        PurchaseRequisition.custom_id.ilike(f"%{search}%")
                    )
                )

            query = query.order_by(desc(PurchaseRequisition.created_at))
            query = query.offset(offset).limit(size)

            result = await self.db.execute(query)
            requisitions = result.scalars().all()

            total_query = select(func.count(PurchaseRequisition.id)).where(
                PurchaseRequisition.org_id == user.org_id
            )
            if status_filter:
                total_query = total_query.where(PurchaseRequisition.status == status_filter)
            if search:
                total_query = total_query.where(
                    or_(
                        PurchaseRequisition.description.ilike(f"%{search}%"),
                        PurchaseRequisition.custom_id.ilike(f"%{search}%")
                    )
                )

            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0

            # Get user names for all requisitions
            requisition_responses = []
            for req in requisitions:
                requested_by_name = await self._get_user_name(req.requested_by)
                response = PurchaseRequisitionResponse.model_validate(req)
                response.requested_by_name = requested_by_name
                requisition_responses.append(response)

            return PurchaseRequisitionListResponse(
                requisitions=requisition_responses,
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if total > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error listing requisitions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list requisitions"
            )

    async def update_requisition(
        self,
        requisition_id: UUID,
        requisition_data: PurchaseRequisitionUpdate,
        user: User
    ) -> Optional[PurchaseRequisitionResponse]:
        """Update requisition"""
        try:
            result = await self.db.execute(
                select(PurchaseRequisition)
                .where(
                    and_(
                        PurchaseRequisition.id == requisition_id,
                        PurchaseRequisition.org_id == user.org_id
                    )
                )
            )
            requisition = result.scalar_one_or_none()
            if not requisition:
                return None

            update_data = requisition_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(requisition, key, value)

            requisition.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(requisition)

            return PurchaseRequisitionResponse.model_validate(requisition)
        except Exception as e:
            logger.error(f"Error updating requisition {requisition_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update requisition"
            )

    async def approve_requisition(
        self,
        requisition_id: UUID,
        approval_data: RequisitionApprovalRequest,
        user: User
    ) -> Optional[PurchaseRequisitionResponse]:
        """Approve or reject requisition"""
        try:
            result = await self.db.execute(
                select(PurchaseRequisition)
                .where(
                    and_(
                        PurchaseRequisition.id == requisition_id,
                        PurchaseRequisition.org_id == user.org_id
                    )
                )
            )
            requisition = result.scalar_one_or_none()
            if not requisition:
                return None

            requisition.status = approval_data.status
            requisition.updated_at = datetime.utcnow()

            if approval_data.status == RequisitionStatus.APPROVED:
                requisition.approved_by = user.id
                requisition.approved_at = datetime.utcnow()
            elif approval_data.status == RequisitionStatus.REJECTED:
                # requisition.rejection_reason = approval_data.rejection_reason  # Column doesn't exist in DB yet
                pass

            await self.db.flush()
            await self.db.refresh(requisition)

            return PurchaseRequisitionResponse.model_validate(requisition)
        except Exception as e:
            logger.error(f"Error approving requisition {requisition_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve requisition"
            )

    async def delete_requisition(
        self,
        requisition_id: UUID,
        user: User
    ) -> bool:
        """Delete requisition"""
        try:
            result = await self.db.execute(
                select(PurchaseRequisition)
                .where(
                    and_(
                        PurchaseRequisition.id == requisition_id,
                        PurchaseRequisition.org_id == user.org_id
                    )
                )
            )
            requisition = result.scalar_one_or_none()
            if not requisition:
                return False

            await self.db.delete(requisition)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting requisition {requisition_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete requisition"
            )

    # Purchase Order Methods
    async def create_purchase_order(
        self,
        order_data: PurchaseOrderCreate,
        user: User
    ) -> PurchaseOrderResponse:
        """Create a new purchase order"""
        try:
            if not user.org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must be associated with an organization"
                )

            from app.services.id_generator import IDGenerator
            custom_id = await IDGenerator.generate_po_id(str(user.org_id), self.db)

            order = PurchaseOrder(
                custom_id=custom_id,
                org_id=user.org_id,
                requisition_id=order_data.requisition_id,
                vendor_id=order_data.vendor_id,
                created_by=user.id,
                vendor_name=order_data.vendor_name,
                description=order_data.description,
                amount=order_data.amount,
                project_code=order_data.project_code,
                issue_date=order_data.issue_date,
                due_date=order_data.due_date,
                expected_delivery_date=order_data.expected_delivery_date,
                terms_and_conditions=order_data.terms_and_conditions,
                notes=order_data.notes,
                status=PurchaseOrderStatus.ISSUED,
            )

            self.db.add(order)
            await self.db.flush()
            await self.db.refresh(order)

            logger.info(f"Created purchase order {order.id}")
            return PurchaseOrderResponse.model_validate(order)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating purchase order: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create purchase order"
            )

    async def get_purchase_order(
        self,
        order_id: UUID,
        user: User
    ) -> Optional[PurchaseOrderResponse]:
        """Get purchase order by ID"""
        try:
            result = await self.db.execute(
                select(PurchaseOrder)
                .where(
                    and_(
                        PurchaseOrder.id == order_id,
                        PurchaseOrder.org_id == user.org_id
                    )
                )
            )
            order = result.scalar_one_or_none()
            if not order:
                return None
            
            # Get user name
            created_by_name = await self._get_user_name(order.created_by)
            
            response = PurchaseOrderResponse.model_validate(order)
            response.created_by_name = created_by_name
            return response
        except Exception as e:
            logger.error(f"Error getting purchase order {order_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve purchase order"
            )

    async def list_purchase_orders(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> PurchaseOrderListResponse:
        """List purchase orders with pagination and filters"""
        try:
            offset = (page - 1) * size
            query = select(PurchaseOrder).where(
                PurchaseOrder.org_id == user.org_id
            )

            if status_filter:
                query = query.where(PurchaseOrder.status == status_filter)

            if search:
                query = query.where(
                    or_(
                        PurchaseOrder.description.ilike(f"%{search}%"),
                        PurchaseOrder.custom_id.ilike(f"%{search}%"),
                        PurchaseOrder.vendor_name.ilike(f"%{search}%")
                    )
                )

            query = query.order_by(desc(PurchaseOrder.created_at))
            query = query.offset(offset).limit(size)

            result = await self.db.execute(query)
            orders = result.scalars().all()

            total_query = select(func.count(PurchaseOrder.id)).where(
                PurchaseOrder.org_id == user.org_id
            )
            if status_filter:
                total_query = total_query.where(PurchaseOrder.status == status_filter)
            if search:
                total_query = total_query.where(
                    or_(
                        PurchaseOrder.description.ilike(f"%{search}%"),
                        PurchaseOrder.custom_id.ilike(f"%{search}%"),
                        PurchaseOrder.vendor_name.ilike(f"%{search}%")
                    )
                )

            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0

            # Get user names for all orders
            order_responses = []
            for order in orders:
                created_by_name = await self._get_user_name(order.created_by)
                response = PurchaseOrderResponse.model_validate(order)
                response.created_by_name = created_by_name
                order_responses.append(response)

            return PurchaseOrderListResponse(
                orders=order_responses,
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if total > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error listing purchase orders: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list purchase orders"
            )

    async def update_purchase_order(
        self,
        order_id: UUID,
        order_data: PurchaseOrderUpdate,
        user: User
    ) -> Optional[PurchaseOrderResponse]:
        """Update purchase order"""
        try:
            result = await self.db.execute(
                select(PurchaseOrder)
                .where(
                    and_(
                        PurchaseOrder.id == order_id,
                        PurchaseOrder.org_id == user.org_id
                    )
                )
            )
            order = result.scalar_one_or_none()
            if not order:
                return None

            update_data = order_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(order, key, value)

            # If status is being set to cancelled, ensure rejection_reason is handled
            # Note: rejection_reason column doesn't exist in DB yet, so we skip setting it
            # if 'status' in update_data and update_data['status'] == PurchaseOrderStatus.CANCELLED:
            #     if 'rejection_reason' in update_data:
            #         order.rejection_reason = update_data['rejection_reason']

            order.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(order)

            return PurchaseOrderResponse.model_validate(order)
        except Exception as e:
            logger.error(f"Error updating purchase order {order_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update purchase order"
            )

    async def delete_purchase_order(
        self,
        order_id: UUID,
        user: User
    ) -> bool:
        """Delete purchase order"""
        try:
            result = await self.db.execute(
                select(PurchaseOrder)
                .where(
                    and_(
                        PurchaseOrder.id == order_id,
                        PurchaseOrder.org_id == user.org_id
                    )
                )
            )
            order = result.scalar_one_or_none()
            if not order:
                return False

            await self.db.delete(order)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting purchase order {order_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete purchase order"
            )

    # RFQ Methods
    async def create_rfq(
        self,
        rfq_data: RFQCreate,
        user: User
    ) -> RFQResponseSchema:
        """Create a new RFQ"""
        from sqlalchemy.exc import IntegrityError
        
        if not user.org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be associated with an organization"
            )

        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                from app.services.id_generator import IDGenerator
                custom_id = await IDGenerator.generate_rfq_id(str(user.org_id), self.db)

                rfq = RFQ(
                    custom_id=custom_id,
                    org_id=user.org_id,
                    requisition_id=rfq_data.requisition_id,
                    created_by=user.id,
                    title=rfq_data.title,
                    description=rfq_data.description,
                    category=rfq_data.category,
                    estimated_value=rfq_data.estimated_value,
                    due_date=rfq_data.due_date,
                    status=RFQStatus.DRAFT,
                    vendors_invited=0,
                    responses_received=0,
                )

                self.db.add(rfq)
                await self.db.flush()
                await self.db.refresh(rfq)

                logger.info(f"Created RFQ {rfq.id}")
                return RFQResponseSchema.model_validate(rfq)

            except IntegrityError as ie:
                # Check if it's a unique constraint violation on custom_id
                if 'custom_id' in str(ie.orig) or 'ix_rfqs_custom_id' in str(ie.orig):
                    # Rollback the failed attempt
                    await self.db.rollback()
                    # Try again with a new ID
                    if attempt < max_attempts - 1:
                        logger.warning(f"Duplicate RFQ custom_id detected, retrying... (attempt {attempt + 1}/{max_attempts})")
                        continue
                    else:
                        # Last attempt failed, use timestamp-based ID
                        import time
                        from app.models.organization import Organization
                        org_stmt = select(Organization).where(Organization.id == user.org_id)
                        org_result = await self.db.execute(org_stmt)
                        organization = org_result.scalar_one_or_none()
                        org_prefix = "ORG"
                        if organization:
                            org_name = organization.name or "ORG"
                            org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
                        custom_id = f"RFQ-{org_prefix}{int(time.time())}"
                        
                        rfq = RFQ(
                            custom_id=custom_id,
                            org_id=user.org_id,
                            requisition_id=rfq_data.requisition_id,
                            created_by=user.id,
                            title=rfq_data.title,
                            description=rfq_data.description,
                            category=rfq_data.category,
                            estimated_value=rfq_data.estimated_value,
                            due_date=rfq_data.due_date,
                            status=RFQStatus.DRAFT,
                            vendors_invited=0,
                            responses_received=0,
                        )
                        
                        self.db.add(rfq)
                        await self.db.flush()
                        await self.db.refresh(rfq)
                        
                        logger.info(f"Created RFQ {rfq.id} with timestamp-based ID")
                        return RFQResponseSchema.model_validate(rfq)
                else:
                    # Other integrity errors, re-raise
                    await self.db.rollback()
                    raise
            except HTTPException:
                raise
            except Exception as e:
                await self.db.rollback()
                logger.error(f"Error creating RFQ: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create RFQ"
                )
        
        # Should never reach here, but just in case
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create RFQ after multiple attempts"
        )

    async def get_rfq(
        self,
        rfq_id: UUID,
        user: User
    ) -> Optional[RFQResponseSchema]:
        """Get RFQ by ID"""
        try:
            result = await self.db.execute(
                select(RFQ)
                .where(
                    and_(
                        RFQ.id == rfq_id,
                        RFQ.org_id == user.org_id
                    )
                )
            )
            rfq = result.scalar_one_or_none()
            if not rfq:
                return None
            
            # Get user name
            created_by_name = await self._get_user_name(rfq.created_by)
            
            response = RFQResponseSchema.model_validate(rfq)
            response.created_by_name = created_by_name
            return response
        except Exception as e:
            logger.error(f"Error getting RFQ {rfq_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve RFQ"
            )

    async def list_rfqs(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> RFQListResponse:
        """List RFQs with pagination and filters"""
        try:
            offset = (page - 1) * size
            query = select(RFQ).where(RFQ.org_id == user.org_id)

            if status_filter:
                query = query.where(RFQ.status == status_filter)

            if search:
                query = query.where(
                    or_(
                        RFQ.title.ilike(f"%{search}%"),
                        RFQ.custom_id.ilike(f"%{search}%")
                    )
                )

            query = query.order_by(desc(RFQ.created_at))
            query = query.offset(offset).limit(size)

            result = await self.db.execute(query)
            rfqs = result.scalars().all()

            total_query = select(func.count(RFQ.id)).where(RFQ.org_id == user.org_id)
            if status_filter:
                total_query = total_query.where(RFQ.status == status_filter)
            if search:
                total_query = total_query.where(
                    or_(
                        RFQ.title.ilike(f"%{search}%"),
                        RFQ.custom_id.ilike(f"%{search}%")
                    )
                )

            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0

            # Get user names for all RFQs
            rfq_responses = []
            for rfq in rfqs:
                created_by_name = await self._get_user_name(rfq.created_by)
                response = RFQResponseSchema.model_validate(rfq)
                response.created_by_name = created_by_name
                rfq_responses.append(response)

            return RFQListResponse(
                rfqs=rfq_responses,
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if total > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error listing RFQs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list RFQs"
            )

    async def update_rfq(
        self,
        rfq_id: UUID,
        rfq_data: RFQUpdate,
        user: User
    ) -> Optional[RFQResponseSchema]:
        """Update RFQ"""
        try:
            result = await self.db.execute(
                select(RFQ)
                .where(
                    and_(
                        RFQ.id == rfq_id,
                        RFQ.org_id == user.org_id
                    )
                )
            )
            rfq = result.scalar_one_or_none()
            if not rfq:
                return None

            update_data = rfq_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(rfq, key, value)

            rfq.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(rfq)

            return RFQResponseSchema.model_validate(rfq)
        except Exception as e:
            logger.error(f"Error updating RFQ {rfq_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update RFQ"
            )

    async def delete_rfq(
        self,
        rfq_id: UUID,
        user: User
    ) -> bool:
        """Delete RFQ"""
        try:
            result = await self.db.execute(
                select(RFQ)
                .where(
                    and_(
                        RFQ.id == rfq_id,
                        RFQ.org_id == user.org_id
                    )
                )
            )
            rfq = result.scalar_one_or_none()
            if not rfq:
                return False

            await self.db.delete(rfq)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting RFQ {rfq_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete RFQ"
            )

    # RFQ Response Methods
    async def create_rfq_response(
        self,
        response_data: RFQResponseCreateSchema,
        user: User
    ) -> RFQResponseResponse:
        """Create an RFQ response from a vendor"""
        try:
            rfq_result = await self.db.execute(
                select(RFQ).where(RFQ.id == response_data.rfq_id)
            )
            rfq = rfq_result.scalar_one_or_none()
            if not rfq:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="RFQ not found"
                )

            response = RFQResponseModel(
                rfq_id=response_data.rfq_id,
                vendor_id=response_data.vendor_id,
                quoted_amount=response_data.quoted_amount,
                delivery_time=response_data.delivery_time,
                terms=response_data.terms,
                status="submitted",
            )

            self.db.add(response)
            await self.db.flush()

            rfq.responses_received = (rfq.responses_received or 0) + 1
            if rfq.status == RFQStatus.DRAFT:
                rfq.status = RFQStatus.RESPONSES_RECEIVED
            await self.db.flush()
            await self.db.refresh(response)

            logger.info(f"Created RFQ response {response.id}")
            return RFQResponseResponse.model_validate(response)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating RFQ response: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create RFQ response"
            )

    async def list_rfq_responses(
        self,
        rfq_id: UUID,
        user: User
    ) -> List[RFQResponseResponse]:
        """List responses for an RFQ"""
        try:
            result = await self.db.execute(
                select(RFQResponseModel).where(RFQResponseModel.rfq_id == rfq_id)
            )
            responses = result.scalars().all()
            return [RFQResponseResponse.model_validate(r) for r in responses]
        except Exception as e:
            logger.error(f"Error listing RFQ responses: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list RFQ responses"
            )

    # Employee Expense Methods
    async def create_expense(
        self,
        expense_data: EmployeeExpenseCreate,
        user: User
    ) -> EmployeeExpenseResponse:
        """Create a new employee expense"""
        try:
            if not user.org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must be associated with an organization"
                )

            from app.services.id_generator import IDGenerator
            from sqlalchemy.exc import IntegrityError
            
            # Retry logic to handle race conditions in ID generation
            max_attempts = 10
            expense = None
            
            for attempt in range(max_attempts):
                try:
                    custom_id = await IDGenerator.generate_expense_id(str(user.org_id), self.db)
                    
                    # Check if this ID already exists
                    existing_check = await self.db.execute(
                        select(EmployeeExpense).where(EmployeeExpense.custom_id == custom_id)
                    )
                    if existing_check.scalar_one_or_none():
                        # ID exists, generate a new one with timestamp fallback
                        import time
                        from app.models.organization import Organization
                        org_stmt = select(Organization).where(Organization.id == user.org_id)
                        org_result = await self.db.execute(org_stmt)
                        organization = org_result.scalar_one_or_none()
                        org_prefix = "ORG"
                        if organization:
                            org_name = organization.name or "ORG"
                            org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
                        custom_id = f"EXP-{org_prefix}{int(time.time())}"
                    
                    expense = EmployeeExpense(
                        custom_id=custom_id,
                        org_id=user.org_id,
                        employee_id=user.id,
                        expense_date=expense_data.expense_date,
                        amount=expense_data.amount,
                        category=expense_data.category,
                        description=expense_data.description,
                        project_code=expense_data.project_code,
                        receipt_url=expense_data.receipt_url,
                        receipt_uploaded=bool(expense_data.receipt_url),
                        status=ExpenseStatus.DRAFT,
                    )

                    self.db.add(expense)
                    await self.db.flush()
                    await self.db.refresh(expense)
                    
                    # Success - break out of retry loop
                    break
                    
                except IntegrityError as ie:
                    # Check if it's a unique constraint violation on custom_id
                    if 'custom_id' in str(ie.orig) or 'ix_employee_expenses_custom_id' in str(ie.orig):
                        # Rollback the failed attempt
                        await self.db.rollback()
                        # Try again with a new ID
                        if attempt < max_attempts - 1:
                            logger.warning(f"Duplicate custom_id detected, retrying... (attempt {attempt + 1}/{max_attempts})")
                            continue
                        else:
                            # Last attempt failed, use timestamp-based ID
                            import time
                            from app.models.organization import Organization
                            org_stmt = select(Organization).where(Organization.id == user.org_id)
                            org_result = await self.db.execute(org_stmt)
                            organization = org_result.scalar_one_or_none()
                            org_prefix = "ORG"
                            if organization:
                                org_name = organization.name or "ORG"
                                org_prefix = org_name[:2].upper() if len(org_name) >= 2 else "OR"
                            custom_id = f"EXP-{org_prefix}{int(time.time())}"
                            
                            expense = EmployeeExpense(
                                custom_id=custom_id,
                                org_id=user.org_id,
                                employee_id=user.id,
                                expense_date=expense_data.expense_date,
                                amount=expense_data.amount,
                                category=expense_data.category,
                                description=expense_data.description,
                                project_code=expense_data.project_code,
                                receipt_url=expense_data.receipt_url,
                                receipt_uploaded=bool(expense_data.receipt_url),
                                status=ExpenseStatus.DRAFT,
                            )
                            self.db.add(expense)
                            await self.db.flush()
                            await self.db.refresh(expense)
                            break
                    else:
                        # Different integrity error, re-raise
                        raise
                except Exception as e:
                    # Other errors, re-raise
                    await self.db.rollback()
                    raise

            if not expense:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate unique expense ID after multiple attempts"
                )

            logger.info(f"Created expense {expense.id} with custom_id {expense.custom_id}")
            return EmployeeExpenseResponse.model_validate(expense)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating expense: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create expense"
            )

    async def upload_expense_receipt(
        self,
        file_content: bytes,
        file_name: str,
        file_type: str,
        user_id: UUID,
        org_id: Optional[UUID]
    ) -> str:
        """Upload expense receipt file to S3 or local storage and return URL"""
        try:
            # Initialize S3 client if credentials are available
            s3_enabled = all([
                environment.AWS_ACCESS_KEY_ID,
                environment.AWS_SECRET_ACCESS_KEY,
                environment.AWS_S3_BUCKET_NAME
            ])
            
            file_extension = file_name.split('.')[-1] if '.' in file_name else 'jpg'
            timestamp = int(datetime.utcnow().timestamp())
            s3_key = f"expense-receipts/{org_id}/{user_id}/{timestamp}.{file_extension}"
            
            if s3_enabled:
                try:
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=environment.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=environment.AWS_SECRET_ACCESS_KEY,
                        region_name=environment.AWS_S3_REGION or "us-east-1"
                    )
                    s3_client.put_object(
                        Bucket=environment.AWS_S3_BUCKET_NAME,
                        Key=s3_key,
                        Body=file_content,
                        ContentType=file_type
                    )
                    region_segment = f".{environment.AWS_S3_REGION}" if environment.AWS_S3_REGION else ""
                    file_url = f"https://{environment.AWS_S3_BUCKET_NAME}.s3{region_segment}.amazonaws.com/{s3_key}"
                    logger.info(f"Receipt uploaded to S3: {s3_key}")
                    return file_url
                except ClientError as e:
                    logger.error(f"S3 upload failed: {e}")
                    # Fallback to local storage
                    pass
            
            # Local storage fallback
            upload_root = os.path.join("uploads", "expense_receipts")
            os.makedirs(upload_root, exist_ok=True)
            if org_id:
                org_dir = os.path.join(upload_root, str(org_id))
                os.makedirs(org_dir, exist_ok=True)
                user_dir = os.path.join(org_dir, str(user_id))
                os.makedirs(user_dir, exist_ok=True)
                local_path = os.path.join(user_dir, f"{timestamp}.{file_extension}")
            else:
                local_path = os.path.join(upload_root, f"{timestamp}.{file_extension}")
            
            with open(local_path, "wb") as f:
                f.write(file_content)
            
            file_url = f"/local/expense-receipts/{org_id}/{user_id}/{timestamp}.{file_extension}" if org_id else f"/local/expense-receipts/{timestamp}.{file_extension}"
            logger.info(f"Receipt stored locally at: {local_path}")
            return file_url
            
        except Exception as e:
            logger.error(f"Error uploading expense receipt: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload receipt: {str(e)}"
            )

    async def get_expense(
        self,
        expense_id: UUID,
        user: User
    ) -> Optional[EmployeeExpenseResponse]:
        """Get expense by ID"""
        try:
            result = await self.db.execute(
                select(EmployeeExpense)
                .where(
                    and_(
                        EmployeeExpense.id == expense_id,
                        EmployeeExpense.org_id == user.org_id
                    )
                )
            )
            expense = result.scalar_one_or_none()
            if not expense:
                return None
            
            # Get user name
            employee_name = await self._get_user_name(expense.employee_id)
            
            response = EmployeeExpenseResponse.model_validate(expense)
            response.employee_name = employee_name
            return response
        except Exception as e:
            logger.error(f"Error getting expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve expense"
            )

    async def list_expenses(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> EmployeeExpenseListResponse:
        """List expenses with pagination and filters"""
        try:
            offset = (page - 1) * size
            query = select(EmployeeExpense).where(
                EmployeeExpense.org_id == user.org_id
            )

            if status_filter:
                query = query.where(EmployeeExpense.status == status_filter)

            if search:
                query = query.where(
                    or_(
                        EmployeeExpense.description.ilike(f"%{search}%"),
                        EmployeeExpense.custom_id.ilike(f"%{search}%")
                    )
                )

            query = query.order_by(desc(EmployeeExpense.created_at))
            query = query.offset(offset).limit(size)

            result = await self.db.execute(query)
            expenses = result.scalars().all()

            total_query = select(func.count(EmployeeExpense.id)).where(
                EmployeeExpense.org_id == user.org_id
            )
            if status_filter:
                total_query = total_query.where(EmployeeExpense.status == status_filter)
            if search:
                total_query = total_query.where(
                    or_(
                        EmployeeExpense.description.ilike(f"%{search}%"),
                        EmployeeExpense.custom_id.ilike(f"%{search}%")
                    )
                )

            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0

            # Get user names for all expenses
            expense_responses = []
            for expense in expenses:
                employee_name = await self._get_user_name(expense.employee_id)
                response = EmployeeExpenseResponse.model_validate(expense)
                response.employee_name = employee_name
                expense_responses.append(response)

            return EmployeeExpenseListResponse(
                expenses=expense_responses,
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if total > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error listing expenses: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list expenses"
            )

    async def update_expense(
        self,
        expense_id: UUID,
        expense_data: EmployeeExpenseUpdate,
        user: User
    ) -> Optional[EmployeeExpenseResponse]:
        """Update employee expense"""
        try:
            result = await self.db.execute(
                select(EmployeeExpense)
                .where(
                    and_(
                        EmployeeExpense.id == expense_id,
                        EmployeeExpense.org_id == user.org_id
                    )
                )
            )
            expense = result.scalar_one_or_none()
            if not expense:
                return None

            update_data = expense_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(expense, key, value)

            expense.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(expense)

            return EmployeeExpenseResponse.model_validate(expense)
        except Exception as e:
            logger.error(f"Error updating expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update expense"
            )

    async def approve_expense(
        self,
        expense_id: UUID,
        approval_data: ExpenseApprovalRequest,
        user: User
    ) -> Optional[EmployeeExpenseResponse]:
        """Approve or reject expense"""
        try:
            result = await self.db.execute(
                select(EmployeeExpense)
                .where(
                    and_(
                        EmployeeExpense.id == expense_id,
                        EmployeeExpense.org_id == user.org_id
                    )
                )
            )
            expense = result.scalar_one_or_none()
            if not expense:
                return None

            expense.status = approval_data.status
            expense.updated_at = datetime.utcnow()

            if approval_data.status == ExpenseStatus.APPROVED:
                expense.approved_by = user.id
                expense.approved_at = datetime.utcnow()
            elif approval_data.status == ExpenseStatus.REJECTED:
                expense.rejected_reason = approval_data.rejection_reason

            await self.db.flush()
            await self.db.refresh(expense)

            return EmployeeExpenseResponse.model_validate(expense)
        except Exception as e:
            logger.error(f"Error approving expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve expense"
            )

    async def delete_expense(
        self,
        expense_id: UUID,
        user: User
    ) -> bool:
        """Delete employee expense"""
        try:
            result = await self.db.execute(
                select(EmployeeExpense)
                .where(
                    and_(
                        EmployeeExpense.id == expense_id,
                        EmployeeExpense.org_id == user.org_id
                    )
                )
            )
            expense = result.scalar_one_or_none()
            if not expense:
                return False

            await self.db.delete(expense)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting expense {expense_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete expense"
            )

    # Vendor Invoice Methods
    async def create_invoice(
        self,
        invoice_data: VendorInvoiceCreate,
        user: User
    ) -> VendorInvoiceResponse:
        """Create a new vendor invoice"""
        try:
            if not user.org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must be associated with an organization"
                )

            invoice = VendorInvoice(
                org_id=user.org_id,
                po_id=invoice_data.po_id,
                vendor_id=invoice_data.vendor_id,
                invoice_number=invoice_data.invoice_number,
                vendor_name=invoice_data.vendor_name,
                amount=invoice_data.amount,
                invoice_date=invoice_data.invoice_date,
                due_date=invoice_data.due_date,
                invoice_file_url=invoice_data.invoice_file_url,
                status=InvoiceStatus.PENDING,
                matching_status=MatchingStatus.NO_MATCH,
                fraud_detected=False,
            )

            if invoice_data.po_id:
                po_result = await self.db.execute(
                    select(PurchaseOrder).where(PurchaseOrder.id == invoice_data.po_id)
                )
                po = po_result.scalar_one_or_none()
                if po:
                    invoice.po_amount = po.amount
                    if invoice.amount == po.amount:
                        invoice.matching_status = MatchingStatus.PERFECT_MATCH
                        invoice.status = InvoiceStatus.MATCHED
                    else:
                        invoice.matching_status = MatchingStatus.PARTIAL_MATCH
                        invoice.variance = invoice.amount - po.amount

            self.db.add(invoice)
            await self.db.flush()
            await self.db.refresh(invoice)

            logger.info(f"Created invoice {invoice.id}")
            return VendorInvoiceResponse.model_validate(invoice)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create invoice"
            )

    async def get_invoice(
        self,
        invoice_id: UUID,
        user: User
    ) -> Optional[VendorInvoiceResponse]:
        """Get invoice by ID"""
        try:
            result = await self.db.execute(
                select(VendorInvoice)
                .where(
                    and_(
                        VendorInvoice.id == invoice_id,
                        VendorInvoice.org_id == user.org_id
                    )
                )
            )
            invoice = result.scalar_one_or_none()
            if not invoice:
                return None
            return VendorInvoiceResponse.model_validate(invoice)
        except Exception as e:
            logger.error(f"Error getting invoice {invoice_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve invoice"
            )

    async def list_invoices(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> VendorInvoiceListResponse:
        """List invoices with pagination and filters"""
        try:
            offset = (page - 1) * size
            query = select(VendorInvoice).where(
                VendorInvoice.org_id == user.org_id
            )

            if status_filter:
                query = query.where(VendorInvoice.status == status_filter)

            if search:
                query = query.where(
                    or_(
                        VendorInvoice.invoice_number.ilike(f"%{search}%"),
                        VendorInvoice.vendor_name.ilike(f"%{search}%")
                    )
                )

            query = query.order_by(desc(VendorInvoice.created_at))
            query = query.offset(offset).limit(size)

            result = await self.db.execute(query)
            invoices = result.scalars().all()

            total_query = select(func.count(VendorInvoice.id)).where(
                VendorInvoice.org_id == user.org_id
            )
            if status_filter:
                total_query = total_query.where(VendorInvoice.status == status_filter)
            if search:
                total_query = total_query.where(
                    or_(
                        VendorInvoice.invoice_number.ilike(f"%{search}%"),
                        VendorInvoice.vendor_name.ilike(f"%{search}%")
                    )
                )

            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0

            return VendorInvoiceListResponse(
                invoices=[VendorInvoiceResponse.model_validate(i) for i in invoices],
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if total > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error listing invoices: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list invoices"
            )

    async def update_invoice(
        self,
        invoice_id: UUID,
        invoice_data: VendorInvoiceUpdate,
        user: User
    ) -> Optional[VendorInvoiceResponse]:
        """Update vendor invoice"""
        try:
            result = await self.db.execute(
                select(VendorInvoice)
                .where(
                    and_(
                        VendorInvoice.id == invoice_id,
                        VendorInvoice.org_id == user.org_id
                    )
                )
            )
            invoice = result.scalar_one_or_none()
            if not invoice:
                return None

            update_data = invoice_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(invoice, key, value)

            invoice.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(invoice)

            return VendorInvoiceResponse.model_validate(invoice)
        except Exception as e:
            logger.error(f"Error updating invoice {invoice_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update invoice"
            )

    async def delete_invoice(
        self,
        invoice_id: UUID,
        user: User
    ) -> bool:
        """Delete vendor invoice"""
        try:
            result = await self.db.execute(
                select(VendorInvoice)
                .where(
                    and_(
                        VendorInvoice.id == invoice_id,
                        VendorInvoice.org_id == user.org_id
                    )
                )
            )
            invoice = result.scalar_one_or_none()
            if not invoice:
                return False

            await self.db.delete(invoice)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting invoice {invoice_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete invoice"
            )

    async def extract_invoice_data(
        self,
        file_content: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """Extract invoice data from uploaded file using AI"""
        try:
            # Extract text from file
            text = FileExtractor.extract_text_from_file(file_content, filename)
            if not text or len(text.strip()) < 10:
                logger.warning(f"Could not extract text from {filename} or text too short")
                return {
                    "invoice_number": None,
                    "po_number": None,
                    "vendor_name": None,
                    "amount": None,
                    "invoice_date": None,
                    "due_date": None,
                    "confidence": 0.0,
                    "extracted_fields": {},
                    "error": "Could not extract text from file. File may be corrupted or image-based PDF."
                }

            # Clean text for AI processing
            cleaned_text = FileExtractor.clean_text(text, max_length=10000)
            
            # Always try pattern-based extraction first as fallback
            pattern_result = self._extract_invoice_patterns(text)
            
            # Use Gemini AI to extract invoice data if available
            if gemini_service.enabled:
                try:
                    prompt = f"""
Analyze this invoice document and extract key information. Return ONLY a valid JSON object.

Invoice Text:
{cleaned_text}

Extract and return ONLY a valid JSON object with this exact structure:
{{
  "invoice_number": "Invoice number or ID (e.g., INV-2024-001)",
  "po_number": "Purchase Order number if mentioned (e.g., PO-2024-001)",
  "vendor_name": "Vendor/Supplier company name",
  "amount": 1234.56,
  "invoice_date": "YYYY-MM-DD format",
  "due_date": "YYYY-MM-DD format"
}}

Rules:
- Extract invoice number from fields like "Invoice #", "Invoice Number", "INV-", etc.
- Extract PO number from fields like "PO #", "Purchase Order", "PO-", etc.
- Extract vendor name from "From:", "Vendor:", "Supplier:", "Bill From:", etc.
- Extract amount as a number (total amount, not subtotal)
- Extract dates in YYYY-MM-DD format
- If any field is not found, use null
- Return ONLY the JSON object, no explanation or markdown
"""

                    response = gemini_service.model.generate_content(prompt)
                    response_text = response.text.strip()
                    
                    # Clean response
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                    data = json.loads(response_text)
                    
                    # Calculate confidence based on extracted fields
                    confidence = 0.0
                    if data.get("invoice_number"):
                        confidence += 0.3
                    if data.get("vendor_name"):
                        confidence += 0.3
                    if data.get("amount"):
                        confidence += 0.2
                    if data.get("invoice_date"):
                        confidence += 0.1
                    if data.get("po_number"):
                        confidence += 0.1
                    
                    # Merge AI results with pattern results (AI takes precedence)
                    result = {
                        "invoice_number": data.get("invoice_number") or pattern_result.get("invoice_number"),
                        "po_number": data.get("po_number") or pattern_result.get("po_number"),
                        "vendor_name": data.get("vendor_name") or pattern_result.get("vendor_name"),
                        "amount": Decimal(str(data.get("amount", 0))) if data.get("amount") else pattern_result.get("amount"),
                        "invoice_date": data.get("invoice_date") or pattern_result.get("invoice_date"),
                        "due_date": data.get("due_date") or pattern_result.get("due_date"),
                        "confidence": min(confidence, 1.0),
                        "extracted_fields": data
                    }
                    
                    logger.info(f"Successfully extracted invoice data with confidence {result['confidence']:.2f}")
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse AI response as JSON: {e}. Using pattern-based extraction.")
                    # Use pattern-based results
                    pattern_result["error"] = "AI extraction failed, using pattern matching"
                    return pattern_result
                except Exception as e:
                    logger.warning(f"AI extraction error: {e}. Using pattern-based extraction.")
                    # Use pattern-based results
                    pattern_result["error"] = f"AI extraction unavailable: {str(e)}"
                    return pattern_result
            else:
                # AI not enabled, use pattern-based extraction
                logger.info("Gemini AI not enabled, using pattern-based extraction")
                pattern_result["error"] = "AI extraction not configured. Using pattern matching."
                return pattern_result
                
        except Exception as e:
            logger.error(f"Error extracting invoice data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "invoice_number": None,
                "po_number": None,
                "vendor_name": None,
                "amount": None,
                "invoice_date": None,
                "due_date": None,
                "confidence": 0.0,
                "extracted_fields": {},
                "error": f"Extraction failed: {str(e)}"
            }

    def _extract_invoice_patterns(self, text: str) -> Dict[str, Any]:
        """Fallback pattern-based extraction"""
        extracted = {
            "invoice_number": None,
            "po_number": None,
            "vendor_name": None,
            "amount": None,
            "invoice_date": None,
            "due_date": None,
            "confidence": 0.0,
            "extracted_fields": {}
        }
        
        # Extract invoice number
        invoice_patterns = [
            r'invoice\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'inv[\.\s]*#?\s*:?\s*([A-Z0-9\-]+)',
            r'invoice\s+number\s*:?\s*([A-Z0-9\-]+)',
            r'invoice\s+no\.?\s*:?\s*([A-Z0-9\-]+)',
            r'inv[\.\s]*no\.?\s*:?\s*([A-Z0-9\-]+)',
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted["invoice_number"] = match.group(1).strip()
                extracted["confidence"] += 0.2
                break
        
        # Extract PO number
        po_patterns = [
            r'p\.?o\.?\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'purchase\s+order\s*:?\s*([A-Z0-9\-]+)',
            r'po\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'p\.?o\.?\s+no\.?\s*:?\s*([A-Z0-9\-]+)',
        ]
        for pattern in po_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted["po_number"] = match.group(1).strip()
                extracted["confidence"] += 0.1
                break
        
        # Extract vendor name (from common patterns)
        vendor_patterns = [
            r'(?:from|vendor|supplier|bill\s+from|sold\s+to)[\s:]+([A-Z][A-Za-z\s&,\.]+?)(?:\n|$)',
            r'company\s+name[\s:]+([A-Z][A-Za-z\s&,\.]+?)(?:\n|$)',
        ]
        for pattern in vendor_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                vendor_name = match.group(1).strip()
                if len(vendor_name) > 2 and len(vendor_name) < 100:
                    extracted["vendor_name"] = vendor_name
                    extracted["confidence"] += 0.2
                    break
        
        # Extract amount
        amount_patterns = [
            r'total\s*:?\s*\$?\s*([\d,]+\.?\d*)',
            r'amount\s+due\s*:?\s*\$?\s*([\d,]+\.?\d*)',
            r'grand\s+total\s*:?\s*\$?\s*([\d,]+\.?\d*)',
            r'total\s+amount\s*:?\s*\$?\s*([\d,]+\.?\d*)',
            r'balance\s+due\s*:?\s*\$?\s*([\d,]+\.?\d*)',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    extracted["amount"] = Decimal(amount_str)
                    extracted["confidence"] += 0.2
                    break
                except:
                    pass
        
        # Extract dates
        date_patterns = [
            r'invoice\s+date[\s:]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'date[\s:]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'due\s+date[\s:]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Try to parse and format as YYYY-MM-DD
                try:
                    from datetime import datetime
                    # Try different date formats
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            if 'due' in pattern.lower():
                                extracted["due_date"] = dt.strftime('%Y-%m-%d')
                            else:
                                extracted["invoice_date"] = dt.strftime('%Y-%m-%d')
                            extracted["confidence"] += 0.05
                            break
                        except:
                            continue
                except:
                    pass
        
        return extracted

    async def extract_receipt_data(
        self,
        file_content: bytes,
        filename: str
    ) -> Dict[str, Any]:
        """Extract receipt data from uploaded file using AI OCR"""
        try:
            # Extract text from file
            text = FileExtractor.extract_text_from_file(file_content, filename)
            if not text or len(text.strip()) < 10:
                logger.warning(f"Could not extract text from {filename} or text too short")
                return {
                    "amount": None,
                    "date": None,
                    "vendor": None,
                    "category": None,
                    "description": None,
                    "confidence": 0.0,
                    "extracted_fields": {},
                    "error": "Could not extract text from file. File may be corrupted or image-based PDF."
                }

            # Clean text for AI processing
            cleaned_text = FileExtractor.clean_text(text, max_length=10000)
            
            # Always try pattern-based extraction first as fallback
            pattern_result = self._extract_receipt_patterns(text)
            
            # Use Gemini AI to extract receipt data if available
            if gemini_service.enabled:
                try:
                    prompt = f"""
Analyze this receipt document and extract key information. Return ONLY a valid JSON object.

Receipt Text:
{cleaned_text}

Extract and return ONLY a valid JSON object with this exact structure:
{{
  "amount": 1234.56,
  "date": "YYYY-MM-DD format",
  "vendor": "Vendor/Store name",
  "category": "Category (e.g., Travel, Office Supplies, Meals, etc.)",
  "description": "Brief description of purchase"
}}

Rules:
- Extract total amount as a number (look for "Total", "Amount", "Sum", etc.)
- Extract date in YYYY-MM-DD format (look for "Date", "Purchase Date", etc.)
- Extract vendor/store name from header or "From:", "Merchant:", etc.
- Suggest category based on vendor name or items purchased
- Extract description from item list or summary
- If any field is not found, use null
- Return ONLY the JSON object, no explanation or markdown
"""

                    response = gemini_service.model.generate_content(prompt)
                    response_text = response.text.strip()
                    
                    # Clean response
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                    data = json.loads(response_text)
                    
                    # Calculate confidence based on extracted fields
                    confidence = 0.0
                    if data.get("amount"):
                        confidence += 0.4
                    if data.get("date"):
                        confidence += 0.2
                    if data.get("vendor"):
                        confidence += 0.2
                    if data.get("category"):
                        confidence += 0.1
                    if data.get("description"):
                        confidence += 0.1
                    
                    # Merge AI results with pattern results (AI takes precedence)
                    result = {
                        "amount": Decimal(str(data.get("amount", 0))) if data.get("amount") else pattern_result.get("amount"),
                        "date": data.get("date") or pattern_result.get("date"),
                        "vendor": data.get("vendor") or pattern_result.get("vendor"),
                        "category": data.get("category") or pattern_result.get("category"),
                        "description": data.get("description") or pattern_result.get("description"),
                        "confidence": min(confidence, 1.0),
                        "extracted_fields": data
                    }
                    
                    logger.info(f"Successfully extracted receipt data with confidence {result['confidence']:.2f}")
                    return result
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse AI response as JSON: {e}. Using pattern-based extraction.")
                    # Use pattern-based results
                    return {
                        **pattern_result,
                        "confidence": 0.5,
                        "extracted_fields": {}
                    }
                except Exception as e:
                    logger.warning(f"AI extraction failed: {e}. Using pattern-based extraction.")
                    # Use pattern-based results
                    return {
                        **pattern_result,
                        "confidence": 0.5,
                        "extracted_fields": {}
                    }
            else:
                # No AI service, use pattern-based extraction only
                return {
                    **pattern_result,
                    "confidence": 0.4,
                    "extracted_fields": {}
                }
                
        except Exception as e:
            logger.error(f"Error extracting receipt data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract receipt data"
            )

    def _extract_receipt_patterns(self, text: str) -> Dict[str, Any]:
        """Extract receipt data using pattern matching"""
        import re
        from decimal import Decimal
        
        result = {
            "amount": None,
            "date": None,
            "vendor": None,
            "category": None,
            "description": None
        }
        
        # Extract amount - look for "Total", "Amount", etc.
        amount_patterns = [
            r'(?:Total|Amount|Sum|Grand Total)[\s:]*\$?[\s]*([\d,]+\.?\d*)',
            r'\$[\s]*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)[\s]*USD',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    result["amount"] = Decimal(amount_str)
                    break
                except:
                    pass
        
        # Extract date
        date_patterns = [
            r'(?:Date|Purchase Date|Transaction Date)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Try to convert to YYYY-MM-DD format
                try:
                    from datetime import datetime
                    if '/' in date_str:
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            if len(parts[2]) == 2:
                                parts[2] = '20' + parts[2]
                            result["date"] = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                except:
                    result["date"] = date_str
                break
        
        # Extract vendor - look for header or "From:", "Merchant:"
        vendor_patterns = [
            r'(?:From|Merchant|Store|Vendor)[\s:]*([A-Za-z0-9\s&.,-]+)',
            r'^([A-Za-z0-9\s&.,-]+)(?:\n|$)',
        ]
        for pattern in vendor_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result["vendor"] = match.group(1).strip()
                break
        
        # Extract description - first few lines or item list
        lines = text.split('\n')[:5]
        description = ' '.join([line.strip() for line in lines if line.strip() and not any(keyword in line.lower() for keyword in ['total', 'amount', 'date', 'from', 'merchant'])])
        if description:
            result["description"] = description[:200]  # Limit length
        
        return result

    # GRN Methods
    async def create_grn(
        self,
        grn_data: GRNCreate,
        user: User
    ) -> GRNResponse:
        """Create a new GRN"""
        try:
            if not user.org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must be associated with an organization"
                )

            items_dict = [item.dict() for item in grn_data.items]
            total_amount = sum(
                Decimal(str(item["received_quantity"])) * Decimal("1.0")  # Simplified calculation
                for item in items_dict
            )

            grn = GRN(
                org_id=user.org_id,
                po_id=grn_data.po_id,
                received_by=user.id,
                grn_number=grn_data.grn_number,
                received_date=grn_data.received_date,
                items=items_dict,
                total_amount=total_amount,
                notes=grn_data.notes,
                status=GRNStatus.DRAFT,
            )

            self.db.add(grn)
            await self.db.flush()
            await self.db.refresh(grn)

            logger.info(f"Created GRN {grn.id}")
            return GRNResponse.model_validate(grn)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating GRN: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create GRN"
            )

    async def get_grn(
        self,
        grn_id: UUID,
        user: User
    ) -> Optional[GRNResponse]:
        """Get GRN by ID"""
        try:
            result = await self.db.execute(
                select(GRN)
                .where(
                    and_(
                        GRN.id == grn_id,
                        GRN.org_id == user.org_id
                    )
                )
            )
            grn = result.scalar_one_or_none()
            if not grn:
                return None
            return GRNResponse.model_validate(grn)
        except Exception as e:
            logger.error(f"Error getting GRN {grn_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve GRN"
            )

    async def list_grns(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        po_id: Optional[UUID] = None
    ) -> GRNListResponse:
        """List GRNs with pagination"""
        try:
            offset = (page - 1) * size
            query = select(GRN).where(GRN.org_id == user.org_id)

            if po_id:
                query = query.where(GRN.po_id == po_id)

            query = query.order_by(desc(GRN.created_at))
            query = query.offset(offset).limit(size)

            result = await self.db.execute(query)
            grns = result.scalars().all()

            total_query = select(func.count(GRN.id)).where(GRN.org_id == user.org_id)
            if po_id:
                total_query = total_query.where(GRN.po_id == po_id)

            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0

            return GRNListResponse(
                grns=[GRNResponse.model_validate(g) for g in grns],
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if total > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error listing GRNs: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list GRNs"
            )

    async def update_grn(
        self,
        grn_id: UUID,
        grn_data: GRNUpdate,
        user: User
    ) -> Optional[GRNResponse]:
        """Update GRN"""
        try:
            result = await self.db.execute(
                select(GRN)
                .where(
                    and_(
                        GRN.id == grn_id,
                        GRN.org_id == user.org_id
                    )
                )
            )
            grn = result.scalar_one_or_none()
            if not grn:
                return None

            update_data = grn_data.dict(exclude_unset=True)
            if 'items' in update_data and update_data['items']:
                items_dict = [item.dict() if hasattr(item, 'dict') else item for item in update_data['items']]
                update_data['items'] = items_dict
                total_amount = sum(
                    Decimal(str(item.get("received_quantity", 0))) * Decimal("1.0")
                    for item in items_dict
                )
                update_data['total_amount'] = total_amount

            for key, value in update_data.items():
                setattr(grn, key, value)

            grn.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(grn)

            return GRNResponse.model_validate(grn)
        except Exception as e:
            logger.error(f"Error updating GRN {grn_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update GRN"
            )

    async def delete_grn(
        self,
        grn_id: UUID,
        user: User
    ) -> bool:
        """Delete GRN"""
        try:
            result = await self.db.execute(
                select(GRN)
                .where(
                    and_(
                        GRN.id == grn_id,
                        GRN.org_id == user.org_id
                    )
                )
            )
            grn = result.scalar_one_or_none()
            if not grn:
                return False

            await self.db.delete(grn)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting GRN {grn_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete GRN"
            )

    # Delivery Milestone Methods
    async def create_milestone(
        self,
        milestone_data: DeliveryMilestoneCreate,
        user: User
    ) -> DeliveryMilestoneResponse:
        """Create a new delivery milestone"""
        try:
            milestone = DeliveryMilestone(
                po_id=milestone_data.po_id,
                milestone_name=milestone_data.milestone_name,
                due_date=milestone_data.due_date,
                notes=milestone_data.notes,
                status=DeliveryMilestoneStatus.PENDING,
            )

            self.db.add(milestone)
            await self.db.flush()
            await self.db.refresh(milestone)

            logger.info(f"Created milestone {milestone.id}")
            return DeliveryMilestoneResponse.model_validate(milestone)

        except Exception as e:
            logger.error(f"Error creating milestone: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create milestone"
            )

    async def list_milestones(
        self,
        po_id: UUID,
        user: User
    ) -> DeliveryMilestoneListResponse:
        """List delivery milestones for a PO"""
        try:
            query = select(DeliveryMilestone).where(
                DeliveryMilestone.po_id == po_id
            )
            query = query.order_by(asc(DeliveryMilestone.due_date))

            result = await self.db.execute(query)
            milestones = result.scalars().all()

            return DeliveryMilestoneListResponse(
                milestones=[DeliveryMilestoneResponse.model_validate(m) for m in milestones],
                total=len(milestones)
            )
        except Exception as e:
            logger.error(f"Error listing milestones: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list milestones"
            )

    async def update_milestone(
        self,
        milestone_id: UUID,
        milestone_data: DeliveryMilestoneUpdate,
        user: User
    ) -> Optional[DeliveryMilestoneResponse]:
        """Update delivery milestone"""
        try:
            result = await self.db.execute(
                select(DeliveryMilestone).where(DeliveryMilestone.id == milestone_id)
            )
            milestone = result.scalar_one_or_none()
            if not milestone:
                return None

            update_data = milestone_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(milestone, key, value)

            milestone.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(milestone)

            return DeliveryMilestoneResponse.model_validate(milestone)
        except Exception as e:
            logger.error(f"Error updating milestone {milestone_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update milestone"
            )

    async def delete_milestone(
        self,
        milestone_id: UUID,
        user: User
    ) -> bool:
        """Delete delivery milestone"""
        try:
            result = await self.db.execute(
                select(DeliveryMilestone).where(DeliveryMilestone.id == milestone_id)
            )
            milestone = result.scalar_one_or_none()
            if not milestone:
                return False

            await self.db.delete(milestone)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting milestone {milestone_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete milestone"
            )

    # Dashboard Stats
    async def get_dashboard_stats(
        self,
        user: User
    ) -> ProcurementDashboardStats:
        """Get procurement dashboard statistics"""
        try:
            pending_reqs = await self.db.execute(
                select(func.count(PurchaseRequisition.id), func.coalesce(func.sum(PurchaseRequisition.estimated_cost), 0))
                .where(
                    and_(
                        PurchaseRequisition.org_id == user.org_id,
                        PurchaseRequisition.status == RequisitionStatus.PENDING
                    )
                )
            )
            pending_result = pending_reqs.first()
            pending_count = pending_result[0] or 0
            pending_amount = Decimal(str(pending_result[1] or 0))

            active_orders = await self.db.execute(
                select(func.count(PurchaseOrder.id))
                .where(
                    and_(
                        PurchaseOrder.org_id == user.org_id,
                        PurchaseOrder.status.in_([PurchaseOrderStatus.ISSUED, PurchaseOrderStatus.PARTIALLY_FULFILLED])
                    )
                )
            )
            active_count = active_orders.scalar() or 0

            total_spend = await self.db.execute(
                select(func.coalesce(func.sum(PurchaseOrder.amount), 0))
                .where(PurchaseOrder.org_id == user.org_id)
            )
            spend = Decimal(str(total_spend.scalar() or 0))

            total_reqs = await self.db.execute(
                select(func.count(PurchaseRequisition.id))
                .where(PurchaseRequisition.org_id == user.org_id)
            )
            total_req_count = total_reqs.scalar() or 0

            approved_reqs = await self.db.execute(
                select(func.count(PurchaseRequisition.id))
                .where(
                    and_(
                        PurchaseRequisition.org_id == user.org_id,
                        PurchaseRequisition.status == RequisitionStatus.APPROVED
                    )
                )
            )
            approved_count = approved_reqs.scalar() or 0

            approval_rate = (approved_count / total_req_count * 100) if total_req_count > 0 else 0.0

            return ProcurementDashboardStats(
                pending_approvals=pending_count,
                pending_amount=pending_amount,
                active_orders=active_count,
                total_spend=spend,
                approval_rate=float(approval_rate)
            )
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get dashboard stats"
            )

    # Procurement Budget Methods
    async def get_category_historical_spending(
        self,
        category_id: int,
        org_id: UUID,
        budget_year: str
    ) -> Dict[str, Decimal]:
        """Get historical spending for a category from finance module and employee expenses"""
        from app.models.finance_planning import FinanceAnnualBudget, FinanceExpenseLine
        from app.models.procurement import EmployeeExpense, ExpenseStatus
        from app.models.expense_category import ExpenseCategory
        from datetime import date
        from decimal import Decimal
        
        current_year = int(budget_year)
        last_year = current_year - 1
        
        result = {
            'actual_last_year': Decimal('0.00'),
            'actual_current_year': Decimal('0.00')
        }
        
        # Get category name
        category_result = await self.db.execute(
            select(ExpenseCategory).where(ExpenseCategory.id == category_id)
        )
        category = category_result.scalar_one_or_none()
        if not category:
            return result
        
        category_name = category.name
        
        # Get spending from FinanceExpenseLine (finance module) - match by label
        # Get budget for last year
        last_year_budget_result = await self.db.execute(
            select(FinanceAnnualBudget)
            .where(
                and_(
                    FinanceAnnualBudget.budget_year == str(last_year),
                    FinanceAnnualBudget.org_id == org_id
                )
            )
        )
        last_budget = last_year_budget_result.scalar_one_or_none()
        
        if last_budget:
            # Get expense lines matching category name
            expense_lines_result = await self.db.execute(
                select(func.sum(FinanceExpenseLine.target))
                .where(
                    and_(
                        FinanceExpenseLine.budget_id == last_budget.id,
                        FinanceExpenseLine.label.ilike(f'%{category_name}%')
                    )
                )
            )
            last_year_finance_total = expense_lines_result.scalar() or Decimal('0.00')
            result['actual_last_year'] += Decimal(str(last_year_finance_total))
        
        # Get budget for current year
        current_year_budget_result = await self.db.execute(
            select(FinanceAnnualBudget)
            .where(
                and_(
                    FinanceAnnualBudget.budget_year == str(current_year),
                    FinanceAnnualBudget.org_id == org_id
                )
            )
        )
        current_budget = current_year_budget_result.scalar_one_or_none()
        
        if current_budget:
            expense_lines_result = await self.db.execute(
                select(func.sum(FinanceExpenseLine.target))
                .where(
                    and_(
                        FinanceExpenseLine.budget_id == current_budget.id,
                        FinanceExpenseLine.label.ilike(f'%{category_name}%')
                    )
                )
            )
            current_year_finance_total = expense_lines_result.scalar() or Decimal('0.00')
            result['actual_current_year'] += Decimal(str(current_year_finance_total))
        
        # Also get from EmployeeExpense table - match by category name
        last_year_start = date(last_year, 1, 1)
        last_year_end = date(last_year, 12, 31)
        current_year_start = date(current_year, 1, 1)
        current_year_end = date(current_year, 12, 31)
        
        # Get expenses for last year matching category
        last_year_expenses_result = await self.db.execute(
            select(func.sum(EmployeeExpense.amount))
            .where(
                and_(
                    EmployeeExpense.org_id == org_id,
                    EmployeeExpense.expense_date >= last_year_start,
                    EmployeeExpense.expense_date <= last_year_end,
                    EmployeeExpense.status.in_([ExpenseStatus.APPROVED, ExpenseStatus.REIMBURSED]),
                    EmployeeExpense.category.ilike(f'%{category_name}%')
                )
            )
        )
        last_year_expense_total = last_year_expenses_result.scalar() or Decimal('0.00')
        result['actual_last_year'] += Decimal(str(last_year_expense_total))
        
        # Get expenses for current year matching category
        current_year_expenses_result = await self.db.execute(
            select(func.sum(EmployeeExpense.amount))
            .where(
                and_(
                    EmployeeExpense.org_id == org_id,
                    EmployeeExpense.expense_date >= current_year_start,
                    EmployeeExpense.expense_date <= current_year_end,
                    EmployeeExpense.status.in_([ExpenseStatus.APPROVED, ExpenseStatus.REIMBURSED]),
                    EmployeeExpense.category.ilike(f'%{category_name}%')
                )
            )
        )
        current_year_expense_total = current_year_expenses_result.scalar() or Decimal('0.00')
        result['actual_current_year'] += Decimal(str(current_year_expense_total))
        
        return result

    async def create_budget(
        self,
        budget_data: "ProcurementBudgetCreate",
        user: User
    ) -> "ProcurementBudgetResponse":
        """Create a new procurement budget"""
        try:
            if not user.org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must be associated with an organization"
                )

            from app.models.procurement_budget import ProcurementBudget, ProcurementBudgetCategory, ProcurementBudgetSubcategory, ProcurementBudgetStatus
            from app.schemas.procurement import ProcurementBudgetResponse, BudgetCategoryResponse, BudgetSubcategoryResponse
            from decimal import Decimal

            total_budget = sum(
                Decimal(str(cat.proposed_budget)) for cat in budget_data.categories
            )

            budget = ProcurementBudget(
                org_id=user.org_id,
                budget_year=budget_data.budget_year,
                status=ProcurementBudgetStatus(budget_data.status or "draft"),
                total_budget=total_budget,
                created_by=user.id,
            )

            self.db.add(budget)
            await self.db.flush()

            for cat_data in budget_data.categories:
                category = ProcurementBudgetCategory(
                    budget_id=budget.id,
                    category_id=cat_data.category_id,
                    name=cat_data.name,
                    description=cat_data.description,
                    actual_last_year=Decimal(str(cat_data.actual_last_year)),
                    actual_current_year=Decimal(str(cat_data.actual_current_year)),
                    proposed_budget=Decimal(str(cat_data.proposed_budget)),
                    ai_suggested_budget=Decimal(str(cat_data.ai_suggested_budget)) if cat_data.ai_suggested_budget else None,
                    ai_confidence=cat_data.ai_confidence,
                    market_growth_rate=cat_data.market_growth_rate,
                )
                self.db.add(category)
                await self.db.flush()

                for sub_data in cat_data.subcategories:
                    subcategory = ProcurementBudgetSubcategory(
                        category_id=category.id,
                        subcategory_id=sub_data.subcategory_id,
                        name=sub_data.name,
                        actual_last_year=Decimal(str(sub_data.actual_last_year)),
                        actual_current_year=Decimal(str(sub_data.actual_current_year)),
                        proposed_budget=Decimal(str(sub_data.proposed_budget)),
                        ai_suggested_budget=Decimal(str(sub_data.ai_suggested_budget)) if sub_data.ai_suggested_budget else None,
                    )
                    self.db.add(subcategory)

            await self.db.commit()
            
            # Reload budget with relationships
            result = await self.db.execute(
                select(ProcurementBudget)
                .options(
                    selectinload(ProcurementBudget.categories).selectinload(ProcurementBudgetCategory.subcategories)
                )
                .where(ProcurementBudget.id == budget.id)
            )
            budget = result.scalar_one()

            logger.info(f"Created procurement budget {budget.id}")
            
            # Sync to Finance module
            try:
                from app.services.finance_planning import sync_procurement_budget_to_finance
                await sync_procurement_budget_to_finance(
                    self.db,
                    budget.id,
                    user.org_id,
                    budget.budget_year,
                    user.id
                )
                logger.info(f"Synced Procurement budget {budget.id} to Finance module")
            except Exception as sync_error:
                # Don't fail the Procurement budget creation if sync fails
                logger.warning(f"Failed to sync Procurement budget to Finance: {sync_error}")
            
            # Build response
            categories_response = []
            for cat in budget.categories:
                subcategories_response = [
                    BudgetSubcategoryResponse(
                        id=sub.id,
                        subcategory_id=sub.subcategory_id,
                        name=sub.name,
                        actual_last_year=sub.actual_last_year,
                        actual_current_year=sub.actual_current_year,
                        proposed_budget=sub.proposed_budget,
                        ai_suggested_budget=sub.ai_suggested_budget,
                    )
                    for sub in cat.subcategories
                ]
                categories_response.append(
                    BudgetCategoryResponse(
                        id=cat.id,
                        category_id=cat.category_id,
                        name=cat.name,
                        description=cat.description,
                        actual_last_year=cat.actual_last_year,
                        actual_current_year=cat.actual_current_year,
                        proposed_budget=cat.proposed_budget,
                        ai_suggested_budget=cat.ai_suggested_budget,
                        ai_confidence=cat.ai_confidence,
                        market_growth_rate=cat.market_growth_rate,
                        subcategories=subcategories_response,
                    )
                )

            return ProcurementBudgetResponse(
                id=budget.id,
                org_id=budget.org_id,
                budget_year=budget.budget_year,
                status=budget.status.value,
                total_budget=budget.total_budget,
                created_by=budget.created_by,
                created_at=budget.created_at,
                updated_at=budget.updated_at,
                categories=categories_response,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating budget: {e}", exc_info=True)
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create budget: {str(e)}"
            )

    async def get_budget(
        self,
        budget_id: UUID,
        user: User
    ) -> Optional["ProcurementBudgetResponse"]:
        """Get budget by ID"""
        try:
            from app.models.procurement_budget import ProcurementBudget, ProcurementBudgetCategory
            from app.schemas.procurement import ProcurementBudgetResponse, BudgetCategoryResponse, BudgetSubcategoryResponse

            result = await self.db.execute(
                select(ProcurementBudget)
                .options(
                    selectinload(ProcurementBudget.categories).selectinload(ProcurementBudgetCategory.subcategories)
                )
                .where(
                    and_(
                        ProcurementBudget.id == budget_id,
                        ProcurementBudget.org_id == user.org_id
                    )
                )
            )
            budget = result.scalar_one_or_none()
            if not budget:
                return None

            categories_response = []
            for cat in budget.categories:
                subcategories_response = [
                    BudgetSubcategoryResponse(
                        id=sub.id,
                        subcategory_id=sub.subcategory_id,
                        name=sub.name,
                        actual_last_year=sub.actual_last_year,
                        actual_current_year=sub.actual_current_year,
                        proposed_budget=sub.proposed_budget,
                        ai_suggested_budget=sub.ai_suggested_budget,
                    )
                    for sub in cat.subcategories
                ]
                categories_response.append(
                    BudgetCategoryResponse(
                        id=cat.id,
                        category_id=cat.category_id,
                        name=cat.name,
                        description=cat.description,
                        actual_last_year=cat.actual_last_year,
                        actual_current_year=cat.actual_current_year,
                        proposed_budget=cat.proposed_budget,
                        ai_suggested_budget=cat.ai_suggested_budget,
                        ai_confidence=cat.ai_confidence,
                        market_growth_rate=cat.market_growth_rate,
                        subcategories=subcategories_response,
                    )
                )

            return ProcurementBudgetResponse(
                id=budget.id,
                org_id=budget.org_id,
                budget_year=budget.budget_year,
                status=budget.status.value,
                total_budget=budget.total_budget,
                created_by=budget.created_by,
                created_at=budget.created_at,
                updated_at=budget.updated_at,
                categories=categories_response,
            )
        except Exception as e:
            logger.error(f"Error getting budget {budget_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve budget"
            )

    async def list_budgets(
        self,
        user: User,
        page: int = 1,
        size: int = 10,
        budget_year: Optional[str] = None,
        status: Optional[str] = None
    ) -> "ProcurementBudgetListResponse":
        """List budgets with pagination and filters"""
        try:
            from app.models.procurement_budget import ProcurementBudget, ProcurementBudgetCategory
            from app.schemas.procurement import ProcurementBudgetResponse, ProcurementBudgetListResponse, BudgetCategoryResponse, BudgetSubcategoryResponse

            offset = (page - 1) * size
            query = select(ProcurementBudget).where(
                ProcurementBudget.org_id == user.org_id
            )

            if budget_year:
                query = query.where(ProcurementBudget.budget_year == budget_year)

            if status:
                query = query.where(ProcurementBudget.status == status)

            query = query.options(
                selectinload(ProcurementBudget.categories).selectinload(ProcurementBudgetCategory.subcategories)
            )
            query = query.order_by(desc(ProcurementBudget.created_at))
            query = query.offset(offset).limit(size)

            result = await self.db.execute(query)
            budgets = result.scalars().all()

            total_query = select(func.count(ProcurementBudget.id)).where(
                ProcurementBudget.org_id == user.org_id
            )
            if budget_year:
                total_query = total_query.where(ProcurementBudget.budget_year == budget_year)
            if status:
                total_query = total_query.where(ProcurementBudget.status == status)

            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0

            budgets_response = []
            for budget in budgets:
                categories_response = []
                for cat in budget.categories:
                    subcategories_response = [
                        BudgetSubcategoryResponse(
                            id=sub.id,
                            subcategory_id=sub.subcategory_id,
                            name=sub.name,
                            actual_last_year=sub.actual_last_year,
                            actual_current_year=sub.actual_current_year,
                            proposed_budget=sub.proposed_budget,
                            ai_suggested_budget=sub.ai_suggested_budget,
                        )
                        for sub in cat.subcategories
                    ]
                    categories_response.append(
                        BudgetCategoryResponse(
                            id=cat.id,
                            category_id=cat.category_id,
                            name=cat.name,
                            description=cat.description,
                            actual_last_year=cat.actual_last_year,
                            actual_current_year=cat.actual_current_year,
                            proposed_budget=cat.proposed_budget,
                            ai_suggested_budget=cat.ai_suggested_budget,
                            ai_confidence=cat.ai_confidence,
                            market_growth_rate=cat.market_growth_rate,
                            subcategories=subcategories_response,
                        )
                    )

                budgets_response.append(
                    ProcurementBudgetResponse(
                        id=budget.id,
                        org_id=budget.org_id,
                        budget_year=budget.budget_year,
                        status=budget.status.value,
                        total_budget=budget.total_budget,
                        created_by=budget.created_by,
                        created_at=budget.created_at,
                        updated_at=budget.updated_at,
                        categories=categories_response,
                    )
                )

            return ProcurementBudgetListResponse(
                budgets=budgets_response,
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if total > 0 else 0
            )
        except Exception as e:
            logger.error(f"Error listing budgets: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list budgets"
            )

