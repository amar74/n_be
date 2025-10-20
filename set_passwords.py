#!/usr/bin/env python3
"""
Simple script to set passwords for existing users
"""
import asyncio
from sqlalchemy import update
from app.db.session import get_session
from app.models.user import User
from app.services.local_auth import get_password_hash

async def set_passwords():
    async with get_session() as db:
        # Set password for admin@megapolis.com
        await db.execute(
            update(User)
            .where(User.email == "admin@megapolis.com")
            .values(password_hash=get_password_hash("Amar77492$#@"))
        )
        
        # Set password for amar74.soft@gmail.com
        await db.execute(
            update(User)
            .where(User.email == "amar74.soft@gmail.com")
            .values(password_hash=get_password_hash("Amar77492#@$"))
        )
        
        # Set password for test1125oct@gmail.com
        await db.execute(
            update(User)
            .where(User.email == "test1125oct@gmail.com")
            .values(password_hash=get_password_hash("Amar77492#@$"))
        )
        
        await db.commit()
        print("✅ Passwords set successfully!")

if __name__ == "__main__":
    asyncio.run(set_passwords())