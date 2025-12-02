from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.models.user import User
from app.dependencies.user_auth import get_current_user
from app.dependencies.permissions import get_user_permission
from app.schemas.user_permission import UserPermissionResponse
from app.db.session import get_request_transaction
from app.services.procurement import ProcurementService
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
    ProcurementBudgetCreate,
    ProcurementBudgetUpdate,
    ProcurementBudgetResponse,
    ProcurementBudgetListResponse,
)
from app.utils.logger import get_logger

logger = get_logger("procurement_routes")

router = APIRouter(prefix="/procurement", tags=["procurement"])

def _service(db: AsyncSession) -> ProcurementService:
    return ProcurementService(db)

# ========== Purchase Requisitions ==========

@router.post(
    "/requisitions",
    response_model=PurchaseRequisitionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new purchase requisition"
)
async def create_requisition(
    requisition_data: PurchaseRequisitionCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> PurchaseRequisitionResponse:
    service = _service(db)
    return await service.create_requisition(requisition_data, current_user)

@router.get(
    "/requisitions",
    response_model=PurchaseRequisitionListResponse,
    summary="List purchase requisitions"
)
async def list_requisitions(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> PurchaseRequisitionListResponse:
    service = _service(db)
    return await service.list_requisitions(current_user, page, size, status_filter, search)

@router.get(
    "/requisitions/{requisition_id}",
    response_model=PurchaseRequisitionResponse,
    summary="Get purchase requisition by ID"
)
async def get_requisition(
    requisition_id: UUID = Path(..., description="Requisition ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> PurchaseRequisitionResponse:
    service = _service(db)
    requisition = await service.get_requisition(requisition_id, current_user)
    if not requisition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requisition not found"
        )
    return requisition

@router.put(
    "/requisitions/{requisition_id}",
    response_model=PurchaseRequisitionResponse,
    summary="Update purchase requisition"
)
async def update_requisition(
    requisition_id: UUID = Path(..., description="Requisition ID"),
    requisition_data: PurchaseRequisitionUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["edit"]}))
) -> PurchaseRequisitionResponse:
    service = _service(db)
    requisition = await service.update_requisition(requisition_id, requisition_data, current_user)
    if not requisition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requisition not found"
        )
    return requisition

@router.post(
    "/requisitions/{requisition_id}/approve",
    response_model=PurchaseRequisitionResponse,
    summary="Approve or reject purchase requisition"
)
async def approve_requisition(
    requisition_id: UUID = Path(..., description="Requisition ID"),
    approval_data: RequisitionApprovalRequest = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["approve"]}))
) -> PurchaseRequisitionResponse:
    service = _service(db)
    requisition = await service.approve_requisition(requisition_id, approval_data, current_user)
    if not requisition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requisition not found"
        )
    return requisition

