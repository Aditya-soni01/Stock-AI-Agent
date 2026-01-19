class RiskAgent:
    def analyze(self, volume: int):
        if volume > 50_000_000:
            risk = "High Volatility"
        else:
            risk = "Moderate"

        return {
            "risk_level": risk
        }
