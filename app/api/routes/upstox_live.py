from fastapi import APIRouter, HTTPException
from app.state.market_state import LIVE_PRICES
from app.utils.instrument_mapper import INSTRUMENTS

router = APIRouter()


@router.get("/live/{symbol}")
def get_live_price(symbol: str):
    symbol = symbol.upper()

    if symbol not in INSTRUMENTS:
        raise HTTPException(status_code=404, detail="Symbol not supported")

    instrument_key = INSTRUMENTS[symbol]

    if instrument_key not in LIVE_PRICES:
        return {
            "symbol": symbol,
            "status": "waiting_for_data"
        }

    return {
        "symbol": symbol,
        "instrument_key": instrument_key,
        "ltp": LIVE_PRICES[instrument_key]["ltp"],
        "timestamp": LIVE_PRICES[instrument_key]["timestamp"]
    }