@router.delete(
    "/requisitions/{requisition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete purchase requisition"
)
async def delete_requisition(
    requisition_id: UUID = Path(..., description="Requisition ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["delete"]}))
):
    service = _service(db)
    success = await service.delete_requisition(requisition_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requisition not found"
        )

# ========== Purchase Orders ==========

@router.post(
    "/orders",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new purchase order"
)
async def create_purchase_order(
    order_data: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> PurchaseOrderResponse:
    service = _service(db)
    return await service.create_purchase_order(order_data, current_user)

@router.get(
    "/orders",
    response_model=PurchaseOrderListResponse,
    summary="List purchase orders"
)
async def list_purchase_orders(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> PurchaseOrderListResponse:
    service = _service(db)
    return await service.list_purchase_orders(current_user, page, size, status_filter, search)

@router.get(
    "/orders/{order_id}",
    response_model=PurchaseOrderResponse,
    summary="Get purchase order by ID"
)
async def get_purchase_order(
    order_id: UUID = Path(..., description="Order ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> PurchaseOrderResponse:
    service = _service(db)
    order = await service.get_purchase_order(order_id, current_user)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    return order

@router.put(
    "/orders/{order_id}",
    response_model=PurchaseOrderResponse,
    summary="Update purchase order"
)
async def update_purchase_order(
    order_id: UUID = Path(..., description="Order ID"),
    order_data: PurchaseOrderUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["edit"]}))
) -> PurchaseOrderResponse:
    service = _service(db)
    order = await service.update_purchase_order(order_id, order_data, current_user)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    return order

@router.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete purchase order"
)
async def delete_purchase_order(
    order_id: UUID = Path(..., description="Order ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["delete"]}))
):
    service = _service(db)
    success = await service.delete_purchase_order(order_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )

# ========== RFQs ==========

@router.post(
    "/rfqs",
    response_model=RFQResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new RFQ"
)
async def create_rfq(
    rfq_data: RFQCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> RFQResponseSchema:
    service = _service(db)
    return await service.create_rfq(rfq_data, current_user)

@router.get(
    "/rfqs",
    response_model=RFQListResponse,
    summary="List RFQs"
)
async def list_rfqs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> RFQListResponse:
    service = _service(db)
    return await service.list_rfqs(current_user, page, size, status_filter, search)

@router.get(
    "/rfqs/{rfq_id}",
    response_model=RFQResponseSchema,
    summary="Get RFQ by ID"
)
async def get_rfq(
    rfq_id: UUID = Path(..., description="RFQ ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> RFQResponseSchema:
    service = _service(db)
    rfq = await service.get_rfq(rfq_id, current_user)
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found"
        )
    return rfq

@router.put(
    "/rfqs/{rfq_id}",
    response_model=RFQResponseSchema,
    summary="Update RFQ"
)
async def update_rfq(
    rfq_id: UUID = Path(..., description="RFQ ID"),
    rfq_data: RFQUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["edit"]}))
) -> RFQResponseSchema:
    service = _service(db)
    rfq = await service.update_rfq(rfq_id, rfq_data, current_user)
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found"
        )
    return rfq

