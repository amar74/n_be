#!/usr/bin/env python3
"""
Seed script to create 3-4 test employees with different roles for testing employee dashboard
All passwords: password123

Run with: python seed_test_employees.py
"""
import asyncio
from app.services.auth_service import AuthService
from app.db.session import get_session
from app.models.user import User, generate_short_user_id
from app.models.employee import Employee, EmployeeStatus
from app.models.organization import Organization
from sqlalchemy import select
from typing import Optional
import uuid

# Test employees to seed (3-4 with different RBAC roles)
# According to RBAC documentation: platform_admin, org_admin, manager, contributor, viewer
TEST_EMPLOYEES = [
    {
        "email": "test.manager@test.com",
        "password": "password123",
        "name": "Test Manager",
        "role": "manager",  # RBAC manager role
        "department": "Operations",
        "job_title": "Operations Manager",
        "phone": "+1-555-0101",
    },
    {
        "email": "test.contributor@test.com",
        "password": "password123",
        "name": "Test Contributor",
        "role": "contributor",  # RBAC contributor role (standard employee)
        "department": "Engineering",
        "job_title": "Software Engineer",
        "phone": "+1-555-0102",
    },
    {
        "email": "test.sales@test.com",
        "password": "password123",
        "name": "Test Sales",
        "role": "contributor",  # RBAC contributor role (sales employee)
        "department": "Sales",
        "job_title": "Sales Executive",
        "phone": "+1-555-0103",
    },
    {
        "email": "test.viewer@test.com",
        "password": "password123",
        "name": "Test Viewer",
        "role": "viewer",  # RBAC viewer role (read-only)
        "department": "Marketing",
        "job_title": "Marketing Analyst",
        "phone": "+1-555-0104",
    },
]


