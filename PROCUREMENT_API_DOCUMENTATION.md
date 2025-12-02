# Procurement Module API Documentation

## Base URL
- **Development**: `http://127.0.0.1:8000/api/procurement`
- **Production**: `http://your-production-url/api/procurement`

## API Documentation Links
- **Swagger UI (Interactive)**: `http://127.0.0.1:8000/docs`
- **ReDoc (Alternative)**: `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON Schema**: `http://127.0.0.1:8000/openapi.json`

## Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints Summary

### Total Endpoints: **32**

---

## 1. Purchase Requisitions (6 endpoints)

### Create Requisition
- **POST** `/api/procurement/requisitions`
- **Description**: Create a new purchase requisition
- **Request Body**: `PurchaseRequisitionCreate`
- **Response**: `PurchaseRequisitionResponse` (201 Created)

### List Requisitions
- **GET** `/api/procurement/requisitions`
- **Description**: List purchase requisitions with pagination
- **Query Parameters**:
  - `page` (int, default: 1) - Page number
  - `size` (int, default: 10, max: 100) - Page size
  - `status` (string, optional) - Filter by status (draft, pending, approved, rejected, po-created)
  - `search` (string, optional) - Search query
- **Response**: `PurchaseRequisitionListResponse`

### Get Requisition
- **GET** `/api/procurement/requisitions/{requisition_id}`
- **Description**: Get purchase requisition by ID
- **Path Parameters**: `requisition_id` (UUID)
- **Response**: `PurchaseRequisitionResponse`

### Update Requisition
- **PUT** `/api/procurement/requisitions/{requisition_id}`
- **Description**: Update purchase requisition
- **Path Parameters**: `requisition_id` (UUID)
- **Request Body**: `PurchaseRequisitionUpdate`
- **Response**: `PurchaseRequisitionResponse`

### Approve/Reject Requisition
- **POST** `/api/procurement/requisitions/{requisition_id}/approve`
- **Description**: Approve or reject purchase requisition
- **Path Parameters**: `requisition_id` (UUID)
- **Request Body**: `RequisitionApprovalRequest`
  - `status`: "approved" | "rejected"
  - `rejection_reason` (optional): string
- **Response**: `PurchaseRequisitionResponse`

### Delete Requisition
- **DELETE** `/api/procurement/requisitions/{requisition_id}`
- **Description**: Delete purchase requisition
- **Path Parameters**: `requisition_id` (UUID)
- **Response**: 204 No Content

---

## 2. Purchase Orders (5 endpoints)

### Create Purchase Order
- **POST** `/api/procurement/orders`
- **Description**: Create a new purchase order
- **Request Body**: `PurchaseOrderCreate`
- **Response**: `PurchaseOrderResponse` (201 Created)

### List Purchase Orders
- **GET** `/api/procurement/orders`
- **Description**: List purchase orders with pagination
- **Query Parameters**:
  - `page` (int, default: 1)
  - `size` (int, default: 10, max: 100)
  - `status` (string, optional) - Filter by status
  - `search` (string, optional) - Search query
- **Response**: `PurchaseOrderListResponse`

### Get Purchase Order
- **GET** `/api/procurement/orders/{order_id}`
- **Description**: Get purchase order by ID
- **Path Parameters**: `order_id` (UUID)
- **Response**: `PurchaseOrderResponse`

### Update Purchase Order
- **PUT** `/api/procurement/orders/{order_id}`
- **Description**: Update purchase order
- **Path Parameters**: `order_id` (UUID)
- **Request Body**: `PurchaseOrderUpdate`
- **Response**: `PurchaseOrderResponse`

### Delete Purchase Order
- **DELETE** `/api/procurement/orders/{order_id}`
- **Description**: Delete purchase order
- **Path Parameters**: `order_id` (UUID)
- **Response**: 204 No Content

---

## 3. RFQ (Request for Quotation) (7 endpoints)

### Create RFQ
- **POST** `/api/procurement/rfqs`
- **Description**: Create a new RFQ
- **Request Body**: `RFQCreate`
- **Response**: `RFQResponse` (201 Created)

