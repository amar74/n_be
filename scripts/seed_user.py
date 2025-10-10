"""
Script to create a user in Supabase for testing/seeding purposes.
This creates a user in Supabase Auth, which will then be synced to PostgreSQL on first login.
"""
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_supabase_user(email: str, password: str):
    """Create a user in Supabase using Admin API"""
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_service_key:
        print("❌ Error: Missing Supabase credentials in .env file")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    try:
        # Create Supabase client with service role key (admin access)
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        print(f"🔄 Creating user in Supabase: {email}")
        
        # Create user with auto-confirm enabled
        response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Auto-confirm the email
            "user_metadata": {
                "created_via": "seed_script"
            }
        })
        
        if response.user:
            print(f"✅ User created successfully in Supabase!")
            print(f"   User ID: {response.user.id}")
            print(f"   Email: {response.user.email}")
            print(f"   Email Confirmed: {response.user.email_confirmed_at is not None}")
            print("")
            print("🎉 You can now login with:")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print("")
            print("📝 Note: User will be automatically created in PostgreSQL on first login")
            return True
        else:
            print("❌ Failed to create user - no user returned")
            return False
            
    except Exception as e:
        error_msg = str(e)
        
        # Check for specific error cases
        if "already been registered" in error_msg or "already exists" in error_msg.lower():
            print(f"⚠️  User {email} already exists in Supabase")
            print("   You can use this email to login directly")
            return True
        else:
            print(f"❌ Error creating user: {error_msg}")
            return False


def main():
    """Main function to seed the user"""
    
    # User credentials
    email = "amar74.soft@gmail.com"
    password = "Amar77492#@$"
    
    print("=" * 60)
    print("🌱 Seeding User to Supabase")
    print("=" * 60)
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    print("")
    
    success = create_supabase_user(email, password)
    
    if success:
        print("")
        print("=" * 60)
        print("✅ Seeding Complete!")
        print("=" * 60)
        print("")
        print("🚀 Next Steps:")
        print("   1. Go to http://localhost:5173/auth/login")
        print(f"   2. Login with email: {email}")
        print("   3. User will be created in PostgreSQL automatically")
        print("")
    else:
        print("")
        print("=" * 60)
        print("❌ Seeding Failed!")
        print("=" * 60)
        print("")
        print("Please check your Supabase credentials in .env file")
        sys.exit(1)


if __name__ == "__main__":
    main()