async def seed_test_employees():
    """Seed 3-4 test employees into the database"""
    print("🔧 Seeding test employees into database...")
    print(f"📝 Creating {len(TEST_EMPLOYEES)} test employees\n")
    
    async with get_session() as db:
        # Get the first organization (or create a default one if none exists)
        org_result = await db.execute(select(Organization).limit(1))
        org = org_result.scalar_one_or_none()
        
        if not org:
            print("⚠️  No organization found. Creating a default organization...")
            org = Organization(
                name="Test Organization",
                owner_id=uuid.uuid4(),  # Placeholder owner
            )
            db.add(org)
            await db.flush()
            await db.refresh(org)
            print(f"✅ Created organization: {org.name} (ID: {org.id})")
        else:
            print(f"✅ Using organization: {org.name} (ID: {org.id})")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for emp_data in TEST_EMPLOYEES:
            try:
                # Check if user already exists
                result = await db.execute(
                    select(User).where(User.email == emp_data["email"])
                )
                existing_user = result.scalar_one_or_none()
                
                # Helper to get a unique short_id
                async def ensure_short_id(user: User):
                    if user.short_id:
                        return
                    # generate unique short_id
                    for _ in range(10):
                        candidate = generate_short_user_id()
                        exists = await db.scalar(select(User).where(User.short_id == candidate))
                        if not exists:
                            user.short_id = candidate
                            return
                    raise RuntimeError("Unable to generate unique short_id")

                if existing_user:
                    # Update existing user
                    existing_user.password_hash = AuthService.get_password_hash(emp_data["password"])
                    existing_user.name = emp_data["name"]
                    existing_user.role = emp_data["role"]
                    existing_user.org_id = org.id
                    await ensure_short_id(existing_user)
                    
                    # Update username if it's the email
                    if not existing_user.username:
                        existing_user.username = emp_data["email"].split("@")[0]
                    
                    print(f"✅ Updated user: {emp_data['email']} (Role: {emp_data['role']})")
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
                        existing_employee.company_id = org.id
                        existing_employee.status = EmployeeStatus.ACTIVE.value
                        print(f"   ↳ Updated employee record: {existing_employee.employee_number}")
                    else:
                        # Create employee record directly in the same session
                        try:
                            # Generate employee number
                            org_name = org.name if org else None
                            employee_number = None
                            for offset in range(10):
                                candidate = await Employee._next_employee_number(db, org_name, emp_data["name"], offset=offset)
                                existing = await db.execute(
                                    select(Employee).where(Employee.employee_number == candidate)
                                )
                                if not existing.scalar_one_or_none():
                                    employee_number = candidate
                                    break
                            
                            if not employee_number:
                                raise RuntimeError("Unable to generate unique employee number")
                            
                            employee = Employee(
                                name=emp_data["name"],
                                email=emp_data["email"],
                                company_id=org.id,
                                phone=emp_data.get("phone"),
                                job_title=emp_data["job_title"],
                                role=None,  # Employee role enum
                                department=emp_data["department"],
                                location=None,
                                bill_rate=None,
                                status=EmployeeStatus.ACTIVE.value,
                                user_id=existing_user.id,
                                employee_number=employee_number,
                            )
                            db.add(employee)
                            await db.flush()
                            print(f"   ↳ Created employee record: {employee.employee_number}")
                        except Exception as e:
                            print(f"   ⚠️  Could not create employee record: {e}")
                            # Continue without employee record
                    
                else:
                    # Create new user
                    # Generate unique short_id first
                    short_id = generate_short_user_id()
                    while await db.scalar(select(User).where(User.short_id == short_id)):
                        short_id = generate_short_user_id()
                    
                    user = User(
                        email=emp_data["email"],
                        password_hash=AuthService.get_password_hash(emp_data["password"]),
                        role=emp_data["role"],
                        name=emp_data["name"],
                        username=emp_data["email"].split("@")[0],  # Use email prefix as username
                        org_id=org.id,
                        short_id=short_id,
                    )
                    db.add(user)
                    await db.flush()
                    await db.refresh(user)
                    
                    print(f"✅ Created user: {emp_data['email']} (Role: {emp_data['role']})")
                    created_count += 1
                    
                    # Create employee record directly in the same session
                    try:
                        # Generate employee number
                        org_name = org.name if org else None
                        employee_number = None
                        for offset in range(10):
                            candidate = await Employee._next_employee_number(db, org_name, emp_data["name"], offset=offset)
                            existing = await db.execute(
                                select(Employee).where(Employee.employee_number == candidate)
                            )
                            if not existing.scalar_one_or_none():
                                employee_number = candidate
                                break
                        
                        if not employee_number:
                            raise RuntimeError("Unable to generate unique employee number")
                        
                        employee = Employee(
                            name=emp_data["name"],
                            email=emp_data["email"],
                            company_id=org.id,
                            phone=emp_data.get("phone"),
                            job_title=emp_data["job_title"],
                            role=None,  # Employee role enum
                            department=emp_data["department"],
                            location=None,
                            bill_rate=None,
                            status=EmployeeStatus.ACTIVE.value,
                            user_id=user.id,
                            employee_number=employee_number,
                        )
                        db.add(employee)
                        await db.flush()
                        print(f"   ↳ Created employee record: {employee.employee_number}")
                    except Exception as e:
                        print(f"   ⚠️  Could not create employee record: {e}")
                        # Continue without employee record
                
            except Exception as e:
                print(f"❌ Error processing {emp_data['email']}: {e}")
                import traceback
                traceback.print_exc()
                skipped_count += 1
                continue
        
        await db.commit()
        
        print(f"\n🎉 Seeding completed!")
        print(f"   ✅ Created: {created_count} users")
        print(f"   🔄 Updated: {updated_count} users")
        print(f"   ⏭️  Skipped: {skipped_count} users")
        print(f"\n📋 All passwords: password123")
        print(f"\n📖 Test credentials (RBAC roles):")
        print(f"   1. Manager (RBAC): test.manager@test.com / password123")
        print(f"   2. Contributor (RBAC): test.contributor@test.com / password123")
        print(f"   3. Sales Contributor (RBAC): test.sales@test.com / password123")
        print(f"   4. Viewer (RBAC): test.viewer@test.com / password123")


if __name__ == "__main__":
    asyncio.run(seed_test_employees())

