import os

import requests

from .db import record_email_event
from .email_templates import build_email


def _split_recipients(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def send_scheduled_email(job_key, scheduled_for=None, scheduled_at=None, trigger="manual"):
    frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")
    email = build_email(job_key, frontend_url)
    recipients = _split_recipients(os.getenv("EMAIL_TO", ""))
    sender = os.getenv("EMAIL_FROM", "Prep Tracker <onboarding@resend.dev>")
    dry_run = os.getenv("EMAIL_DRY_RUN", "true").lower() == "true"

    event = {
        "job_key": job_key,
        "subject": email["subject"],
        "to": recipients,
        "provider": os.getenv("EMAIL_PROVIDER", "resend"),
        "status": "queued",
        "trigger": trigger,
    }
    if scheduled_for:
        event["scheduled_for"] = scheduled_for
    if scheduled_at:
        event["scheduled_at"] = scheduled_at

    if dry_run:
        event.update({"status": "dry_run", "message": "EMAIL_DRY_RUN is enabled."})
        return record_email_event(event)

    api_key = os.getenv("RESEND_API_KEY")
    if not api_key or not recipients:
        event.update(
            {
                "status": "skipped",
                "message": "RESEND_API_KEY and EMAIL_TO are required to send email.",
            }
        )
        return record_email_event(event)

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": sender,
            "to": recipients,
            "subject": email["subject"],
            "text": email["text"],
            "html": email["html"],
        },
        timeout=20,
    )

    if 200 <= response.status_code < 300:
        event.update({"status": "sent", "provider_response": response.json()})
    else:
        event.update(
            {
                "status": "failed",
                "provider_status": response.status_code,
                "provider_response": response.text[:1000],
            }
        )

    return record_email_event(event)
