import time
import requests
from app.services.upstox_auth_service import load_token, save_token
from app.core.config import UPSTOX_API_KEY, UPSTOX_API_SECRET

TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"


def is_token_expired(token: dict) -> bool:
    expires_in = token["expires_in"]
    created_at = token["created_at"]
    return time.time() > (created_at + expires_in - 300)  # 5 min buffer


def refresh_token():
    token = load_token()
    if not token:
        raise Exception("No Upstox token found")

    payload = {
        "refresh_token": token["refresh_token"],
        "client_id": UPSTOX_API_KEY,
        "client_secret": UPSTOX_API_SECRET,
        "grant_type": "refresh_token"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    res = requests.post(TOKEN_URL, data=payload, headers=headers)
    res.raise_for_status()

    data = res.json()
    data["created_at"] = int(time.time())
    save_token(data)

    return data
