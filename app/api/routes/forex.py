from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from app.services.oanda_service import OandaService
from app.services.technical_indicators import (
    calculate_indicators, 
    generate_trading_signal, 
    calculate_support_resistance
)

router = APIRouter()

# Initialize service (will be used across endpoints)
oanda = OandaService()


# ==================== DATA MODELS ====================

class OrderRequest(BaseModel):
    pair: str
    units: int  # Positive = BUY, Negative = SELL
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PairsList(BaseModel):
    pairs: List[str]


# ==================== MARKET DATA ENDPOINTS ====================

@router.get("/price/{pair}")
def get_forex_price(pair: str):
    """
    Get real-time forex price for a currency pair
    
    Example: /forex/price/EUR_USD
    """
    try:
        price = oanda.get_live_price(pair)
        return {
            "pair": pair,
            "data": price,
            "bid": price['bids'][0]['price'],
            "ask": price['asks'][0]['price'],
            "spread": round(float(price['asks'][0]['price']) - float(price['bids'][0]['price']), 5)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price: {str(e)}")


@router.get("/historical/{pair}")
def get_historical_data(
    pair: str, 
    timeframe: str = Query("H1", description="Candle timeframe (M1, M5, M15, H1, H4, D)"),
    count: int = Query(100, ge=1, le=5000, description="Number of candles")
):
    """
    Get historical candlestick data
    
    Timeframes: M1, M5, M15, M30, H1, H4, D, W, M
    """
    try:
        candles = oanda.get_historical_data(pair, granularity=timeframe, count=count)
        
        # Format response
        formatted_candles = []
        for candle in candles:
            formatted_candles.append({
                "time": candle['time'],
                "open": float(candle['mid']['o']),
                "high": float(candle['mid']['h']),
                "low": float(candle['mid']['l']),
                "close": float(candle['mid']['c']),
                "volume": int(candle['volume'])
            })
        
        return {
            "pair": pair,
            "timeframe": timeframe,
            "count": len(formatted_candles),
            "candles": formatted_candles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")


# ==================== TECHNICAL ANALYSIS ENDPOINTS ====================

@router.get("/analyze/{pair}")
def analyze_pair(
    pair: str, 
    timeframe: str = Query("H1", description="Analysis timeframe")
):
    """
    Get complete technical analysis for a currency pair
    
    Returns:
    - All technical indicators (RSI, MACD, Bollinger Bands, etc.)
    - Trading signal (BUY/SELL/HOLD)
    - Support/Resistance levels
    - Confidence score
    """
    try:
        # Get historical data
        candles = oanda.get_historical_data(pair, granularity=timeframe, count=100)
        
        # Calculate all indicators
        indicators = calculate_indicators(candles)
        
        # Generate trading signal
        signal = generate_trading_signal(indicators)
        
        # Support/Resistance levels
        levels = calculate_support_resistance(candles)
        
        return {
            "pair": pair,
            "timeframe": timeframe,
            "timestamp": candles[-1]['time'],
            "signal": signal,
            "indicators": indicators,
            "levels": levels,
            "recommendation": {
                "action": signal['signal'],
                "confidence": f"{signal['confidence']}%",
                "reasons": signal['reasons']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/indicators/{pair}")
def get_indicators_only(
    pair: str, 
    timeframe: str = Query("H1", description="Timeframe for indicators")
):
    """
    Get only technical indicators without trading signal
    """
    try:
        candles = oanda.get_historical_data(pair, granularity=timeframe, count=100)
        indicators = calculate_indicators(candles)
        
        return {
            "pair": pair,
            "timeframe": timeframe,
            "indicators": indicators
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signal/{pair}")
def get_trading_signal(
    pair: str, 
    timeframe: str = Query("H1", description="Signal timeframe")
):
    """
    Get trading signal only (BUY/SELL/HOLD)
    """
    try:
        candles = oanda.get_historical_data(pair, granularity=timeframe, count=100)
        indicators = calculate_indicators(candles)
        signal = generate_trading_signal(indicators)
        
        return {
            "pair": pair,
            "timeframe": timeframe,
            "signal": signal['signal'],
            "confidence": signal['confidence'],
            "reasons": signal['reasons'],
            "current_price": indicators['current_price']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MULTI-PAIR ANALYSIS ====================

@router.post("/scan")
def scan_multiple_pairs(pairs_list: PairsList, timeframe: str = "H1"):
    """
    Scan multiple currency pairs for trading opportunities
    
    Request body:
    {
        "pairs": ["EUR_USD", "GBP_USD", "USD_JPY"]
    }
    """
    results = []
    
    for pair in pairs_list.pairs:
        try:
            candles = oanda.get_historical_data(pair, granularity=timeframe, count=100)
            indicators = calculate_indicators(candles)
            signal = generate_trading_signal(indicators)
            
            # Only include pairs with actionable signals
            if signal['signal'] != "HOLD" and signal['confidence'] > 60:
                results.append({
                    "pair": pair,
                    "signal": signal['signal'],
                    "confidence": signal['confidence'],
                    "current_price": indicators['current_price'],
                    "rsi": indicators['rsi'],
                    "reasons": signal['reasons']
                })
        except Exception as e:
            print(f"Error scanning {pair}: {e}")
            continue
    
    # Sort by confidence
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        "timeframe": timeframe,
        "total_scanned": len(pairs_list.pairs),
        "opportunities_found": len(results),
        "results": results
    }


@router.get("/scan/major")
def scan_major_pairs(timeframe: str = Query("H1", description="Scan timeframe")):
    """
    Quick scan of major forex pairs
    
    Scans: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CHF, USD/CAD
    """
    major_pairs = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CHF", "USD_CAD"]
    
    return scan_multiple_pairs(PairsList(pairs=major_pairs), timeframe)


# ==================== TRADING ENDPOINTS ====================

@router.post("/order")
def place_order(order: OrderRequest):
    """
    Place a market order
    
    Request body:
    {
        "pair": "EUR_USD",
        "units": 1000,        // Positive = BUY, Negative = SELL
        "stop_loss": 1.0850,  // Optional
        "take_profit": 1.0950 // Optional
    }
    """
    try:
        response = oanda.place_order(
            instrument=order.pair,
            units=order.units,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit
        )
        
        return {
            "status": "success",
            "order": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Order failed: {str(e)}")


@router.get("/positions")
def get_open_positions():
    """Get all open positions"""
    try:
        # You'll need to add this method to OandaService
        positions = oanda.get_open_positions()
        return {"positions": positions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/pending")
def get_pending_orders():
    """Get all pending orders"""
    try:
        # You'll need to add this method to OandaService
        orders = oanda.get_pending_orders()
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ACCOUNT ENDPOINTS ====================

@router.get("/account")
def get_account():
    """Get account summary (balance, equity, margin, etc.)"""
    try:
        account_info = oanda.get_account_summary()
        
        return {
            "account_id": account_info['account']['id'],
            "currency": account_info['account']['currency'],
            "balance": account_info['account']['balance'],
            "unrealized_pl": account_info['account'].get('unrealizedPL', 0),
            "margin_used": account_info['account'].get('marginUsed', 0),
            "margin_available": account_info['account'].get('marginAvailable', 0),
            "open_trades": account_info['account'].get('openTradeCount', 0),
            "open_positions": account_info['account'].get('openPositionCount', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Account error: {str(e)}")


@router.get("/account/summary")
def get_account_performance():
    """Get account performance metrics"""
    try:
        account_info = oanda.get_account_summary()
        account = account_info['account']
        
        balance = float(account['balance'])
        unrealized_pl = float(account.get('unrealizedPL', 0))
        equity = balance + unrealized_pl
        
        return {
            "balance": balance,
            "equity": equity,
            "profit_loss": unrealized_pl,
            "profit_loss_percent": round((unrealized_pl / balance) * 100, 2) if balance > 0 else 0,
            "open_trades": account.get('openTradeCount', 0),
            "margin_used_percent": round((float(account.get('marginUsed', 0)) / balance) * 100, 2) if balance > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== UTILITY ENDPOINTS ====================

@router.get("/pairs")
def get_available_pairs():
    """Get list of available forex pairs"""
    major_pairs = [
        "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD", "USD_CAD", "NZD_USD"
    ]
    
    cross_pairs = [
        "EUR_GBP", "EUR_JPY", "EUR_CHF", "EUR_AUD", "EUR_CAD",
        "GBP_JPY", "GBP_CHF", "GBP_AUD", "GBP_CAD",
        "AUD_JPY", "AUD_CAD", "AUD_CHF",
        "NZD_JPY", "CAD_JPY", "CHF_JPY"
    ]
    
    return {
        "major_pairs": major_pairs,
        "cross_pairs": cross_pairs,
        "total": len(major_pairs) + len(cross_pairs)
    }


@router.get("/health")
def health_check():
    """Check if OANDA service is working"""
    try:
        oanda.get_account_summary()
        return {
            "status": "healthy",
            "service": "oanda",
            "authenticated": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "oanda",
            "authenticated": False,
            "error": str(e)
        }
