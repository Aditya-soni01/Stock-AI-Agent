from fastapi import APIRouter, HTTPException
from app.agents.orchestrator import StockOrchestrator

router = APIRouter()

@router.get("/analyze/{symbol}")
def analyze_stock(symbol: str):
    try:
        orchestrator = StockOrchestrator()
        result = orchestrator.run(symbol)

        if not result:
            raise HTTPException(status_code=404, detail="No market data found")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
