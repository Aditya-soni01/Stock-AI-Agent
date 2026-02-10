import requests
import json
import time
from app.core.config import (
    UPSTOX_API_KEY,
    UPSTOX_API_SECRET,
    UPSTOX_REDIRECT_URI,
    UPSTOX_TOKEN_FILE
)

AUTH_URL = "https://api.upstox.com/v2/login/authorization/token"


def get_login_url():
    return (
        "https://api.upstox.com/v2/login/authorization/dialog"
        f"?response_type=code"
        f"&client_id={UPSTOX_API_KEY}"
        f"&redirect_uri={UPSTOX_REDIRECT_URI}"
    )


def exchange_code_for_token(code: str):
    payload = {
        "code": code,
        "client_id": UPSTOX_API_KEY,
        "client_secret": UPSTOX_API_SECRET,
        "redirect_uri": UPSTOX_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = requests.post(AUTH_URL, data=payload, headers=headers)
    res.raise_for_status()

    data = res.json()
    data["created_at"] = int(time.time())

    save_token(data)
    return data


def save_token(data: dict):
    with open(UPSTOX_TOKEN_FILE, "w") as f:
        json.dump(data, f)


def load_token():
    try:
        with open(UPSTOX_TOKEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
