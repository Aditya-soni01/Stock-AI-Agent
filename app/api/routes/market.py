import json
from datetime import datetime, time, timedelta
from threading import Event, Lock, Thread
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Body, HTTPException
from app.agents.india_market_scanner import IndiaMarketScanner
from app.agents.paper_trading_agent import PaperTradingAgent
from app.core.config import EXECUTION_MODE
from app.data.india_symbols import INDIA_INDEX_SYMBOLS, NIFTY_50
from app.services.paper_ledger import PaperLedger
from app.services.paper_learning_stats import build_learning_stats
from app.state.market_state import LIVE_PRICES, PAPER_ENGINE_STATE, PAPER_LAST_SIGNALS
from app.utils.instrument_mapper import INSTRUMENTS

router = APIRouter()

_IST = ZoneInfo("Asia/Kolkata")
_RUNNER_LOCK = Lock()
_RUNNER_STOP_EVENT = Event()
_RUNNER_THREAD: Optional[Thread] = None
_RUNNER_STATE: Dict[str, Any] = {
    "running": False,
    "started_at": None,
    "stopped_at": None,
    "last_cycle_at": None,
    "last_cycle_result": None,
    "last_guard": None,
    "config": {
        "interval_seconds": 60,
        "max_trades_per_day": 10,
        "max_daily_loss": 5000.0,
        "cooldown_after_loss_minutes": 15,
        "cutoff_time_ist": "15:00",
        "market_open_ist": "09:15",
        "market_close_ist": "15:30",
    },
}


def _log_event(event: str, payload: Dict[str, Any]) -> None:
    print(json.dumps({"event": event, "ts": datetime.utcnow().isoformat(), **payload}))


def _parse_hhmm(value: str) -> time:
    hh, mm = value.split(":")
    return time(hour=int(hh), minute=int(mm))


