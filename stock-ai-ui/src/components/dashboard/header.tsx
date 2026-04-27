import { Bell, ChevronDown, Circle, Link2, RefreshCw, Search, Settings, Signal, User } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { loginWithUpstox, type FeedStatusResponse, type LivePriceResponse, type RunnerStatusResponse } from "@/lib/api";

const timeframes = ["1m", "5m", "15m", "1h", "Daily"];

interface HeaderProps {
  livePrice: LivePriceResponse | null;
  feedStatus: FeedStatusResponse | null;
  runnerStatus: RunnerStatusResponse | null;
  isRefreshing: boolean;
}

function formatPrice(livePrice: LivePriceResponse | null, feedStatus: FeedStatusResponse | null): string {
  if (livePrice?.status === "live" && typeof livePrice.ltp === "number") {
    return `INR ${livePrice.ltp.toFixed(2)}`;
  }
  if (!feedStatus) return "Loading...";
  if (!feedStatus.token.ready) return "Connect Upstox";
  if (!feedStatus.running) return "Feed stopped";
  return "Waiting for live tick";
}

export function Header({ livePrice, feedStatus, runnerStatus, isRefreshing }: HeaderProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState("1m");

  const topBar = useMemo(() => {
    const marketOpen = runnerStatus?.current_guard?.allow_new_entries ?? false;
    const feedRunning = feedStatus?.running ?? false;
    const runnerRunning = runnerStatus?.runner.running ?? false;
    return { marketOpen, feedRunning, runnerRunning };
  }, [feedStatus, runnerStatus]);

  return (
    <header className="sticky top-0 z-30 border-b border-[#1a2e1a] bg-black/85 px-4 py-4 backdrop-blur-xl md:px-6">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          <div className="relative w-full lg:w-80">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#8fa98f]" />
            <Input
              placeholder="Search markets..."
              className="h-10 rounded-xl border-[#1a2e1a] bg-[#0a0f0a] pl-10 text-sm text-white placeholder:text-[#6d856e] focus-visible:border-[#00ff88] focus-visible:ring-0"
            />
          </div>

          <div className="flex items-center gap-3">
            {timeframes.map((tf) => (
              <button
                type="button"
                key={tf}
                onClick={() => setSelectedTimeframe(tf)}
                className={`pb-1 text-base font-semibold tracking-tight transition-colors ${
                  selectedTimeframe === tf
                    ? "border-b-2 border-[#00ff88] text-[#00ff88]"
                    : "text-[#8fa98f] hover:text-[#00ff88]"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="terminal-pill border-[#1a2e1a] bg-[#0d1a0d] text-[#00ff88]">
            <span className="mr-2 inline-block h-2 w-2 rounded-full bg-[#00ff88]" />
            Market {topBar.marketOpen ? "Open" : "Blocked"}
          </div>

          <div className="rounded-full border border-[#1a2e1a] bg-[#0a0f0a] px-3 py-1 text-xs text-[#8fa98f]">
            NIFTY: <span className="font-semibold text-white">{formatPrice(livePrice, feedStatus)}</span>
          </div>

          <div className="rounded-full border border-[#1a2e1a] bg-[#0a0f0a] px-3 py-1 text-xs text-[#8fa98f]">
            Feed: <span className="text-white">{topBar.feedRunning ? "running" : "stopped"}</span> | Runner:{" "}
            <span className="text-white">{topBar.runnerRunning ? "running" : "stopped"}</span>
            {isRefreshing && <RefreshCw className="ml-2 inline h-3.5 w-3.5 animate-spin text-[#00ff88]" />}
          </div>

          <div className="flex items-center gap-2 text-[#8fa98f]">
            <Signal className="h-4 w-4 cursor-pointer transition-colors hover:text-[#00ff88]" />
            <Bell className="h-4 w-4 cursor-pointer transition-colors hover:text-[#00ff88]" />
            <Settings className="h-4 w-4 cursor-pointer transition-colors hover:text-[#00ff88]" />
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-9 rounded-full border border-[#1a2e1a] bg-[#0a0f0a] px-2 hover:bg-[#0d1a0d]">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[#152215]">
                  <User className="h-3.5 w-3.5 text-[#8fa98f]" />
                </div>
                <ChevronDown className="h-3.5 w-3.5 text-[#8fa98f]" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 border-[#1a2e1a] bg-[#0a0f0a] text-[#dae6d8]">
              <DropdownMenuItem onClick={loginWithUpstox} className="cursor-pointer focus:bg-[#112112] focus:text-[#00ff88]">
                <Link2 className="mr-2 h-4 w-4" />
                Connect Upstox
              </DropdownMenuItem>
              <DropdownMenuItem className="focus:bg-[#112112] focus:text-[#00ff88]">
                <Circle className="mr-2 h-4 w-4" />
                Profile
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
