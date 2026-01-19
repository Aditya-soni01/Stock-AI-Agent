class TrendAgent:
    def analyze(self, close_price: float):
        if close_price > 200:
            trend = "Bullish"
        else:
            trend = "Neutral"

        return {
            "trend": trend,
            "confidence": "low"
        }
