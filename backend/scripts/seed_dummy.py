from datetime import timedelta
from pathlib import Path
import random
import sys

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from app.db import now_ist, update_log  # noqa: E402


def seed_last_seven_days():
    today = now_ist().date()
    seeded = []

    for offset in range(6, -1, -1):
        current = today - timedelta(days=offset)
        date_str = current.isoformat()
        completion_bias = max(0.35, 0.9 - offset * 0.07)

        payload = {
            "sessions": {
                "morning": {
                    "cf_done": random.random() < completion_bias,
                    "lc_done": random.random() < completion_bias,
                    "notes": "Seeded local-testing data.",
                },
                "evening": {
                    "cf_done": random.random() < completion_bias,
                    "lc_done": random.random() < completion_bias,
                    "notes": "Seeded local-testing data.",
                },
            },
            "striver": {
                "done": random.random() < completion_bias,
                "minutes": random.choice([0, 30, 45, 60, 75]),
                "notes": "Seeded Striver A2Z revision.",
            },
            "jobs": {
                "applications_done": random.random() < completion_bias,
                "recruiters_done": random.random() < completion_bias,
                "applications_count": random.randint(0, 8),
                "recruiters_count": random.randint(0, 7),
                "notes": "Seeded job outreach data.",
            },
            "behavioral": {
                "done": random.random() < completion_bias,
                "minutes": random.choice([0, 15, 30, 45]),
                "notes": "Seeded behavioral prep data.",
            },
            "ml_research": {
                "done": random.random() < completion_bias,
                "minutes": random.choice([0, 30, 45, 60, 90]),
                "focus": random.choice(
                    ["Kaggle competition", "Hugging Face model work", "GenAI research"]
                ),
                "notes": "Seeded ML and research prep data.",
            },
            "weekly_codechef": {
                "done": current.weekday() in {5, 6} and random.random() < completion_bias,
                "notes": "Seeded weekly CodeChef data." if current.weekday() in {5, 6} else "",
            },
            "resume": {
                "done": current.weekday() in {5, 6} and random.random() < completion_bias,
                "notes": "Seeded weekly resume prep data." if current.weekday() in {5, 6} else "",
            },
            "daily_review": {
                "filled": random.random() < completion_bias,
                "notes": "Seeded end-of-day review.",
            },
        }
        update_log(date_str, payload)
        seeded.append(date_str)

    return seeded


if __name__ == "__main__":
    dates = seed_last_seven_days()
    print(f"Seeded dummy logs for: {', '.join(dates)}")
