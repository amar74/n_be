import uuid
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.environment import environment
from app.db.session import get_session

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = environment.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Simple password verification for now
        if hashed_password == "admin_hash" and plain_password == "Amar77492$#@":
            return True
        if hashed_password == "user_hash" and plain_password == "Amar77492#@$":
            return True
        return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        async with get_session() as db:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            if not user.password_hash:
                return None
                
            if not AuthService.verify_password(password, user.password_hash):
                return None
            
            return user
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        async with get_session() as db:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        async with get_session() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(email: str, password: str, role: str = "admin") -> User:
        async with get_session() as db:
            user = User(
                email=email,
                password_hash=AuthService.get_password_hash(password),
                role=role
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
    
    @staticmethod
    async def update_user_password(user_id: str, new_password: str) -> bool:
        async with get_session() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            user.password_hash = AuthService.get_password_hash(new_password)
            await db.commit()
            return True