from pydantic import BaseModel

class ForexPair(BaseModel):
    pair: str  # e.g., "EUR_USD"
    bid: float
    ask: float
    spread: float
    timestamp: str

class ForexSignal(BaseModel):
    pair: str
    action: str  # "BUY" or "SELL"
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
