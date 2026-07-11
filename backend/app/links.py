import os


PRODUCTION_FRONTEND_URL = "https://preptracker1.netlify.app/"
LOCAL_FRONTEND_URLS = {"http://localhost:5173", "http://127.0.0.1:5173"}


def get_frontend_url():
    frontend_url = os.getenv("FRONTEND_URL", PRODUCTION_FRONTEND_URL).strip()
    if frontend_url.rstrip("/") in LOCAL_FRONTEND_URLS:
        return PRODUCTION_FRONTEND_URL
    return frontend_url or PRODUCTION_FRONTEND_URL
