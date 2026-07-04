# Prep Tracker

Full-stack DSA, job application, behavioral interview, and weekly resume-prep tracker.

- Frontend: React + Tailwind CSS
- Backend: Flask + MongoDB Atlas
- Email delivery: Resend-compatible HTTP API
- Timezone: IST (`Asia/Kolkata`)

## Local Setup

### Backend

```powershell
cd C:\samhi\prep_tracker\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

The backend runs on `http://127.0.0.1:5000`.

### Frontend

```powershell
cd C:\samhi\prep_tracker\frontend
npm install
npm run dev
```

The frontend runs on `http://127.0.0.1:5173`.

## Email Scheduling

For local testing, set `ENABLE_LOCAL_SCHEDULER=true` in `backend/.env`.

For Render deployment, prefer external cron jobs that call:

```text
GET /api/cron/send/<job_key>?key=<CRON_SECRET>
```

Valid job keys:

- `morning_dsa`
- `midday_check`
- `afternoon_dsa`
- `evening_dsa`
- `behavioral_prep`
- `daily_log_reminder`
- `weekly_resume_start`
- `weekly_resume_check`

