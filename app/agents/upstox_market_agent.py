import websocket
import json
from app.services.upstox_feed_service import get_market_feed_url
from app.utils.instrument_mapper import INSTRUMENTS
from app.proto.market_data_pb2 import FeedResponse
from app.state.market_state import LIVE_PRICES


def on_open(ws):
    payload = {
        "guid": "market-feed",
        "method": "sub",
        "data": {
            "mode": "ltp",
            "instrumentKeys": list(INSTRUMENTS.values())
        }
    }
    ws.send(json.dumps(payload))
    print("✅ Subscribed to Upstox Market Feed")


def on_message(ws, message):
    feed = FeedResponse()
    feed.ParseFromString(message)

    for instrument_key, data in feed.feeds.items():
        if data.HasField("ltp"):
            LIVE_PRICES[instrument_key] = {
                "ltp": data.ltp,
                "open": data.open if data.HasField("open") else data.ltp,
                "timestamp": data.ltt
            }
            print(f"{instrument_key} → {data.ltp}")


def start_market_feed():
    ws = websocket.WebSocketApp(
        get_market_feed_url(),
        on_open=on_open,
        on_message=on_message
    )
    ws.run_forever()
