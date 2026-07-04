import os
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request

from .db import get_logs_between, get_or_create_log, now_ist, update_log
from .emailer import send_scheduled_email
from .email_templates import JOB_DEFINITIONS, build_email
from .scheduler import SCHEDULES

bp = Blueprint("api", __name__)


def _validate_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except (TypeError, ValueError):
        return None


@bp.get("/health")
def health():
    return jsonify({"ok": True, "timezone": os.getenv("APP_TIMEZONE", "Asia/Kolkata")})


@bp.get("/config")
def config():
    today = now_ist().date().isoformat()
    return jsonify(
        {
            "today": today,
            "timezone": os.getenv("APP_TIMEZONE", "Asia/Kolkata"),
            "email_to_configured": os.getenv("EMAIL_TO", "") not in {"", "your-email@example.com"},
            "email_dry_run": os.getenv("EMAIL_DRY_RUN", "true").lower() == "true",
            "schedule": {
                key: {
                    **SCHEDULES[key],
                    "label": JOB_DEFINITIONS[key]["schedule"],
                    "subject": JOB_DEFINITIONS[key]["subject"],
                }
                for key in SCHEDULES
            },
        }
    )


@bp.get("/schedule")
def schedule():
    return jsonify(
        {
            key: {
                **SCHEDULES[key],
                "label": JOB_DEFINITIONS[key]["schedule"],
                "subject": JOB_DEFINITIONS[key]["subject"],
            }
            for key in SCHEDULES
        }
    )


@bp.get("/logs/<date_str>")
def get_log(date_str):
    if not _validate_date(date_str):
        return jsonify({"error": "Date must be YYYY-MM-DD."}), 400
    return jsonify(get_or_create_log(date_str))


@bp.put("/logs/<date_str>")
def put_log(date_str):
    if not _validate_date(date_str):
        return jsonify({"error": "Date must be YYYY-MM-DD."}), 400
    payload = request.get_json(silent=True) or {}
    return jsonify(update_log(date_str, payload))


@bp.get("/logs")
def list_logs():
    end = request.args.get("end") or now_ist().date().isoformat()
    if not _validate_date(end):
        return jsonify({"error": "start and end must be YYYY-MM-DD."}), 400

    start = request.args.get("start") or (date.fromisoformat(end) - timedelta(days=6)).isoformat()
    if not _validate_date(start):
        return jsonify({"error": "start and end must be YYYY-MM-DD."}), 400

    return jsonify(get_logs_between(start, end))


@bp.get("/email/preview/<job_key>")
def email_preview(job_key):
    try:
        return jsonify(build_email(job_key, os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")))
    except KeyError:
        return jsonify({"error": "Unknown email job."}), 404


@bp.post("/email/send/<job_key>")
def manual_email_send(job_key):
    if job_key not in JOB_DEFINITIONS:
        return jsonify({"error": "Unknown email job."}), 404
    return jsonify(send_scheduled_email(job_key))


@bp.route("/cron/send/<job_key>", methods=["GET", "POST"])
def cron_email_send(job_key):
    expected = os.getenv("CRON_SECRET", "")
    provided = request.args.get("key") or request.headers.get("X-Cron-Key", "")
    if expected and provided != expected:
        return jsonify({"error": "Invalid cron key."}), 401

    if job_key not in JOB_DEFINITIONS:
        return jsonify({"error": "Unknown email job."}), 404

    return jsonify(send_scheduled_email(job_key))
