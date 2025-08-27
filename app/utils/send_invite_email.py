# send invite email to the user
import os
from email.message import EmailMessage
import aiosmtplib
from app.models.invite import Invite
from app.utils.logger import logger


async def send_invite_email(invite: Invite)->None:
    """
    Send an invite email to the user so that they can login.
    """
    # Compose the invite link (assuming you have a frontend URL)
    frontend_url = os.getenv("FRONTEND_URL", "https://megapolis.example.com")
    invite_link = f"{frontend_url}/invite/accept?token={invite.token}"

    subject = "You're invited to join Megapolis!"
    body = (
        f"Hello,\n\n"
        f"You have been invited to join the organization (ID: {invite.org_id}) on Megapolis.\n"
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

    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_pass,
            start_tls=True,
        )
        logger.info(f"Invite email sent to {invite.email}")
        return True
        
    except MegapolisHTTPException as e:
        logger.error(f"Failed to send invite email to {invite.email}: {e}")
        # You may want to log this error in production
        raise MegapolisHTTPException(status_code=500, details="Failed to send invite email")
