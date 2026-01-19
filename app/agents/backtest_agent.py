class BacktestAgent:
    def run(self, data, indicators_fn, decision_fn):
        position = None
        trades = []
        peak_price = 0

        for i in range(20, len(data)):
            window = data.iloc[:i]
            price = float(window["Close"].iloc[-1])

            indicators = indicators_fn(window)
            action = decision_fn(
                price=price,
                sma=indicators["sma_20"],
                rsi=indicators["rsi"]
            )["action"]

            # BUY
            if action.startswith("Buy") and position is None:
                position = {
                    "entry_price": price,
                    "peak_price": price
                }

            # TRACK DRAWDOWN
            if position:
                position["peak_price"] = max(position["peak_price"], price)

            # SELL
            if action.startswith("Sell") and position:
                pnl = price - position["entry_price"]
                drawdown = position["entry_price"] - position["peak_price"]
                trade_date = window.index[-1]

                trades.append({
                    "entry_price": round(position["entry_price"], 2),
                    "exit_price": round(price, 2),
                    "pnl": round(pnl, 2),
                    "drawdown": round(drawdown, 2),
                    "exit_date": str(trade_date)
                })

                position = None

        final_pnl = round(sum(t["pnl"] for t in trades), 2)

        return {
            "total_trades": len(trades),
            "final_pnl": final_pnl,
            "trades": trades[-5:]  # last 5 completed trades
        }







# class BacktestAgent:
#     def run(self, data, indicators_fn, decision_fn):
#         cash = 0
#         position = 0
#         trades = []

#         for i in range(20, len(data)):
#             window = data.iloc[:i]
#             price = float(window["Close"].iloc[-1])

#             indicators = indicators_fn(window)
#             decision = decision_fn(
#                 price=price,
#                 sma=indicators["sma_20"],
#                 rsi=indicators["rsi"]
#             )["action"]

#             if decision.startswith("Buy") and position == 0:
#                 position = 1
#                 cash -= price
#                 trades.append({"type": "BUY", "price": price})

#             elif decision.startswith("Sell") and position == 1:
#                 position = 0
#                 cash += price
#                 trades.append({"type": "SELL", "price": price})

#         final_value = cash + (position * data["Close"].iloc[-1])

#         return {
#             "total_trades": len(trades),
#             "final_pnl": round(final_value, 2),
#             "trades": trades[-5:]  # last 5 trades
#         }
