#!/usr/bin/env python3
"""
Seed script to create test employees in the database
All passwords: password123

Run with: python seed_employees.py
"""
import asyncio
from app.services.auth_service import AuthService
from app.db.session import get_session
from app.models.user import User
from app.models.employee import Employee, EmployeeStatus
from sqlalchemy import select
from typing import Optional
import uuid

# Map frontend roles to backend roles
ROLE_MAPPING = {
    'platform_admin': 'super_admin',
    'org_admin': 'admin',
    'manager': 'admin',  # Managers get admin role in backend
    'contributor': 'admin',  # Contributors get admin role
    'viewer': 'admin',  # Viewers get admin role (permissions handled separately)
}

# Test employees to seed
EMPLOYEES_TO_SEED = [
    # Platform Admin
    {
        "email": "admin@nyftaa.com",
        "password": "password123",
        "name": "System Administrator",
        "role": "platform_admin",
        "department": None,
        "job_title": "System Administrator",
    },
    
    # Org Admin
    {
        "email": "orgadmin@nyftaa.com",
        "password": "password123",
        "name": "Organization Admin",
        "role": "org_admin",
        "department": None,
        "job_title": "Organization Administrator",
    },

    # Managers
    {
        "email": "manager@nyftaa.com",
        "password": "password123",
        "name": "John Manager",
        "role": "manager",
        "department": "operations",
        "job_title": "Operations Manager",
    },
    {
        "email": "manager2@nyftaa.com",
        "password": "password123",
        "name": "Jane Manager",
        "role": "manager",
        "department": "sales",
        "job_title": "Sales Manager",
    },

    # Finance Managers
    {
        "email": "finance@nyftaa.com",
        "password": "password123",
        "name": "Sarah Finance",
        "role": "manager",
        "department": "finance",
        "job_title": "Finance Manager",
    },
    {
        "email": "finance2@nyftaa.com",
        "password": "password123",
        "name": "Michael Finance",
        "role": "manager",
        "department": "finance",
        "job_title": "Senior Finance Manager",
    },

    # HR
    {
        "email": "hr@nyftaa.com",
        "password": "password123",
        "name": "Emily HR",
        "role": "contributor",
        "department": "hr",
        "job_title": "HR Manager",
    },
    {
        "email": "hr2@nyftaa.com",
        "password": "password123",
        "name": "David HR",
        "role": "contributor",
        "department": "hr",
        "job_title": "HR Specialist",
    },

    # Contributors (Regular Employees)
    {
        "email": "employee@nyftaa.com",
        "password": "password123",
        "name": "Alex Employee",
        "role": "contributor",
        "department": "engineering",
        "job_title": "Software Engineer",
    },
    {
        "email": "employee2@nyftaa.com",
        "password": "password123",
        "name": "Maria Employee",
        "role": "contributor",
        "department": "design",
        "job_title": "UI/UX Designer",
    },
    {
        "email": "employee3@nyftaa.com",
        "password": "password123",
        "name": "Robert Employee",
        "role": "contributor",
        "department": "sales",
        "job_title": "Sales Executive",
    },

    # Viewers (Read-only)
    {
        "email": "viewer@nyftaa.com",
        "password": "password123",
        "name": "Lisa Viewer",
        "role": "viewer",
        "department": "marketing",
        "job_title": "Marketing Analyst",
    },
    {
        "email": "viewer2@nyftaa.com",
        "password": "password123",
        "name": "Tom Viewer",
        "role": "viewer",
        "department": "support",
        "job_title": "Support Specialist",
    },
]


