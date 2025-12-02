from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.models.procurement import (
    RequisitionStatus,
    PurchaseType,
    UrgencyLevel,
    PurchaseOrderStatus,
    RFQStatus,
    ExpenseStatus,
    InvoiceStatus,
    MatchingStatus,
    GRNStatus,
    DeliveryMilestoneStatus,
)

# Purchase Requisition Schemas
class PurchaseRequisitionCreate(BaseModel):
    purchase_type: PurchaseType = Field(..., description="Type of purchase")
    description: str = Field(..., min_length=1, description="Purchase description")
    category: Optional[str] = Field(None, max_length=255, description="Purchase category")
    estimated_cost: Decimal = Field(..., gt=0, description="Estimated cost")
    vendor: Optional[str] = Field(None, max_length=255, description="Preferred vendor")
    justification: str = Field(..., min_length=1, description="Business justification")
    department: str = Field(..., min_length=1, max_length=100, description="Department")
    project_code: Optional[str] = Field(None, max_length=50, description="Project code if project-specific")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.MEDIUM, description="Urgency level")
    needed_by: Optional[datetime] = Field(None, description="Required by date")

    class Config:
        use_enum_values = True

class PurchaseRequisitionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=255)
    estimated_cost: Optional[Decimal] = Field(None, gt=0)
    vendor: Optional[str] = Field(None, max_length=255)
    justification: Optional[str] = Field(None, min_length=1)
    department: Optional[str] = Field(None, max_length=100)
    project_code: Optional[str] = Field(None, max_length=50)
    urgency: Optional[UrgencyLevel] = None
    needed_by: Optional[datetime] = None
    status: Optional[RequisitionStatus] = None
    rejection_reason: Optional[str] = None

    class Config:
        use_enum_values = True

class PurchaseRequisitionResponse(BaseModel):
    id: UUID
    custom_id: Optional[str] = None
    org_id: UUID
    requested_by: UUID
    requested_by_name: Optional[str] = None
    purchase_type: str
    description: str
    category: Optional[str] = None
    estimated_cost: Decimal
    vendor: Optional[str] = None
    justification: str
    department: str
    project_code: Optional[str] = None
    urgency: str
    needed_by: Optional[datetime] = None
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PurchaseRequisitionListResponse(BaseModel):
    requisitions: List[PurchaseRequisitionResponse]
    total: int
    page: int
    size: int
    total_pages: int

# Purchase Order Schemas
class PurchaseOrderCreate(BaseModel):
    requisition_id: Optional[UUID] = Field(None, description="Related requisition ID")
    vendor_id: Optional[UUID] = Field(None, description="Vendor ID")
    vendor_name: str = Field(..., min_length=1, max_length=255, description="Vendor name")
    description: str = Field(..., min_length=1, description="Order description")
    amount: Decimal = Field(..., gt=0, description="Order amount")
    project_code: Optional[str] = Field(None, max_length=50, description="Project code")
    issue_date: datetime = Field(..., description="Issue date")
    due_date: Optional[datetime] = Field(None, description="Due date")
    expected_delivery_date: Optional[datetime] = Field(None, description="Expected delivery date")
    terms_and_conditions: Optional[str] = Field(None, description="Terms and conditions")
    notes: Optional[str] = Field(None, description="Additional notes")

class PurchaseOrderUpdate(BaseModel):
    vendor_id: Optional[UUID] = None
    vendor_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    amount: Optional[Decimal] = Field(None, gt=0)
    project_code: Optional[str] = Field(None, max_length=50)
    due_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    status: Optional[PurchaseOrderStatus] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    rejection_reason: Optional[str] = Field(None, description="Rejection reason if rejected")

    class Config:
        use_enum_values = True

class PurchaseOrderResponse(BaseModel):
    id: UUID
    custom_id: Optional[str] = None
    org_id: UUID
    requisition_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    created_by: UUID
    created_by_name: Optional[str] = None
    vendor_name: str
    description: str
    amount: Decimal
    project_code: Optional[str] = None
    issue_date: datetime
    due_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    status: str
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PurchaseOrderListResponse(BaseModel):
    orders: List[PurchaseOrderResponse]
    total: int
    page: int
    size: int
    total_pages: int

