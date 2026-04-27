# app/agents/decision_agent.py

from app.core.config import settings

class DecisionAgent:
    def __init__(self):
        # Only import OANDA if configured
        if settings.OANDA_API_KEY and settings.OANDA_ACCOUNT_ID:
            from app.services.oanda_service import OandaService
            self.oanda = OandaService()
        else:
            self.oanda = None
            print("⚠️  OANDA not configured - forex trading disabled")

    def analyze_forex(self, pair: str):
        if not self.oanda:
            return {"error": "OANDA not configured"}

        # Your forex analysis logic
        pass

    def analyze_stock(self, symbol: str):
        # Your stock analysis logic (using other services)
        pass
