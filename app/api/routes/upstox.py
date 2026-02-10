"""
Upstox OAuth flow. API Key & Secret are used only in backend.
React never touches Upstox directly; it redirects to /upstox/login.
"""
from typing import Optional
import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.config.settings import (
    UPSTOX_API_KEY,
    UPSTOX_API_SECRET,
    UPSTOX_REDIRECT_URI,
    UPSTOX_FRONTEND_REDIRECT_URI,
)

router = APIRouter()

# In-memory store for access_token. TODO: Replace with DB/Redis for production.
_upstox_access_token: Optional[str] = None


def get_upstox_access_token() -> Optional[str]:
    """Return current Upstox access token (for REST/WebSocket use)."""
    return _upstox_access_token


@router.get("/login")
def upstox_login():
    """
    Redirects user to Upstox login/authorization dialog.
    React should call: window.location.href = API_BASE + "/upstox/login"
    """
    if not UPSTOX_API_KEY or not UPSTOX_REDIRECT_URI:
        raise HTTPException(
            status_code=500,
            detail="Upstox is not configured. Set UPSTOX_API_KEY and UPSTOX_REDIRECT_URI.",
        )
    auth_url = (
        "https://api.upstox.com/v2/login/authorization/dialog"
        f"?response_type=code"
        f"&client_id={UPSTOX_API_KEY}"
        f"&redirect_uri={UPSTOX_REDIRECT_URI}"
    )
    return RedirectResponse(auth_url)

@router.get("/top-movers")
def upstox_top_movers():
    """
    Return recent top movers (or positions) seen by backend.
    If not connected to Upstox yet, returns connected=False and empty list.
    Replace mock data below with real Upstox API calls using get_upstox_access_token().
    """
    token = get_upstox_access_token()
    if not token:
        return {"connected": False, "top_movers": []}

    # TODO: Replace this mock with a real Upstox REST call using the token.
    top_movers = [
        {
            "symbol": "RELIANCE",
            "trend": "Bullish",
            "signal": "BUY",
            "confidence": 88,
            "timeframe": "15m",
            "lastUpdated": "just now",
        },
        {
            "symbol": "TCS",
            "trend": "Bearish",
            "signal": "SELL",
            "confidence": 75,
            "timeframe": "1h",
            "lastUpdated": "2 min ago",
        },
    ]
    return {"connected": True, "top_movers": top_movers}

@router.get("/callback")
def upstox_callback(code: Optional[str] = None):
    """
    Upstox redirects HERE automatically after the user authorizes (you never put a code in the URL).
    Flow: User clicks Connect Upstox -> /upstox/login -> Upstox login page -> user approves
    -> Upstox redirects to this URL with ?code=XXXXX -> we exchange code for access_token.
    """
    global _upstox_access_token

    # You do NOT manually open this URL with a code. Upstox redirects with ?code=... after login.
    if not code or not code.strip():
        return RedirectResponse(
            url=f"{UPSTOX_FRONTEND_REDIRECT_URI}?upstox=error&reason=missing_code"
        )

    if not UPSTOX_API_KEY or not UPSTOX_API_SECRET or not UPSTOX_REDIRECT_URI:
        raise HTTPException(
            status_code=500,
            detail="Upstox is not configured. Set UPSTOX_API_KEY, UPSTOX_API_SECRET, UPSTOX_REDIRECT_URI.",
        )

    token_url = "https://api.upstox.com/v2/login/authorization/token"
    payload = {
        "code": code.strip(),
        "client_id": UPSTOX_API_KEY,
        "client_secret": UPSTOX_API_SECRET,
        "redirect_uri": UPSTOX_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=payload, headers=headers, timeout=10)

    if not response.ok:
        # Invalid/expired code or redirect_uri mismatch -> send user to app with error
        return RedirectResponse(
            url=f"{UPSTOX_FRONTEND_REDIRECT_URI}?upstox=error&reason=invalid_code"
        )

    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return RedirectResponse(
            url=f"{UPSTOX_FRONTEND_REDIRECT_URI}?upstox=error&reason=no_token"
        )

    _upstox_access_token = access_token
    # TODO: Store access_token securely (DB / Redis / encrypted file) and associate with user/session
    return RedirectResponse(url=f"{UPSTOX_FRONTEND_REDIRECT_URI}?upstox=connected")
