import pandas as pd
import numpy as np
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from typing import List, Dict

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
