from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json
import jwt
import os
import httpx
from datetime import datetime, timedelta

from app.db.session import get_session
from app.models.user import User
from app.services.supabase import verify_user_token

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


@router.get("/verify_supabase_token")
async def verify_supabase_token(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Verify token from Supabase and generate our own JWT"""
    print("Endpoint hit: /auth/verify_supabase_token")
    
    # Get the authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        sb_header = request.headers.get('sb-mzdvwfoepfagypseyvfh-auth-token')
        if not sb_header:
            print("No authentication token provided")
            raise HTTPException(status_code=401, detail="No authentication token provided")
        auth_token = sb_header
    else:
        auth_token = auth_header.replace('Bearer ', '')
    
    print(f"Processing auth token: {auth_token[:20]}...")
    
    try:
        # Verify the token with Supabase
        user_data = verify_user_token(auth_token)
        
        if not user_data:
            # Fallback to decoding token without verification
            print("Token verification failed with Supabase client, trying fallback...")
            decoded_token = jwt.decode(auth_token, options={"verify_signature": False})
            
            # Try to extract email from decoded token
            user_email = decoded_token.get('email')
            
            if not user_email and 'user_metadata' in decoded_token:
                user_metadata = decoded_token.get('user_metadata', {})
                if isinstance(user_metadata, dict):
                    user_email = user_metadata.get('email')
            
            if not user_email:
                print("No email found in token or metadata")
                raise HTTPException(status_code=401, detail="Invalid token - no email found")
        else:
            # Use the email from verified user data
            user_email = user_data.get('email')
            print(f"Token verified successfully for user {user_email}")
            
        # Check if user exists in our database or create them
        user = await User.get_by_email(session, user_email)
        
        if not user:
            # Create the user if they don't exist
            user = await User.create(session, user_email)
            print(f"Created new user with email {user_email}")
        else:
            print(f"Found existing user with email {user_email}")
        
        # Generate our own JWT token
        token_expiry = datetime.utcnow() + timedelta(days=30)
        payload = {
            "sub": str(user.id),
            "email": user_email,
            "exp": token_expiry
        }
        
        # Use a secret key from environment or create one
        secret_key = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        
        print(f"Generated JWT token for user {user_email}")
        return {
            "message": "Token verified successfully",
            "token": token,
            "user": user.to_dict(),
            "expires_at": token_expiry.isoformat()
        }
        
    except jwt.DecodeError:
        print("Invalid token format")
        raise HTTPException(status_code=401, detail="Invalid token format")
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error verifying token: {str(e)}")


@router.get("/me")
async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Get current authenticated user info"""
    print("Endpoint hit: /auth/me")
    print(f"Request headers: {request.headers}")
    
    # Get the authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        print("No valid Authorization header found")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Extract the token
    token = auth_header.replace('Bearer ', '')
    print("Hello: ",token)
    
    try:
        # First attempt to decode as a Supabase token
        try:
            # Decode without verification to extract email
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            
            # Check if this looks like a Supabase token
            is_supabase_token = ('iss' in decoded_token and 'supabase' in decoded_token['iss'])
            
            if is_supabase_token:
                print("Detected Supabase token")
                # Extract email from token
                user_email = decoded_token.get('email')
                
                if not user_email:
                    print("No email found in Supabase token")
                    raise HTTPException(status_code=401, detail="Invalid token - no email found")
                    
                # Look up user by email
                user = await User.get_by_email(session, user_email)
                
                if not user:
                    # Create new user if they don't exist in our database
                    print(f"User with email {user_email} not found, creating new user")
                    user = await User.create(session, user_email)
                
                print(f"Found user from Supabase token: {user.email}")
                return {"user": user.to_dict()}
                
        except (jwt.InvalidTokenError, KeyError) as e:
            print(f"Not a valid Supabase token, trying custom token: {str(e)}")
            # If not a valid Supabase token, continue to try as our custom JWT
        
        # Try as our custom JWT token
        secret_key = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        user_id = payload.get("sub")
        if not user_id:
            print("No user ID found in token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await User.get_by_id(session, int(user_id))
        if not user:
            print(f"User with ID {user_id} not found in database")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"Found user from custom JWT: {user.email}")
        return {"user": user.to_dict()}
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        print("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error verifying token: {str(e)}")