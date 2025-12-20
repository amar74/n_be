import uuid
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy import select, text, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.environment import environment
from app.db.session import get_session
from app.utils.logger import logger

# Password hashing configuration | check the reference @amar.softication don't change it
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = environment.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours (changed from 30 minutes to prevent frequent logouts)

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if environment.ENVIRONMENT == "dev":
            if hashed_password == "admin_hash" and plain_password == "Amar77492$#@":
                logger.warning("Using hardcoded password - SECURITY RISK in production!")
                return True
            if hashed_password == "user_hash" and plain_password == "Amar77492#@$":
                logger.warning("Using hardcoded password - SECURITY RISK in production!")
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
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        try:
            hashed = pwd_context.hash(password)
            logger.info("Password hashed using bcrypt")
            return hashed
        except Exception as e:
            logger.warning(f"Bcrypt hashing failed, using SHA-256 fallback: {e}")
            import hashlib
            import secrets
            
            salt = secrets.token_hex(16)
            salted_password = password + salt
            hash_obj = hashlib.sha256()
            hash_obj.update(salted_password.encode('utf-8'))
            password_hash = hash_obj.hexdigest()
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
    async def authenticate_user(email_or_username: str, password: str) -> Optional[User]:
        """
        Authenticate user by username OR email
        - Employees login with username (employee_number like EMP-12345)
        - Vendors/Admins login with email
        """
        from sqlalchemy import or_
        async with get_session() as db:
            username_column_exists = False

            try:
                column_check = await db.execute(
                    text(
                        """
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'users'
                          AND column_name = 'username'
                        LIMIT 1
                        """
                    )
                )
                username_column_exists = column_check.scalar_one_or_none() is not None
            except Exception as exc:
                from app.utils.logger import logger
                logger.warning("Failed to verify users.username column presence: %s", exc)
                username_column_exists = False

            selectable_columns = [
                User.id,
                User.short_id,
                User.email,
                User.name,
                User.phone,
                User.bio,
                User.address,
                User.city,
                User.state,
                User.zip_code,
                User.country,
                User.timezone,
                User.language,
                User.org_id,
                User.role,
                User.formbricks_user_id,
                User.password_hash,
                User.created_at,
                User.updated_at,
                User.last_login,
            ]

            if username_column_exists:
                selectable_columns.append(User.username)

            query = select(*selectable_columns)

            if username_column_exists:
                query = query.where(
                    or_(
                        User.email == email_or_username,
                        User.username == email_or_username,
                    )
                )
            else:
                query = query.where(User.email == email_or_username)

            result = await db.execute(query)
            row = result.mappings().first()

            if not row:
                return None

            user = User()
            for key, value in row.items():
                setattr(user, key, value)
            
            if not user:
                return None
            
            if not user.password_hash:
                from app.utils.logger import logger
                logger.warning(f"User {email_or_username} has no password hash")
                return None
                
            password_valid = AuthService.verify_password(password, user.password_hash)
            if not password_valid:
                from app.utils.logger import logger
                logger.warning(f"Password verification failed for user {email_or_username}")
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
    async def create_user(
        email: str, 
        password: str, 
        role: str = "admin",
        name: str = None,
        org_id: uuid.UUID = None,
        username: str = None  # Employee code for employees, None for vendors/admins
    ) -> User:
        from app.models.user import generate_short_user_id
        from sqlalchemy import select
        
        async with get_session() as db:
            # Generate unique short_id
            short_id = generate_short_user_id()
            
            # Check if short_id already exists and regenerate if needed
            while True:
                existing = await db.execute(select(User).where(User.short_id == short_id))
                if not existing.scalar_one_or_none():
                    break
                short_id = generate_short_user_id()
            
            user = User(
                email=email,
                username=username,  # Will be employee_number for employees, None for vendors
                password_hash=AuthService.get_password_hash(password),
                role=role,
                name=name,
                org_id=org_id,
                short_id=short_id
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
    
    @staticmethod
    async def update_user_profile(
        user_id: str, 
        name: Optional[str] = None,
        phone: Optional[str] = None,
        bio: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        country: Optional[str] = None,
        timezone: Optional[str] = None,
        language: Optional[str] = None
    ) -> bool:
        """Update user profile information"""
        async with get_session() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            if name is not None:
                user.name = name
            if phone is not None:
                user.phone = phone
            if bio is not None:
                user.bio = bio
            if address is not None:
                user.address = address
            if city is not None:
                user.city = city
            if state is not None:
                user.state = state
            if zip_code is not None:
                user.zip_code = zip_code
            if country is not None:
                user.country = country
            if timezone is not None:
                user.timezone = timezone
            if language is not None:
                user.language = language
            
            await db.commit()
            return True
