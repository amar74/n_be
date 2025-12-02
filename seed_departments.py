#!/usr/bin/env python3
"""
Seed script to create 10 default departments in the database

Run with: python seed_departments.py
"""
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.db.session import get_session
from app.models.department import Department
from app.models.organization import Organization
# Import all models to ensure relationships are properly initialized
from app.models import *  # noqa: F401, F403
from sqlalchemy import select
import uuid

# 10 default departments to seed
DEPARTMENTS = [
    {
        'name': 'Engineering',
        'code': 'ENG',
        'description': 'Software development, product engineering, and technical innovation',
    },
    {
        'name': 'Sales',
        'code': 'SALES',
        'description': 'Business development, client acquisition, and revenue generation',
    },
    {
        'name': 'Marketing',
        'code': 'MKT',
        'description': 'Brand management, digital marketing, and customer engagement',
    },
    {
        'name': 'Operations',
        'code': 'OPS',
        'description': 'Business operations, process optimization, and day-to-day management',
    },
    {
        'name': 'Finance',
        'code': 'FIN',
        'description': 'Financial planning, accounting, budgeting, and financial analysis',
    },
    {
        'name': 'Human Resources',
        'code': 'HR',
        'description': 'Talent acquisition, employee relations, and organizational development',
    },
    {
        'name': 'Customer Success',
        'code': 'CS',
        'description': 'Customer support, account management, and client satisfaction',
    },
    {
        'name': 'Product Management',
        'code': 'PM',
        'description': 'Product strategy, roadmap planning, and feature development',
    },
    {
        'name': 'Quality Assurance',
        'code': 'QA',
        'description': 'Testing, quality control, and ensuring product reliability',
    },
    {
        'name': 'Information Technology',
        'code': 'IT',
        'description': 'IT infrastructure, system administration, and technical support',
    },
]


async def seed_departments():
    """Seed default departments into the database for all organizations."""
    print("🌱 Starting department seeding...")
    
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
                
                for dept_data in DEPARTMENTS:
                    # Check if department already exists
                    result = await db.execute(
                        select(Department).where(
                            Department.org_id == org.id,
                            Department.name == dept_data['name']
                        )
                    )
                    existing_dept = result.scalar_one_or_none()
                    
                    if existing_dept:
                        print(f"   ⏭️  Skipping '{dept_data['name']}' (already exists)")
                        total_skipped += 1
                        continue
                    
                    # Create new department
                    department = Department(
                        id=uuid.uuid4(),
                        org_id=org.id,
                        name=dept_data['name'],
                        code=dept_data['code'],
                        description=dept_data['description'],
                        is_active=True,
                    )
                    db.add(department)
                    print(f"   ✅ Created '{dept_data['name']}' ({dept_data['code']})")
                    total_created += 1
            
            await db.commit()
            print(f"\n🎉 Department seeding completed!")
            print(f"   ✅ Created: {total_created} departments")
            print(f"   ⏭️  Skipped: {total_skipped} departments (already exist)")
            
    except Exception as e:
        print(f"❌ Error seeding departments: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(seed_departments())