### List RFQs
- **GET** `/api/procurement/rfqs`
- **Description**: List RFQs with pagination
- **Query Parameters**:
  - `page` (int, default: 1)
  - `size` (int, default: 10, max: 100)
  - `status` (string, optional) - Filter by status
  - `search` (string, optional) - Search query
- **Response**: `RFQListResponse`

### Get RFQ
- **GET** `/api/procurement/rfqs/{rfq_id}`
- **Description**: Get RFQ by ID
- **Path Parameters**: `rfq_id` (UUID)
- **Response**: `RFQResponse`

### Update RFQ
- **PUT** `/api/procurement/rfqs/{rfq_id}`
- **Description**: Update RFQ
- **Path Parameters**: `rfq_id` (UUID)
- **Request Body**: `RFQUpdate`
- **Response**: `RFQResponse`

### Delete RFQ
- **DELETE** `/api/procurement/rfqs/{rfq_id}`
- **Description**: Delete RFQ
- **Path Parameters**: `rfq_id` (UUID)
- **Response**: 204 No Content

### Submit RFQ Response
- **POST** `/api/procurement/rfqs/{rfq_id}/responses`
- **Description**: Submit vendor response to RFQ
- **Path Parameters**: `rfq_id` (UUID)
- **Request Body**: `RFQResponseCreate`
- **Response**: `RFQResponseResponse` (201 Created)

### List RFQ Responses
- **GET** `/api/procurement/rfqs/{rfq_id}/responses`
- **Description**: List all responses for an RFQ
- **Path Parameters**: `rfq_id` (UUID)
- **Response**: `List[RFQResponseResponse]`

---

## 4. Employee Expenses (4 endpoints)

### Create Expense
- **POST** `/api/procurement/expenses`
- **Description**: Create a new employee expense
- **Request Body**: `EmployeeExpenseCreate`
- **Response**: `EmployeeExpenseResponse` (201 Created)

### List Expenses
- **GET** `/api/procurement/expenses`
- **Description**: List employee expenses with pagination
- **Query Parameters**:
  - `page` (int, default: 1)
  - `size` (int, default: 10, max: 100)
  - `status` (string, optional) - Filter by status
  - `search` (string, optional) - Search query
- **Response**: `EmployeeExpenseListResponse`

### Get Expense
- **GET** `/api/procurement/expenses/{expense_id}`
- **Description**: Get employee expense by ID
- **Path Parameters**: `expense_id` (UUID)
- **Response**: `EmployeeExpenseResponse`

### Approve/Reject Expense
- **POST** `/api/procurement/expenses/{expense_id}/approve`
- **Description**: Approve or reject employee expense
- **Path Parameters**: `expense_id` (UUID)
- **Request Body**: `ExpenseApprovalRequest`
  - `status`: "approved" | "rejected"
  - `rejection_reason` (optional): string
- **Response**: `EmployeeExpenseResponse`

---

## 5. Vendor Invoices (3 endpoints)

### Create Invoice
- **POST** `/api/procurement/invoices`
- **Description**: Create a new vendor invoice
- **Request Body**: `VendorInvoiceCreate`
- **Response**: `VendorInvoiceResponse` (201 Created)

### List Invoices
- **GET** `/api/procurement/invoices`
- **Description**: List vendor invoices with pagination
- **Query Parameters**:
  - `page` (int, default: 1)
  - `size` (int, default: 10, max: 100)
  - `status` (string, optional) - Filter by status
  - `search` (string, optional) - Search query
- **Response**: `VendorInvoiceListResponse`

### Get Invoice
- **GET** `/api/procurement/invoices/{invoice_id}`
- **Description**: Get vendor invoice by ID
- **Path Parameters**: `invoice_id` (UUID)
- **Response**: `VendorInvoiceResponse`

---

## 6. GRN (Goods Receipt Notes) (3 endpoints)

### Create GRN
- **POST** `/api/procurement/grns`
- **Description**: Create a new GRN
- **Request Body**: `GRNCreate`
- **Response**: `GRNResponse` (201 Created)

