import pandas as pd

class IndicatorAgent:
    def analyze(self, data: pd.DataFrame):
        close = data["Close"]

        # SMA
        sma_20 = close.rolling(window=20).mean().iloc[-1]

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_value = rsi.iloc[-1]

        return {
            "sma_20": round(float(sma_20), 2),
            "rsi": round(float(rsi_value), 2)
        }
        
    def indicator_fn(self, data):
        close = data["Close"]

        sma_20 = close.rolling(window=20).mean().iloc[-1]

        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return {
            "sma_20": float(sma_20),
            "rsi": float(rsi.iloc[-1])
        }
