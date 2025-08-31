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
    try:
        # Compose the invite link
        frontend_url = environment.FRONTEND_URL or "https://megapolis.example.com"
        invite_link = f"{frontend_url}/invite/accept?token={invite.token}"

        subject = "You're invited to join Megapolis!"
        body = (
            f"Hello,\n\n"
            f"You have been invited to join the organization on Megapolis.\n"
            f"Please click the link below to accept your invitation and set up your account:\n\n"
            f"{invite_link}\n\n"
            f"This invite will expire on {invite.expires_at}.\n\n"
            f"If you did not expect this invitation, you can ignore this email.\n\n"
            f"Best regards,\n"
            f"{environment.SMTP_FROM_NAME or 'The Megapolis Team'}"
        )

        message = EmailMessage()
        message["From"] = f"{environment.SMTP_FROM_NAME or 'Megapolis'} <{environment.SMTP_FROM_EMAIL}>"
        message["To"] = invite.email
        message["Subject"] = subject
        message.set_content(body)

        # SMTP Configuration from environment
        smtp_host = environment.SMTP_HOST
        smtp_port = environment.SMTP_PORT
        smtp_user = environment.SMTP_USER
        smtp_pass = environment.SMTP_PASSWORD

        logger.info(f"Sending invite email to {invite.email} via {smtp_host}:{smtp_port}")

        # Gmail SMTP configuration
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Enable TLS encryption
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
                logger.info(f"SMTP login successful for {smtp_user}")
            server.sendmail(environment.SMTP_FROM_EMAIL, [invite.email], message.as_string())
            logger.info(f"Email sent successfully to {invite.email}")

    except Exception as e:
        logger.error(f"Failed to send invite email to {invite.email}: {str(e)}")
        # Don't raise exception to prevent invitation creation from failing
        # The invitation will still be created even if email fails
