from openai import OpenAI
from app.config.settings import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENAI_API_KEY
)

class ExplanationAgent:
    def explain(self, symbol, price, indicators, decision):
        prompt = f"""
You are a stock market mentor.

Explain this analysis clearly and briefly.

Stock: {symbol}
Price: {price}

Indicators:
- RSI: {indicators['rsi']}
- 20-day SMA: {indicators['sma_20']}

Decision: {decision['action']}

Rules:
- If no trades happened historically, explain why
- If user already holds the stock, mention caution
- Avoid repeating generic explanations
- Focus on THIS situation only

Explain:
1. What the indicators say NOW
2. Why the decision makes sense NOW
3. What would change the decision
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()
