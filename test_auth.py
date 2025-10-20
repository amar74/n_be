#!/usr/bin/env python3
"""
Simple test script to verify authentication works
"""
import asyncio
from app.services.local_auth import authenticate_user

async def test_auth():
    print("Testing authentication...")
    
    # Test admin user
    user = await authenticate_user("admin@megapolis.com", "Amar77492$#@")
    if user:
        print(f"✅ Admin login successful: {user.email}, role: {user.role}")
    else:
        print("❌ Admin login failed")
    
    # Test regular user
    user = await authenticate_user("amar74.soft@gmail.com", "Amar77492#@$")
    if user:
        print(f"✅ User login successful: {user.email}, role: {user.role}")
    else:
        print("❌ User login failed")

if __name__ == "__main__":
    asyncio.run(test_auth())