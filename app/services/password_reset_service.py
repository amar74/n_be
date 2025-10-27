import secrets
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.utils.logger import logger

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def update_user_password(user_id: UUID, new_password: str) -> bool:
    try:
        user = await User.get_by_id(str(user_id))
        
        if not user:
            return False
        
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update user password using AuthService
        from app.services.auth_service import AuthService
        from app.db.session import get_transaction
        
        async with get_transaction() as db:
            from sqlalchemy import update as sql_update
            from app.models.user import User as UserModel
            
            await db.execute(
                sql_update(UserModel)
                .where(UserModel.id == user_id)
                .values(password_hash=hashed_password)
            )
            await db.flush()
        
        logger.info(f"Password updated successfully for user {user.email}")
        return True
        
    except Exception as e:
        logger.exception(f"Error updating user password: {str(e)}")
        return False
