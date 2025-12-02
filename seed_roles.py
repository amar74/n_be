#!/usr/bin/env python3
"""
Seed script to create system roles with RBAC permissions based on rbac-entitlements.md

Run with: python seed_roles.py
"""
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.db.session import get_session
from app.models.role import Role
from app.models.organization import Organization
# Import all models to ensure relationships are properly initialized
from app.models import *  # noqa: F401, F403
from sqlalchemy import select
import uuid

# Define permissions based on RBAC matrix
# Permission IDs must match what's used in the frontend (RoleManagement.tsx)
# Available permissions from frontend:
ALL_PERMISSIONS = [
    'view_projects',
    'edit_projects',
    'delete_projects',
    'view_accounts',
    'edit_accounts',
    'delete_accounts',
    'view_opportunities',
    'edit_opportunities',
    'view_resources',
    'edit_resources',
    'manage_team',
    'view_reports',
    'export_data',
    'manage_roles',
    'system_settings',
]

# Role definitions based on RBAC matrix
# Mapping RBAC roles to frontend permission IDs
ROLES = [
    {
        'name': 'Platform Admin',
        'description': 'Full system access with all permissions across all organizations',
        'permissions': ALL_PERMISSIONS.copy(),  # All permissions
        'color': 'bg-red-100 text-red-700 border-red-200',
        'is_system': True,
    },
    {
        'name': 'Organization Admin',
        'description': 'Full access within organization including user management and settings',
        'permissions': ALL_PERMISSIONS.copy(),  # All permissions for org admin
        'color': 'bg-amber-100 text-amber-700 border-amber-200',
        'is_system': True,
    },
    {
        'name': 'Manager',
        'description': 'Manages team members and projects with write access to most resources',
        'permissions': [
            'view_projects', 'edit_projects', 'delete_projects',
            'view_accounts', 'edit_accounts', 'delete_accounts',
            'view_opportunities', 'edit_opportunities',
            'view_resources', 'edit_resources',
            'manage_team',
            'view_reports', 'export_data',
        ],
        'color': 'bg-purple-100 text-purple-700 border-purple-200',
        'is_system': True,
    },
    {
        'name': 'Contributor',
        'description': 'Standard employee with basic access to view and create resources',
        'permissions': [
            'view_projects', 'edit_projects',
            'view_accounts', 'edit_accounts',
            'view_opportunities', 'edit_opportunities',
            'view_resources', 'edit_resources',
            'view_reports',
        ],
        'color': 'bg-blue-100 text-blue-700 border-blue-200',
        'is_system': True,
    },
    {
        'name': 'Viewer',
        'description': 'Read-only access to most resources, no write permissions',
        'permissions': [
            'view_projects',
            'view_accounts',
            'view_opportunities',
            'view_resources',
            'view_reports',
        ],
        'color': 'bg-gray-100 text-gray-700 border-gray-200',
        'is_system': True,
    },
    {
        'name': 'External Client',
        'description': 'Limited read-only access to shared proposals and projects',
        'permissions': [
            'view_projects',  # limited
            'view_accounts',  # limited
        ],
        'color': 'bg-indigo-100 text-indigo-700 border-indigo-200',
        'is_system': True,
    },
]


async def seed_roles():
    """Seed system roles into the database for all organizations."""
    print("🌱 Starting role seeding...")
    
    try:
        async with get_session() as db:
            # Get all organizations
            result = await db.execute(select(Organization))
            organizations = result.scalars().all()
            
            if not organizations:
                print("⚠️  No organizations found. Please create an organization first.")
                return
            
            print(f"📦 Found {len(organizations)} organization(s)")
            
            total_created = 0
            total_skipped = 0
            
            for org in organizations:
                print(f"\n📋 Processing organization: {org.name} (ID: {org.id})")
                
                for role_data in ROLES:
                    # Check if role already exists
                    result = await db.execute(
                        select(Role).where(
                            Role.org_id == org.id,
                            Role.name == role_data['name'],
                            Role.is_system == True
                        )
                    )
                    existing_role = result.scalar_one_or_none()
                    
                    if existing_role:
                        print(f"   ⏭️  Skipping '{role_data['name']}' (already exists)")
                        total_skipped += 1
                        continue
                    
                    # Create new role
                    role = Role(
                        id=uuid.uuid4(),
                        org_id=org.id,
                        name=role_data['name'],
                        description=role_data['description'],
                        permissions=role_data['permissions'],
                        color=role_data['color'],
                        is_system=role_data['is_system'],
                    )
                    db.add(role)
                    print(f"   ✅ Created '{role_data['name']}' with {len(role_data['permissions'])} permissions")
                    total_created += 1
            
            await db.commit()
            print(f"\n🎉 Role seeding completed!")
            print(f"   ✅ Created: {total_created} roles")
            print(f"   ⏭️  Skipped: {total_skipped} roles (already exist)")
            
    except Exception as e:
        print(f"❌ Error seeding roles: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(seed_roles())

