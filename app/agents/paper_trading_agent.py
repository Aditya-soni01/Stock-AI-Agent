from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict, List

from app.core.config import PAPER_DEFAULT_QTY
from app.data.india_symbols import NIFTY_50
from app.models.paper_trade import PaperTrade
from app.services.paper_ledger import PaperLedger
from app.services.technical_indicators import build_paper_signal_snapshot
from app.state.market_state import LIVE_PRICES
from app.tools.market_data import fetch_price
from app.utils.instrument_mapper import INSTRUMENTS


class PaperTradingAgent:
    def __init__(self):
        self.ledger = PaperLedger()
        self._strategy_multipliers: Dict[str, float] = {}

    def evaluate_nifty50_once(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        signals: List[Dict[str, Any]] = []
        opened: List[Dict[str, Any]] = []

        for symbol in NIFTY_50:
            signal = self._evaluate_symbol(symbol)
            signals.append(signal)
            if signal.get("action") == "BUY":
                opened_trade = self._open_paper_trade_if_buy(signal, now)
                if opened_trade:
                    opened.append(opened_trade)

        return {
            "run_at": now,
            "universe": "NIFTY50",
            "signals_count": len(signals),
            "buy_signals": len([s for s in signals if s.get("action") == "BUY"]),
            "opened_trades": opened,
            "signals": signals,
        }

    def run_paper_cycle(self, allow_new_entries: bool) -> Dict[str, Any]:
        update_result = self.update_open_paper_trades_once()
        if not allow_new_entries:
            return {
                "run_at": update_result["run_at"],
                "allow_new_entries": False,
                "update_result": update_result,
                "entry_result": None,
            }
        entry_result = self.evaluate_nifty50_once()
        return {
            "run_at": update_result["run_at"],
            "allow_new_entries": True,
            "update_result": update_result,
            "entry_result": entry_result,
        }

    def update_open_paper_trades_once(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        open_trades = list(self.ledger.get_open_trades())
        closed_trades: List[Dict[str, Any]] = []
        skipped: List[Dict[str, Any]] = []

        for trade in open_trades:
            trade_id = trade.get("trade_id")
            symbol = str(trade.get("symbol", ""))
            if not trade_id or not symbol:
                skipped.append(
                    {
                        "trade_id": trade_id,
                        "symbol": symbol,
                        "message": "Skipping malformed open trade entry",
                    }
                )
                continue

            latest_price = self._get_latest_price_for_symbol(symbol)
            if latest_price is None:
                skipped.append(
                    {
                        "trade_id": trade_id,
                        "symbol": symbol,
                        "message": "Waiting for live/latest price",
                    }
                )
                continue

            stop_loss = float(trade.get("stop_loss", 0.0))
            target = float(trade.get("target", 0.0))
            strategy_name = str(trade.get("strategy_name") or "")

            close_reason = None
            if latest_price <= stop_loss:
                close_reason = "stop_loss_hit"
            elif latest_price >= target:
                close_reason = "target_hit"
            elif self._should_exit_by_strategy(strategy_name, symbol):
                close_reason = "strategy_exit_signal"

            if close_reason:
                closed = self.ledger.close_trade(
                    trade_id=trade_id,
                    exit_price=latest_price,
                    close_reason=close_reason,
                    exit_time=now,
                )
                if closed:
                    closed_trades.append(closed)

        return {
            "run_at": now,
            "open_trades_checked": len(open_trades),
            "closed_count": len(closed_trades),
            "closed_trades": closed_trades,
            "skipped_count": len(skipped),
            "skipped": skipped,
        }

    def _evaluate_symbol(self, symbol: str) -> Dict[str, Any]:
        candles = fetch_price(symbol, period="1y")
        status, snapshot = build_paper_signal_snapshot(candles)
        if status != "ok":
            return {
                "symbol": symbol,
                "action": "HOLD",
                "status": "insufficient_data",
                "strategy_name": None,
                "confidence": 0.0,
                "reason": "insufficient_data",
                "indicators_snapshot": snapshot,
            }

        close = snapshot["close"]
        ema50 = snapshot["ema50"]
        ema200 = snapshot["ema200"]
        rsi2 = snapshot["rsi2"]
        st = snapshot["supertrend"]

        # Strategy 1: Trend-following EMA50/200 + Supertrend filter
        trend_ok = close > ema50 > ema200
        if st.get("status") == "ok":
            trend_ok = trend_ok and st.get("trend") == "up"
        if trend_ok:
            signal = {
                "symbol": symbol,
                "action": "BUY",
                "status": "ok",
                "strategy_name": "ema50_200_supertrend",
                "confidence": 0.68,
                "reason": "trend_filter_passed",
                "indicators_snapshot": snapshot,
            }
            return self._apply_confidence_multiplier(signal)

        # Strategy 2: RSI(2) oversold bounce above EMA200
        mean_rev_ok = close > ema200 and rsi2 <= 10.0
        if mean_rev_ok:
            signal = {
                "symbol": symbol,
                "action": "BUY",
                "status": "ok",
                "strategy_name": "rsi2_mean_reversion_above_ema200",
                "confidence": 0.62,
                "reason": "rsi2_oversold_above_ema200",
                "indicators_snapshot": snapshot,
            }
            return self._apply_confidence_multiplier(signal)

        return {
            "symbol": symbol,
            "action": "HOLD",
            "status": "ok",
            "strategy_name": None,
            "confidence": 0.5,
            "reason": "no_entry_condition",
            "indicators_snapshot": snapshot,
        }

    def _apply_confidence_multiplier(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        strategy = signal.get("strategy_name")
        if not strategy:
            return signal

        if not self._strategy_multipliers:
            stats = self.ledger.learning_stats()
            self._strategy_multipliers = {
                name: float(data.get("confidence_multiplier", 1.0))
                for name, data in stats.get("strategies", {}).items()
            }

        multiplier = float(self._strategy_multipliers.get(strategy, 1.0))
        base_conf = float(signal.get("confidence", 0.0))
        adjusted = max(0.0, min(0.99, round(base_conf * multiplier, 3)))

        out = dict(signal)
        out["base_confidence"] = base_conf
        out["confidence_multiplier"] = multiplier
        out["confidence"] = adjusted
        return out

    def _open_paper_trade_if_buy(self, signal: Dict[str, Any], now_iso: str) -> Dict[str, Any] | None:
        symbol = signal["symbol"]
        open_trades = self.ledger.get_open_trades()
        if any(t.get("symbol") == symbol and t.get("status") == "OPEN" for t in open_trades):
            return None

        # Prefer live mapped LTP when available.
        base_symbol = symbol.upper().split(".")[0]
        instrument_key = INSTRUMENTS.get(base_symbol)
        live_price = None
        if instrument_key and instrument_key in LIVE_PRICES:
            live_price = LIVE_PRICES[instrument_key].get("ltp")

        entry_price = float(live_price if live_price is not None else signal["indicators_snapshot"]["close"])
        strategy = signal["strategy_name"]
        if strategy == "ema50_200_supertrend":
            stop_loss = round(entry_price * 0.98, 2)
            target = round(entry_price * 1.04, 2)
        else:
            stop_loss = round(entry_price * 0.985, 2)
            target = round(entry_price * 1.025, 2)

        trade = PaperTrade(
            trade_id=str(uuid4()),
            strategy_name=strategy or "unknown",
            symbol=symbol,
            entry_time=now_iso,
            entry_price=round(entry_price, 2),
            exit_time=None,
            exit_price=None,
            qty=int(PAPER_DEFAULT_QTY),
            stop_loss=stop_loss,
            target=target,
            reason=signal.get("reason", ""),
            confidence=float(signal.get("confidence", 0.0)),
            pnl=None,
            result=None,
            indicators_snapshot=signal.get("indicators_snapshot", {}),
            status="OPEN",
        )
        return self.ledger.open_trade(trade)

    def _get_latest_price_for_symbol(self, symbol: str) -> float | None:
        base_symbol = symbol.upper().split(".")[0]
        instrument_key = INSTRUMENTS.get(base_symbol)
        if instrument_key and instrument_key in LIVE_PRICES:
            ltp = LIVE_PRICES[instrument_key].get("ltp")
            if ltp is not None:
                return float(ltp)

        candles = fetch_price(symbol, period="5d")
        if candles is None or candles.empty:
            return None
        close_value = candles["Close"].iloc[-1]
        return float(close_value)

    def _should_exit_by_strategy(self, strategy_name: str, symbol: str) -> bool:
        candles = fetch_price(symbol, period="1y")
        status, snapshot = build_paper_signal_snapshot(candles)
        if status != "ok":
            return False

        close = float(snapshot["close"])
        ema50 = float(snapshot["ema50"])
        ema200 = float(snapshot["ema200"])
        rsi2 = float(snapshot["rsi2"])
        supertrend = snapshot.get("supertrend", {})

        if strategy_name == "ema50_200_supertrend":
            st_down = supertrend.get("status") == "ok" and supertrend.get("trend") == "down"
            return close < ema50 or st_down

        if strategy_name == "rsi2_mean_reversion_above_ema200":
            return close < ema200 or rsi2 >= 70.0

        return False
