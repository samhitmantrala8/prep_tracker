import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from .db import ensure_indexes
from .routes import bp
from .scheduler import start_scheduler


def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.before_request
    def require_app_code():
        if request.method == "OPTIONS":
            return None

        public_paths = {
            "/api/health",
            "/api/schedule",
        }
        if request.path in public_paths or request.path.startswith("/api/cron/"):
            return None

        expected_code = os.getenv("APP_ACCESS_CODE", "2121")
        provided_code = request.headers.get("X-App-Code", "")
        if expected_code and provided_code != expected_code:
            return jsonify({"error": "Invalid or missing access code."}), 401

        return None

    ensure_indexes()
    app.register_blueprint(bp, url_prefix="/api")

    if os.getenv("ENABLE_LOCAL_SCHEDULER", "false").lower() == "true":
        start_scheduler(app)

    return app

