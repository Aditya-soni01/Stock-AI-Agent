import { BarChart3, CheckCircle2 } from "lucide-react";

import type { FeedStatusResponse, LivePriceResponse } from "@/lib/api";

interface StockChartProps {
  livePrice: LivePriceResponse | null;
  feedStatus: FeedStatusResponse | null;
  isLoading: boolean;
}

function formatPrice(
  livePrice: LivePriceResponse | null,
  feedStatus: FeedStatusResponse | null,
  isLoading: boolean,
): string {
  if (isLoading) return "loading...";
  if (livePrice?.status === "live" && typeof livePrice.ltp === "number") {
    return `INR ${livePrice.ltp.toFixed(2)}`;
  }
  if (!feedStatus) return "Loading...";
  if (!feedStatus.token.ready) return "Connect Upstox";
  if (!feedStatus.running) return "Feed stopped";
  return "Waiting for live tick";
}

function statusLabel(livePrice: LivePriceResponse | null, feedStatus: FeedStatusResponse | null, isLoading: boolean): string {
  if (isLoading) return "loading";
  if (livePrice?.status === "live") return "Live";
  if (!feedStatus) return "Loading...";
  if (!feedStatus.token.ready) return "Connect Upstox";
  if (!feedStatus.running) return "Feed stopped";
  return "Waiting for live tick";
}

export function StockChart({ livePrice, feedStatus, isLoading }: StockChartProps) {
  const price = formatPrice(livePrice, feedStatus, isLoading);
  const status = statusLabel(livePrice, feedStatus, isLoading);

  return (
    <section className="glass-card p-5 md:p-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <h2 className="text-5xl font-semibold tracking-tight text-white">NIFTY50</h2>
            <CheckCircle2 className="h-4 w-4 text-[#00ff88]" />
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-4xl font-black text-white md:text-6xl">{price}</span>
            <span className="rounded-md border border-[#1a2e1a] bg-[#111d11] px-2 py-1 text-xs font-medium text-[#8fa98f]">
              {status}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <button type="button" className="rounded-lg border border-[#1a2e1a] bg-[#1a2e1a] px-3 py-1 text-sm text-white">
            Indicator
          </button>
          <button type="button" className="rounded-lg border border-[#1a2e1a] bg-[#1a2e1a] px-3 py-1 text-sm text-white">
            Compare
          </button>
        </div>
      </div>

      <div className="relative flex h-[440px] items-center justify-center overflow-hidden rounded-xl border border-[#1a2e1a] bg-[#050b05]">
        <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,#1a2e1a_1px,transparent_1px),linear-gradient(to_bottom,#1a2e1a_1px,transparent_1px)] bg-[size:16.6%_25%]" />
        <div className="relative z-10 rounded-xl border border-dashed border-[#294729] bg-[#0a150a]/70 px-5 py-4 text-center">
          <BarChart3 className="mx-auto mb-2 h-7 w-7 text-[#8fa98f]" />
          <p className="text-sm font-semibold text-white">Live Chart Wiring Pending</p>
          <p className="mt-1 text-xs text-[#8fa98f]">
            Price and status above are real API values. Chart candles are intentionally not fabricated.
          </p>
        </div>
      </div>
    </section>
  );
}
