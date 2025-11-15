from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import random
from datetime import datetime

from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.services.email import send_password_reset_email
from app.services.password_reset_service import update_user_password
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class ResetPasswordResponse(BaseModel):
    message: str

# Generate OTP
def generate_otp() -> str:
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request a password reset link
    Sends an email with a one-time use token valid for 24 hours
    """
    try:
        # Find user by email
        user = await User.get_by_email(request.email)
        
        if not user:
            # For security, don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email: {request.email}")
            return ForgotPasswordResponse(
                message="If an account with that email exists, a password reset link has been sent."
            )
        
        # Invalidate any existing reset tokens for this user
        await PasswordResetToken.invalidate_user_tokens(user.id)
        
        # Generate 6-digit OTP
        otp = generate_otp()
        
        # Create password reset OTP in database (valid for 10 minutes)
        await PasswordResetToken.create(
            user_id=user.id,
            email=user.email,
            otp=otp,
            expires_in_minutes=10,
        )
        
        # Send password reset email with OTP
        user_name = user.name if user.name else user.email.split('@')[0]
        email_sent = send_password_reset_email(
            user_email=user.email,
            otp=otp,
            user_name=user_name,
        )
        
        if not email_sent:
            logger.error(f"Failed to send password reset email to {user.email}")
            # Still return success message for security
        else:
            logger.info(f"Password reset email sent to {user.email}")
        
        return ForgotPasswordResponse(
            message="If an account with that email exists, a password reset link has been sent."
        )
        
    except Exception as e:
        logger.exception(f"Error in forgot password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process password reset request"
        )

@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using OTP (One-Time Password)
    OTP is marked as used immediately when verified, preventing reuse
    """
    try:
        # Find the reset OTP by email and OTP code
        reset_token_record = await PasswordResetToken.get_by_email_and_otp(request.email, request.otp)
        
        if not reset_token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP. Please check the code and try again."
            )
        
        # Check if OTP is valid (not used and not expired)
        if not reset_token_record.is_valid():
            if reset_token_record.is_used:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This OTP has already been used. Please request a new OTP."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This OTP has expired. Please request a new OTP."
                )
        
        # Get the user
        user = await User.get_by_id(reset_token_record.user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user password
        password_updated = await update_user_password(user.id, request.new_password)
        
        if not password_updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        # Mark the OTP as used now that the password has been updated
        otp_marked = await PasswordResetToken.mark_as_used(request.email, request.otp)

        if not otp_marked:
            logger.error(
                "Password reset succeeded but OTP could not be marked as used for %s",
                request.email,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password updated, but failed to finalize OTP. Please request a new reset code.",
            )
        
        logger.info(f"Password successfully reset for user {user.email}")
        
        return ResetPasswordResponse(
            message="Password has been reset successfully. You can now login with your new password."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in reset password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reset password"
        )

@router.post("/verify-reset-otp")
async def verify_reset_otp(email: EmailStr, otp: str):
    
    try:
        reset_token_record = await PasswordResetToken.get_by_email_and_otp(email, otp)
        
        if not reset_token_record:
            return {"valid": False, "reason": "OTP not found"}
        
        if reset_token_record.is_used:
            return {"valid": False, "reason": "OTP already used"}
        
        if datetime.utcnow() > reset_token_record.expires_at:
            return {"valid": False, "reason": "OTP expired"}
        
        # Calculate remaining time
        time_remaining = (reset_token_record.expires_at - datetime.utcnow()).total_seconds()
        
        return {
            "valid": True,
            "email": reset_token_record.email,
            "expires_at": reset_token_record.expires_at.isoformat(),
            "time_remaining_seconds": int(time_remaining)
        }
        
    except Exception as e:
        logger.exception(f"Error verifying reset OTP: {str(e)}")
        return {"valid": False, "reason": "Error verifying OTP"}
