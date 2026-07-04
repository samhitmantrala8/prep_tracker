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

Set `ENABLE_LOCAL_SCHEDULER=true` on Render if you want the Flask backend to run the IST reminder schedule itself.

For Render deployment, prefer external cron jobs that call:

```text
GET /api/cron/send/<job_key>?key=<CRON_SECRET>
```

If using UptimeRobot, call this every 5 minutes instead:

```text
GET /api/cron/tick?key=<CRON_SECRET>
```

The tick endpoint checks the current IST time, sends only due emails, and avoids duplicate sends for the same scheduled reminder.

Valid job keys:

- `morning_dsa`
- `midday_check`
- `afternoon_dsa`
- `evening_dsa`
- `behavioral_prep`
- `daily_log_reminder`
- `weekly_resume_start`
- `weekly_resume_check`

## Deployment

Docker is not required for this project.

### Backend on Render

Create a Render Web Service from the GitHub repo and set:

```text
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn run:app --bind 0.0.0.0:$PORT --workers 1
```

Add the backend environment variables from `backend/.env.example` in the Render dashboard. Keep `EMAIL_DRY_RUN=false` only when the Resend API key and sender/recipient are correct.

For this app, set `ENABLE_LOCAL_SCHEDULER=true` and keep the Render start command at one Gunicorn worker. Multiple workers can start multiple scheduler processes.

### Frontend on Netlify

Create a Netlify site from the same GitHub repo and set:

```text
Base directory: frontend
Build command: npm run build
Publish directory: dist
```

Add this frontend environment variable in Netlify:

```text
VITE_API_BASE_URL=https://your-render-backend.onrender.com/api
```

The included Dockerfiles are optional. They are useful if you later want container-based deployment, but the normal Render and Netlify flows do not need them.

### UptimeRobot

The backend exposes public health endpoints for uptime checks:

```text
https://your-render-backend.onrender.com/
https://your-render-backend.onrender.com/health
https://your-render-backend.onrender.com/api/health
```

The root health URL only keeps the backend awake. It does not send reminder emails. Use `/api/cron/tick?key=<CRON_SECRET>` for scheduled reminder dispatch.