async def seed_employees():
    """Seed employees into the database"""
    print("🔧 Seeding employees into database...")
    print(f"📝 Creating {len(EMPLOYEES_TO_SEED)} test employees\n")
    
    async with get_session() as db:
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for emp_data in EMPLOYEES_TO_SEED:
            try:
                # Check if user already exists
                result = await db.execute(
                    select(User).where(User.email == emp_data["email"])
                )
                existing_user = result.scalar_one_or_none()
                
                # Map frontend role to backend role
                backend_role = ROLE_MAPPING.get(emp_data["role"], "admin")
                
                if existing_user:
                    # Update existing user
                    existing_user.password_hash = AuthService.get_password_hash(emp_data["password"])
                    existing_user.name = emp_data["name"]
                    existing_user.role = backend_role
                    
                    # Update username if it's the email
                    if not existing_user.username:
                        existing_user.username = emp_data["email"].split("@")[0]
                    
                    print(f"✅ Updated user: {emp_data['email']} ({emp_data['role']} → {backend_role})")
                    updated_count += 1
                    
                    # Check if employee record exists
                    emp_result = await db.execute(
                        select(Employee).where(Employee.email == emp_data["email"])
                    )
                    existing_employee = emp_result.scalar_one_or_none()
                    
                    if existing_employee:
                        # Update employee record
                        existing_employee.name = emp_data["name"]
                        existing_employee.job_title = emp_data["job_title"]
                        existing_employee.department = emp_data["department"]
                        existing_employee.user_id = existing_user.id
                        print(f"   ↳ Updated employee record")
                    else:
                        # Create employee record
                        try:
                            employee = await Employee.create(
                                name=emp_data["name"],
                                email=emp_data["email"],
                                company_id=None,  # Set if you have org_id
                                phone=None,
                                job_title=emp_data["job_title"],
                                role=None,  # Employee role enum
                                department=emp_data["department"],
                                location=None,
                                bill_rate=None,
                                status=EmployeeStatus.ACTIVE.value,
                                user_id=existing_user.id,
                            )
                            await db.flush()
                            print(f"   ↳ Created employee record: {employee.employee_number}")
                        except Exception as e:
                            print(f"   ⚠️  Could not create employee record: {e}")
                            # Continue without employee record
                    
                else:
                    # Create new user
                    user = User(
                        email=emp_data["email"],
                        password_hash=AuthService.get_password_hash(emp_data["password"]),
                        role=backend_role,
                        name=emp_data["name"],
                        username=emp_data["email"].split("@")[0],  # Use email prefix as username
                    )
                    db.add(user)
                    await db.flush()
                    await db.refresh(user)
                    
                    print(f"✅ Created user: {emp_data['email']} ({emp_data['role']} → {backend_role})")
                    created_count += 1
                    
                    # Create employee record
                    try:
                        employee = await Employee.create(
                            name=emp_data["name"],
                            email=emp_data["email"],
                            company_id=None,  # Set if you have org_id
                            phone=None,
                            job_title=emp_data["job_title"],
                            role=None,  # Employee role enum
                            department=emp_data["department"],
                            location=None,
                            bill_rate=None,
                            status=EmployeeStatus.ACTIVE.value,
                            user_id=user.id,
                        )
                        await db.flush()
                        print(f"   ↳ Created employee record: {employee.employee_number}")
                    except Exception as e:
                        print(f"   ⚠️  Could not create employee record: {e}")
                        # Continue without employee record
                
            except Exception as e:
                print(f"❌ Error processing {emp_data['email']}: {e}")
                skipped_count += 1
                continue
        
        await db.commit()
        
        print(f"\n🎉 Seeding completed!")
        print(f"   ✅ Created: {created_count} users")
        print(f"   🔄 Updated: {updated_count} users")
        print(f"   ⏭️  Skipped: {skipped_count} users")
        print(f"\n📋 All passwords: password123")
        print(f"\n📖 Test credentials:")
        print(f"   Admin: admin@nyftaa.com / password123")
        print(f"   Manager: manager@nyftaa.com / password123")
        print(f"   Finance: finance@nyftaa.com / password123")
        print(f"   HR: hr@nyftaa.com / password123")
        print(f"   Employee: employee@nyftaa.com / password123")
        print(f"   Viewer: viewer@nyftaa.com / password123")


if __name__ == "__main__":
    asyncio.run(seed_employees())

