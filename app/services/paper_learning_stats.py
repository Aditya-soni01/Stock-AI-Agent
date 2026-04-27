from __future__ import annotations

from typing import Any, Dict, List


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _max_drawdown_proxy(pnls: List[float]) -> float:
    """
    Drawdown proxy from cumulative trade PnL sequence.
    Returns positive number representing worst peak-to-trough drop.
    """
    if not pnls:
        return 0.0
    cumulative = 0.0
    peak = 0.0
    max_dd = 0.0
    for pnl in pnls:
        cumulative += pnl
        if cumulative > peak:
            peak = cumulative
        dd = peak - cumulative
        if dd > max_dd:
            max_dd = dd
    return round(max_dd, 2)


def _confidence_multiplier(
    total: int, win_rate: float, expectancy: float, drawdown_proxy: float, gross_profit: float, gross_loss: float
) -> float:
    if total < 5:
        return 1.0

    multiplier = 1.0

    if win_rate >= 0.60:
        multiplier += 0.08
    elif win_rate <= 0.40:
        multiplier -= 0.08

    if expectancy > 0:
        multiplier += 0.07
    elif expectancy < 0:
        multiplier -= 0.07

    if gross_profit > 0 and drawdown_proxy > (gross_profit * 0.50):
        multiplier -= 0.08

    if gross_loss == 0 and gross_profit > 0:
        multiplier += 0.02

    return round(max(0.70, min(1.20, multiplier)), 3)


def build_learning_stats(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute strategy-level paper-learning stats from stored trades.
    Uses only trades that have numeric pnl.
    """
    strategies: Dict[str, List[Dict[str, Any]]] = {}
    for trade in trades:
        name = str(trade.get("strategy_name") or "unknown")
        strategies.setdefault(name, []).append(trade)

    strategy_stats: Dict[str, Dict[str, Any]] = {}
    for strategy_name, items in strategies.items():
        pnl_series: List[float] = []
        wins = 0
        losses = 0
        gross_profit = 0.0
        gross_loss = 0.0

        for item in items:
            pnl = _safe_float(item.get("pnl"))
            if pnl is None:
                continue
            pnl_series.append(pnl)
            if pnl > 0:
                wins += 1
                gross_profit += pnl
            elif pnl < 0:
                losses += 1
                gross_loss += pnl

        total = len(pnl_series)
        if total == 0:
            strategy_stats[strategy_name] = {
                "trades_with_pnl": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "expectancy": 0.0,
                "drawdown_proxy": 0.0,
                "confidence_multiplier": 1.0,
            }
            continue

        win_rate = round(wins / total, 4)
        expectancy = round(sum(pnl_series) / total, 2)
        drawdown_proxy = _max_drawdown_proxy(pnl_series)
        avg_win = round(gross_profit / wins, 2) if wins > 0 else 0.0
        avg_loss = round(gross_loss / losses, 2) if losses > 0 else 0.0
        multiplier = _confidence_multiplier(
            total=total,
            win_rate=win_rate,
            expectancy=expectancy,
            drawdown_proxy=drawdown_proxy,
            gross_profit=round(gross_profit, 2),
            gross_loss=round(gross_loss, 2),
        )

        strategy_stats[strategy_name] = {
            "trades_with_pnl": total,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "expectancy": expectancy,
            "drawdown_proxy": drawdown_proxy,
            "confidence_multiplier": multiplier,
        }

    all_pnls: List[float] = []
    for trade in trades:
        pnl = _safe_float(trade.get("pnl"))
        if pnl is not None:
            all_pnls.append(pnl)

    overall_total = len(all_pnls)
    overall_wins = len([x for x in all_pnls if x > 0])
    overall_losses = len([x for x in all_pnls if x < 0])
    overall_win_rate = round(overall_wins / overall_total, 4) if overall_total else 0.0
    overall_expectancy = round(sum(all_pnls) / overall_total, 2) if overall_total else 0.0
    overall_drawdown = _max_drawdown_proxy(all_pnls)

    return {
        "overall": {
            "trades_with_pnl": overall_total,
            "wins": overall_wins,
            "losses": overall_losses,
            "win_rate": overall_win_rate,
            "expectancy": overall_expectancy,
            "drawdown_proxy": overall_drawdown,
        },
        "strategies": strategy_stats,
    }
