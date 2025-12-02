import enum
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization import Organization
    from app.models.vendor import Vendor

class RequisitionStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PO_CREATED = "po-created"

class PurchaseType(str, enum.Enum):
    OVERHEAD = "overhead"
    PROJECT = "project"

class UrgencyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PurchaseOrderStatus(str, enum.Enum):
    ISSUED = "issued"
    PARTIALLY_FULFILLED = "partially-fulfilled"
    FULFILLED = "fulfilled"
    INVOICED = "invoiced"
    PAID = "paid"
    CANCELLED = "cancelled"

class RFQStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    RESPONSES_RECEIVED = "responses-received"
    EVALUATING = "evaluating"
    AWARDED = "awarded"
    CLOSED = "closed"

class ExpenseStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REIMBURSED = "reimbursed"

class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    APPROVED = "approved"
    PAID = "paid"
    EXCEPTION = "exception"

class MatchingStatus(str, enum.Enum):
    PERFECT_MATCH = "perfect_match"
    PARTIAL_MATCH = "partial_match"
    NO_MATCH = "no_match"
    EXCEPTION = "exception"

class GRNStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    APPROVED = "approved"

class DeliveryMilestoneStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    DELAYED = "delayed"

class PurchaseRequisition(Base):
    __tablename__ = "purchase_requisitions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    custom_id: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    
    purchase_type: Mapped[PurchaseType] = mapped_column(
        SQLEnum(PurchaseType, name="purchase_type"),
        nullable=False,
        default=PurchaseType.OVERHEAD
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    vendor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    project_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    urgency: Mapped[UrgencyLevel] = mapped_column(
        SQLEnum(UrgencyLevel, name="urgency_level"),
        nullable=False,
        default=UrgencyLevel.MEDIUM
    )
    needed_by: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[RequisitionStatus] = mapped_column(
        SQLEnum(RequisitionStatus, name="requisition_status"),
        nullable=False,
        default=RequisitionStatus.DRAFT,
        index=True
    )
    
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Column doesn't exist in DB yet
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    requester: Mapped["User"] = relationship("User", foreign_keys=[requested_by])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    custom_id: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    requisition_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_requisitions.id"), nullable=True, index=True
    )
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    project_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[PurchaseOrderStatus] = mapped_column(
        SQLEnum(PurchaseOrderStatus, name="po_status"),
        nullable=False,
        default=PurchaseOrderStatus.ISSUED,
        index=True
    )
    
    terms_and_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Column doesn't exist in DB yet
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    requisition: Mapped[Optional["PurchaseRequisition"]] = relationship("PurchaseRequisition", foreign_keys=[requisition_id])
    vendor: Mapped[Optional["Vendor"]] = relationship("Vendor", foreign_keys=[vendor_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])

class RFQ(Base):
    __tablename__ = "rfqs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    custom_id: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    requisition_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_requisitions.id"), nullable=True, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    status: Mapped[RFQStatus] = mapped_column(
        SQLEnum(RFQStatus, name="rfq_status"),
        nullable=False,
        default=RFQStatus.DRAFT,
        index=True
    )
    
    sent_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    vendors_invited: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    responses_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    requisition: Mapped[Optional["PurchaseRequisition"]] = relationship("PurchaseRequisition", foreign_keys=[requisition_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])

class RFQResponse(Base):
    __tablename__ = "rfq_responses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    rfq_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rfqs.id"), nullable=False, index=True
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False, index=True
    )
    
    quoted_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    delivery_time: Mapped[str] = mapped_column(String(255), nullable=False)
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="submitted", index=True
    )
    
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    rfq: Mapped["RFQ"] = relationship("RFQ", foreign_keys=[rfq_id])
    vendor: Mapped["Vendor"] = relationship("Vendor", foreign_keys=[vendor_id])

class EmployeeExpense(Base):
    __tablename__ = "employee_expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    custom_id: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    
    expense_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    project_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    receipt_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    receipt_uploaded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    status: Mapped[ExpenseStatus] = mapped_column(
        SQLEnum(ExpenseStatus, name="expense_status"),
        nullable=False,
        default=ExpenseStatus.DRAFT,
        index=True
    )
    
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reimbursed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    employee: Mapped["User"] = relationship("User", foreign_keys=[employee_id])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])

class VendorInvoice(Base):
    __tablename__ = "vendor_invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    po_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=True, index=True
    )
    vendor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True, index=True
    )
    grn_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grns.id"), nullable=True, index=True
    )
    
    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    invoice_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    po_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    grn_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    variance: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus, name="invoice_status"),
        nullable=False,
        default=InvoiceStatus.PENDING,
        index=True
    )
    matching_status: Mapped[MatchingStatus] = mapped_column(
        SQLEnum(MatchingStatus, name="matching_status"),
        nullable=False,
        default=MatchingStatus.NO_MATCH,
        index=True
    )
    
    invoice_file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fraud_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fraud_reasons: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship("PurchaseOrder", foreign_keys=[po_id])
    vendor: Mapped[Optional["Vendor"]] = relationship("Vendor", foreign_keys=[vendor_id])
    grn: Mapped[Optional["GRN"]] = relationship("GRN", foreign_keys=[grn_id])

class GRN(Base):
    __tablename__ = "grns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    custom_id: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    po_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False, index=True
    )
    received_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    
    grn_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    received_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    items: Mapped[dict] = mapped_column(JSONB, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    
    status: Mapped[GRNStatus] = mapped_column(
        SQLEnum(GRNStatus, name="grn_status"),
        nullable=False,
        default=GRNStatus.DRAFT,
        index=True
    )
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", foreign_keys=[po_id])
    receiver: Mapped["User"] = relationship("User", foreign_keys=[received_by])

class DeliveryMilestone(Base):
    __tablename__ = "delivery_milestones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    po_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=False, index=True
    )
    
    milestone_name: Mapped[str] = mapped_column(String(255), nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[DeliveryMilestoneStatus] = mapped_column(
        SQLEnum(DeliveryMilestoneStatus, name="milestone_status"),
        nullable=False,
        default=DeliveryMilestoneStatus.PENDING,
        index=True
    )
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship("PurchaseOrder", foreign_keys=[po_id])