# RFQ Schemas
class RFQCreate(BaseModel):
    requisition_id: Optional[UUID] = Field(None, description="Related requisition ID")
    title: str = Field(..., min_length=1, max_length=500, description="RFQ title")
    description: str = Field(..., min_length=1, description="RFQ description")
    category: str = Field(..., min_length=1, max_length=255, description="Category")
    estimated_value: Decimal = Field(..., gt=0, description="Estimated value")
    due_date: datetime = Field(..., description="Response due date")

class RFQUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=255)
    estimated_value: Optional[Decimal] = Field(None, gt=0)
    due_date: Optional[datetime] = None
    status: Optional[RFQStatus] = None

    class Config:
        use_enum_values = True

class RFQResponse(BaseModel):
    id: UUID
    custom_id: Optional[str] = None
    org_id: UUID
    requisition_id: Optional[UUID] = None
    created_by: UUID
    created_by_name: Optional[str] = None
    title: str
    description: str
    category: str
    estimated_value: Decimal
    due_date: datetime
    status: str
    sent_date: Optional[datetime] = None
    vendors_invited: int
    responses_received: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RFQListResponse(BaseModel):
    rfqs: List[RFQResponse]
    total: int
    page: int
    size: int
    total_pages: int

# RFQ Response Schemas
class RFQResponseCreate(BaseModel):
    rfq_id: UUID = Field(..., description="RFQ ID")
    vendor_id: UUID = Field(..., description="Vendor ID")
    quoted_amount: Decimal = Field(..., gt=0, description="Quoted amount")
    delivery_time: str = Field(..., max_length=255, description="Delivery time")
    terms: Optional[str] = Field(None, description="Terms and conditions")

class RFQResponseUpdate(BaseModel):
    quoted_amount: Optional[Decimal] = Field(None, gt=0)
    delivery_time: Optional[str] = Field(None, max_length=255)
    terms: Optional[str] = None
    score: Optional[Decimal] = Field(None, ge=0, le=100)
    status: Optional[str] = None

class RFQResponseResponse(BaseModel):
    id: UUID
    rfq_id: UUID
    vendor_id: UUID
    quoted_amount: Decimal
    delivery_time: str
    terms: Optional[str] = None
    score: Optional[Decimal] = None
    status: str
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Employee Expense Schemas
class EmployeeExpenseCreate(BaseModel):
    expense_date: datetime = Field(..., description="Expense date")
    amount: Decimal = Field(..., gt=0, description="Expense amount")
    category: str = Field(..., min_length=1, max_length=255, description="Expense category")
    description: str = Field(..., min_length=1, description="Expense description")
    project_code: Optional[str] = Field(None, max_length=50, description="Project code")
    receipt_url: Optional[str] = Field(None, max_length=500, description="Receipt URL")

class EmployeeExpenseUpdate(BaseModel):
    expense_date: Optional[datetime] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    project_code: Optional[str] = Field(None, max_length=50)
    receipt_url: Optional[str] = Field(None, max_length=500)
    status: Optional[ExpenseStatus] = None
    rejection_reason: Optional[str] = None

    class Config:
        use_enum_values = True

class EmployeeExpenseResponse(BaseModel):
    id: UUID
    custom_id: Optional[str] = None
    org_id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None
    expense_date: datetime
    amount: Decimal
    category: str
    description: str
    project_code: Optional[str] = None
    receipt_url: Optional[str] = None
    receipt_uploaded: bool
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejected_reason: Optional[str] = None
    reimbursed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EmployeeExpenseListResponse(BaseModel):
    expenses: List[EmployeeExpenseResponse]
    total: int
    page: int
    size: int
    total_pages: int

