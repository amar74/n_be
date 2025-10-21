#!/usr/bin/env python3
import asyncio
import asyncpg
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def setup_users():
    print("🔧 Setting up users directly in database...")
    
    # Database connection
    conn = await asyncpg.connect("postgresql://postgres:postgres123@localhost:5432/megapolis_dev")
    
    try:
        # Users to create/update
        users = [
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
        
        for user_data in users:
            # Hash the password
            password_hash = pwd_context.hash(user_data["password"])
            
            # Check if user exists
            existing_user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", user_data["email"]
            )
            
            if existing_user:
                # Update existing user
                await conn.execute(
                    "UPDATE users SET password_hash = $1, role = $2 WHERE email = $3",
                    password_hash, user_data["role"], user_data["email"]
                )
                print(f"✅ Updated user {user_data['email']}")
            else:
                # Create new user
                await conn.execute(
                    "INSERT INTO users (id, email, password_hash, role) VALUES (gen_random_uuid(), $1, $2, $3)",
                    user_data["email"], password_hash, user_data["role"]
                )
                print(f"✅ Created user {user_data['email']}")
        
        print("🎉 User setup completed successfully!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(setup_users())