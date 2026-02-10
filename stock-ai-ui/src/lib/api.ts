const API_BASE = "http://127.0.0.1:8000";

/** Upstox login: redirect to backend; backend redirects to Upstox. React never sees API key/secret. */
export function getUpstoxLoginUrl(): string {
  return `${API_BASE}/upstox/login`;
}

/** Redirect user to backend Upstox login (backend then redirects to Upstox). */
export function loginWithUpstox(): void {
  window.location.href = getUpstoxLoginUrl();
}

export async function analyzeStock(symbol: string) {
  const res = await fetch(`${API_BASE}/analyze/${symbol}`);

  if (!res.ok) {
    throw new Error("Failed to analyze stock");
  }

  return res.json();
}

export async function getTopMovers(){
  const res = await fetch(`${API_BASE}/upstox/top-movers`)
  if (!res.ok) {
    throw new Error("Failed to fetch top movers");
  }
  return res.json();
}

export interface StockBotResponse {
  question: string;
  understood_intent: string;
  answer: {
    summary: string;
    reasoning: string[];
    market_bias: string;
    what_to_watch: string[];
    confidence_level: string;
    risk_note: string;
  };
}

export async function askStockBot(question: string): Promise<StockBotResponse> {
  const res = await fetch(`${API_BASE}/api/stock/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error("Unable to fetch analysis. Please try again.");
  }

  return res.json();
}
