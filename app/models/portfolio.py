from typing import Dict

class Portfolio:
    def __init__(self, holdings: Dict):
        """
        holdings example:
        {
          "AAPL": {"quantity": 10, "avg_price": 230},
          "MSFT": {"quantity": 5, "avg_price": 320}
        }
        """
        self.holdings = holdings

    def has_stock(self, symbol: str) -> bool:
        return symbol in self.holdings

    def get_position(self, symbol: str):
        return self.holdings.get(symbol)
