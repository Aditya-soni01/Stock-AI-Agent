# app/agents/market_agent.py
import datetime
from typing import Any, Optional

def is_forex_market_open():
    """Forex market is open 24/5 (closed weekends)"""
    now = datetime.datetime.utcnow()
    weekday = now.weekday()
    
    # Monday 00:00 UTC to Friday 22:00 UTC
    if weekday < 5:  # Monday to Friday
        return True
    return False


class MarketAgent:
    """Agent responsible for market data analysis"""
    
    def __init__(self):
        """Initialize the Market Agent"""
        self.name = "MarketAgent"
    
    def analyze_market(self, symbol: str) -> dict[str, Any]:
        """
        Analyze market conditions for a given symbol
        
        Args:
            symbol: Stock/Forex symbol to analyze
            
        Returns:
            Dictionary containing market analysis
        """
        return {
            "symbol": symbol,
            "market_open": is_forex_market_open(),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "status": "success"
        }
    
    def get_market_data(self, symbol: str, timeframe: Optional[str] = "1D") -> dict[str, Any]:
        """
        Fetch market data for a symbol
        
        Args:
            symbol: Stock/Forex symbol
            timeframe: Timeframe for data (1D, 1H, etc.)
            
        Returns:
            Market data dictionary
        """
        # Add your market data fetching logic here
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": []
        }
