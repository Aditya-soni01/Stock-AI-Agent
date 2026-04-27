const API_BASE = "http://127.0.0.1:8000";

export interface LivePriceResponse {
  symbol: string;
  instrument_key: string;
  status: "waiting_for_data" | "live";
  ltp?: number | null;
  timestamp?: string | null;
}

export interface FeedTokenStatus {
  token_file: string;
  exists: boolean;
  ready: boolean;
  expired: boolean | null;
  reason: string;
  created_at: number | null;
  expires_in: number | null;
  expires_at: number | null;
  has_access_token: boolean;
  has_refresh_token: boolean;
}

export interface FeedStatusResponse {
  running: boolean;
  started_at: string | null;
  stopped_at: string | null;
  last_message_at: string | null;
  last_update_at: string | null;
  last_error: string | null;
  last_warning: string | null;
  instrument_key: string;
  token_file: string;
  live_price: {
    instrument_key: string;
    status: "waiting_for_data" | "live";
    ltp: number | null;
    timestamp: string | null;
  };
  token: FeedTokenStatus;
}

export interface RunnerGuard {
  allow_new_entries: boolean;
  reason: string;
  now_ist?: string;
  day_iso?: string;
}

export interface RunnerCycleSignal {
  action?: string;
  confidence?: number;
  strategy_name?: string | null;
  reason?: string;
}

export interface RunnerCycle {
  run_at?: string;
  allow_new_entries?: boolean;
  entry_result?: {
    signals_count?: number;
    buy_signals?: number;
    signals?: RunnerCycleSignal[];
  } | null;
  update_result?: {
    open_trades_checked?: number;
    closed_count?: number;
    skipped_count?: number;
  } | null;
}

export interface RunnerStatusResponse {
  execution_mode: string;
  runner: {
    running: boolean;
    started_at: string | null;
    stopped_at: string | null;
    last_cycle_at: string | null;
    last_cycle_result: RunnerCycle | { error?: string } | null;
    last_guard: RunnerGuard | null;
    config: {
      interval_seconds: number;
      max_trades_per_day: number;
      max_daily_loss: number;
      cooldown_after_loss_minutes: number;
      cutoff_time_ist: string;
      market_open_ist: string;
      market_close_ist: string;
    };
  };
  current_guard: RunnerGuard;
  market_data?: {
    symbol: string;
    instrument_key: string;
    status: "waiting_for_data" | "live";
    ltp?: number | null;
    timestamp?: string | null;
    message?: string;
  };
}

export interface PaperReportResponse {
  execution_mode: string;
  report: string;
  total_trades: number;
  open_trades: number;
  closed_trades: number;
  win_rate: number;
  total_pnl: number;
  max_drawdown_proxy: number;
  best_strategy: { name: string; pnl: number; trades: number } | null;
  worst_strategy: { name: string; pnl: number; trades: number } | null;
  latest_guard_reason: string | null;
  market_data?: {
    symbol: string;
    instrument_key: string;
    status: "waiting_for_data" | "live";
    ltp?: number | null;
    timestamp?: string | null;
    message?: string;
  };
}

export interface PaperTrade {
  trade_id?: string;
  symbol?: string;
  strategy_name?: string;
  status?: string;
  entry_time?: string;
  exit_time?: string | null;
  entry_price?: number | null;
  exit_price?: number | null;
  pnl?: number | null;
  qty?: number | null;
  reason?: string;
}

export interface PaperTradesResponse {
  execution_mode: string;
  trades: PaperTrade[];
  count: number;
}

interface FeedActionResponse {
  message: string;
  feed: FeedStatusResponse;
}

interface RunnerActionResponse {
  message: string;
  runner: RunnerStatusResponse["runner"];
}

function safeString(value: unknown): string | null {
  if (typeof value === "string" && value.trim().length > 0) return value.trim();
  return null;
}

