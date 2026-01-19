import yfinance as yf

def fetch_price(symbol: str, period="6mo"):
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)

    if hist.empty:
        return None

    return hist
