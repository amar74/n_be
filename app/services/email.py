
from typing import Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.environment import environment
from app.utils.logger import logger

def send_vendor_invitation_email(
    vendor_id: str,
    vendor_name: str,
    company_name: str,
    vendor_email: str,
    password: str,
    login_url: str
) -> bool:

    try:
        subject = "Vendor Creation Confirmation"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .header {{
                    background-color: #161950;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .credentials {{
                    background-color: #fff;
                    padding: 15px;
                    margin: 20px 0;
                    border-left: 4px solid #161950;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #161950;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Vendor Creation Confirmation</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{vendor_name}</strong>,</p>
                    <p>
                        We're pleased to inform you that your vendor profile has been successfully created in our system.
                    </p>
                    
                    <div class="credentials">
                        <p><strong>Vendor ID:</strong> {vendor_id}</p>
                        <p><strong>Company:</strong> {company_name}</p>
                        <p><strong>User ID (Email):</strong> {vendor_email}</p>
                        <p><strong>Password:</strong> {password}</p>
                        <p><strong>Login URL:</strong> <a href="{login_url}">{login_url}</a></p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{login_url}" class="button">Login to Vendor Portal</a>
                    </div>
                    
                    <p>
                        You will shortly receive further details regarding documentation, onboarding, and payment processes.
                    </p>
                    
                    <p>
                        Thank you for partnering with us.
                    </p>
                    
                    <p>Warm regards,<br><strong>Nyftaa Team</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>&copy; 2025 Nyftaa. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Vendor Creation Confirmation

Dear {vendor_name},

We're pleased to inform you that your vendor profile has been successfully created in our system.

Vendor ID: {vendor_id}
Company: {company_name}
User ID (Email): {vendor_email}
Password: {password}
Login URL: {login_url}

You will shortly receive further details regarding documentation, onboarding, and payment processes.

Thank you for partnering with us.

Warm regards,
Nyftaa Team
        """
        
        return _send_email_via_smtp(vendor_email, subject, text_body, html_body)
        
    except Exception as e:
        logger.exception(f"Error preparing vendor invitation email: {str(e)}")
        return False

def send_password_reset_email(
    user_email: str,
    otp: str,
    user_name: str = "User",
) -> bool:
    try:
        subject = "OTP for Password Reset"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .header {{
                    background-color: #161950;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .otp-box {{
                    background-color: #fff;
                    border: 2px dashed #161950;
                    padding: 20px;
                    margin: 20px 0;
                    text-align: center;
                    border-radius: 8px;
                }}
                .otp-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #161950;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 12px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>OTP for Password Reset</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{user_name}</strong>,</p>
                    <p>
                        We received a request to reset your password. Please use the following One-Time Password (OTP) to complete the reset process:
                    </p>
                    
                    <div class="otp-box">
                        <p style="margin: 0 0 10px 0; color: #667085; font-size: 14px;">Your OTP</p>
                        <div class="otp-code">{otp}</div>
                    </div>
                    
                    <div class="warning">
                        <p style="margin: 0; font-weight: 600; color: #856404;">⚠️ Security Notice:</p>
                        <ul style="margin: 8px 0 0 0; padding-left: 20px; color: #856404;">
                            <li>This OTP will be <strong>valid for the next 10 minutes</strong></li>
                            <li>Do not share it with anyone for security reasons</li>
                        </ul>
                    </div>
                    
                    <p>
                        If you didn't request this, please ignore this email.
                    </p>
                    
                    <p>Best regards,<br><strong>Nyftaa Team</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>&copy; 2025 Megapolis Advisory. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
OTP for Password Reset

Dear {user_name},

We received a request to reset your password. Please use the following One-Time Password (OTP) to complete the reset process:

OTP: {otp}

This OTP will be valid for the next 10 minutes. Do not share it with anyone for security reasons.

If you didn't request this, please ignore this email.

Best regards,
Nyftaa Team
        """
        
        return _send_email_via_smtp(user_email, subject, text_body, html_body)
        
    except Exception as e:
        logger.exception(f"Error preparing password reset email: {str(e)}")
        return False

def send_vendor_welcome_email(
    vendor_name: str,
    company_name: str,
    vendor_email: str,
) -> bool:
    try:
        subject = f"Welcome Onboard to {company_name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                .header {{
                    background-color: #161950;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome Onboard to {company_name}</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{vendor_name}</strong>,</p>
                    <p>
                        Welcome to <strong>{company_name}!</strong> We're thrilled to have you join our team.
                    </p>
                    
                    <p>
                        Your employee account has been successfully created. You can log in using your registered email and the credentials shared separately.
                    </p>
                    
                    <p>
                        Please take a moment to explore our onboarding portal and review the welcome resources to get started.
                    </p>
                    
                    <p>
                        We look forward to achieving great milestones together!
                    </p>
                    
                    <p>Warm regards,<br><strong>HR Team</strong><br><strong>{company_name}</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>&copy; 2025 {company_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Welcome Onboard to {company_name}

Dear {vendor_name},

Welcome to {company_name}! We're thrilled to have you join our team.

Your employee account has been successfully created. You can log in using your registered email and the credentials shared separately.

Please take a moment to explore our onboarding portal and review the welcome resources to get started.

We look forward to achieving great milestones together!

Warm regards,
HR Team
{company_name}
        """
        
        return _send_email_via_smtp(vendor_email, subject, text_body, html_body)
        
    except Exception as e:
        logger.exception(f"Error preparing vendor welcome email: {str(e)}")
        return False

def _send_email_via_smtp(to_email: str, subject: str, text_body: str, html_body: str) -> bool:
    """
    Internal function to send email via SMTP
    Configure your email settings in environment variables
    """
    try:
        smtp_host = getattr(environment, 'SMTP_HOST', None)
        smtp_port = getattr(environment, 'SMTP_PORT', 587)
        smtp_user = getattr(environment, 'SMTP_USER', None)
        smtp_password = getattr(environment, 'SMTP_PASSWORD', None)
        from_email = getattr(environment, 'FROM_EMAIL', smtp_user)
        
        if not smtp_host or not smtp_user:
            logger.warning(
                f"Email not configured. Would send to {to_email}: {subject}"
            )
            logger.info(f"Email content (text): {text_body[:200]}...")
            return True  # Return True in development mode
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = to_email
        
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
        
        return True
        
    except Exception as e:
        logger.exception(f"Error sending email via SMTP: {str(e)}")
        return False
