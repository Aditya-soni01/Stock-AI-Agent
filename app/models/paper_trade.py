from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class PaperTrade:
    trade_id: str
    strategy_name: str
    symbol: str
    entry_time: str
    entry_price: float
    exit_time: Optional[str]
    exit_price: Optional[float]
    qty: int
    stop_loss: float
    target: float
    reason: str
    confidence: float
    pnl: Optional[float]
    result: Optional[str]
    indicators_snapshot: Dict[str, Any]
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