def _sanitize_runner_config(base_cfg: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    cfg = dict(base_cfg)
    for k in cfg.keys():
        if k in incoming:
            cfg[k] = incoming[k]

    cfg["interval_seconds"] = int(cfg["interval_seconds"])
    cfg["max_trades_per_day"] = int(cfg["max_trades_per_day"])
    cfg["max_daily_loss"] = float(cfg["max_daily_loss"])
    cfg["cooldown_after_loss_minutes"] = int(cfg["cooldown_after_loss_minutes"])
    cfg["cutoff_time_ist"] = str(cfg["cutoff_time_ist"])
    cfg["market_open_ist"] = str(cfg["market_open_ist"])
    cfg["market_close_ist"] = str(cfg["market_close_ist"])

    if cfg["interval_seconds"] < 1:
        raise ValueError("interval_seconds must be >= 1")
    if cfg["max_trades_per_day"] < 0:
        raise ValueError("max_trades_per_day must be >= 0")
    if cfg["max_daily_loss"] <= 0:
        raise ValueError("max_daily_loss must be > 0")
    if cfg["cooldown_after_loss_minutes"] < 0:
        raise ValueError("cooldown_after_loss_minutes must be >= 0")

    _parse_hhmm(cfg["cutoff_time_ist"])
    _parse_hhmm(cfg["market_open_ist"])
    _parse_hhmm(cfg["market_close_ist"])
    return cfg


def _is_weekday(now_ist: datetime) -> bool:
    return now_ist.weekday() <= 4


def _is_market_hours(now_ist: datetime, open_hhmm: str, close_hhmm: str) -> bool:
    if not _is_weekday(now_ist):
        return False
    start_t = _parse_hhmm(open_hhmm)
    end_t = _parse_hhmm(close_hhmm)
    now_t = now_ist.time()
    return start_t <= now_t <= end_t


def _is_after_cutoff(now_ist: datetime, cutoff_hhmm: str) -> bool:
    cutoff_t = _parse_hhmm(cutoff_hhmm)
    return now_ist.time() >= cutoff_t


def _runner_guard(ledger: PaperLedger, cfg: Dict[str, Any]) -> Dict[str, Any]:
    now_ist = datetime.now(_IST)
    day_iso = now_ist.date().isoformat()
    guard = {
        "allow_new_entries": True,
        "reason": "ok",
        "now_ist": now_ist.isoformat(),
        "day_iso": day_iso,
    }

    if not _is_market_hours(now_ist, cfg["market_open_ist"], cfg["market_close_ist"]):
        guard["allow_new_entries"] = False
        guard["reason"] = "market_hours_block"
        return guard

    if _is_after_cutoff(now_ist, cfg["cutoff_time_ist"]):
        guard["allow_new_entries"] = False
        guard["reason"] = "cutoff_time_block"
        return guard

    daily_trade_count = ledger.daily_opened_trade_count(day_iso=day_iso)
    if daily_trade_count >= int(cfg["max_trades_per_day"]):
        guard["allow_new_entries"] = False
        guard["reason"] = "max_trades_per_day_block"
        return guard

    daily_pnl = ledger.daily_pnl(day_iso=day_iso)
    if daily_pnl <= -abs(float(cfg["max_daily_loss"])):
        guard["allow_new_entries"] = False
        guard["reason"] = "max_daily_loss_block"
        return guard

    last_loss_time = ledger.last_loss_time(day_iso=day_iso)
    if last_loss_time is not None:
        cooldown_mins = int(cfg["cooldown_after_loss_minutes"])
        cooldown_until = last_loss_time.astimezone(_IST) + timedelta(minutes=cooldown_mins)
        if now_ist < cooldown_until:
            guard["allow_new_entries"] = False
            guard["reason"] = "cooldown_after_loss_block"
            guard["cooldown_until_ist"] = cooldown_until.isoformat()
            return guard

    return guard


def _paper_runner_loop():
    while not _RUNNER_STOP_EVENT.is_set():
        cfg = {"interval_seconds": 60}
        try:
            with _RUNNER_LOCK:
                cfg = dict(_RUNNER_STATE["config"])
            ledger = PaperLedger()
            guard = _runner_guard(ledger, cfg)
            if not guard.get("allow_new_entries", False):
                _log_event(
                    "paper_runner_guard_block",
                    {
                        "reason": guard.get("reason"),
                        "day_iso": guard.get("day_iso"),
                        "now_ist": guard.get("now_ist"),
                    },
                )
            agent = PaperTradingAgent()
            cycle = agent.run_paper_cycle(allow_new_entries=bool(guard["allow_new_entries"]))
            with _RUNNER_LOCK:
                _RUNNER_STATE["last_cycle_at"] = cycle["run_at"]
                _RUNNER_STATE["last_cycle_result"] = cycle
                _RUNNER_STATE["last_guard"] = guard
        except Exception as e:
            with _RUNNER_LOCK:
                _RUNNER_STATE["last_cycle_at"] = datetime.utcnow().isoformat()
                _RUNNER_STATE["last_cycle_result"] = {"error": str(e)}
                _RUNNER_STATE["last_guard"] = {"allow_new_entries": False, "reason": "runner_error"}

        wait_sec = int(cfg.get("interval_seconds", 60))
        if _RUNNER_STOP_EVENT.wait(timeout=max(1, wait_sec)):
            break

    with _RUNNER_LOCK:
        _RUNNER_STATE["running"] = False
        _RUNNER_STATE["stopped_at"] = datetime.utcnow().isoformat()


def _nifty50_market_data_status() -> Dict[str, Any]:
    instrument_key = INSTRUMENTS.get("NIFTY50", "NSE_INDEX|Nifty 50")
    live = LIVE_PRICES.get(instrument_key)
    if not live:
        return {
            "symbol": "NIFTY50",
            "instrument_key": instrument_key,
            "status": "waiting_for_data",
            "message": "No live Upstox feed data available yet for NIFTY50.",
        }

    return {
        "symbol": "NIFTY50",
        "instrument_key": instrument_key,
        "status": "live",
        "ltp": live.get("ltp"),
        "timestamp": live.get("timestamp"),
    }

@router.get("/top-movers")
def top_movers():
    try:
        scanner = IndiaMarketScanner()
        symbols = NIFTY_50 + INDIA_INDEX_SYMBOLS
        return scanner.scan(symbols)

    except Exception as e:
        print("[API ERROR]", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch intraday market movers"
        )


@router.post("/paper/start")
def start_paper_trading():
    if EXECUTION_MODE != "paper":
        raise HTTPException(
            status_code=400,
            detail="Paper trading endpoint is disabled when execution_mode is not 'paper'",
        )
    try:
        agent = PaperTradingAgent()
        result = agent.evaluate_nifty50_once()
        PAPER_ENGINE_STATE["running"] = True
        PAPER_ENGINE_STATE["last_run_at"] = result["run_at"]
        PAPER_ENGINE_STATE["last_result"] = {
            "signals_count": result["signals_count"],
            "buy_signals": result["buy_signals"],
            "opened_trades": len(result["opened_trades"]),
        }
        PAPER_LAST_SIGNALS.clear()
        PAPER_LAST_SIGNALS.extend(result["signals"])
        return {
            "execution_mode": "paper",
            "running": PAPER_ENGINE_STATE["running"],
            "result": PAPER_ENGINE_STATE["last_result"],
            "learning_stats": agent.ledger.learning_stats(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Paper trading start failed: {e}")


@router.get("/paper/status")
def paper_status():
    ledger = PaperLedger()
    return {
        "execution_mode": EXECUTION_MODE,
        "engine": PAPER_ENGINE_STATE,
        "ledger": ledger.status(),
        "learning_stats": ledger.learning_stats(),
        "last_signals_count": len(PAPER_LAST_SIGNALS),
    }


@router.get("/paper/trades")
def paper_trades():
    ledger = PaperLedger()
    all_trades = ledger.get_all_trades()
    return {
        "execution_mode": EXECUTION_MODE,
        "trades": all_trades,
        "count": len(all_trades),
        "learning_stats": ledger.learning_stats(),
    }


@router.post("/paper/update")
def paper_update():
    if EXECUTION_MODE != "paper":
        raise HTTPException(
            status_code=400,
            detail="Paper trading update endpoint is disabled when execution_mode is not 'paper'",
        )
    try:
        agent = PaperTradingAgent()
        update_result = agent.update_open_paper_trades_once()
        return {
            "execution_mode": "paper",
            "message": "Paper trades updated successfully",
            "update": update_result,
            "learning_stats": agent.ledger.learning_stats(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Paper trading update failed: {e}")


@router.post("/paper/close/{trade_id}")
def paper_manual_close(trade_id: str):
    if EXECUTION_MODE != "paper":
        raise HTTPException(
            status_code=400,
            detail="Manual paper close endpoint is disabled when execution_mode is not 'paper'",
        )
    ledger = PaperLedger()
    trade = ledger.get_trade_by_id(trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail=f"Trade not found: {trade_id}")
    if trade.get("status") != "OPEN":
        raise HTTPException(status_code=400, detail=f"Trade is not open: {trade_id}")

    try:
        agent = PaperTradingAgent()
        symbol = str(trade.get("symbol", ""))
        latest_price = agent._get_latest_price_for_symbol(symbol)
        if latest_price is None:
            raise HTTPException(
                status_code=409,
                detail=f"Unable to close trade {trade_id}: waiting for latest price for {symbol}",
            )

        closed = ledger.close_trade(
            trade_id=trade_id,
            exit_price=latest_price,
            close_reason="manual_close",
        )
        if closed is None:
            raise HTTPException(status_code=404, detail=f"Open trade not found: {trade_id}")
        return {
            "execution_mode": "paper",
            "message": f"Trade {trade_id} closed manually",
            "trade": closed,
            "learning_stats": ledger.learning_stats(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual paper close failed: {e}")


@router.post("/paper/runner/start")
def paper_runner_start(payload: Dict[str, Any] = Body(default=None)):
    if EXECUTION_MODE != "paper":
        raise HTTPException(
            status_code=400,
            detail="Runner start failed: execution_mode must be 'paper'",
        )

    global _RUNNER_THREAD
    with _RUNNER_LOCK:
        if _RUNNER_STATE["running"]:
            runner_snapshot = dict(_RUNNER_STATE)
            runner_snapshot["config"] = dict(_RUNNER_STATE["config"])
            return {
                "execution_mode": EXECUTION_MODE,
                "running": True,
                "message": "Paper runner is already running",
                "runner": runner_snapshot,
            }

        incoming = payload or {}
        try:
            cfg = _sanitize_runner_config(dict(_RUNNER_STATE["config"]), incoming)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid runner config: {e}")
        _RUNNER_STATE["config"] = cfg
        _RUNNER_STATE["running"] = True
        _RUNNER_STATE["started_at"] = datetime.utcnow().isoformat()
        _RUNNER_STATE["stopped_at"] = None
        _RUNNER_STATE["last_cycle_at"] = None
        _RUNNER_STATE["last_cycle_result"] = None
        _RUNNER_STATE["last_guard"] = None

    _RUNNER_STOP_EVENT.clear()
    _RUNNER_THREAD = Thread(target=_paper_runner_loop, daemon=True, name="paper-runner")
    _RUNNER_THREAD.start()
    with _RUNNER_LOCK:
        runner_snapshot = dict(_RUNNER_STATE)
        runner_snapshot["config"] = dict(_RUNNER_STATE["config"])
    _log_event(
        "paper_runner_started",
        {
            "running": True,
            "config": runner_snapshot["config"],
        },
    )
    return {
        "execution_mode": EXECUTION_MODE,
        "running": True,
        "message": "Paper runner started",
        "runner": runner_snapshot,
    }


@router.post("/paper/runner/stop")
def paper_runner_stop():
    global _RUNNER_THREAD
    with _RUNNER_LOCK:
        was_running = bool(_RUNNER_STATE["running"])
    if not was_running:
        with _RUNNER_LOCK:
            runner_snapshot = dict(_RUNNER_STATE)
            runner_snapshot["config"] = dict(_RUNNER_STATE["config"])
        return {
            "execution_mode": EXECUTION_MODE,
            "running": False,
            "message": "Paper runner is already stopped",
            "runner": runner_snapshot,
        }

    _RUNNER_STOP_EVENT.set()
    thread = _RUNNER_THREAD
    if thread is not None:
        thread.join(timeout=5)
    with _RUNNER_LOCK:
        _RUNNER_STATE["running"] = False
        _RUNNER_STATE["stopped_at"] = datetime.utcnow().isoformat()
        runner_snapshot = dict(_RUNNER_STATE)
        runner_snapshot["config"] = dict(_RUNNER_STATE["config"])
    _RUNNER_THREAD = None
    _log_event(
        "paper_runner_stopped",
        {
            "running": False,
            "stopped_at": runner_snapshot.get("stopped_at"),
        },
    )
    return {
        "execution_mode": EXECUTION_MODE,
        "running": False,
        "message": "Paper runner stopped safely",
        "runner": runner_snapshot,
    }


@router.get("/paper/runner/status")
def paper_runner_status():
    ledger = PaperLedger()
    with _RUNNER_LOCK:
        runner_snapshot = dict(_RUNNER_STATE)
        runner_snapshot["config"] = dict(_RUNNER_STATE["config"])
    guard = _runner_guard(ledger, dict(runner_snapshot["config"]))
    return {
        "execution_mode": EXECUTION_MODE,
        "runner": runner_snapshot,
        "current_guard": guard,
        "market_data": _nifty50_market_data_status(),
        "learning_stats": ledger.learning_stats(),
    }


def _trade_timestamp_in_window(trade: Dict[str, Any], start_dt: datetime, end_dt: datetime) -> bool:
    for raw in (trade.get("entry_time"), trade.get("exit_time")):
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(str(raw))
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        if start_dt <= dt <= end_dt:
            return True
    return False


def _report_for_window(start_dt: datetime, end_dt: datetime, report_name: str) -> Dict[str, Any]:
    ledger = PaperLedger()
    all_trades = ledger.get_all_trades()
    scoped = [t for t in all_trades if _trade_timestamp_in_window(t, start_dt, end_dt)]
    open_trades = [t for t in scoped if t.get("status") == "OPEN"]
    closed_trades = [t for t in scoped if t.get("status") == "CLOSED"]
    stats = build_learning_stats(scoped)
    overall = stats.get("overall", {})
    total_pnl = 0.0
    for trade in scoped:
        pnl = trade.get("pnl")
        if pnl is None:
            continue
        try:
            total_pnl += float(pnl)
        except (TypeError, ValueError):
            continue

    by_strategy: Dict[str, Dict[str, float]] = {}
    for trade in closed_trades:
        strategy = str(trade.get("strategy_name") or "unknown")
        by_strategy.setdefault(strategy, {"count": 0.0, "pnl": 0.0})
        by_strategy[strategy]["count"] += 1
        try:
            by_strategy[strategy]["pnl"] += float(trade.get("pnl") or 0.0)
        except (TypeError, ValueError):
            continue

    best_strategy = None
    worst_strategy = None
    if by_strategy:
        ranked = sorted(by_strategy.items(), key=lambda x: x[1]["pnl"], reverse=True)
        best_strategy = {"name": ranked[0][0], "pnl": round(ranked[0][1]["pnl"], 2), "trades": int(ranked[0][1]["count"])}
        worst_strategy = {
            "name": ranked[-1][0],
            "pnl": round(ranked[-1][1]["pnl"], 2),
            "trades": int(ranked[-1][1]["count"]),
        }

    with _RUNNER_LOCK:
        latest_guard_reason = (_RUNNER_STATE.get("last_guard") or {}).get("reason")

    return {
        "execution_mode": EXECUTION_MODE,
        "report": report_name,
        "window": {
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
        },
        "total_trades": len(scoped),
        "open_trades": len(open_trades),
        "closed_trades": len(closed_trades),
        "win_rate": overall.get("win_rate", 0.0),
        "total_pnl": round(total_pnl, 2),
        "max_drawdown_proxy": overall.get("drawdown_proxy", 0.0),
        "best_strategy": best_strategy,
        "worst_strategy": worst_strategy,
        "latest_guard_reason": latest_guard_reason,
        "market_data": _nifty50_market_data_status(),
        "learning_stats": stats,
    }


@router.get("/paper/report/daily")
def paper_daily_report():
    now_ist = datetime.now(_IST)
    start_ist = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
    return _report_for_window(
        start_dt=start_ist.astimezone(ZoneInfo("UTC")),
        end_dt=now_ist.astimezone(ZoneInfo("UTC")),
        report_name="daily",
    )


@router.get("/paper/report/session")
def paper_session_report():
    now_utc = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    with _RUNNER_LOCK:
        started_at = _RUNNER_STATE.get("started_at")

    if started_at:
        try:
            start_dt = datetime.fromisoformat(str(started_at))
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=ZoneInfo("UTC"))
        except ValueError:
            start_dt = now_utc - timedelta(hours=24)
    else:
        start_dt = now_utc - timedelta(hours=24)

    return _report_for_window(
        start_dt=start_dt,
        end_dt=now_utc,
        report_name="session",
    )
