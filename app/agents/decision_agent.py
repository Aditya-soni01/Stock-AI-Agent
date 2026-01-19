class DecisionAgent:
    def decide(self, price: float, sma: float, rsi: float, news: dict=None):
        reasons = []

        # --- Indicator interpretation ---
        if price > sma:
            reasons.append("Price above SMA (uptrend)")
        else:
            reasons.append("Price below SMA (downtrend)")

        if rsi < 35:
            reasons.append("RSI oversold")
        elif rsi > 65:
            reasons.append("RSI overbought")

        # --- Base technical decision ---
        if price > sma and rsi < 40:
            action = "Buy"
        elif price < sma and rsi > 60:
            action = "Sell"
        elif abs(price - sma) / sma < 0.01:
            action = "Wait"
        else:
            action = "Hold"

        # --- NEWS RISK OVERRIDE (IMPORTANT PART) ---
        if news:
            if news["sentiment"] == "Bearish" and news["confidence"] > 0.6:
                return {
                    "action": "Wait",
                    "override": "Negative news sentiment",
                    "reasons": reasons + ["High-confidence bearish news"]
                }

            if news["sentiment"] == "Bullish" and news["confidence"] > 0.6 and action == "Sell":
                return {
                    "action": "Hold",
                    "override": "Positive news sentiment",
                    "reasons": reasons + ["High-confidence bullish news"]
                }

        # --- Final decision ---
        return {
            "action": action,
            "reasons": reasons
        }
