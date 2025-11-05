
from typing import Dict, Optional
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

def send_vendor_creation_email(
    vendor_email: str,
    vendor_name: str,
    password: str,
    login_url: str,
    organization_name: Optional[str] = None,
) -> bool:
    """
    Send email to vendor when super admin creates them with all credentials
    """
    try:
        subject = "Your Vendor Account Has Been Created"
        
        vendor_display_name = vendor_name if vendor_name else vendor_email.split('@')[0]
        
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
                    padding: 20px;
                    margin: 20px 0;
                    border-left: 4px solid #161950;
                    border-radius: 4px;
                }}
                .credential-row {{
                    padding: 10px 0;
                    border-bottom: 1px solid #eee;
                }}
                .credential-row:last-child {{
                    border-bottom: none;
                }}
                .credential-label {{
                    font-weight: 600;
                    color: #555;
                    display: inline-block;
                    width: 140px;
                }}
                .credential-value {{
                    color: #161950;
                    font-weight: 500;
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
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 12px;
                    margin: 15px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Vendor Account Created Successfully</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{vendor_display_name}</strong>,</p>
                    <p>
                        Your vendor account has been successfully created by the system administrator. 
                        Below are your login credentials and important information:
                    </p>
                    
                    <div class="credentials">
                        <div class="credential-row">
                            <span class="credential-label">Email Address:</span>
                            <span class="credential-value">{vendor_email}</span>
                        </div>
                        <div class="credential-row">
                            <span class="credential-label">Password:</span>
                            <span class="credential-value">{password}</span>
                        </div>
                        {f'<div class="credential-row"><span class="credential-label">Organization:</span><span class="credential-value">{organization_name}</span></div>' if organization_name else ''}
                        <div class="credential-row">
                            <span class="credential-label">Login URL:</span>
                            <span class="credential-value"><a href="{login_url}">{login_url}</a></span>
                        </div>
                    </div>
                    
                    <div class="warning">
                        <p style="margin: 0; font-weight: 600; color: #856404;">🔒 Security Notice:</p>
                        <ul style="margin: 8px 0 0 0; padding-left: 20px; color: #856404;">
                            <li>Please change your password after first login</li>
                            <li>Do not share your credentials with anyone</li>
                            <li>Keep this email secure for your records</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{login_url}" class="button">Login to Your Account</a>
                    </div>
                    
                    <p>
                        <strong>Next Steps:</strong>
                    </p>
                    <ol>
                        <li>Log in using the credentials provided above</li>
                        <li>Create your organization profile (if not already assigned)</li>
                        <li>Complete your profile setup</li>
                        <li>Start using the platform</li>
                    </ol>
                    
                    <p>
                        If you have any questions or need assistance, please contact our support team.
                    </p>
                    
                    <p>Warm regards,<br><strong>Megapolis Advisory Team</strong></p>
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
Vendor Account Created Successfully

Dear {vendor_display_name},

Your vendor account has been successfully created by the system administrator. 
Below are your login credentials and important information:

Email Address: {vendor_email}
Password: {password}
{f'Organization: {organization_name}' if organization_name else ''}
Login URL: {login_url}

🔒 Security Notice:
- Please change your password after first login
- Do not share your credentials with anyone
- Keep this email secure for your records

Next Steps:
1. Log in using the credentials provided above
2. Create your organization profile (if not already assigned)
3. Complete your profile setup
4. Start using the platform

If you have any questions or need assistance, please contact our support team.

Warm regards,
Megapolis Advisory Team

---
This is an automated email. Please do not reply to this message.
© 2025 Megapolis Advisory. All rights reserved.
        """
        
        return _send_email_via_smtp(vendor_email, subject, text_body, html_body)
        
    except Exception as e:
        logger.exception(f"Error preparing vendor creation email: {str(e)}")
        return False

def send_organization_creation_email(
    vendor_email: str,
    vendor_name: str,
    organization_name: str,
    organization_website: Optional[str] = None,
    dashboard_url: str = "http://localhost:5173",
) -> bool:
    """
    Send email to vendor when they successfully create an organization
    """
    try:
        subject = f"Organization '{organization_name}' Created Successfully"
        
        vendor_display_name = vendor_name if vendor_name else vendor_email.split('@')[0]
        
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
                .org-info {{
                    background-color: #fff;
                    padding: 20px;
                    margin: 20px 0;
                    border-left: 4px solid #161950;
                    border-radius: 4px;
                }}
                .org-info-row {{
                    padding: 10px 0;
                    border-bottom: 1px solid #eee;
                }}
                .org-info-row:last-child {{
                    border-bottom: none;
                }}
                .org-label {{
                    font-weight: 600;
                    color: #555;
                    display: inline-block;
                    width: 140px;
                }}
                .org-value {{
                    color: #161950;
                    font-weight: 500;
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
                .success-box {{
                    background-color: #d4edda;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Organization Created Successfully!</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{vendor_display_name}</strong>,</p>
                    
                    <div class="success-box">
                        <p style="margin: 0; font-weight: 600; color: #155724;">
                            ✅ Your organization has been created successfully!
                        </p>
                    </div>
                    
                    <p>
                        Congratulations! Your organization <strong>"{organization_name}"</strong> has been 
                        successfully set up in our system. You can now start managing your accounts, 
                        opportunities, and resources.
                    </p>
                    
                    <div class="org-info">
                        <div class="org-info-row">
                            <span class="org-label">Organization Name:</span>
                            <span class="org-value">{organization_name}</span>
                        </div>
                        {f'<div class="org-info-row"><span class="org-label">Website:</span><span class="org-value"><a href="{organization_website}">{organization_website}</a></span></div>' if organization_website else ''}
                        <div class="org-info-row">
                            <span class="org-label">Account Email:</span>
                            <span class="org-value">{vendor_email}</span>
                        </div>
                    </div>
                    
                    <p>
                        <strong>What's Next?</strong>
                    </p>
                    <ul>
                        <li>✅ Complete your organization profile details</li>
                        <li>✅ Add your company address and contact information</li>
                        <li>✅ Start creating accounts and opportunities</li>
                        <li>✅ Manage your team and resources</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="{dashboard_url}" class="button">Go to Dashboard</a>
                    </div>
                    
                    <p>
                        If you need any assistance or have questions, our support team is here to help.
                    </p>
                    
                    <p>Best regards,<br><strong>Megapolis Advisory Team</strong></p>
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
Organization Created Successfully

Dear {vendor_display_name},

🎉 Congratulations! Your organization "{organization_name}" has been successfully set up in our system. 
You can now start managing your accounts, opportunities, and resources.

Organization Details:
- Organization Name: {organization_name}
{f'- Website: {organization_website}' if organization_website else ''}
- Account Email: {vendor_email}

What's Next?
✅ Complete your organization profile details
✅ Add your company address and contact information
✅ Start creating accounts and opportunities
✅ Manage your team and resources

Dashboard URL: {dashboard_url}

If you need any assistance or have questions, our support team is here to help.

Best regards,
Megapolis Advisory Team

---
This is an automated email. Please do not reply to this message.
© 2025 Megapolis Advisory. All rights reserved.
        """
        
        return _send_email_via_smtp(vendor_email, subject, text_body, html_body)
        
    except Exception as e:
        logger.exception(f"Error preparing organization creation email: {str(e)}")
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
        from_email = getattr(environment, 'SMTP_FROM_EMAIL', smtp_user)
        from_name = getattr(environment, 'SMTP_FROM_NAME', 'Megapolis Advisory')
        
        logger.info(f"📧 Attempting to send email to {to_email}, Subject: {subject}")
        logger.info(f"📧 SMTP Config: host={smtp_host}, port={smtp_port}, user={smtp_user}")
        
        if not smtp_host or not smtp_user:
            logger.warning(
                f"❌ Email not configured! SMTP_HOST={smtp_host}, SMTP_USER={smtp_user}. Would send to {to_email}: {subject}"
            )
            logger.info(f"Email content (text): {text_body[:200]}...")
            return True  # Return True in development mode
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        # Format: "Name <email@example.com>" or just email
        if from_name and from_email:
            message["From"] = f"{from_name} <{from_email}>"
        else:
            message["From"] = from_email or smtp_user
        message["To"] = to_email
        
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)
        
        logger.info(f"📧 Connecting to SMTP server {smtp_host}:{smtp_port}...")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            logger.info(f"📧 TLS started, logging in as {smtp_user}...")
            server.login(smtp_user, smtp_password)
            logger.info(f"📧 Login successful, sending message...")
            server.send_message(message)
            logger.info(f"✅ Email sent successfully to {to_email}")
        
        return True
        
    except Exception as e:
        logger.exception(f"❌ Error sending email via SMTP to {to_email}: {str(e)}")
        return False
