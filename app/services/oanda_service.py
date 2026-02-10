import oandapyV20
from typing import Any, Optional
from oandapyV20 import API
from oandapyV20.endpoints import instruments, orders, pricing, accounts
from app.core.config import settings

class OandaService:
    def __init__(self):
        self.client = API(access_token=settings.OANDA_API_KEY, 
                          environment=settings.OANDA_ENV)  # 'practice' or 'live'
        self.account_id = settings.OANDA_ACCOUNT_ID
    
    def get_live_price(self, instrument="EUR_USD"):
        """Get real-time forex price"""
        params = {"instruments": instrument}
        r = pricing.PricingInfo(accountID=self.account_id, params=params)
        response = self.client.request(r)
        return response['prices'][0]
    
    def get_historical_data(self, instrument="EUR_USD", granularity="M5", count=500):
        """Get candlestick data"""
        params = {
            "granularity": granularity,  # M1, M5, H1, D
            "count": count
        }
        r = instruments.InstrumentsCandles(instrument=instrument, params=params)
        response = self.client.request(r)
        return response['candles']
    
    def place_order(self, instrument, units, stop_loss=None, take_profit=None):
        """Place market order"""
        order_data = {
            "order": {
                "instrument": instrument,
                "units": units,  # Positive = buy, Negative = sell
                "type": "MARKET",
                "stopLossOnFill": {"price": stop_loss} if stop_loss else None,
                "takeProfitOnFill": {"price": take_profit} if take_profit else None,
            }
        }
        r = orders.OrderCreate(accountID=self.account_id, data=order_data)
        response = self.client.request(r)
        return response
    
    def get_account_summary(self):
        """Get account balance and info"""
        r = accounts.AccountSummary(accountID=self.account_id)
        return self.client.request(r)
