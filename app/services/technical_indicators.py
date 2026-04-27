import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from typing import Any, Dict, List, Tuple

def calculate_indicators(candles: List[Dict]) -> Dict:
    """
    Calculate technical indicators from OANDA candles
    
    Args:
        candles: List of candle dictionaries from OANDA API
        
    Returns:
        Dictionary with all calculated indicators
    """
    df = pd.DataFrame(candles)
    
    # Extract OHLC data from OANDA format
    df['open'] = df['mid'].apply(lambda x: float(x['o']))
    df['high'] = df['mid'].apply(lambda x: float(x['h']))
    df['low'] = df['mid'].apply(lambda x: float(x['l']))
    df['close'] = df['mid'].apply(lambda x: float(x['c']))
    df['volume'] = df['volume'].astype(float)
    
    # Initialize indicators dictionary
    indicators = {}
    
    # RSI (Relative Strength Index)
    rsi = RSIIndicator(close=df['close'], window=14)
    indicators['rsi'] = round(rsi.rsi().iloc[-1], 2)
    indicators['rsi_signal'] = get_rsi_signal(indicators['rsi'])
    
    # MACD (Moving Average Convergence Divergence)
    macd = MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
    indicators['macd'] = round(macd.macd().iloc[-1], 5)
    indicators['macd_signal'] = round(macd.macd_signal().iloc[-1], 5)
    indicators['macd_diff'] = round(macd.macd_diff().iloc[-1], 5)
    indicators['macd_crossover'] = get_macd_signal(indicators['macd'], indicators['macd_signal'])
    
    # Moving Averages
    sma_20 = SMAIndicator(close=df['close'], window=20)
    sma_50 = SMAIndicator(close=df['close'], window=50)
    ema_12 = EMAIndicator(close=df['close'], window=12)
    ema_26 = EMAIndicator(close=df['close'], window=26)
    
    indicators['sma_20'] = round(sma_20.sma_indicator().iloc[-1], 5)
    indicators['sma_50'] = round(sma_50.sma_indicator().iloc[-1], 5)
    indicators['ema_12'] = round(ema_12.ema_indicator().iloc[-1], 5)
    indicators['ema_26'] = round(ema_26.ema_indicator().iloc[-1], 5)
    
    # Bollinger Bands
    bollinger = BollingerBands(close=df['close'], window=20, window_dev=2)
    indicators['bb_upper'] = round(bollinger.bollinger_hband().iloc[-1], 5)
    indicators['bb_middle'] = round(bollinger.bollinger_mavg().iloc[-1], 5)
    indicators['bb_lower'] = round(bollinger.bollinger_lband().iloc[-1], 5)
    indicators['bb_width'] = round(bollinger.bollinger_wband().iloc[-1], 5)
    
    # ATR (Average True Range) - Volatility
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
    indicators['atr'] = round(atr.average_true_range().iloc[-1], 5)
    
    # Stochastic Oscillator
    stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
    indicators['stoch_k'] = round(stoch.stoch().iloc[-1], 2)
    indicators['stoch_d'] = round(stoch.stoch_signal().iloc[-1], 2)
    
    # Current price
    indicators['current_price'] = df['close'].iloc[-1]
    indicators['price_change'] = round(df['close'].iloc[-1] - df['close'].iloc[-2], 5)
    indicators['price_change_percent'] = round(((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) * 100, 2)
    
    return indicators


def get_rsi_signal(rsi: float) -> str:
    """Get trading signal from RSI"""
    if rsi < 30:
        return "OVERSOLD - BUY"
    elif rsi > 70:
        return "OVERBOUGHT - SELL"
    else:
        return "NEUTRAL"


def get_macd_signal(macd: float, signal: float) -> str:
    """Get trading signal from MACD crossover"""
    if macd > signal:
        return "BULLISH - BUY"
    elif macd < signal:
        return "BEARISH - SELL"
    else:
        return "NEUTRAL"


def calculate_support_resistance(candles: List[Dict], window: int = 20) -> Dict:
    """Calculate support and resistance levels"""
    df = pd.DataFrame(candles)
    df['high'] = df['mid'].apply(lambda x: float(x['h']))
    df['low'] = df['mid'].apply(lambda x: float(x['l']))
    
    # Recent highs and lows
    resistance = df['high'].rolling(window=window).max().iloc[-1]
    support = df['low'].rolling(window=window).min().iloc[-1]
    
    return {
        "resistance": round(resistance, 5),
        "support": round(support, 5)
    }


def generate_trading_signal(indicators: Dict) -> Dict:
    """
    Generate comprehensive trading signal based on multiple indicators
    
    Returns:
        Dictionary with signal, confidence, and reasoning
    """
    signals = []
    
    # RSI Signal
    if indicators['rsi'] < 30:
        signals.append(("BUY", 0.7, "RSI oversold"))
    elif indicators['rsi'] > 70:
        signals.append(("SELL", 0.7, "RSI overbought"))
    
    # MACD Signal
    if indicators['macd_diff'] > 0:
        signals.append(("BUY", 0.6, "MACD bullish crossover"))
    elif indicators['macd_diff'] < 0:
        signals.append(("SELL", 0.6, "MACD bearish crossover"))
    
    # Moving Average Signal
    if indicators['ema_12'] > indicators['ema_26']:
        signals.append(("BUY", 0.5, "EMA bullish trend"))
    else:
        signals.append(("SELL", 0.5, "EMA bearish trend"))
    
    # Bollinger Bands Signal
    current_price = indicators['current_price']
    if current_price < indicators['bb_lower']:
        signals.append(("BUY", 0.6, "Price below lower Bollinger Band"))
    elif current_price > indicators['bb_upper']:
        signals.append(("SELL", 0.6, "Price above upper Bollinger Band"))
    
    # Aggregate signals
    buy_signals = [s for s in signals if s[0] == "BUY"]
    sell_signals = [s for s in signals if s[0] == "SELL"]
    
    if len(buy_signals) > len(sell_signals):
        avg_confidence = sum([s[1] for s in buy_signals]) / len(buy_signals)
        reasons = [s[2] for s in buy_signals]
        return {
            "signal": "BUY",
            "confidence": round(avg_confidence * 100, 1),
            "reasons": reasons,
            "strength": len(buy_signals)
        }
    elif len(sell_signals) > len(buy_signals):
        avg_confidence = sum([s[1] for s in sell_signals]) / len(sell_signals)
        reasons = [s[2] for s in sell_signals]
        return {
            "signal": "SELL",
            "confidence": round(avg_confidence * 100, 1),
            "reasons": reasons,
            "strength": len(sell_signals)
        }
    else:
        return {
            "signal": "HOLD",
            "confidence": 50.0,
            "reasons": ["Mixed signals"],
            "strength": 0
        }


def _to_ohlc_dataframe(candles: Any) -> pd.DataFrame:
    """
    Normalize candles into a dataframe with open/high/low/close columns.
    Accepts:
    - pandas DataFrame with OHLC columns (any case)
    - list of dict candles with close/high/low/open keys
    - list of dict candles with OANDA 'mid' object
    """
    if isinstance(candles, pd.DataFrame):
        df = candles.copy()
        renamed = {}
        for c in df.columns:
            lc = str(c).lower()
            if lc == "close":
                renamed[c] = "close"
            elif lc == "open":
                renamed[c] = "open"
            elif lc == "high":
                renamed[c] = "high"
            elif lc == "low":
                renamed[c] = "low"
        if renamed:
            df = df.rename(columns=renamed)
        return df

    if isinstance(candles, list) and candles:
        df = pd.DataFrame(candles)
        if "mid" in df.columns:
            df["open"] = df["mid"].apply(lambda x: float(x["o"]))
            df["high"] = df["mid"].apply(lambda x: float(x["h"]))
            df["low"] = df["mid"].apply(lambda x: float(x["l"]))
            df["close"] = df["mid"].apply(lambda x: float(x["c"]))
            return df

        lower_cols = {str(c).lower(): c for c in df.columns}
        out = pd.DataFrame()
        for name in ("open", "high", "low", "close"):
            if name in lower_cols:
                out[name] = pd.to_numeric(df[lower_cols[name]], errors="coerce")
        return out

    return pd.DataFrame()


def compute_ema_series(candles: Any, period: int) -> Dict[str, Any]:
    df = _to_ohlc_dataframe(candles)
    if df.empty or "close" not in df.columns or len(df) < period:
        return {"status": "insufficient_data", "period": period, "value": None}
    ema = EMAIndicator(close=df["close"], window=period).ema_indicator().iloc[-1]
    return {"status": "ok", "period": period, "value": float(ema)}


def compute_rsi_series(candles: Any, period: int = 2) -> Dict[str, Any]:
    df = _to_ohlc_dataframe(candles)
    if df.empty or "close" not in df.columns or len(df) < period + 1:
        return {"status": "insufficient_data", "period": period, "value": None}
    rsi = RSIIndicator(close=df["close"], window=period).rsi().iloc[-1]
    return {"status": "ok", "period": period, "value": float(rsi)}


def compute_supertrend(candles: Any, period: int = 10, multiplier: float = 3.0) -> Dict[str, Any]:
    """
    Safe/simple Supertrend helper.
    Returns trend in {'up','down'} when enough data is present.
    """
    df = _to_ohlc_dataframe(candles)
    needed = max(period + 2, 20)
    if df.empty or not {"high", "low", "close"}.issubset(df.columns) or len(df) < needed:
        return {"status": "insufficient_data", "trend": None, "value": None}

    atr = AverageTrueRange(
        high=df["high"], low=df["low"], close=df["close"], window=period
    ).average_true_range()
    hl2 = (df["high"] + df["low"]) / 2.0
    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr

    final_upper = upper_band.copy()
    final_lower = lower_band.copy()
    direction = [True] * len(df)  # True => uptrend

    for i in range(1, len(df)):
        final_upper.iloc[i] = (
            upper_band.iloc[i]
            if (upper_band.iloc[i] < final_upper.iloc[i - 1] or df["close"].iloc[i - 1] > final_upper.iloc[i - 1])
            else final_upper.iloc[i - 1]
        )
        final_lower.iloc[i] = (
            lower_band.iloc[i]
            if (lower_band.iloc[i] > final_lower.iloc[i - 1] or df["close"].iloc[i - 1] < final_lower.iloc[i - 1])
            else final_lower.iloc[i - 1]
        )

        if direction[i - 1]:
            direction[i] = df["close"].iloc[i] > final_upper.iloc[i]
        else:
            direction[i] = df["close"].iloc[i] >= final_lower.iloc[i]

    last_idx = len(df) - 1
    st_value = final_lower.iloc[last_idx] if direction[last_idx] else final_upper.iloc[last_idx]
    return {
        "status": "ok",
        "trend": "up" if direction[last_idx] else "down",
        "value": float(st_value),
    }


def build_paper_signal_snapshot(candles: Any) -> Tuple[str, Dict[str, Any]]:
    """
    Build signal snapshot for paper trading strategies.
    Returns tuple: (status, snapshot_dict)
    status in {'ok','insufficient_data'}.
    """
    df = _to_ohlc_dataframe(candles)
    if df.empty or "close" not in df.columns:
        return "insufficient_data", {"reason": "missing_close_data"}

    ema50 = compute_ema_series(df, 50)
    ema200 = compute_ema_series(df, 200)
    rsi2 = compute_rsi_series(df, 2)
    st = compute_supertrend(df, period=10, multiplier=3.0)

    if any(x.get("status") != "ok" for x in (ema50, ema200, rsi2)):
        return "insufficient_data", {
            "ema50": ema50,
            "ema200": ema200,
            "rsi2": rsi2,
            "supertrend": st,
        }

    snapshot = {
        "close": float(df["close"].iloc[-1]),
        "ema50": float(ema50["value"]),
        "ema200": float(ema200["value"]),
        "rsi2": float(rsi2["value"]),
        "supertrend": st,
    }
    return "ok", snapshot