### List GRNs
- **GET** `/api/procurement/grns`
- **Description**: List GRNs with pagination
- **Query Parameters**:
  - `page` (int, default: 1)
  - `size` (int, default: 10, max: 100)
  - `po_id` (UUID, optional) - Filter by purchase order ID
- **Response**: `GRNListResponse`

### Get GRN
- **GET** `/api/procurement/grns/{grn_id}`
- **Description**: Get GRN by ID
- **Path Parameters**: `grn_id` (UUID)
- **Response**: `GRNResponse`

---

## 7. Delivery Milestones (3 endpoints)

### Create Milestone
- **POST** `/api/procurement/orders/{order_id}/milestones`
- **Description**: Create a delivery milestone for a purchase order
- **Path Parameters**: `order_id` (UUID)
- **Request Body**: `DeliveryMilestoneCreate`
- **Response**: `DeliveryMilestoneResponse` (201 Created)

### List Milestones
- **GET** `/api/procurement/orders/{order_id}/milestones`
- **Description**: List delivery milestones for a purchase order
- **Path Parameters**: `order_id` (UUID)
- **Response**: `DeliveryMilestoneListResponse`

### Update Milestone
- **PUT** `/api/procurement/milestones/{milestone_id}`
- **Description**: Update delivery milestone
- **Path Parameters**: `milestone_id` (UUID)
- **Request Body**: `DeliveryMilestoneUpdate`
- **Response**: `DeliveryMilestoneResponse`

---

## 8. Dashboard (1 endpoint)

### Get Dashboard Stats
- **GET** `/api/procurement/dashboard/stats`
- **Description**: Get procurement dashboard statistics
- **Response**: `ProcurementDashboardStats`
  - `pending_approvals`: int
  - `pending_amount`: Decimal
  - `active_orders`: int
  - `total_spend`: Decimal
  - `approval_rate`: float

---

## Status Values

### Requisition Status
- `draft`
- `pending`
- `approved`
- `rejected`
- `po-created`

### Purchase Order Status
- `issued`
- `partially-fulfilled`
- `fulfilled`
- `invoiced`
- `paid`
- `cancelled`

### RFQ Status
- `draft`
- `sent`
- `responses-received`
- `evaluating`
- `awarded`
- `closed`

### Expense Status
- `draft`
- `pending`
- `approved`
- `rejected`
- `reimbursed`

### Invoice Status
- `pending`
- `matched`
- `approved`
- `paid`
- `exception`

### Matching Status
- `perfect_match`
- `partial_match`
- `no_match`
- `exception`

### GRN Status
- `draft`
- `submitted`
- `verified`
- `approved`

### Delivery Milestone Status
- `pending`
- `in-progress`
- `completed`
- `delayed`

---

## Error Responses

All endpoints may return the following error responses:

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

---

## Example Request/Response

### Create Requisition Example

**Request:**
```http
POST /api/procurement/requisitions
Authorization: Bearer <token>
Content-Type: application/json

{
  "purchase_type": "overhead",
  "description": "Office supplies for Q1",
  "category": "Office Operations",
  "estimated_cost": 5000.00,
  "vendor": "ABC Supplies",
  "justification": "Required for daily operations",
  "department": "Operations",
  "urgency": "medium",
  "needed_by": "2024-03-31T00:00:00Z"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "custom_id": "REQ-OR0001",
  "org_id": "123e4567-e89b-12d3-a456-426614174001",
  "requested_by": "123e4567-e89b-12d3-a456-426614174002",
  "purchase_type": "overhead",
  "description": "Office supplies for Q1",
  "category": "Office Operations",
  "estimated_cost": 5000.00,
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Quick Access Links

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

---

## Notes

1. All endpoints require authentication via Bearer token
2. All endpoints require appropriate permissions (procurement: create, view, edit, delete, approve)
3. All UUIDs in path parameters must be valid UUID format
4. Pagination defaults to page 1, size 10 (max 100)
5. All monetary values are in Decimal format
6. All dates are in ISO 8601 format (UTC)

