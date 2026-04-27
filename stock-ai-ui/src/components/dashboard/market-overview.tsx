import { BarChart3, Briefcase, Gauge, ShieldCheck, TrendingUp } from "lucide-react";

import type { PaperReportResponse, PaperTradesResponse, RunnerStatusResponse } from "@/lib/api";

interface MarketOverviewProps {
  dailyReport: PaperReportResponse | null;
  sessionReport: PaperReportResponse | null;
  runnerStatus: RunnerStatusResponse | null;
  trades: PaperTradesResponse | null;
  actionError: string | null;
  isLoading: boolean;
}

interface MetricCard {
  label: string;
  value: string;
  note: string;
  positive: boolean;
  icon: typeof BarChart3;
}

function formatInr(value: number | undefined): string {
  if (typeof value !== "number") return "waiting";
  return `INR ${value.toFixed(2)}`;
}

function formatPercent(value: number | undefined): string {
  if (typeof value !== "number") return "waiting";
  return `${(value * 100).toFixed(1)}%`;
}

function guardReasonLabel(runnerStatus: RunnerStatusResponse | null): string {
  const reason = runnerStatus?.current_guard?.reason;
  const nowIst = runnerStatus?.current_guard?.now_ist ?? "--";
  const open = runnerStatus?.runner.config.market_open_ist ?? "--";
  const close = runnerStatus?.runner.config.market_close_ist ?? "--";

  if (reason === "market_hours_block") {
    return `Market closed / outside market hours (${open}-${close} IST). Now: ${nowIst}`;
  }
  if (reason === "cutoff_time_block") {
    return `Entry cutoff reached. Now: ${nowIst}`;
  }
  if (reason === "cooldown_after_loss_block") {
    return "Cooldown active after recent loss";
  }
  if (reason === "max_daily_loss_block") {
    return "Daily loss limit reached";
  }
  if (reason === "max_trades_per_day_block") {
    return "Daily trade limit reached";
  }
  if (reason === "ok") {
    return `Within market window (${open}-${close} IST)`;
  }
  return "Waiting for runner guard data";
}

export function MarketOverview({
  dailyReport,
  sessionReport,
  runnerStatus,
  trades,
  actionError,
  isLoading,
}: MarketOverviewProps) {
  const runnerOn = runnerStatus?.runner.running ?? false;
  const cards: MetricCard[] = [
    {
      label: "Daily PnL",
      value: isLoading ? "loading..." : formatInr(dailyReport?.total_pnl),
      note: dailyReport ? `${dailyReport.closed_trades} closed trades` : "Waiting for report",
      positive: (dailyReport?.total_pnl ?? 0) >= 0,
      icon: BarChart3,
    },
    {
      label: "Win Rate",
      value: isLoading ? "loading..." : formatPercent(dailyReport?.win_rate),
      note: dailyReport ? `${dailyReport.total_trades} total trades` : "Waiting for report",
      positive: (dailyReport?.win_rate ?? 0) >= 0.5,
      icon: Gauge,
    },
    {
      label: "Open Trades",
      value: isLoading ? "loading..." : String(sessionReport?.open_trades ?? 0),
      note: sessionReport?.market_data?.status === "live" ? "Live prices active" : "Price feed waiting",
      positive: (sessionReport?.open_trades ?? 0) > 0,
      icon: Briefcase,
    },
    {
      label: "Bot Guard",
      value: isLoading ? "loading..." : runnerStatus?.current_guard?.allow_new_entries ? "active" : "blocked",
      note: isLoading ? "Loading guard status" : guardReasonLabel(runnerStatus),
      positive: runnerStatus?.current_guard?.allow_new_entries ?? false,
      icon: ShieldCheck,
    },
    {
      label: "Session State",
      value: isLoading ? "loading..." : runnerOn ? "Runner running" : "Runner stopped",
      note: runnerOn
        ? trades
          ? `${trades.count} trades logged`
          : "Waiting for trades"
        : actionError ?? "Runner is currently stopped",
      positive: runnerOn,
      icon: TrendingUp,
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
      {cards.map((item) => (
        <article key={item.label} className="glass-card glass-card-hover p-4">
          <div className="mb-3 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8fa98f]">{item.label}</p>
            <item.icon className="h-4 w-4 text-[#6f8a71]" />
          </div>
          <p className={`text-3xl font-semibold leading-none ${item.positive ? "text-[#00ff88]" : "text-white"}`}>
            {item.value}
          </p>
          <p className={`mt-2 text-xs ${item.positive ? "text-[#00ff88]" : "text-[#8fa98f]"}`}>{item.note}</p>
        </article>
      ))}
    </div>
  );
}
