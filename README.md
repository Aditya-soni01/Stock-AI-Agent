# stock-ai-agent

An AI-assisted trading agent that integrates with the **Upstox** broker API via OAuth2, with a FastAPI backend and a React frontend for monitoring positions, running market scans, and executing paper trades.

## Why this exists

A hands-on project demonstrating end-to-end broker API integration (Upstox OAuth2) combined with AI-assisted decision logic. It runs in paper-trading mode by default for safe experimentation with automated strategies.

## Features

- **Upstox OAuth2 integration** — full token exchange and refresh flow with a real
  brokerage API
- **FastAPI backend** — REST endpoints for stock/market analysis, forex, Upstox live auth,
  and paper trading, organized under `app/api/routes` with a background scheduler
- **React frontend** — a Vite-based dashboard (`stock-ai-ui/`) for viewing positions,
  market scans, and paper-trade activity
- **AI/LLM component** — OpenAI/OpenRouter-powered agents (default model `openai/gpt-oss-120b:free`) for stock Q&A, news sentiment, decision, explanation, and risk analysis
- **Multi-agent architecture** — dedicated agents for indicators, trends, backtesting, portfolio, and India market scanning

## Tech stack

Python · FastAPI · React (Vite) · Upstox API · OpenAI / OpenRouter · pandas · yfinance

## Getting started

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export UPSTOX_API_KEY="<your-key>"
export UPSTOX_API_SECRET="<your-secret>"
export UPSTOX_REDIRECT_URI="<your-redirect-uri>"

uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Demo

[Link to a live deployment if you have one, or a screenshot/GIF]

## Troubleshooting

### Upstox OAuth callback

You do NOT put any "code" in the callback URL. The callback `http://127.0.0.1:8000/upstox/callback` is only used when Upstox redirects the user after they approve your app — Upstox adds the `code` automatically (`?code=XXXXX`).

**Correct flow:**

1. In your app, click **Connect Upstox** (header dropdown).
2. You are sent to the backend `/upstox/login`, then to Upstox's login page.
3. Log in to Upstox and approve the app.
4. Upstox redirects the browser to `http://127.0.0.1:8000/upstox/callback?code=...` (code is added by Upstox).
5. The backend exchanges that code for an access token and redirects you back to the app.

Do not open the callback URL manually or paste a code into it. The code is single-use and short-lived (about 1–2 minutes).

**If you see "Invalid Auth code" (UDAPI100057):**

- The redirect URI must match exactly between your `.env` and the Upstox developer dashboard (same scheme, host, no trailing slash — e.g. `http://127.0.0.1:8000/upstox/callback`, not `http://localhost:8000/...`).
- Always start from **Connect Upstox**; don't reuse an old callback URL or refresh the callback page (the code is one-time use).
- Complete login and approval within a couple of minutes so the code doesn't expire.

## License

[MIT / your choice]
