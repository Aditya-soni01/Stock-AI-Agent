import json
import os
import time
from typing import Any, Dict
from urllib.parse import urlencode

import requests

from app.core.config import UPSTOX_API_KEY, UPSTOX_API_SECRET, UPSTOX_REDIRECT_URI, UPSTOX_TOKEN_FILE

AUTH_DIALOG_URL = "https://api.upstox.com/v2/login/authorization/dialog"
AUTH_TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"
_EXPIRY_BUFFER_SECONDS = 300


def _token_file_path() -> str:
    return str(UPSTOX_TOKEN_FILE or "upstox_token.json")


def get_login_url() -> str:
    if not UPSTOX_API_KEY:
        raise RuntimeError("UPSTOX_API_KEY is not configured")
    if not UPSTOX_REDIRECT_URI:
        raise RuntimeError("UPSTOX_REDIRECT_URI is not configured")

    query = urlencode(
        {
            "response_type": "code",
            "client_id": UPSTOX_API_KEY,
            "redirect_uri": UPSTOX_REDIRECT_URI,
        }
    )
    return f"{AUTH_DIALOG_URL}?{query}"


def exchange_code_for_token(code: str) -> Dict[str, Any]:
    if not code or not str(code).strip():
        raise RuntimeError("Missing OAuth code from Upstox callback")
    if not UPSTOX_API_KEY or not UPSTOX_API_SECRET:
        raise RuntimeError("UPSTOX_API_KEY / UPSTOX_API_SECRET are not configured")
    if not UPSTOX_REDIRECT_URI:
        raise RuntimeError("UPSTOX_REDIRECT_URI is not configured")

    payload = {
        "code": str(code).strip(),
        "client_id": UPSTOX_API_KEY,
        "client_secret": UPSTOX_API_SECRET,
        "redirect_uri": UPSTOX_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Api-Version": "2.0",
    }

    response = requests.post(AUTH_TOKEN_URL, data=payload, headers=headers, timeout=20)
    if response.status_code >= 400:
        message = f"Upstox token exchange failed: HTTP {response.status_code}"
        try:
            error_payload = response.json()
            error_detail = error_payload.get("errors") or error_payload.get("message")
            if error_detail:
                message = f"{message} ({error_detail})"
        except Exception:
            pass
        raise RuntimeError(message)

    token_payload = response.json()
    token_payload["created_at"] = int(time.time())
    save_token(token_payload)
    return token_payload


def save_token(data: Dict[str, Any]) -> None:
    token_file = _token_file_path()
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_token() -> Dict[str, Any] | None:
    token_file = _token_file_path()
    try:
        with open(token_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except FileNotFoundError:
        return None

    if not isinstance(loaded, dict):
        return None
    return loaded


def get_token_status() -> Dict[str, Any]:
    token_file = _token_file_path()
    token = load_token()
    status: Dict[str, Any] = {
        "token_file": token_file,
        "exists": bool(token is not None and os.path.exists(token_file)),
        "ready": False,
        "expired": None,
        "reason": "",
        "created_at": None,
        "expires_in": None,
        "expires_at": None,
        "has_access_token": False,
        "has_refresh_token": False,
    }

    if token is None:
        status["reason"] = "token_missing"
        return status

    created_at = token.get("created_at")
    expires_in = token.get("expires_in")
    access_token = token.get("access_token")
    refresh_token = token.get("refresh_token")

    status["has_access_token"] = bool(access_token)
    status["has_refresh_token"] = bool(refresh_token)

    if not access_token:
        status["reason"] = "access_token_missing"
        status["expired"] = True
        return status

    if created_at is None:
        status["reason"] = "expiry_metadata_missing"
        status["expired"] = True
        return status

    if expires_in is None:
        try:
            status["created_at"] = int(created_at)
        except (TypeError, ValueError):
            status["reason"] = "expiry_metadata_invalid"
            status["expired"] = True
            return status

        status["reason"] = "ready_expiry_unknown"
        status["expired"] = None
        status["ready"] = True
        return status

    try:
        created_at_int = int(created_at)
        expires_in_int = int(expires_in)
    except (TypeError, ValueError):
        status["reason"] = "expiry_metadata_invalid"
        status["expired"] = True
        return status

    expires_at = created_at_int + expires_in_int
    now_ts = int(time.time())
    expired = now_ts >= (expires_at - _EXPIRY_BUFFER_SECONDS)

    status["created_at"] = created_at_int
    status["expires_in"] = expires_in_int
    status["expires_at"] = expires_at
    status["expired"] = expired
    status["ready"] = not expired
    status["reason"] = "ready" if not expired else "token_expired"
    return status
