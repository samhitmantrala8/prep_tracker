from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .db import now_ist, timezone
from .emailer import send_scheduled_email


SCHEDULES = {
    "morning_dsa": {"day_of_week": "*", "hour": 9, "minute": 0},
    "midday_check": {"day_of_week": "*", "hour": 13, "minute": 0},
    "afternoon_dsa": {"day_of_week": "*", "hour": 13, "minute": 5},
    "evening_dsa": {"day_of_week": "*", "hour": 17, "minute": 35},
    "behavioral_prep": {"day_of_week": "*", "hour": 21, "minute": 30},
    "daily_log_reminder": {"day_of_week": "*", "hour": 22, "minute": 15},
    "weekly_resume_start": {"day_of_week": "sat", "hour": 9, "minute": 0},
    "weekly_resume_check": {"day_of_week": "sun", "hour": 22, "minute": 0},
}


def send_scheduler_email(job_key):
    current_time = now_ist()
    return send_scheduled_email(
        job_key,
        scheduled_for=f"{current_time.date().isoformat()}:{job_key}",
        scheduled_at=current_time.isoformat(),
        trigger="apscheduler",
    )


def start_scheduler(app):
    scheduler = BackgroundScheduler(timezone=timezone())

    for job_key, cron_kwargs in SCHEDULES.items():
        scheduler.add_job(
            func=lambda key=job_key: send_scheduler_email(key),
            trigger=CronTrigger(timezone=timezone(), **cron_kwargs),
            id=f"email_{job_key}",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

    scheduler.start()
    app.extensions["prep_tracker_scheduler"] = scheduler
    return scheduler
