from fastapi import APIRouter
from app.services.upstox_auth_service import (
    get_login_url,
    exchange_code_for_token
)

router = APIRouter(prefix="/upstox", tags=["Upstox"])


@router.get("/login")
def login():
    return {"login_url": get_login_url()}


@router.get("/callback")
def callback(code: str):
    exchange_code_for_token(code)
    return {"status": "Upstox authenticated successfully"}


@router.get("/live/{symbol}")
def get_live_price(symbol: str):
    instrument_key = INSTRUMENTS.get(symbol.upper())
    if not instrument_key:
        return {"error": "Symbol not mapped"}

    data = LIVE_PRICES.get(instrument_key)
    if not data:
        return {"status": "Waiting for live data..."}

    return {
        "symbol": symbol,
        "instrument_key": instrument_key,
        "ltp": data["ltp"],
        "timestamp": data["timestamp"]
    }


@router.get("/live")
def get_all_live_prices():
    return LIVE_PRICES
