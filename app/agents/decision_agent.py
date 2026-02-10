from app.services.technical_indicators import calculate_indicators, generate_trading_signal
from app.services.oanda_service import OandaService
from typing import Dict, List, Any

def make_trading_decision(pair: str, timeframe: str = "H1"):
    """Make trading decision for a specific pair"""
    oanda = OandaService()
    
    # Get data
    candles = oanda.get_historical_data(pair, granularity=timeframe, count=100)
    
    # Calculate indicators
    indicators = calculate_indicators(candles)
    
    # Generate signal
    signal = generate_trading_signal(indicators)
    
    return {
        "pair": pair,
        "action": signal['signal'],
        "confidence": signal['confidence'],
        "entry_price": indicators['current_price'],
        "stop_loss": calculate_stop_loss(indicators),
        "take_profit": calculate_take_profit(indicators),
        "indicators": indicators
    }

def calculate_stop_loss(indicators: Dict) -> float:
    """Calculate stop loss based on ATR"""
    atr = indicators['atr']
    current_price = indicators['current_price']
    return round(current_price - (2 * atr), 5)  # 2x ATR

def calculate_take_profit(indicators: Dict) -> float:
    """Calculate take profit based on ATR"""
    atr = indicators['atr']
    current_price = indicators['current_price']
    return round(current_price + (3 * atr), 5)  # 3x ATR (1.5 risk-reward)
