def simple_trend(close_price: float):
    if close_price > 180:
        return "BULLISH"
    elif close_price < 160:
        return "BEARISH"
    return "SIDEWAYS"
