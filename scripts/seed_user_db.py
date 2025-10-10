"""
Script to create a user directly in PostgreSQL database.
This bypasses Supabase and creates the user directly in the database.
"""
import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.user import User
from app.db.session import get_transaction
from app.schemas.user import Roles


async def seed_user(email: str):
    """Create a user directly in PostgreSQL"""
    
    try:
        print("=" * 60)
        print("🌱 Seeding User to PostgreSQL Database")
        print("=" * 60)
        print(f"Email: {email}")
        print("")
        
        # Check if user already exists
        print(f"🔍 Checking if user exists...")
        existing_user = await User.get_by_email(email)
        
        if existing_user:
            print(f"⚠️  User {email} already exists in database!")
            print(f"   User ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Role: {existing_user.role}")
            if existing_user.org_id:
                print(f"   Organization ID: {existing_user.org_id}")
            print("")
            print("✅ You can login with this email")
            return True
        
        # Create new user
        print(f"🔄 Creating user in database...")
        new_user = await User.create(email=email)
        
        print(f"✅ User created successfully in PostgreSQL!")
        print(f"   User ID: {new_user.id}")
        print(f"   Email: {new_user.email}")
        print(f"   Role: {new_user.role}")
        print("")
        
        print("=" * 60)
        print("✅ Seeding Complete!")
        print("=" * 60)
        print("")
        print("⚠️  IMPORTANT: You still need to create this user in Supabase")
        print("   to be able to login through the frontend.")
        print("")
        print("📝 To create in Supabase:")
        print("   1. Go to https://supabase.com")
        print("   2. Open your project")
        print("   3. Go to Authentication > Users")
        print("   4. Click 'Add user'")
        print(f"   5. Email: {email}")
        print(f"   6. Password: Amar77492#@$")
        print("   7. Check 'Auto Confirm User'")
        print("   8. Click 'Create user'")
        print("")
        print("🚀 Then you can login at:")
        print("   http://localhost:5173/auth/login")
        print("")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main function"""
    email = "amar74.soft@gmail.com"
    success = await seed_user(email)
    
    if not success:
        print("")
        print("=" * 60)
        print("❌ Seeding Failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
