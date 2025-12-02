# Vendor Systems Documentation

## Overview

This application has **TWO COMPLETELY SEPARATE** vendor systems that serve different purposes. They are **NOT** related and should **NEVER** be confused or mixed.

---

## 1. Super Admin Vendor Creation (`/admin/create_new_user`)

### Purpose
Super Admin creates **vendor users** who will **log into and use the SaaS application**.

### Context
- **Super Admin** = The main client who created this SaaS application
- Super Admin **sells** the application to contractors/clients on a **subscription basis**
- When a client wants to use the application, Super Admin creates a vendor user account for them
- These vendor users will **log into the application** and use its features

### Technical Details
- **Model**: `User` (from `app.models.user`)
- **Table**: `users`
- **Role**: `VENDOR` (from `app.models.user.Roles`)
- **Endpoint**: `POST /admin/create_new_user`
- **Service**: `app.services.admin.admin_create_user()`
- **Route**: `app.routes.admin.admin_create_new_user()`
- **Frontend Hook**: `useSuperAdmin` (from `megapolis_fe/src/hooks/useSuperAdmin.ts`)
- **Frontend Pages**: 
  - `/super-admin/vendors` - Vendor list
  - `/super-admin/vendors/create` - Create vendor user
  - `/super-admin/vendors/:id` - Vendor profile

### Features
- ✅ **Password Required** - Vendor users need passwords to log in
- ✅ **Login Capability** - These users can authenticate and access the application
- ✅ **Organization Creation** - Vendor users create their organization on first login
- ✅ **Email Sent** - Invitation email with login credentials sent to vendor
- ✅ **User Management** - Part of user management system

### Example Flow
```
Super Admin → Creates Vendor User → Vendor receives email with credentials → 
Vendor logs in → Creates organization → Uses application features
```

### Database Schema
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,  -- REQUIRED
  role VARCHAR(50) DEFAULT 'vendor',
  org_id UUID,  -- Created on first login
  short_id VARCHAR(10),
  ...
)
```

---

## 2. Procurement Vendor Creation (`/vendors/`)

### Purpose
Procurement module creates **supplier records** - external companies from which the organization purchases goods/services.

### Context
- **Procurement Vendors** = External suppliers/vendors
- These are **companies** from which the organization **purchases assets, goods, or services**
- They are **NOT users** of the application
- They are **supplier records** for procurement management
- **NO connection** with Super Admin vendor users

### Technical Details
- **Model**: `Vendor` (from `app.models.vendor`)
- **Table**: `vendors`
- **Endpoint**: `POST /vendors/`
- **Service**: `app.services.vendor.create_vendor()`
- **Route**: `app.routes.vendor.create_vendor()`
- **Frontend Hook**: `useProcurementVendors` (from `megapolis_fe/src/hooks/useProcurementVendors.ts`)
- **Frontend Pages**: 
  - `/module/procurement` → Vendors tab
  - Modal: `AddVendorModal` component

### Features
- ❌ **NO Password** - Suppliers don't need passwords (they don't log in)
- ❌ **NO Login Capability** - These are records, not user accounts
- ✅ **Supplier Information** - Name, organization, contact, address, payment terms, etc.
- ✅ **Welcome Email** - Welcome email sent (NO login credentials)
- ✅ **Procurement Management** - Used for purchase orders, invoices, requisitions

### Example Flow
```
Organization Admin → Creates Supplier Record → Supplier receives welcome email → 
Supplier information stored → Used in purchase orders/invoices
```

### Database Schema
```sql
vendors (
  id UUID PRIMARY KEY,
  vendor_name VARCHAR(255),
  organisation VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  contact_number VARCHAR(20),
  password_hash VARCHAR(255) NULL,  -- NULL (not used)
  status VARCHAR(50) DEFAULT 'pending',
  website VARCHAR(255) NULL,
  ...
)
```

---

## Key Differences Summary

| Aspect | Super Admin Vendors | Procurement Vendors |
|--------|---------------------|---------------------|
| **Purpose** | Users who log into application | Supplier records |
| **Model** | `User` | `Vendor` |
| **Table** | `users` | `vendors` |
| **Password** | ✅ Required | ❌ Not needed (NULL) |
| **Login** | ✅ Can log in | ❌ Cannot log in |
| **Email Type** | Invitation with credentials | Welcome (no credentials) |
| **Created By** | Super Admin | Organization Admin |
| **Use Case** | SaaS subscription clients | Procurement suppliers |
| **Endpoint** | `/admin/create_new_user` | `/vendors/` |
| **Frontend** | Super Admin pages | Procurement module |

---

## Important Rules

### ❌ DO NOT:
1. **DO NOT** use `/vendors/` endpoint to create user accounts
2. **DO NOT** add password logic to Procurement vendor creation
3. **DO NOT** send login credentials to Procurement vendors
4. **DO NOT** mix Super Admin vendor management with Procurement vendor management
5. **DO NOT** use `useSuperAdminVendors` hook in Procurement module
6. **DO NOT** use `useProcurementVendors` hook in Super Admin pages

### ✅ DO:
1. **DO** use `/admin/create_new_user` for creating vendor users (Super Admin)
2. **DO** use `/vendors/` for creating supplier records (Procurement)
3. **DO** keep these systems completely separate
4. **DO** use appropriate hooks in respective modules
5. **DO** document any new vendor-related features clearly

---

## Code References

### Super Admin Vendor Creation
- **Backend Route**: `megapolis-api/app/routes/admin.py` → `admin_create_new_user()`
- **Backend Service**: `megapolis-api/app/services/admin.py` → `admin_create_user()`
- **Model**: `megapolis-api/app/models/user.py` → `User`
- **Frontend Hook**: `megapolis_fe/src/hooks/useSuperAdmin.ts`
- **Frontend Pages**: `megapolis_fe/src/pages/super-admin/VendorListPage.tsx`

### Procurement Vendor Creation
- **Backend Route**: `megapolis-api/app/routes/vendor.py` → `create_vendor()`
- **Backend Service**: `megapolis-api/app/services/vendor.py` → `create_vendor()`
- **Model**: `megapolis-api/app/models/vendor.py` → `Vendor`
- **Frontend Hook**: `megapolis_fe/src/hooks/useProcurementVendors.ts`
- **Frontend Component**: `megapolis_fe/src/pages/modules/procurement/modals/AddVendorModal.tsx`

---

## Future Development Guidelines

When adding new vendor-related features:

1. **First, identify which system**:
   - Is this for users who log into the application? → Super Admin Vendors
   - Is this for supplier management? → Procurement Vendors

2. **Use the correct model and endpoints**:
   - Super Admin Vendors → `User` model, `/admin/*` endpoints
   - Procurement Vendors → `Vendor` model, `/vendors/*` endpoints

3. **Document clearly** in code comments which system you're working with

4. **Never mix** the two systems in the same feature

---

## Migration Notes

- The `vendors.password_hash` column is **nullable** (can be NULL)
- Procurement vendors are created with `password_hash = NULL`
- The `/vendors/login` endpoint exists but only works for vendors with passwords (rare use case for future vendor portal)
- Super Admin vendor users are stored in `users` table with `password_hash` required

---

## Questions?

If you're unsure which system to use:
- **"I need to create a user account"** → Super Admin Vendors (`/admin/create_new_user`)
- **"I need to add a supplier"** → Procurement Vendors (`/vendors/`)

**When in doubt, ask!** It's better to clarify than to mix these systems.

---

*Last Updated: 2025-11-28*
*Documentation created to prevent confusion between Super Admin vendor users and Procurement supplier records.*

