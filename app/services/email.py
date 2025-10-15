
from typing import Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.environment import environment
from app.utils.logger import logger

def send_vendor_invitation_email(
    vendor_name: str,
    vendor_email: str,
    password: str,
    login_url: str
) -> bool:

    try:
        subject = "Welcome to Megapolis - Your Vendor Account is Ready!"
        
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
                    background-color: #4CAF50;
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
                    border-left: 4px solid #4CAF50;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #4CAF50;
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
                    <h1>Welcome to Megapolis!</h1>
                </div>
                <div class="content">
                    <h2>Hello {vendor_name},</h2>
                    <p>
                        Your vendor account has been sucessfully created on the Megapolis platform. 
                        You can now log in and start managing your business operations.
                    </p>
                    
                    <div class="credentials">
                        <h3>Your Login Credentials:</h3>
                        <p><strong>Email (User ID):</strong> {vendor_email}</p>
                        <p><strong>Temporary Password:</strong> {password}</p>
                    </div>
                    
                    <p>
                        Please use the button below to access the vendor login page:
                    </p>
                    
                    <div style="text-align: center;">
                        <a href="{login_url}" class="button">Login to Vendor Portal</a>
                    </div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>Please change your password after your first login</li>
                        <li>Keep your credentials secure and do not share them with anyone</li>
                        <li>Your account status is currently pending approval</li>
                    </ul>
                    
                    <p>
                        If you have any questions or need assistance, please contact our support team.
                    </p>
                    
                    <p>Best regards,<br>The Megapolis Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply to this message.</p>
                    <p>&copy; 2025 Megapolis. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>

        Welcome to Megapolis!
        
        Hello {vendor_name},
        
        Your vendor account has been successfully created on the Megapolis platform.
        
        Your Login Credentials:
        Email (User ID): {vendor_email}
        Temporary Password: {password}
        
        Login URL: {login_url}
        
        Important:
        - Please change your password after your first login
        - Keep your credentials secure and do not share them with anyone
        - Your account status is currently pending approval
        
        If you have any questions or need assistance, please contact our support team.
        
        Best regards,
        The Megapolis Team

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
