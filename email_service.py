
import logging
import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app

logger = logging.getLogger(__name__)


def send_status_change_email(recipient, complaint, old_status, new_status):
    """Send an email notifying a user that their complaint status changed."""

    config = current_app.config

    mail_server = config.get("MAIL_SERVER")
    sender = config.get("MAIL_DEFAULT_SENDER")
    username = config.get("MAIL_USERNAME")
    password = config.get("MAIL_PASSWORD")

    # Email notifications remain disabled until SMTP is configured.
    if not mail_server or not sender:
        logger.info("Email notifications are not configured.")
        return False

    if bool(username) != bool(password):
        logger.warning("SMTP username and password must both be configured.")
        return False

    message = EmailMessage()
    message["Subject"] = f"Complaint #{complaint.id} status updated"
    message["From"] = sender
    message["To"] = recipient

    message.set_content(
        f"""Hello,

There has been an update to your complaint.

Complaint ID: {complaint.id}
Title: {complaint.title}
Category: {complaint.category}

Previous status: {old_status}
New status: {new_status}

"""
        + (
            f"Resolution: {complaint.resolution}\n\n"
            if new_status == "Resolved" and complaint.resolution
            else ""
        )
        + """You can log in to the Smart Complaint Management System
to view your complaint details.

Regards,
Smart Complaint Management System
"""
    )

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP(
            mail_server,
            config.get("MAIL_PORT", 587),
            timeout=10
        ) as smtp:

            smtp.ehlo()

            if config.get("MAIL_USE_TLS", True):
                smtp.starttls(context=context)
                smtp.ehlo()

            if username and password:
                smtp.login(username, password)

            smtp.send_message(message)

        logger.info(
            "Status notification email sent for complaint_id=%s",
            complaint.id
        )
        return True

    except (smtplib.SMTPException, OSError, ValueError):
        logger.exception(
            "Failed to send status notification for complaint_id=%s",
            complaint.id
        )
        return False
