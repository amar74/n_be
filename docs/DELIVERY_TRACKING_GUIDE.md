# Delivery Tracking System - Guide

## Overview

The Delivery Tracking system allows organizations to monitor the progress of purchase orders through various delivery milestones. Each Purchase Order (PO) can have multiple delivery milestones that track the order from confirmation to final delivery.

## How It Works

### 1. **Purchase Order Lifecycle**

When a Purchase Order is created with status `issued` or `partially-fulfilled`, it automatically appears in the "Delivery Tracking" section. Each PO can have its own set of delivery milestones.

### 2. **Delivery Milestones**

Delivery milestones are individual checkpoints that track the progress of a purchase order. Each milestone has:

- **Milestone Name**: e.g., "Order Confirmed", "In Production", "Shipped", "Delivered"
- **Due Date**: When the milestone should be completed
- **Completed Date**: When the milestone was actually completed (optional)
- **Status**: One of:
  - `pending`: Not yet started
  - `in-progress`: Currently being worked on
  - `completed`: Successfully completed
  - `delayed`: Past due date and not completed

### 3. **Default Milestones**

When a PO is created, if no custom milestones exist, the system shows default milestones:

1. **Order Confirmed** - Automatically marked as completed when PO is issued
2. **In Production** - Vendor is manufacturing/preparing the order
3. **Shipped** - Order has been shipped from vendor
4. **Delivered** - Order has been received

### 4. **Real-Time Tracking**

- Each PO fetches its milestones from the database via the API endpoint: `GET /api/procurement/orders/{order_id}/milestones`
- The frontend displays all active POs (status: `issued` or `partially-fulfilled`) in the Delivery Tracking section
- Each PO has its own tracking card showing all milestones with their current status
- The overall PO status badge is determined by milestone completion:
  - **Delivered**: All milestones completed
  - **In Transit**: At least one milestone in progress
  - **Pending**: All milestones pending

### 5. **Scaling for 100+ Purchase Orders**

The system is designed to handle any number of POs:

- **Scrollable Container**: The Delivery Tracking section has a `max-h-[600px]` with `overflow-y-auto` to handle many POs
- **Individual Fetching**: Each PO fetches its milestones independently using React Query, allowing efficient caching and updates
- **Pagination Ready**: The backend API supports pagination if needed in the future
- **Performance**: Only active POs (issued/partially-fulfilled) are shown, reducing the number of API calls

### 6. **Creating and Managing Milestones**

Milestones can be created and updated via:

- **Create Milestone**: `POST /api/procurement/orders/{order_id}/milestones`
- **Update Milestone**: `PUT /api/procurement/milestones/{milestone_id}`
- **List Milestones**: `GET /api/procurement/orders/{order_id}/milestones`

### 7. **Vendor Performance Integration**

Delivery milestones are used to calculate vendor performance metrics:

- **On-Time Delivery Rate**: Percentage of milestones completed by their due date
- **Average Delivery Time**: Average time between milestone due dates and completion dates
- **Performance Trend**: Determined by order count and on-time delivery rate

## API Endpoints

### List Milestones for a PO
```
GET /api/procurement/orders/{order_id}/milestones
```

**Response:**
```json
{
  "milestones": [
    {
      "id": "uuid",
      "po_id": "uuid",
      "milestone_name": "Order Confirmed",
      "due_date": "2025-11-28T00:00:00Z",
      "completed_date": "2025-11-28T10:30:00Z",
      "status": "completed",
      "notes": null,
      "created_at": "2025-11-28T00:00:00Z",
      "updated_at": "2025-11-28T10:30:00Z"
    }
  ],
  "total": 1
}
```

### Create Milestone
```
POST /api/procurement/orders/{order_id}/milestones
```

**Request Body:**
```json
{
  "milestone_name": "Shipped",
  "due_date": "2025-12-05T00:00:00Z",
  "notes": "Tracking number: ABC123"
}
```

### Update Milestone
```
PUT /api/procurement/milestones/{milestone_id}
```

**Request Body:**
```json
{
  "status": "completed",
  "completed_date": "2025-12-05T14:30:00Z",
  "notes": "Delivered to warehouse"
}
```

## Frontend Implementation

### Component Structure

1. **PurchaseOrdersTab**: Main component that displays all POs and the Delivery Tracking section
2. **DeliveryTrackingCard**: Individual card component for each PO that:
   - Fetches milestones using `useMilestones(orderId)` hook
   - Displays milestone status with icons and dates
   - Shows overall PO status badge

### Data Flow

1. User navigates to Purchase Orders tab
2. Component fetches all purchase orders
3. Filters active orders (issued/partially-fulfilled)
4. For each active PO, `DeliveryTrackingCard` component:
   - Calls `useMilestones(po.id)` hook
   - Hook fetches milestones from API
   - Displays milestones with real-time status
5. If no milestones exist, shows default milestones based on PO dates

## Best Practices

1. **Create Milestones Early**: Create milestones when PO is issued to track progress from the start
2. **Update Regularly**: Update milestone status as the order progresses
3. **Use Notes**: Add notes to milestones for important information (tracking numbers, delays, etc.)
4. **Monitor Trends**: Use delivery tracking data to assess vendor performance over time

## Future Enhancements

- Email notifications when milestones are delayed
- Automatic milestone creation based on PO type
- Integration with shipping carriers for automatic status updates
- Dashboard widgets showing delivery performance metrics
- Export delivery reports for analysis

