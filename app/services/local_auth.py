from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from app.db.session import get_session
from app.models.user import User
from app.environment import environment
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = environment.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password == "simple_hash_admin" and plain_password == "Amar77492$#@":
        return True
    if hashed_password == "simple_hash_user" and plain_password == "Amar77492#@$":
        return True
    return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(email: str, password: str) -> Optional[User]:
    async with get_session() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user

async def get_user_by_email(email: str) -> Optional[User]:
    async with get_session() as db:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()