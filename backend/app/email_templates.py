from datetime import datetime


SHARED_REMINDER = """Every block also carries the daily baseline:
- Revise Striver A2Z for 1 hour today.
- Apply to jobs on LinkedIn, email, Instahyre, Naukri, and similar platforms.
- Message at least 5 recruiters properly on LinkedIn or relevant hiring platforms.
"""


JOB_DEFINITIONS = {
    "morning_dsa": {
        "schedule": "Daily at 9:00 AM IST",
        "subject": "9 AM DSA Block: CF + LeetCode before 1 PM",
        "body": """Before 1 PM, complete:
- 1 Codeforces question.
- Either 1 LeetCode Hard or 2 LeetCode Mediums.

Start clean, keep the timer honest, and mark this block in the tracker after you finish.
""",
    },
    "midday_check": {
        "schedule": "Daily at 1:00 PM IST",
        "subject": "1 PM Check-in: Did you finish the morning DSA block?",
        "body": """Quick check-in:
- Did you finish 1 Codeforces question?
- Did you finish either 1 LeetCode Hard or 2 LeetCode Mediums?

Open the tracker and mark the morning block as Yes or No.
""",
    },
    "afternoon_dsa": {
        "schedule": "Daily at 1:05 PM IST",
        "subject": "1:05 PM DSA Block: CF + LeetCode before 5:30 PM",
        "body": """Before 5:30 PM, complete:
- 1 Codeforces question.
- Either 1 LeetCode Hard or 2 LeetCode Mediums.

This is the second DSA push of the day. Mark it in the tracker once it is done.
""",
    },
    "evening_dsa": {
        "schedule": "Daily at 5:35 PM IST",
        "subject": "5:35 PM Final DSA Block: CF + LeetCode before 9:30 PM",
        "body": """Before 9:30 PM, complete:
- 1 Codeforces question.
- Either 1 LeetCode Hard or 2 LeetCode Mediums.

Finish the third DSA block and update the tracker honestly.
""",
    },
    "behavioral_prep": {
        "schedule": "Daily at 9:30 PM IST",
        "subject": "9:30 PM Behavioral Prep: 30 minutes with AI and internet resources",
        "body": """Now spend 30 minutes on behavioral interview prep:
- Practice stories using STAR format.
- Use AI for mock questions and feedback.
- Check LinkedIn, Reddit, company blogs, and internet resources for role-specific patterns.

After the session, mark behavioral prep in the tracker.
""",
    },
    "daily_log_reminder": {
        "schedule": "Daily at 10:15 PM IST",
        "subject": "Daily Tracker Reminder: Mark today's progress",
        "body": """Open Prep Tracker and mark what you completed today:
- All 3 DSA blocks.
- Striver A2Z revision.
- Job applications and recruiter messages.
- Behavioral prep.
- Notes for anything missed.

The point is not to look perfect. The point is to keep the data honest.
""",
    },
    "weekly_resume_start": {
        "schedule": "Every Saturday at 9:00 AM IST",
        "subject": "Saturday Resume Prep: Update this week's resume work",
        "body": """This week's resume-prep task:
- Improve one resume section.
- Add or sharpen project bullets with measurable impact.
- Update LinkedIn/GitHub/portfolio details if needed.
- Save notes about what changed.

Mark resume prep in the tracker when it is complete.
""",
    },
    "weekly_resume_check": {
        "schedule": "Every Sunday at 10:00 PM IST",
        "subject": "Sunday Resume Check: Mark weekly resume prep complete",
        "body": """Before ending the week, open Prep Tracker and mark whether resume prep was completed.

If it was missed, add a note with the blocker so next week starts with clarity.
""",
    },
}


def build_email(job_key, frontend_url):
    if job_key not in JOB_DEFINITIONS:
        raise KeyError(f"Unknown job key: {job_key}")

    job = JOB_DEFINITIONS[job_key]
    today = datetime.now().strftime("%Y-%m-%d")
    text_body = f"""Date: {today}
Schedule: {job["schedule"]}

{job["body"].strip()}

{SHARED_REMINDER.strip()}

Tracker: {frontend_url}
"""
    html_body = text_body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_body = html_body.replace("\n", "<br>")

    return {
        "job_key": job_key,
        "subject": job["subject"],
        "text": text_body,
        "html": f"<div style=\"font-family:Arial,sans-serif;line-height:1.55;color:#111827\">{html_body}</div>",
        "schedule": job["schedule"],
    }

