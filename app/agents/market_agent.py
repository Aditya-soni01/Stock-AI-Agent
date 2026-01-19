from app.tools.market_data import fetch_price

class MarketAgent:
    def analyze(self, symbol: str):
        data = fetch_price(symbol)
        return data
