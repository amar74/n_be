import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import get_session
from app.models.user import User
from app.models.organization import Organization
from sqlalchemy import select

async def check_vendor():
    email = 'aedalkhlfaejhfk@gmail.com'
    
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User {email} not found in database!")
            return
        
        print(f"✅ User found:")
        print(f"   User ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Org ID: {user.org_id}")
        print(f"   Role: {user.role}")
        print()
        
        if not user.org_id:
            print("❌ User has NO org_id!")
            return
        
        print(f"🔍 Fetching organization {user.org_id}...")
        org_result = await session.execute(
            select(Organization).where(Organization.id == user.org_id)
        )
        org = org_result.scalar_one_or_none()
        
        if not org:
            print(f"❌ Organization {user.org_id} NOT FOUND in database!")
            print("   This is why /orgs/me is failing!")
            return
        
        print(f"✅ Organization found:")
        print(f"   Org ID: {org.id}")
        print(f"   Name: {org.name}")
        print(f"   Owner ID: {org.owner_id}")
        print(f"   Created At: {org.created_at}")

asyncio.run(check_vendor())
