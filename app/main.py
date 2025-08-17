from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.db.session import get_session
from app.models.user import User, UserCreateRequest, UserUpdateRequest

app = FastAPI(title="Megapolis API", version="0.1.0")


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello, world!"}


# User CRUD endpoints - MC Architecture (Controller directly uses Model)
@app.post("/users/", status_code=201)
async def create_user(
    user_data: UserCreateRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Create a new user"""
    # Check if user with email already exists
    existing_user = await User.get_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = await User.create(session, user_data.email)
    return user.to_dict()


@app.get("/users/")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    session: AsyncSession = Depends(get_session)
) -> List[Dict[str, Any]]:
    """Get all users with pagination"""
    users = await User.get_all(session, skip=skip, limit=limit)
    return [user.to_dict() for user in users]


@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get a specific user by ID"""
    user = await User.get_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Update an existing user"""
    user = await User.get_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await user.update(session, email=user_data.email)
    return updated_user.to_dict()


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    """Delete a user"""
    user = await User.get_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user.delete(session)
    return {"message": "User deleted successfully"}


