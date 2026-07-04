import os

import requests

from .db import claim_email_event, record_email_event, update_email_event
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

    claimed_event = None
    if scheduled_for:
        claimed_event, is_new_claim = claim_email_event(event.copy())
        if not is_new_claim:
            claimed_event["duplicate_skipped"] = True
            return claimed_event

    if dry_run:
        updates = {"status": "dry_run", "message": "EMAIL_DRY_RUN is enabled."}
        return (
            update_email_event(claimed_event["_id"], updates)
            if claimed_event
            else record_email_event({**event, **updates})
        )

    api_key = os.getenv("RESEND_API_KEY")
    if not api_key or not recipients:
        updates = {
            "status": "skipped",
            "message": "RESEND_API_KEY and EMAIL_TO are required to send email.",
        }
        return (
            update_email_event(claimed_event["_id"], updates)
            if claimed_event
            else record_email_event({**event, **updates})
        )

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
        updates = {"status": "sent", "provider_response": response.json()}
    else:
        updates = {
            "status": "failed",
            "provider_status": response.status_code,
            "provider_response": response.text[:1000],
        }

    return (
        update_email_event(claimed_event["_id"], updates)
        if claimed_event
        else record_email_event({**event, **updates})
    )
