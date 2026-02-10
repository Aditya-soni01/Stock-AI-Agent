from fastapi import APIRouter, HTTPException
from app.agents.india_market_scanner import IndiaMarketScanner
from app.data.india_symbols import NIFTY_50

router = APIRouter()

@router.get("/top-movers")
def top_movers():
    try:
        scanner = IndiaMarketScanner()
        return scanner.scan(NIFTY_50)

    except Exception as e:
        print("[API ERROR]", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch intraday market movers"
        )
