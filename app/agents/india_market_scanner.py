from app.state.market_state import LIVE_PRICES
from app.utils.instrument_mapper import INSTRUMENTS


def scan_forex_opportunities():
    """Scan major forex pairs for trading signals"""
    # Lazy import keeps India/Upstox paths bootable when forex deps are absent.
    from app.services.oanda_service import OandaService
    from app.services.technical_indicators import (
        calculate_indicators,
        generate_trading_signal,
    )

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


class IndiaMarketScanner:
    """Scanner for India symbols based on mapped instrument live prices."""

    def scan(self, symbols):
        results = []

        for raw_symbol in symbols:
            symbol = (raw_symbol or "").upper()
            base_symbol = symbol.split(".")[0]
            mapped_symbol = base_symbol if base_symbol in INSTRUMENTS else symbol
            instrument_key = INSTRUMENTS.get(mapped_symbol)

            if not instrument_key:
                results.append(
                    {
                        "symbol": symbol,
                        "status": "unsupported_symbol",
                    }
                )
                continue

            live_data = LIVE_PRICES.get(instrument_key)
            if not live_data:
                results.append(
                    {
                        "symbol": symbol,
                        "instrument_key": instrument_key,
                        "status": "waiting_for_data",
                    }
                )
                continue

            ltp = live_data.get("ltp")
            timestamp = live_data.get("timestamp")
            if ltp is None:
                results.append(
                    {
                        "symbol": symbol,
                        "instrument_key": instrument_key,
                        "status": "invalid_live_payload",
                    }
                )
                continue

            results.append(
                {
                    "symbol": symbol,
                    "instrument_key": instrument_key,
                    "ltp": ltp,
                    "timestamp": timestamp,
                    "status": "live",
                }
            )

        live_results = [item for item in results if item.get("status") == "live"]
        waiting_results = [item for item in results if item.get("status") != "live"]
        live_results.sort(key=lambda item: item.get("ltp", 0), reverse=True)
        return live_results + waiting_results
