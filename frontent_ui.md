# NIFTY50 AI BOT Dashboard

## 🎯 Goal
Build a real-time AI trading dashboard using existing backend APIs.
UI should match Stitch design.

## 🎨 Design Reference
- Stitch URL: <your link>
- HTML reference: see attached UI

## ⚙️ Tech Stack
- React (Vite)
- Tailwind CSS
- Axios / fetch

## 📡 APIs

### Market Data
- GET /upstox/live/NIFTY50
- GET /upstox/feed/status

### Bot Control
- POST /market/india/paper/runner/start
- POST /market/india/paper/runner/stop
- GET /market/india/paper/runner/status

### Reports
- GET /market/india/paper/report/daily
- GET /market/india/paper/report/session

### Trades
- GET /market/india/paper/trades

---

## 🧩 UI Sections Mapping

### Top Bar
- NIFTY Price → /upstox/live/NIFTY50
- Feed status → /upstox/feed/status
- Bot status → /runner/status

### Bot Status Card
- strategy → runner/status
- confidence → runner/status
- regime → derived

### Portfolio
- report/daily

### Chart
- placeholder for now

### Live Execution
- current trade from trades

### Trade Log
- /paper/trades

---

## 🔁 Polling
- Poll every 5 seconds
- Use interval or React Query

---

## 🚨 Rules
- NO fake data
- NO hardcoded trades
- show loading if no data
- do NOT touch backend

---

## ▶️ Actions

### Start Bot
1. POST /upstox/feed/start
2. POST /market/india/paper/runner/start

### Stop Bot
1. POST /market/india/paper/runner/stop

---

## 🧱 Components

- DashboardPage
- TopBar
- BotStatusCard
- PortfolioCard
- ChartSection
- LiveExecutionCard
- StrategyCard
- TradeLogTable

---

## 🧪 Testing

- Verify API integration
- Verify start/stop works
- Verify no fake UI data
- Verify loading states