@router.delete(
    "/rfqs/{rfq_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete RFQ"
)
async def delete_rfq(
    rfq_id: UUID = Path(..., description="RFQ ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["delete"]}))
):
    service = _service(db)
    success = await service.delete_rfq(rfq_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFQ not found"
        )

@router.post(
    "/rfqs/{rfq_id}/responses",
    response_model=RFQResponseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit RFQ response"
)
async def create_rfq_response(
    rfq_id: UUID = Path(..., description="RFQ ID"),
    response_data: RFQResponseCreateSchema = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> RFQResponseResponse:
    service = _service(db)
    if response_data:
        response_data.rfq_id = rfq_id
    return await service.create_rfq_response(response_data, current_user)

@router.get(
    "/rfqs/{rfq_id}/responses",
    response_model=List[RFQResponseResponse],
    summary="List RFQ responses"
)
async def list_rfq_responses(
    rfq_id: UUID = Path(..., description="RFQ ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
):
    service = _service(db)
    return await service.list_rfq_responses(rfq_id, current_user)

# ========== Employee Expenses ==========

@router.post(
    "/expenses",
    response_model=EmployeeExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee expense"
)
async def create_expense(
    expense_data: EmployeeExpenseCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> EmployeeExpenseResponse:
    service = _service(db)
    return await service.create_expense(expense_data, current_user)

@router.get(
    "/expenses",
    response_model=EmployeeExpenseListResponse,
    summary="List employee expenses"
)
async def list_expenses(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> EmployeeExpenseListResponse:
    service = _service(db)
    return await service.list_expenses(current_user, page, size, status_filter, search)

@router.get(
    "/expenses/{expense_id}",
    response_model=EmployeeExpenseResponse,
    summary="Get employee expense by ID"
)
async def get_expense(
    expense_id: UUID = Path(..., description="Expense ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> EmployeeExpenseResponse:
    service = _service(db)
    expense = await service.get_expense(expense_id, current_user)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense

@router.put(
    "/expenses/{expense_id}",
    response_model=EmployeeExpenseResponse,
    summary="Update employee expense"
)
async def update_expense(
    expense_id: UUID = Path(..., description="Expense ID"),
    expense_data: EmployeeExpenseUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["edit"]}))
) -> EmployeeExpenseResponse:
    service = _service(db)
    expense = await service.update_expense(expense_id, expense_data, current_user)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense

@router.post(
    "/expenses/{expense_id}/approve",
    response_model=EmployeeExpenseResponse,
    summary="Approve or reject employee expense"
)
async def approve_expense(
    expense_id: UUID = Path(..., description="Expense ID"),
    approval_data: ExpenseApprovalRequest = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["approve"]}))
) -> EmployeeExpenseResponse:
    service = _service(db)
    expense = await service.approve_expense(expense_id, approval_data, current_user)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense

@router.post(
    "/expenses/extract-receipt",
    summary="Extract receipt data from uploaded file using OCR"
)
async def extract_receipt(
    file: UploadFile = File(..., description="Receipt file (PDF, JPG, PNG)"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
):
    """Extract receipt data from uploaded file using AI OCR"""
    try:
        # Read file content
        file_content = await file.read()
        
        if not file_content or len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        service = _service(db)
        
        # Extract receipt data
        extracted_data = await service.extract_receipt_data(file_content, file.filename or "receipt")
        
        return extracted_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting receipt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract receipt data: {str(e)}"
        )

# ========== Vendor Invoices ==========

@router.post(
    "/invoices",
    response_model=VendorInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vendor invoice"
)
async def create_invoice(
    invoice_data: VendorInvoiceCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> VendorInvoiceResponse:
    service = _service(db)
    return await service.create_invoice(invoice_data, current_user)

@router.get(
    "/invoices",
    response_model=VendorInvoiceListResponse,
    summary="List vendor invoices"
)
async def list_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search query"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> VendorInvoiceListResponse:
    service = _service(db)
    return await service.list_invoices(current_user, page, size, status_filter, search)

@router.get(
    "/invoices/{invoice_id}",
    response_model=VendorInvoiceResponse,
    summary="Get vendor invoice by ID"
)
async def get_invoice(
    invoice_id: UUID = Path(..., description="Invoice ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> VendorInvoiceResponse:
    service = _service(db)
    invoice = await service.get_invoice(invoice_id, current_user)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice

@router.put(
    "/invoices/{invoice_id}",
    response_model=VendorInvoiceResponse,
    summary="Update vendor invoice"
)
async def update_invoice(
    invoice_id: UUID = Path(..., description="Invoice ID"),
    invoice_data: VendorInvoiceUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["edit"]}))
) -> VendorInvoiceResponse:
    service = _service(db)
    invoice = await service.update_invoice(invoice_id, invoice_data, current_user)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice

@router.delete(
    "/invoices/{invoice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete vendor invoice"
)
async def delete_invoice(
    invoice_id: UUID = Path(..., description="Invoice ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["delete"]}))
):
    service = _service(db)
    success = await service.delete_invoice(invoice_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

@router.post(
    "/invoices/extract",
    response_model=Dict[str, Any],
    summary="Extract invoice data from uploaded file"
)
async def extract_invoice(
    file: UploadFile = File(..., description="Invoice file (PDF or DOCX)"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
):
    """Extract invoice data from uploaded file using AI"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required"
            )
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'doc', 'docx']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract invoice data
        service = _service(db)
        extracted_data = await service.extract_invoice_data(file_content, file.filename)
        
        return extracted_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract invoice data: {str(e)}"
        )

# ========== GRNs ==========

@router.post(
    "/grns",
    response_model=GRNResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new GRN"
)
async def create_grn(
    grn_data: GRNCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> GRNResponse:
    service = _service(db)
    return await service.create_grn(grn_data, current_user)

@router.get(
    "/grns",
    response_model=GRNListResponse,
    summary="List GRNs"
)
async def list_grns(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    po_id: Optional[UUID] = Query(None, description="Filter by purchase order ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> GRNListResponse:
    service = _service(db)
    return await service.list_grns(current_user, page, size, po_id)

@router.get(
    "/grns/{grn_id}",
    response_model=GRNResponse,
    summary="Get GRN by ID"
)
async def get_grn(
    grn_id: UUID = Path(..., description="GRN ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> GRNResponse:
    service = _service(db)
    grn = await service.get_grn(grn_id, current_user)
    if not grn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GRN not found"
        )
    return grn

@router.put(
    "/grns/{grn_id}",
    response_model=GRNResponse,
    summary="Update GRN"
)
async def update_grn(
    grn_id: UUID = Path(..., description="GRN ID"),
    grn_data: GRNUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["edit"]}))
) -> GRNResponse:
    service = _service(db)
    grn = await service.update_grn(grn_id, grn_data, current_user)
    if not grn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GRN not found"
        )
    return grn

@router.delete(
    "/grns/{grn_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete GRN"
)
async def delete_grn(
    grn_id: UUID = Path(..., description="GRN ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["delete"]}))
):
    service = _service(db)
    success = await service.delete_grn(grn_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GRN not found"
        )

# ========== Delivery Milestones ==========

@router.post(
    "/orders/{order_id}/milestones",
    response_model=DeliveryMilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a delivery milestone for a purchase order"
)
async def create_milestone(
    order_id: UUID = Path(..., description="Order ID"),
    milestone_data: DeliveryMilestoneCreate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> DeliveryMilestoneResponse:
    service = _service(db)
    if milestone_data:
        milestone_data.po_id = order_id
    return await service.create_milestone(milestone_data, current_user)

@router.get(
    "/orders/{order_id}/milestones",
    response_model=DeliveryMilestoneListResponse,
    summary="List delivery milestones for a purchase order"
)
async def list_milestones(
    order_id: UUID = Path(..., description="Order ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> DeliveryMilestoneListResponse:
    service = _service(db)
    return await service.list_milestones(order_id, current_user)

@router.put(
    "/milestones/{milestone_id}",
    response_model=DeliveryMilestoneResponse,
    summary="Update delivery milestone"
)
async def update_milestone(
    milestone_id: UUID = Path(..., description="Milestone ID"),
    milestone_data: DeliveryMilestoneUpdate = None,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["edit"]}))
) -> DeliveryMilestoneResponse:
    service = _service(db)
    milestone = await service.update_milestone(milestone_id, milestone_data, current_user)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )
    return milestone

@router.delete(
    "/milestones/{milestone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete delivery milestone"
)
async def delete_milestone(
    milestone_id: UUID = Path(..., description="Milestone ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["delete"]}))
):
    service = _service(db)
    success = await service.delete_milestone(milestone_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

# ========== Budgets ==========

@router.post(
    "/budgets",
    response_model=ProcurementBudgetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new procurement budget"
)
async def create_budget(
    budget_data: ProcurementBudgetCreate,
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["create"]}))
) -> ProcurementBudgetResponse:
    service = _service(db)
    return await service.create_budget(budget_data, current_user)

@router.get(
    "/budgets",
    response_model=ProcurementBudgetListResponse,
    summary="List procurement budgets"
)
async def list_budgets(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    budget_year: Optional[str] = Query(None, description="Filter by budget year"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> ProcurementBudgetListResponse:
    service = _service(db)
    return await service.list_budgets(current_user, page, size, budget_year, status)

@router.get(
    "/budgets/{budget_id}",
    response_model=ProcurementBudgetResponse,
    summary="Get procurement budget by ID"
)
async def get_budget(
    budget_id: UUID = Path(..., description="Budget ID"),
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> ProcurementBudgetResponse:
    service = _service(db)
    budget = await service.get_budget(budget_id, current_user)
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    return budget

# ========== Dashboard ==========

@router.get(
    "/dashboard/stats",
    response_model=ProcurementDashboardStats,
    summary="Get procurement dashboard statistics"
)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_request_transaction),
    current_user: User = Depends(get_current_user),
    user_permission: UserPermissionResponse = Depends(get_user_permission({"procurement": ["view"]}))
) -> ProcurementDashboardStats:
    service = _service(db)
    return await service.get_dashboard_stats(current_user)
