import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def send_status_change_notification(
    recipient_email: str,
    lead_name: str,
    old_status: str,
    new_status: str,
) -> bool:
    """Send email when lead/query status changes. Falls back to console log if SMTP is not configured."""
    subject = f"Lead Status Update: {lead_name}"
    body = (
        f"Hello,\n\n"
        f"The status for lead '{lead_name}' has been updated.\n\n"
        f"Previous Status: {old_status}\n"
        f"New Status: {new_status}\n\n"
        f"— NexAltis Lead Management System"
    )

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("NOTIFICATION_FROM", smtp_user)

    if not all([smtp_host, smtp_user, smtp_password, from_email]):
        logger.info(
            "Email notification (SMTP not configured): To=%s | %s -> %s",
            recipient_email,
            old_status,
            new_status,
        )
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, recipient_email, msg.as_string())

        logger.info("Status change email sent to %s", recipient_email)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", recipient_email, exc)
        return False
