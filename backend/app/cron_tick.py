from datetime import datetime, time, timedelta

from .db import get_db, now_ist, timezone
from .emailer import send_scheduled_email


POLL_SCHEDULES = [
    {"job_key": "morning_dsa", "hour": 8, "minute": 0},
    {"job_key": "evening_dsa", "hour": 20, "minute": 0},
    {"job_key": "behavioral_prep", "hour": 21, "minute": 30},
    {"job_key": "daily_log_reminder", "hour": 22, "minute": 15},
    {"job_key": "weekly_resume_start", "hour": 9, "minute": 0, "weekdays": {5}},
    {"job_key": "weekly_resume_check", "hour": 22, "minute": 0, "weekdays": {6}},
]


def _scheduled_at(current_time, item):
    scheduled_date = current_time.date()
    return datetime.combine(
        scheduled_date,
        time(item["hour"], item["minute"]),
        tzinfo=timezone(),
    )


def _already_sent(job_key, scheduled_for):
    db = get_db()
    return db.email_events.find_one(
        {
            "job_key": job_key,
            "scheduled_for": scheduled_for,
            "status": {"$in": ["sent", "dry_run"]},
        }
    ) is not None


def dispatch_due_emails(current_time=None, lookback_minutes=12):
    current_time = current_time or now_ist()
    due = []
    skipped = []
    sent = []

    for item in POLL_SCHEDULES:
        weekdays = item.get("weekdays")
        if weekdays is not None and current_time.weekday() not in weekdays:
            skipped.append({"job_key": item["job_key"], "reason": "wrong_weekday"})
            continue

        scheduled_at = _scheduled_at(current_time, item)
        delta = current_time - scheduled_at
        if delta < timedelta(0) or delta > timedelta(minutes=lookback_minutes):
            skipped.append({"job_key": item["job_key"], "reason": "not_due"})
            continue

        scheduled_for = f"{scheduled_at.date().isoformat()}:{item['job_key']}"
        if _already_sent(item["job_key"], scheduled_for):
            skipped.append({"job_key": item["job_key"], "reason": "already_sent"})
            continue

        due.append(item["job_key"])
        event = send_scheduled_email(
            item["job_key"],
            scheduled_for=scheduled_for,
            scheduled_at=scheduled_at.isoformat(),
            trigger="cron_tick",
        )
        sent.append(event)

    return {
        "ok": True,
        "checked_at": current_time.isoformat(),
        "due": due,
        "sent": sent,
        "skipped": skipped,
    }
