from app.services.oanda_service import OandaService
from app.services.technical_indicators import (
    calculate_indicators,
    generate_trading_signal,
)


def scan_forex_opportunities():
    """Scan major forex pairs for trading signals"""
    oanda = OandaService()
    pairs = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CHF"]

    opportunities = []

    for pair in pairs:
        try:
            # Get historical data
            candles = oanda.get_historical_data(pair, granularity="H1", count=100)

            # Calculate indicators
            indicators = calculate_indicators(candles)

            # Generate signal
            signal = generate_trading_signal(indicators)

            # Only add strong signals
            if signal["confidence"] > 60 and signal["signal"] != "HOLD":
                opportunities.append(
                    {"pair": pair, "signal": signal, "indicators": indicators}
                )

        except Exception as e:
            print(f"Error analyzing {pair}: {e}")

    return opportunities
