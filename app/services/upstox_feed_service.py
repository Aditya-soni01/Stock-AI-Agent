import requests
from app.services.upstox_auth_service import load_token


def get_market_feed_url():
    token = load_token()
    if not token:
        raise Exception("Upstox not authenticated")

    res = requests.get(
        "https://api.upstox.com/v2/feed/market-data-feed/authorize",
        headers={"Authorization": f"Bearer {token['access_token']}"}
    )
    res.raise_for_status()

    return res.json()["data"]["authorized_redirect_uri"]
