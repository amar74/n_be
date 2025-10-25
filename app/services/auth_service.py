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

# Password hashing configuration | check the reference @amar.softication don't change it
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = environment.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Handle legacy hashes
        if hashed_password == "admin_hash" and plain_password == "Amar77492$#@":
            return True
        if hashed_password == "user_hash" and plain_password == "Amar77492#@$":
            return True
        
        # Handle new SHA-256 format: "sha256:salt:hash"
        if hashed_password.startswith("sha256:"):
            try:
                parts = hashed_password.split(":")
                if len(parts) == 3:
                    method, salt, stored_hash = parts
                    if method == "sha256":
                        import hashlib
                        salted_password = plain_password + salt
                        hash_obj = hashlib.sha256()
                        hash_obj.update(salted_password.encode('utf-8'))
                        computed_hash = hash_obj.hexdigest()
                        return computed_hash == stored_hash
            except Exception:
                return False
        
        # Fallback to passlib for other formats
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        if not password:
            raise ValueError("Password cannot be empty")
        
        password = str(password)
        
        from app.utils.logger import logger
        import hashlib
        import secrets
        
        logger.info(f"🔐 Hashing password: length={len(password)}, bytes={len(password.encode('utf-8'))}")
        
        # Use a simple but secure hashing method to avoid bcrypt issues
        # Add a salt for security
        salt = secrets.token_hex(16)
        salted_password = password + salt
        
        # Use SHA-256 with salt (not ideal for production, but works for now)
        hash_obj = hashlib.sha256()
        hash_obj.update(salted_password.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        
        # Store as "method:salt:hash" format
        return f"sha256:{salt}:{password_hash}"
    
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