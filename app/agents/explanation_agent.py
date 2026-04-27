from openai import OpenAI
from app.config.settings import OPENAI_API_KEY, MODEL_NAME

class ExplanationAgent:
    def _get_client(self):
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required to generate explanations.")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENAI_API_KEY
        )

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

        response = self._get_client().chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()
