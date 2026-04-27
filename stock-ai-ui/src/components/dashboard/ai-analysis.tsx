import { Brain, Gauge, Signal, Target } from "lucide-react";

import { Progress } from "@/components/ui/progress";
import type { FeedStatusResponse, PaperReportResponse, RunnerStatusResponse } from "@/lib/api";

interface AIAnalysisProps {
  runnerStatus: RunnerStatusResponse | null;
  feedStatus: FeedStatusResponse | null;
  sessionReport: PaperReportResponse | null;
  isLoading: boolean;
}

function guardToRegime(reason: string | undefined): string {
  switch (reason) {
    case "ok":
      return "Active";
    case "market_hours_block":
      return "Market closed / outside configured market hours";
    case "cutoff_time_block":
      return "Entry cutoff reached";
    case "cooldown_after_loss_block":
      return "Cooldown active";
    case "max_daily_loss_block":
      return "Daily loss limit reached";
    case "max_trades_per_day_block":
      return "Daily trade limit reached";
    default:
      return "Waiting for guard status";
  }
}

function inferConfidence(runnerStatus: RunnerStatusResponse | null): number {
  const cycle = runnerStatus?.runner.last_cycle_result;
  if (!cycle || typeof cycle !== "object" || !("entry_result" in cycle)) return 0;
  const confidenceValues =
    cycle.entry_result?.signals
      ?.map((signal) => (typeof signal.confidence === "number" ? signal.confidence : null))
      .filter((value): value is number => value !== null) ?? [];

  if (confidenceValues.length === 0) return 0;
  const average = confidenceValues.reduce((sum, value) => sum + value, 0) / confidenceValues.length;
  return Math.max(0, Math.min(100, Math.round(average * 100)));
}

export function AIAnalysis({ runnerStatus, feedStatus, sessionReport, isLoading }: AIAnalysisProps) {
  const confidence = inferConfidence(runnerStatus);
  const regime = guardToRegime(runnerStatus?.current_guard?.reason);
  const feedOn = feedStatus?.running ?? false;
  const runnerOn = runnerStatus?.runner.running ?? false;
  const hasLivePrice = feedStatus?.live_price.status === "live";
  const marketOpen = runnerStatus?.runner.config.market_open_ist ?? "--";
  const marketClose = runnerStatus?.runner.config.market_close_ist ?? "--";
  const nowIst = runnerStatus?.current_guard?.now_ist ?? "--";

  const verdict = isLoading
    ? "loading"
    : !runnerOn
      ? "Runner stopped"
      : !feedOn
        ? "Feed stopped"
        : !hasLivePrice
          ? "Waiting for live tick"
          : "Active";

  return (
    <section className="glass-card glass-card-hover p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#0d1a0d]">
            <Brain className="h-4 w-4 text-[#00ff88]" />
          </div>
          <h3 className="text-2xl font-medium text-white">Neural Sentinel v4</h3>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-[#8fa98f]">
              <Gauge className="h-4 w-4" />
              Prediction Confidence
            </span>
            <span className="font-semibold text-[#00ff88]">{isLoading ? "--" : `${confidence}%`}</span>
          </div>
          <Progress value={confidence} className="h-1.5 bg-[#173117] [&>[data-slot=progress-indicator]]:bg-[#00ff88]" />
        </div>

        <div className="rounded-xl border border-[#1a2e1a] bg-[#0a140a] p-3">
          <p className="text-xs uppercase tracking-[0.14em] text-[#8fa98f]">Market Regime</p>
          <p className="mt-1 text-sm font-semibold text-[#00ff88]">{isLoading ? "loading" : regime}</p>
          <p className="mt-2 text-xs text-[#8fa98f]">
            Feed: {feedOn ? "running" : "stopped"} | Runner: {runnerOn ? "running" : "stopped"} | Price:{" "}
            {hasLivePrice ? "live" : "waiting for live tick"}
          </p>
          <p className="mt-1 text-xs text-[#8fa98f]">
            Window: {marketOpen}-{marketClose} IST | Now: {nowIst}
          </p>
        </div>

        <div className="flex items-center justify-between rounded-xl border border-[#1a2e1a] bg-[#0a0f0a] px-3 py-2">
          <span className="flex items-center gap-2 text-sm text-[#8fa98f]">
            <Signal className="h-4 w-4" />
            Bot Verdict
          </span>
          <span className="text-sm font-semibold text-white">{verdict}</span>
        </div>

        <div className="flex items-center justify-between rounded-xl border border-[#1a2e1a] bg-[#0a0f0a] px-3 py-2">
          <span className="flex items-center gap-2 text-sm text-[#8fa98f]">
            <Target className="h-4 w-4" />
            Session PnL
          </span>
          <span className="text-sm font-semibold text-white">
            {isLoading ? "loading..." : `INR ${(sessionReport?.total_pnl ?? 0).toFixed(2)}`}
          </span>
        </div>
      </div>
    </section>
  );
}
