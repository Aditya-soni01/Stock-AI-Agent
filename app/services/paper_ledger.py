import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from app.core.config import PAPER_INITIAL_CAPITAL, PAPER_LEDGER_PATH
from app.models.paper_trade import PaperTrade
from app.services.paper_learning_stats import build_learning_stats


class PaperLedger:
    def __init__(self, ledger_path: str = PAPER_LEDGER_PATH):
        self.path = Path(ledger_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self.load()

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "execution_mode": "paper",
                "capital": float(PAPER_INITIAL_CAPITAL),
                "open_trades": [],
                "closed_trades": [],
            }
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {
                "execution_mode": "paper",
                "capital": float(PAPER_INITIAL_CAPITAL),
                "open_trades": [],
                "closed_trades": [],
            }

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def open_trade(self, trade: PaperTrade) -> Dict[str, Any]:
        trade_dict = trade.to_dict()
        self.data.setdefault("open_trades", []).append(trade_dict)
        self.save()
        print(
            json.dumps(
                {
                    "event": "paper_trade_opened",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "trade_id": trade_dict.get("trade_id"),
                    "symbol": trade_dict.get("symbol"),
                    "strategy_name": trade_dict.get("strategy_name"),
                    "entry_price": trade_dict.get("entry_price"),
                    "qty": trade_dict.get("qty"),
                }
            )
        )
        return trade_dict

    def get_open_trades(self) -> List[Dict[str, Any]]:
        return self.data.get("open_trades", [])

    def get_all_trades(self) -> List[Dict[str, Any]]:
        return self.data.get("open_trades", []) + self.data.get("closed_trades", [])

    def get_closed_trades(self) -> List[Dict[str, Any]]:
        return self.data.get("closed_trades", [])

    def get_trade_by_id(self, trade_id: str) -> Optional[Dict[str, Any]]:
        for trade in self.data.get("open_trades", []):
            if trade.get("trade_id") == trade_id:
                return trade
        for trade in self.data.get("closed_trades", []):
            if trade.get("trade_id") == trade_id:
                return trade
        return None

    def close_trade(
        self,
        trade_id: str,
        exit_price: float,
        close_reason: str,
        exit_time: Optional[str] = None,
    ) -> Dict[str, Any] | None:
        open_trades = self.data.get("open_trades", [])
        close_idx = None
        trade = None
        for idx, item in enumerate(open_trades):
            if item.get("trade_id") == trade_id and item.get("status") == "OPEN":
                close_idx = idx
                trade = dict(item)
                break

        if close_idx is None or trade is None:
            return None

        entry_price = float(trade.get("entry_price", 0.0))
        qty = int(trade.get("qty", 0))
        exit_price_f = float(exit_price)
        pnl = round((exit_price_f - entry_price) * qty, 2)
        if pnl > 0:
            result = "WIN"
        elif pnl < 0:
            result = "LOSS"
        else:
            result = "BREAKEVEN"

        trade["exit_time"] = exit_time or datetime.now(timezone.utc).isoformat()
        trade["exit_price"] = round(exit_price_f, 2)
        trade["pnl"] = pnl
        trade["result"] = result
        trade["status"] = "CLOSED"
        trade["close_reason"] = close_reason

        del open_trades[close_idx]
        self.data.setdefault("closed_trades", []).append(trade)
        self.save()
        print(
            json.dumps(
                {
                    "event": "paper_trade_closed",
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "trade_id": trade.get("trade_id"),
                    "symbol": trade.get("symbol"),
                    "strategy_name": trade.get("strategy_name"),
                    "exit_price": trade.get("exit_price"),
                    "pnl": trade.get("pnl"),
                    "result": trade.get("result"),
                    "close_reason": trade.get("close_reason"),
                }
            )
        )
        return trade

    def learning_stats(self) -> Dict[str, Any]:
        return build_learning_stats(self.get_all_trades())

    def daily_closed_trades(self, day_iso: str, tz_name: str = "Asia/Kolkata") -> List[Dict[str, Any]]:
        tz = ZoneInfo(tz_name)
        target_date = datetime.fromisoformat(day_iso).date()
        out: List[Dict[str, Any]] = []
        for trade in self.get_closed_trades():
            exit_time = trade.get("exit_time")
            if not exit_time:
                continue
            try:
                dt = datetime.fromisoformat(str(exit_time))
            except ValueError:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt.astimezone(tz).date() == target_date:
                out.append(trade)
        return out

    def daily_pnl(self, day_iso: str, tz_name: str = "Asia/Kolkata") -> float:
        trades = self.daily_closed_trades(day_iso=day_iso, tz_name=tz_name)
        total = 0.0
        for trade in trades:
            pnl = trade.get("pnl")
            if pnl is None:
                continue
            try:
                total += float(pnl)
            except (TypeError, ValueError):
                continue
        return round(total, 2)

    def daily_trade_count(self, day_iso: str, tz_name: str = "Asia/Kolkata") -> int:
        return len(self.daily_closed_trades(day_iso=day_iso, tz_name=tz_name))

    def daily_opened_trade_count(self, day_iso: str, tz_name: str = "Asia/Kolkata") -> int:
        tz = ZoneInfo(tz_name)
        target_date = datetime.fromisoformat(day_iso).date()
        count = 0
        for trade in self.get_all_trades():
            entry_time = trade.get("entry_time")
            if not entry_time:
                continue
            try:
                dt = datetime.fromisoformat(str(entry_time))
            except ValueError:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt.astimezone(tz).date() == target_date:
                count += 1
        return count

    def last_loss_time(self, day_iso: str, tz_name: str = "Asia/Kolkata") -> Optional[datetime]:
        trades = self.daily_closed_trades(day_iso=day_iso, tz_name=tz_name)
        latest: Optional[datetime] = None
        for trade in trades:
            pnl = trade.get("pnl")
            try:
                pnl_f = float(pnl)
            except (TypeError, ValueError):
                continue
            if pnl_f >= 0:
                continue
            exit_time = trade.get("exit_time")
            if not exit_time:
                continue
            try:
                dt = datetime.fromisoformat(str(exit_time))
            except ValueError:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if latest is None or dt > latest:
                latest = dt
        return latest

    def status(self) -> Dict[str, Any]:
        return {
            "execution_mode": self.data.get("execution_mode", "paper"),
            "capital": self.data.get("capital", float(PAPER_INITIAL_CAPITAL)),
            "open_trades": len(self.data.get("open_trades", [])),
            "closed_trades": len(self.data.get("closed_trades", [])),
            "ledger_path": str(self.path),
        }
