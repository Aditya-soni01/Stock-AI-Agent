from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from app.core.config import UPSTOX_FRONTEND_REDIRECT_URI
from app.services.upstox_auth_service import exchange_code_for_token, get_login_url, get_token_status
from app.services.upstox_feed_service import UpstoxFeedService
from app.state.market_state import LIVE_PRICES
from app.utils.instrument_mapper import INSTRUMENTS

router = APIRouter()
_feed_service = UpstoxFeedService()


def _frontend_redirect_url(status: str, message: str | None = None) -> str:
    base_url = (UPSTOX_FRONTEND_REDIRECT_URI or "http://localhost:5173").rstrip("/")
    params = {"upstox": status}
    if message:
        params["message"] = message
    return f"{base_url}?{urlencode(params)}"


@router.get("/login")
def upstox_login(redirect: bool = Query(default=False)):
    try:
        login_url = get_login_url()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to build Upstox login URL: {exc}")

    if redirect:
        return RedirectResponse(url=login_url, status_code=307)
    return {"authorize_url": login_url}


@router.get("/callback")
def upstox_callback(code: str | None = Query(default=None)):
    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing 'code' query parameter. Open /upstox/login and finish OAuth flow.",
        )

    try:
        exchange_code_for_token(code)
        return RedirectResponse(
            url=_frontend_redirect_url("connected", "Upstox authentication successful."),
            status_code=303,
        )
    except RuntimeError as exc:
        return RedirectResponse(
            url=_frontend_redirect_url("error", f"Upstox callback failed: {exc}"),
            status_code=303,
        )
    except Exception as exc:
        return RedirectResponse(
            url=_frontend_redirect_url("error", f"Upstox callback failed: {exc}"),
            status_code=303,
        )


@router.get("/token/status")
def upstox_token_status():
    return get_token_status()


@router.get("/live/{symbol}")
def get_live_price(symbol: str):
    symbol = symbol.upper()

    if symbol not in INSTRUMENTS:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Symbol not supported",
                "symbol": symbol,
                "supported_symbols": sorted(INSTRUMENTS.keys()),
            },
        )

    instrument_key = INSTRUMENTS[symbol]

    if instrument_key not in LIVE_PRICES:
        return {
            "symbol": symbol,
            "instrument_key": instrument_key,
            "status": "waiting_for_data"
        }

    live_data = LIVE_PRICES[instrument_key]
    return {
        "symbol": symbol,
        "instrument_key": instrument_key,
        "ltp": live_data.get("ltp"),
        "timestamp": live_data.get("timestamp"),
        "status": "live",
    }


@router.get("/feed/status")
def feed_status():
    return _feed_service.status()


@router.post("/feed/start")
def feed_start():
    try:
        status = _feed_service.start()
        return {
            "message": "Upstox live feed start requested",
            "feed": status,
        }
    except RuntimeError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Cannot start Upstox feed",
                "error": str(exc),
                "token_status": get_token_status(),
                "next_step": "Authenticate via /upstox/login and complete /upstox/callback first.",
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to start Upstox feed",
                "error": str(exc),
                "next_step": "Check Upstox connectivity and token status, then retry.",
            },
        )


@router.post("/feed/stop")
def feed_stop():
    try:
        status = _feed_service.stop()
        return {
            "message": "Upstox live feed stopped",
            "feed": status,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to stop Upstox feed: {exc}")