function tokenProblemHint(tokenStatus: unknown): string | null {
  if (!tokenStatus || typeof tokenStatus !== "object") return null;
  const status = tokenStatus as {
    ready?: boolean;
    reason?: unknown;
    exists?: boolean;
    has_access_token?: boolean;
  };

  if (status.ready === true) return null;
  const reason = safeString(status.reason)?.toLowerCase() ?? "";

  if (status.exists === false || status.has_access_token === false || reason.includes("missing")) {
    return "Token missing. Please connect Upstox first.";
  }
  if (reason.includes("expired") || reason.includes("expiry")) {
    return "Token expired or invalid. Please reconnect Upstox.";
  }
  return "Upstox token is not ready. Please connect Upstox first.";
}

function extractErrorMessage(parsed: unknown, statusCode: number): string {
  if (typeof parsed === "string" && parsed.trim().length > 0) {
    return parsed;
  }

  if (parsed && typeof parsed === "object" && "detail" in parsed) {
    const detail = (parsed as { detail: unknown }).detail;
    if (typeof detail === "string" && detail.trim().length > 0) {
      return detail;
    }
    if (detail && typeof detail === "object") {
      const detailObj = detail as {
        message?: unknown;
        error?: unknown;
        next_step?: unknown;
        token_status?: unknown;
      };

      const parts: string[] = [];
      const message = safeString(detailObj.message);
      const error = safeString(detailObj.error);
      const nextStep = safeString(detailObj.next_step);
      const tokenHint = tokenProblemHint(detailObj.token_status);

      if (tokenHint) {
        parts.push(tokenHint);
      }
      if (message) {
        parts.push(message);
      }
      if (error && error !== message) {
        parts.push(error);
      }
      if (nextStep) {
        parts.push(nextStep);
      }

      if (parts.length > 0) {
        return parts.join(" ");
      }
    }
  }

  return `Request failed (${statusCode})`;
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === "string" && error.trim().length > 0) return error;
  return "Unexpected error";
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const raw = await response.text();
  let parsed: unknown = null;
  if (raw) {
    try {
      parsed = JSON.parse(raw) as unknown;
    } catch {
      parsed = raw;
    }
  }

  if (!response.ok) {
    const errorMessage = extractErrorMessage(parsed, response.status);
    throw new Error(errorMessage);
  }

  return parsed as T;
}

/** Upstox login: redirect to backend; backend redirects to Upstox. React never sees API key/secret. */
export function getUpstoxLoginUrl(): string {
  return `${API_BASE}/upstox/login?redirect=true`;
}

/** Redirect user to backend Upstox login (backend then redirects to Upstox). */
export function loginWithUpstox(): void {
  window.location.href = getUpstoxLoginUrl();
}

export async function analyzeStock(symbol: string) {
  return requestJson(`/analyze/${symbol}`);
}

export async function getTopMovers() {
  return requestJson("/market/india/top-movers");
}

export async function getNiftyLivePrice(): Promise<LivePriceResponse> {
  return requestJson("/upstox/live/NIFTY50");
}

export async function getFeedStatus(): Promise<FeedStatusResponse> {
  return requestJson("/upstox/feed/status");
}

export async function startUpstoxFeed(): Promise<FeedActionResponse> {
  return requestJson("/upstox/feed/start", { method: "POST" });
}

export async function stopUpstoxFeed(): Promise<FeedActionResponse> {
  return requestJson("/upstox/feed/stop", { method: "POST" });
}

export async function getRunnerStatus(): Promise<RunnerStatusResponse> {
  return requestJson("/market/india/paper/runner/status");
}

export async function startPaperRunner(): Promise<RunnerActionResponse> {
  return requestJson("/market/india/paper/runner/start", { method: "POST" });
}

export async function stopPaperRunner(): Promise<RunnerActionResponse> {
  return requestJson("/market/india/paper/runner/stop", { method: "POST" });
}

export async function getDailyReport(): Promise<PaperReportResponse> {
  return requestJson("/market/india/paper/report/daily");
}

export async function getSessionReport(): Promise<PaperReportResponse> {
  return requestJson("/market/india/paper/report/session");
}

export async function getPaperTrades(): Promise<PaperTradesResponse> {
  return requestJson("/market/india/paper/trades");
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
  return requestJson("/api/stock/ask", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}
