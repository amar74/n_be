from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.db.session import get_session
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/onsignup")
async def onsignup(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Handle user signup from external auth provider"""
    print("Endpoint hit: /auth/onsignup")
    
    body = await request.body()
    print('Request body: ', body)
    
    # Parse the JSON body
    body_data = json.loads(body)
    email = body_data.get('email')
    
    if email:
        # Check if user with this email already exists
        existing_user = await User.get_by_email(session, email)
        
        if existing_user:
            print(f"User with email {email} already exists")
            return {"message": "User already exists", "user": existing_user.to_dict()}
        else:
            # Create new user
            new_user = await User.create(session, email)
            print(f"New user created with email {email}")
            return {"message": "User created successfully", "user": new_user.to_dict()}
    else:
        print("No email provided in the request")
        return {"message": "Email is required", "error": "missing_email"}, 400


@router.post("/verify_supabase_token")
async def verify_supabase_token(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Verify token from Supabase"""
    print("Endpoint hit: /auth/verify_supabase_token")
    body = await request.body()
    print('Request body: ', body)
    return {"message": "Token verification endpoint hit successfully"}


@router.get("/me")
async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Get current authenticated user info"""
    print("Endpoint hit: /auth/me")
    return {"message": "Current user endpoint hit successfully"}