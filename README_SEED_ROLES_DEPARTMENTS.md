# Seeding Roles and Departments

This guide explains how to seed system roles and departments into the database.

## Prerequisites

1. Ensure the database migrations have been run:
   ```bash
   cd megapolis-api
   poetry run python manage.py upgrade head
   ```

2. Ensure you have at least one organization in the database (roles and departments are created per organization).

## Seeding Roles

The `seed_roles.py` script creates 6 system roles based on the RBAC matrix:

- **Platform Admin**: Full system access with all permissions
- **Organization Admin**: Full access within organization including user management
- **Manager**: Manages team members and projects with write access
- **Contributor**: Standard employee with basic access to view and create resources
- **Viewer**: Read-only access to most resources
- **External Client**: Limited read-only access to shared proposals and projects

### Running the Role Seed Script

```bash
cd megapolis-api
poetry run python seed_roles.py
```

The script will:
- Find all organizations in the database
- Create the 6 system roles for each organization
- Skip roles that already exist (idempotent)
- Display a summary of created/skipped roles

### Role Permissions

Roles are seeded with permissions that match the frontend permission IDs:
- `view_projects`, `edit_projects`, `delete_projects`
- `view_accounts`, `edit_accounts`, `delete_accounts`
- `view_opportunities`, `edit_opportunities`
- `view_resources`, `edit_resources`
- `manage_team`
- `view_reports`, `export_data`
- `manage_roles`, `system_settings`

## Seeding Departments

The `seed_departments.py` script creates 10 default departments:

1. **Engineering** (ENG) - Software development and technical innovation
2. **Sales** (SALES) - Business development and revenue generation
3. **Marketing** (MKT) - Brand management and customer engagement
4. **Operations** (OPS) - Business operations and process optimization
5. **Finance** (FIN) - Financial planning and budgeting
6. **Human Resources** (HR) - Talent acquisition and employee relations
7. **Customer Success** (CS) - Customer support and account management
8. **Product Management** (PM) - Product strategy and roadmap planning
9. **Quality Assurance** (QA) - Testing and quality control
10. **Information Technology** (IT) - IT infrastructure and technical support

### Running the Department Seed Script

```bash
cd megapolis-api
poetry run python seed_departments.py
```

The script will:
- Find all organizations in the database
- Create the 10 departments for each organization
- Skip departments that already exist (idempotent)
- Display a summary of created/skipped departments

## Running Both Scripts

You can run both scripts in sequence:

```bash
cd megapolis-api
poetry run python seed_roles.py
poetry run python seed_departments.py
```

## Verification

After seeding, verify the data:

### Check Roles

```bash
# Using psql
psql $DATABASE_URL -c "SELECT name, is_system, array_length(permissions, 1) as perm_count FROM roles WHERE is_system = true ORDER BY name;"
```

### Check Departments

```bash
# Using psql
psql $DATABASE_URL -c "SELECT name, code, is_active FROM departments ORDER BY name;"
```

## Notes

- Both scripts are **idempotent** - they can be run multiple times safely
- Roles and departments are created **per organization**
- System roles (`is_system = true`) cannot be deleted from the UI
- Custom roles can be created by admins through the Organization Settings page

