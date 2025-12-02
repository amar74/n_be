# Role System Documentation

## Overview

This document explains the role system used in the application, specifically clarifying the "vendor" role and its privileges.

---

## Role Definitions

### 1. **"vendor" Role = Main Owner/Admin of Subscribed Application**

**IMPORTANT**: The `vendor` role in this system represents the **main owner/admin** of a subscribed application instance. These users have **full admin privileges** and can manage all features of the application.

#### Key Points:
- **"vendor" role users** = Main owners who subscribe to and manage the SaaS application
- They have **full admin privileges** across all modules
- They can approve/reject vendors in Procurement module
- They can manage all features like a regular admin
- This is **NOT** the same as Procurement vendors (suppliers)

#### Where This Applies:
- **Procurement Module**: Vendor role users can approve/reject suppliers
- **All Modules**: Vendor role users have admin-level access
- **Organization Management**: Vendor role users can manage their organization
- **User Management**: Vendor role users can manage users within their organization

### 2. **"admin" Role**

Standard admin role with full privileges within an organization.

### 3. **"manager" Role**

Manager role with elevated privileges but not full admin access.

### 4. **"viewer" Role**

Read-only access with limited privileges.

---

## Role Hierarchy

```
vendor (Main Owner) = Full Admin Privileges
    ↓
admin = Full Admin Privileges (within organization)
    ↓
manager = Elevated Privileges
    ↓
viewer = Read-Only Access
```

**Note**: `vendor` role is equivalent to `admin` role in terms of privileges.

---

## Implementation Guidelines

### Backend Role Checks

When implementing role-based access control, always include `vendor` role as having admin privileges:

```python
# ✅ CORRECT - Include vendor role
user_role_lower = current_user.role.lower() if current_user.role else ''
has_admin_privileges = user_role_lower in ['admin', 'manager', 'vendor']

# ❌ WRONG - Missing vendor role
has_admin_privileges = user_role_lower in ['admin', 'manager']
```

### Frontend Role Checks

When checking permissions in frontend components:

```typescript
// ✅ CORRECT - Include vendor role
const currentUserRole = authState.user?.role?.toLowerCase() || 'viewer';
const canApprove = currentUserRole === 'admin' || 
                   currentUserRole === 'manager' || 
                   currentUserRole === 'vendor';

// ❌ WRONG - Missing vendor role
const canApprove = currentUserRole === 'admin' || currentUserRole === 'manager';
```

---

## Module-Specific Notes

### Procurement Module
- **Vendor role users** can approve/reject suppliers
- **Vendor role users** can create, edit, delete vendors
- **Vendor role users** have full access to all Procurement features

### Finance Module
- **Vendor role users** can manage budgets, expenses, revenue
- **Vendor role users** can approve financial transactions

### All Other Modules
- **Vendor role users** have admin-level access
- Apply the same role check pattern: `['admin', 'manager', 'vendor']`

---

## Important Distinctions

### "vendor" Role (User Role)
- **What**: User role in the `users` table
- **Who**: Main owner/admin of subscribed application
- **Privileges**: Full admin access
- **Created by**: Super Admin when creating vendor user account
- **Endpoint**: `/admin/create_new_user` with `role: 'vendor'`

### Procurement Vendors (Suppliers)
- **What**: Supplier records in the `vendors` table
- **Who**: External companies from which organization purchases
- **Privileges**: None (they don't log in)
- **Created by**: Organization admin/vendor role users
- **Endpoint**: `/vendors/` (Procurement module)

**These are COMPLETELY DIFFERENT concepts. Do NOT confuse them.**

---

## Code Examples

### Backend Permission Check

```python
from app.dependencies.user_auth import get_current_user
from app.schemas.auth import AuthUserResponse

@router.patch("/{resource_id}/status")
async def update_status(
    resource_id: str,
    current_user: AuthUserResponse = Depends(get_current_user)
):
    # Check if user has admin privileges (including vendor role)
    user_role_lower = current_user.role.lower() if current_user.role else ''
    has_admin_privileges = user_role_lower in ['admin', 'manager', 'vendor']
    
    if not has_admin_privileges:
        raise HTTPException(
            status_code=403,
            detail="Only admin, manager, or vendor (main owner) roles can perform this action"
        )
    
    # Proceed with action
    ...
```

### Frontend Permission Check

```typescript
import { useAuth } from '@/hooks/useAuth';

function MyComponent() {
  const { authState } = useAuth();
  const currentUserRole = authState.user?.role?.toLowerCase() || 'viewer';
  
  // Check if user has admin privileges (including vendor role)
  const hasAdminPrivileges = 
    currentUserRole === 'admin' || 
    currentUserRole === 'manager' || 
    currentUserRole === 'vendor';
  
  return (
    <div>
      {hasAdminPrivileges && (
        <Button onClick={handleAdminAction}>Admin Action</Button>
      )}
    </div>
  );
}
```

---

## Migration Notes

If you find existing code that doesn't include `vendor` role in admin checks:

1. **Backend**: Update role checks to include `'vendor'` in the allowed roles list
2. **Frontend**: Update permission checks to include `currentUserRole === 'vendor'`
3. **Documentation**: Update any role documentation to clarify vendor role privileges

---

## Testing

When testing role-based access:

1. **Test as vendor role**: Verify vendor role users can perform admin actions
2. **Test as admin role**: Verify admin role users can perform admin actions
3. **Test as manager role**: Verify manager role users can perform manager actions
4. **Test as viewer role**: Verify viewer role users cannot perform admin actions

---

## Questions?

**Q: Why is "vendor" role treated as admin?**
A: In this SaaS application, "vendor" role represents the main owner/admin of a subscribed application instance. They pay for and manage the application, so they need full admin privileges.

**Q: Should I check for vendor role in all modules?**
A: Yes, wherever you check for admin/manager roles, also include vendor role.

**Q: What about Procurement vendors (suppliers)?**
A: Those are completely different - they are supplier records, not user accounts. They don't have roles or login capabilities.

---

*Last Updated: 2025-11-28*
*Documentation created to clarify vendor role privileges across all modules.*

