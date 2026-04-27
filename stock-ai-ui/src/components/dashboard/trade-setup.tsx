import { Activity, Play, Square, Wifi } from "lucide-react";

import { Button } from "@/components/ui/button";
import { loginWithUpstox, type FeedStatusResponse, type RunnerStatusResponse } from "@/lib/api";

interface TradeSetupProps {
  feedStatus: FeedStatusResponse | null;
  runnerStatus: RunnerStatusResponse | null;
  onStartBot: () => Promise<void>;
  onStopBot: () => Promise<void>;
  isStarting: boolean;
  isStopping: boolean;
  actionError: string | null;
  actionMessage: string | null;
}

export function TradeSetup({
  feedStatus,
  runnerStatus,
  onStartBot,
  onStopBot,
  isStarting,
  isStopping,
  actionError,
  actionMessage,
}: TradeSetupProps) {
  const runnerRunning = runnerStatus?.runner.running ?? false;
  const feedRunning = feedStatus?.running ?? false;
  const tokenReady = feedStatus?.token.ready ?? false;
  const waitingForLiveData = feedStatus?.live_price.status !== "live";

  const feedLabel = !feedStatus
    ? "Loading..."
    : !tokenReady
      ? "Connect Upstox"
      : !feedRunning
        ? "Feed stopped"
        : waitingForLiveData
          ? "Waiting for live tick"
          : "Live";

  const runnerLabel = runnerRunning ? "Runner running" : "Runner stopped";
  const priceLabel = waitingForLiveData ? "Waiting for live tick" : "Live";

  return (
    <section className="glass-card glass-card-hover p-5">
      <h3 className="mb-4 flex items-center gap-2 text-2xl font-medium text-white">
        <Activity className="h-4 w-4 text-[#00ff88]" />
        Bot Control
      </h3>

      <div className="rounded-xl border border-[#1a2e1a] bg-[#040904] p-4 text-sm">
        <p className="text-[#00ff88]">
          Feed: <span className="text-[#8fa98f]">{feedLabel}</span> | Runner:{" "}
          <span className="text-[#8fa98f]">{runnerLabel}</span> | Price:{" "}
          <span className="text-[#8fa98f]">{priceLabel}</span>
        </p>
      </div>

      {!tokenReady && (
        <button
          type="button"
          onClick={loginWithUpstox}
          className="mt-3 rounded-xl border border-[#1a2e1a] bg-[#0b150b] px-3 py-2 text-xs font-semibold uppercase tracking-[0.1em] text-[#00ff88] transition-colors hover:border-[#00ff88]"
        >
          Connect Upstox
        </button>
      )}

      <div className="mt-4 grid grid-cols-2 gap-3">
        <Button
          className="h-12 rounded-2xl bg-[#00ff88] text-base font-bold uppercase tracking-[0.08em] text-black hover:bg-[#00e97c]"
          onClick={() => {
            void onStartBot();
          }}
          disabled={isStarting || isStopping}
        >
          <Play className="mr-1 h-4 w-4" />
          {isStarting ? "Starting" : "Start"}
        </Button>

        <Button
          variant="outline"
          className="h-12 rounded-2xl border-[#1a2e1a] bg-transparent text-base font-bold uppercase tracking-[0.08em] text-white hover:border-[#00ff88] hover:bg-[#0d1a0d]"
          onClick={() => {
            void onStopBot();
          }}
          disabled={isStopping || isStarting}
        >
          <Square className="mr-1 h-4 w-4" />
          {isStopping ? "Stopping" : "Stop"}
        </Button>
      </div>

      {actionMessage && (
        <div className="mt-3 rounded-xl border border-[#00ff88]/40 bg-[#00ff88]/10 p-3 text-xs text-[#7dffbd]">{actionMessage}</div>
      )}
      {actionError && (
        <div className="mt-3 rounded-xl border border-[#ff5f5f]/40 bg-[#ff5f5f]/10 p-3 text-xs text-[#ffabab]">{actionError}</div>
      )}

      <p className="mt-4 flex items-center gap-2 text-xs text-[#8fa98f]">
        <Wifi className="h-4 w-4" />
        Polling every 5 seconds
      </p>
    </section>
  );
}
