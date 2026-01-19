import requests
from app.data.news_keywords import BULLISH_KEYWORDS, BEARISH_KEYWORDS
from app.config.settings import NEWS_API_KEY

class NewsSentimentAgent:
    def __init__(self):
        self.news_url = "https://newsapi.org/v2/top-headlines"
        self.api_key = NEWS_API_KEY

    def fetch_news(self, symbol: str):
        params = {
            "q": f"{symbol} OR India stock market OR RBI OR NIFTY",
            "language": "en",
            "apiKey": self.api_key
        }
        response = requests.get(self.news_url, params=params)
        return response.json().get("articles", [])

    def analyze(self, symbol: str):
        articles = self.fetch_news(symbol)
        score = 0
        reasons = []

        for article in articles[:10]:
            title = article["title"].lower()
            weight = 1

            if "rbi" in title or "interest rate" in title:
                weight = 2

            if "war" in title or "crude" in title:
                weight = 3

            for word in BULLISH_KEYWORDS:
                if word in title:
                    score += weight
                    reasons.append(f"Bullish ({weight}): '{word}'")

            for word in BEARISH_KEYWORDS:
                if word in title:
                    score -= weight
                    reasons.append(f"Bearish ({weight}): '{word}'")

        sentiment = "Neutral"
        if score > 2:
            sentiment = "Bullish"
        elif score < -2:
            sentiment = "Bearish"

        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": round(min(abs(score) / 8, 1.0), 2),
            "reasons": reasons[:5]
        }
