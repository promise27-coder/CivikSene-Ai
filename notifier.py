import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage


@dataclass
class AlertResult:
    sent: bool
    message: str


def _split_emails(value: str | None) -> list[str]:
    if not value:
        return []

    return [email.strip() for email in value.split(",") if email.strip()]


def _category_env_key(category: str) -> str:
    safe_category = category.upper().replace(" ", "_")
    return f"ALERT_{safe_category}_EMAILS"


def _get_recipients(category: str) -> list[str]:
    category_recipients = _split_emails(os.getenv(_category_env_key(category)))
    if category_recipients:
        return category_recipients

    return _split_emails(os.getenv("ALERT_RECIPIENTS"))


def _build_alert_body(complaint) -> str:
    location = "Not provided"
    if complaint.lat is not None and complaint.long is not None:
        location = (
            f"{complaint.lat}, {complaint.long}\n"
            f"Map: https://www.google.com/maps?q={complaint.lat},{complaint.long}"
        )

    image = complaint.image_path or "Not provided"

    return f"""High priority civic complaint received.

Complaint ID: {complaint.id}
Category: {complaint.category}
Priority: {complaint.priority}
Status: {complaint.status}

Description:
{complaint.description}

Location:
{location}

Image:
{image}
"""


def send_high_priority_alert(complaint) -> AlertResult:
    if complaint.priority != "High":
        return AlertResult(sent=False, message="Alert skipped: complaint is not high priority")

    recipients = _get_recipients(complaint.category)
    if not recipients:
        return AlertResult(sent=False, message="Alert skipped: no recipients configured")

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_sender = os.getenv("SMTP_SENDER") or smtp_username
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() != "false"

    if not smtp_host or not smtp_sender:
        return AlertResult(sent=False, message="Alert skipped: SMTP settings missing")

    email = EmailMessage()
    email["From"] = smtp_sender
    email["To"] = ", ".join(recipients)
    email["Subject"] = f"High Priority Complaint #{complaint.id}: {complaint.category}"
    email.set_content(_build_alert_body(complaint))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if smtp_use_tls:
                server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(email)
    except Exception as exc:
        return AlertResult(sent=False, message=f"Alert failed: {exc}")

    return AlertResult(sent=True, message="Alert email sent")
