class PortfolioAgent:
    def analyze(self, symbol: str, portfolio):
        if portfolio.has_stock(symbol):
            position = portfolio.get_position(symbol)

            return {
                "status": "Already Holding",
                "quantity": position["quantity"],
                "avg_price": position["avg_price"]
            }

        return {
            "status": "Not Holding"
        }
