# Employee Seeding Guide

This script seeds test employees into the database for testing the employee dashboard RBAC system.

## Quick Start

```bash
# Make sure you're in the megapolis-api directory
cd megapolis-api

# Run the seed script
python seed_employees.py
```

## What It Does

1. **Creates User Records**: Creates users in the `users` table with:
   - Email and password (all passwords: `password123`)
   - Role (mapped from frontend roles to backend roles)
   - Name and username

2. **Creates Employee Records**: Creates corresponding records in the `employees` table with:
   - Employee number (auto-generated)
   - Job title and department
   - Status (set to ACTIVE)
   - Link to user record

## Role Mapping

Frontend roles are mapped to backend roles:

| Frontend Role | Backend Role | Description |
|---------------|--------------|-------------|
| `platform_admin` | `super_admin` | Full system access |
| `org_admin` | `admin` | Organization admin |
| `manager` | `admin` | Manager (permissions handled separately) |
| `contributor` | `admin` | Regular employee |
| `viewer` | `admin` | Read-only access |

**Note**: The actual RBAC permissions are handled at the application level, not just by the database role.

## Seeded Employees

The script creates the following test employees:

### Admin Accounts
- `admin@nyftaa.com` - Platform Admin
- `orgadmin@nyftaa.com` - Org Admin

### Manager Accounts
- `manager@nyftaa.com` - Operations Manager
- `manager2@nyftaa.com` - Sales Manager

### Finance Manager Accounts
- `finance@nyftaa.com` - Finance Manager
- `finance2@nyftaa.com` - Senior Finance Manager

### HR Accounts
- `hr@nyftaa.com` - HR Manager
- `hr2@nyftaa.com` - HR Specialist

### Employee Accounts
- `employee@nyftaa.com` - Software Engineer
- `employee2@nyftaa.com` - UI/UX Designer
- `employee3@nyftaa.com` - Sales Executive

### Viewer Accounts
- `viewer@nyftaa.com` - Marketing Analyst
- `viewer2@nyftaa.com` - Support Specialist

**All passwords**: `password123`

## Updating Existing Users

If a user already exists:
- Password will be updated to `password123`
- Name and role will be updated
- Employee record will be created/updated if it doesn't exist

## Troubleshooting

### Database Connection Error
Make sure your database is running and the connection string in `app/db/session.py` is correct.

### Employee Record Creation Fails
If employee record creation fails, the user will still be created. Employee records are optional and can be created later through the employee management interface.

### Role Not Working
Remember that RBAC permissions are enforced at the application level. The database role is just a starting point. Check:
- `client/lib/permissions.ts` for permission matrix
- `DashboardRouter.tsx` for dashboard routing
- API middleware for permission checks

## Customization

To add more test employees, edit `seed_employees.py` and add entries to the `EMPLOYEES_TO_SEED` list:

```python
{
    "email": "newemployee@nyftaa.com",
    "password": "password123",
    "name": "New Employee",
    "role": "contributor",
    "department": "engineering",
    "job_title": "Software Engineer",
},
```

## Integration with Frontend

The frontend seed data in `mystic-heaven/client/lib/seedUsers.ts` should match the database seed data. Both use the same emails and passwords for consistency.

When the frontend authenticates:
1. It first checks `seedUsers.ts` (for development/testing)
2. In production, it should authenticate against the database via API

## Next Steps

After seeding:
1. Test login with different roles
2. Verify dashboard routing works correctly
3. Test permission checks in different modules
4. Verify employee records are linked correctly

