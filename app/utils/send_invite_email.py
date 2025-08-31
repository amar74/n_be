# send invite email to the user
import os
from email.message import EmailMessage
from app.models.invite import Invite
from app.utils.logger import logger
from app.utils.error import MegapolisHTTPException
from app.environment import environment
import smtplib


async def send_invite_email(invite: Invite) -> None:
    """
    Send an invite email to the user so that they can login.
    """
    # Compose the invite link (assuming you have a frontend URL)
    frontend_url = os.getenv("FRONTEND_URL", "https://megapolis.example.com")
    invite_link = f"{frontend_url}/invite/accept?token={invite.token}"

    subject = "You're invited to join Megapolis!"
    body = (
        f"Hello,\n\n"
        f"You have been invited to join the organization (ID: {invite.email}) on Megapolis.\n"
        f"Please click the link below to accept your invitation and set up your account:\n\n"
        f"{invite_link}\n\n"
        f"This invite will expire on {invite.expires_at}.\n\n"
        f"If you did not expect this invitation, you can ignore this email.\n\n"
        f"Best regards,\n"
        f"The Megapolis Team"
    )

    message = EmailMessage()
    message["From"] = os.getenv("EMAIL_FROM", "no-reply@megapolis.example.com")
    message["To"] = invite.email
    message["Subject"] = subject
    message.set_content(body)

    smtp_host = "sandbox.smtp.mailtrap.io"
    smtp_port = 2525
    smtp_user = "49ea10c9c53749"
    smtp_pass = "e0e27c53820859"
    # Example SMTP (can replace with SendGrid / AWS SES / Supabase SMTP)
    with smtplib.SMTP(smtp_host, 587) as server:
        server.starttls()
        server.login(smtp_user,smtp_pass)
        server.sendmail(message["From"], [message["To"]], message.as_string())
