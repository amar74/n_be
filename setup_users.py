import asyncio
from app.services.auth_service import AuthService
from app.db.session import get_session
from app.models.user import User
from sqlalchemy import select

async def setup_initial_users():
    print("🔧 Setting up initial users...")
    
    # Users to create
    users_to_create = [
        {
            "email": "admin@megapolis.com",
            "password": "Amar77492$#@",
            "role": "super_admin"
        },
        {
            "email": "amar74.soft@gmail.com", 
            "password": "Amar77492#@$",
            "role": "admin"
        },
        {
            "email": "test1125oct@gmail.com",
            "password": "Amar77492#@$", 
            "role": "admin"
        }
    ]
    
    async with get_session() as db:
        for user_data in users_to_create:
            # Check if user already exists
            result = await db.execute(select(User).where(User.email == user_data["email"]))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Update password if user exists
                existing_user.password_hash = AuthService.get_password_hash(user_data["password"])
                print(f"✅ Updated password for {user_data['email']}")
            else:
                # Create new user
                user = User(
                    email=user_data["email"],
                    password_hash=AuthService.get_password_hash(user_data["password"]),
                    role=user_data["role"]
                )
                db.add(user)
                print(f"✅ Created user {user_data['email']} with role {user_data['role']}")
        
        await db.commit()
        print("🎉 User setup completed successfully!")

if __name__ == "__main__":
    asyncio.run(setup_initial_users())