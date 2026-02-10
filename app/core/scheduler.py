from apscheduler.schedulers.background import BackgroundScheduler
from app.services.upstox_token_manager import refresh_token, is_token_expired
from app.services.upstox_auth_service import load_token


def start_scheduler():
    scheduler = BackgroundScheduler()

    def refresh_job():
        token = load_token()
        if token and is_token_expired(token):
            refresh_token()

    scheduler.add_job(refresh_job, "interval", minutes=30)
    scheduler.start()
