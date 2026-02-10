# app/agents/forex_market_agent.py

from app.services.oanda_service import OandaService
import time

def start_market_feed():
    """Poll forex prices every few seconds"""
    try:
        oanda = OandaService()
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]  # Currency pairs
        
        print("✅ Forex market feed started")
        
        while True:
            for instrument in instruments:
                try:
                    price_data = oanda.get_live_price(instrument)
                    print(f"{instrument}: Bid={price_data['bids'][0]['price']}, Ask={price_data['asks'][0]['price']}")
                    
                    # Store in your database or state management
                    # update_price_in_db(instrument, price_data)
                    
                except Exception as e:
                    print(f"Error fetching {instrument}: {e}")
            
            time.sleep(5)  # Update every 5 seconds
            
    except Exception as e:
        print(f"❌ Market feed error: {e}")
        return
