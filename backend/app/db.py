import os
from copy import deepcopy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from bson import ObjectId
from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError


_client = None


def timezone():
    return ZoneInfo(os.getenv("APP_TIMEZONE", "Asia/Kolkata"))


def now_ist():
    return datetime.now(timezone())


def get_client():
    global _client
    if _client is None:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise RuntimeError("MONGO_URI is not configured.")
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=8000)
    return _client


def get_db():
    return get_client()[os.getenv("MONGO_DB_NAME", "prep_tracker")]


def ensure_indexes():
    db = get_db()
    db.daily_logs.create_index([("date", ASCENDING)], unique=True)
    db.email_events.create_index([("created_at", ASCENDING)])
    db.email_events.create_index([("job_key", ASCENDING), ("created_at", ASCENDING)])
    db.email_events.create_index(
        [("job_key", ASCENDING), ("scheduled_for", ASCENDING)],
        unique=True,
        partialFilterExpression={"scheduled_for": {"$exists": True}},
    )


def default_log(date_str):
    created_at = now_ist()
    return {
        "date": date_str,
        "sessions": {
            "morning": {
                "label": "9 AM to 1 PM",
                "cf_done": False,
                "lc_done": False,
                "notes": "",
            },
            "afternoon": {
                "label": "1:05 PM to 5:30 PM",
                "cf_done": False,
                "lc_done": False,
                "notes": "",
            },
            "evening": {
                "label": "5:35 PM to 9:30 PM",
                "cf_done": False,
                "lc_done": False,
                "notes": "",
            },
        },
        "striver": {
            "done": False,
            "minutes": 0,
            "notes": "",
        },
        "jobs": {
            "applications_done": False,
            "recruiters_done": False,
            "applications_count": 0,
            "recruiters_count": 0,
            "notes": "",
        },
        "behavioral": {
            "done": False,
            "minutes": 0,
            "notes": "",
        },
        "ml_research": {
            "done": False,
            "minutes": 0,
            "focus": "",
            "notes": "",
        },
        "resume": {
            "done": False,
            "notes": "",
        },
        "daily_review": {
            "filled": False,
            "notes": "",
        },
        "created_at": created_at,
        "updated_at": created_at,
    }


def deep_merge(base, updates):
    merged = deepcopy(base)
    for key, value in updates.items():
        if key in {"_id", "created_at"}:
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def serialize_doc(doc):
    if not doc:
        return doc

    serialized = deepcopy(doc)
    serialized["_id"] = str(serialized["_id"])
    for key in ("created_at", "updated_at"):
        if isinstance(serialized.get(key), datetime):
            serialized[key] = serialized[key].isoformat()
    return serialized


def get_or_create_log(date_str):
    db = get_db()
    baseline = default_log(date_str)
    doc = db.daily_logs.find_one_and_update(
        {"date": date_str},
        {"$setOnInsert": baseline},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    hydrated = deep_merge(baseline, doc)
    hydrated["_id"] = doc["_id"]
    hydrated["created_at"] = doc.get("created_at", baseline["created_at"])
    return serialize_doc(hydrated)


def update_log(date_str, updates):
    db = get_db()
    existing = db.daily_logs.find_one({"date": date_str})
    merged = deep_merge(existing or default_log(date_str), updates)
    merged["date"] = date_str
    merged["updated_at"] = now_ist()

    doc = db.daily_logs.find_one_and_replace(
        {"date": date_str},
        merged,
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return serialize_doc(doc)


def get_logs_between(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    days = (end - start).days

    return [
        get_or_create_log((start + timedelta(days=offset)).isoformat())
        for offset in range(days + 1)
    ]


def record_email_event(event):
    db = get_db()
    event["created_at"] = now_ist()
    event["updated_at"] = event["created_at"]
    result = db.email_events.insert_one(event)
    return serialize_doc({**event, "_id": result.inserted_id})


def claim_email_event(event):
    db = get_db()
    event["created_at"] = now_ist()
    event["updated_at"] = event["created_at"]
    event["status"] = "sending"

    try:
        result = db.email_events.insert_one(event)
        return serialize_doc({**event, "_id": result.inserted_id}), True
    except DuplicateKeyError:
        existing = db.email_events.find_one(
            {
                "job_key": event["job_key"],
                "scheduled_for": event["scheduled_for"],
            }
        )
        return serialize_doc(existing), False


def update_email_event(event_id, updates):
    db = get_db()
    updates["updated_at"] = now_ist()
    doc = db.email_events.find_one_and_update(
        {"_id": ObjectId(event_id)},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    return serialize_doc(doc)
