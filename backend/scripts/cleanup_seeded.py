from pathlib import Path
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from app.db import get_db  # noqa: E402


SEEDED_LOG_QUERY = {
    "$or": [
        {"sessions.morning.notes": {"$regex": "Seeded", "$options": "i"}},
        {"sessions.afternoon.notes": {"$regex": "Seeded", "$options": "i"}},
        {"sessions.evening.notes": {"$regex": "Seeded", "$options": "i"}},
        {"striver.notes": {"$regex": "Seeded", "$options": "i"}},
        {"jobs.notes": {"$regex": "Seeded", "$options": "i"}},
        {"behavioral.notes": {"$regex": "Seeded", "$options": "i"}},
        {"ml_research.notes": {"$regex": "Seeded", "$options": "i"}},
        {"resume.notes": {"$regex": "Seeded", "$options": "i"}},
        {"daily_review.notes": {"$regex": "Seeded", "$options": "i"}},
    ]
}


if __name__ == "__main__":
    db = get_db()
    matches = list(db.daily_logs.find(SEEDED_LOG_QUERY, {"date": 1}).sort("date", 1))
    dates = [doc["date"] for doc in matches]
    result = db.daily_logs.delete_many(SEEDED_LOG_QUERY)
    print(f"Deleted {result.deleted_count} seeded daily logs.")
    if dates:
        print("Dates:", ", ".join(dates))
