class TradeStatsAgent:
    def calculate(self, trades: list):
        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "max_drawdown": 0,
                "expectancy": 0,
                "profit_factor": 0
            }

        wins = [t["pnl"] for t in trades if t["pnl"] > 0]
        losses = [t["pnl"] for t in trades if t["pnl"] < 0]

        total_trades = len(trades)
        win_rate = (len(wins) / total_trades) * 100

        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))

        profit_factor = (
            gross_profit / gross_loss if gross_loss > 0 else 0
        )

        expectancy = (
            (win_rate / 100) * avg_win +
            ((100 - win_rate) / 100) * avg_loss
        )

        max_drawdown = min([t["drawdown"] for t in trades], default=0)

        return {
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "max_drawdown": round(max_drawdown, 2),
            "expectancy": round(expectancy, 2),
            "profit_factor": round(profit_factor, 2)
        }
