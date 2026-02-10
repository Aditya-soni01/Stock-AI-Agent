import yfinance as yf

class MarketDataProvider:
    def get_intraday(self, symbol: str):
        data = yf.download(
            symbol,
            period="1d",
            interval="5m",
            progress=False
        )
        return data