# Vendor Invoice Schemas
class VendorInvoiceCreate(BaseModel):
    po_id: Optional[UUID] = Field(None, description="Purchase order ID")
    vendor_id: Optional[UUID] = Field(None, description="Vendor ID")
    invoice_number: str = Field(..., min_length=1, max_length=100, description="Invoice number")
    vendor_name: str = Field(..., min_length=1, max_length=255, description="Vendor name")
    amount: Decimal = Field(..., gt=0, description="Invoice amount")
    invoice_date: datetime = Field(..., description="Invoice date")
    due_date: datetime = Field(..., description="Due date")
    invoice_file_url: Optional[str] = Field(None, max_length=500, description="Invoice file URL")

class VendorInvoiceUpdate(BaseModel):
    po_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    invoice_number: Optional[str] = Field(None, max_length=100)
    vendor_name: Optional[str] = Field(None, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    po_amount: Optional[Decimal] = None
    grn_amount: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    status: Optional[InvoiceStatus] = None
    matching_status: Optional[MatchingStatus] = None
    invoice_file_url: Optional[str] = Field(None, max_length=500)

    class Config:
        use_enum_values = True

class VendorInvoiceResponse(BaseModel):
    id: UUID
    org_id: UUID
    po_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    grn_id: Optional[UUID] = None
    invoice_number: str
    vendor_name: str
    amount: Decimal
    invoice_date: datetime
    due_date: datetime
    po_amount: Optional[Decimal] = None
    grn_amount: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    status: str
    matching_status: str
    invoice_file_url: Optional[str] = None
    fraud_detected: bool
    fraud_reasons: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VendorInvoiceListResponse(BaseModel):
    invoices: List[VendorInvoiceResponse]
    total: int
    page: int
    size: int
    total_pages: int

# Invoice Extraction Schemas
class InvoiceExtractionResponse(BaseModel):
    invoice_number: Optional[str] = None
    po_number: Optional[str] = None
    vendor_name: Optional[str] = None
    amount: Optional[Decimal] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Extraction confidence score")
    extracted_fields: Dict[str, Any] = Field(default_factory=dict, description="All extracted fields")
    
    class Config:
        from_attributes = True

# GRN Schemas
class GRNItem(BaseModel):
    description: str
    quantity: int = Field(..., gt=0)
    received_quantity: int = Field(..., ge=0)
    condition: str = Field(..., pattern="^(good|damaged|partial)$")

class GRNCreate(BaseModel):
    po_id: UUID = Field(..., description="Purchase order ID")
    grn_number: str = Field(..., min_length=1, max_length=100, description="GRN number")
    received_date: datetime = Field(..., description="Received date")
    items: List[GRNItem] = Field(..., min_items=1, description="Received items")
    notes: Optional[str] = Field(None, description="Additional notes")

class GRNUpdate(BaseModel):
    grn_number: Optional[str] = Field(None, max_length=100)
    received_date: Optional[datetime] = None
    items: Optional[List[GRNItem]] = None
    status: Optional[GRNStatus] = None
    notes: Optional[str] = None

    class Config:
        use_enum_values = True

class GRNResponse(BaseModel):
    id: UUID
    custom_id: Optional[str] = None
    org_id: UUID
    po_id: UUID
    received_by: UUID
    grn_number: str
    received_date: datetime
    items: Dict[str, Any]
    total_amount: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GRNListResponse(BaseModel):
    grns: List[GRNResponse]
    total: int
    page: int
    size: int
    total_pages: int

# Delivery Milestone Schemas
class DeliveryMilestoneCreate(BaseModel):
    po_id: UUID = Field(..., description="Purchase order ID")
    milestone_name: str = Field(..., min_length=1, max_length=255, description="Milestone name")
    due_date: datetime = Field(..., description="Due date")
    notes: Optional[str] = Field(None, description="Notes")

class DeliveryMilestoneUpdate(BaseModel):
    milestone_name: Optional[str] = Field(None, max_length=255)
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    status: Optional[DeliveryMilestoneStatus] = None
    notes: Optional[str] = None

    class Config:
        use_enum_values = True

class DeliveryMilestoneResponse(BaseModel):
    id: UUID
    po_id: UUID
    milestone_name: str
    due_date: datetime
    completed_date: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeliveryMilestoneListResponse(BaseModel):
    milestones: List[DeliveryMilestoneResponse]
    total: int

# Approval Schemas
class RequisitionApprovalRequest(BaseModel):
    status: RequisitionStatus = Field(..., description="Approval status")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason if rejected")

    class Config:
        use_enum_values = True

class ExpenseApprovalRequest(BaseModel):
    status: ExpenseStatus = Field(..., description="Approval status")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason if rejected")

    class Config:
        use_enum_values = True

# Dashboard/Stats Schemas
class ProcurementDashboardStats(BaseModel):
    pending_approvals: int
    pending_amount: Decimal
    active_orders: int
    total_spend: Decimal
    approval_rate: float

    class Config:
        from_attributes = True


# Procurement Budget Schemas
class BudgetSubcategoryCreate(BaseModel):
    subcategory_id: int
    name: str
    actual_last_year: Decimal = Decimal("0.00")
    actual_current_year: Decimal = Decimal("0.00")
    proposed_budget: Decimal = Decimal("0.00")
    ai_suggested_budget: Optional[Decimal] = None

    class Config:
        from_attributes = True


class BudgetSubcategoryResponse(BaseModel):
    id: UUID
    subcategory_id: int
    name: str
    actual_last_year: Decimal
    actual_current_year: Decimal
    proposed_budget: Decimal
    ai_suggested_budget: Optional[Decimal] = None

    class Config:
        from_attributes = True


class BudgetCategoryCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    actual_last_year: Decimal = Decimal("0.00")
    actual_current_year: Decimal = Decimal("0.00")
    proposed_budget: Decimal = Decimal("0.00")
    ai_suggested_budget: Optional[Decimal] = None
    ai_confidence: Optional[float] = None
    market_growth_rate: Optional[float] = None
    subcategories: List[BudgetSubcategoryCreate] = []

    class Config:
        from_attributes = True


class BudgetCategoryResponse(BaseModel):
    id: UUID
    category_id: int
    name: str
    description: Optional[str] = None
    actual_last_year: Decimal
    actual_current_year: Decimal
    proposed_budget: Decimal
    ai_suggested_budget: Optional[Decimal] = None
    ai_confidence: Optional[float] = None
    market_growth_rate: Optional[float] = None
    subcategories: List[BudgetSubcategoryResponse] = []

    class Config:
        from_attributes = True


class ProcurementBudgetCreate(BaseModel):
    budget_year: str
    status: Optional[str] = "draft"
    categories: List[BudgetCategoryCreate] = []

    class Config:
        from_attributes = True


class ProcurementBudgetUpdate(BaseModel):
    status: Optional[str] = None
    categories: Optional[List[BudgetCategoryCreate]] = None

    class Config:
        from_attributes = True


class ProcurementBudgetResponse(BaseModel):
    id: UUID
    org_id: UUID
    budget_year: str
    status: str
    total_budget: Decimal
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    categories: List[BudgetCategoryResponse] = []

    class Config:
        from_attributes = True


class ProcurementBudgetListResponse(BaseModel):
    budgets: List[ProcurementBudgetResponse]
    total: int
    page: int
    size: int
    total_pages: int

    class Config:
        from_attributes = True


class VendorPerformanceResponse(BaseModel):
    vendor_id: UUID
    vendor_name: str
    total_orders: int
    total_spend: Decimal
    average_delivery_time: float
    on_time_delivery_rate: float
    quality_rating: float
    communication_rating: float
    overall_rating: float
    performance_trend: str
    last_order_date: Optional[datetime] = None

class VendorQualificationResponse(BaseModel):
    vendor_id: UUID
    vendor_name: str
    qualification_score: float
    financial_stability: str
    credentials_verified: bool
    certifications: List[str]
    risk_level: str
    last_assessed: datetime
    assessed_by: UUID