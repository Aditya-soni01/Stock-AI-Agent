import { Search, ChevronDown, Circle, User, Link2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useState } from "react";
import { loginWithUpstox } from "@/lib/api";

const timeframes = ["1m", "5m", "15m", "1h", "Daily"];

export function Header() {
  const [selectedTimeframe, setSelectedTimeframe] = useState("15m");
  const [marketOpen] = useState(true);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/95 px-6 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      {/* Search */}
      <div className="relative w-80">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search symbol or company..."
          className="h-9 bg-input pl-9 text-sm placeholder:text-muted-foreground"
        />
      </div>

      <div className="flex items-center gap-4">
        {/* Timeframe selector */}
        <div className="flex items-center gap-1 rounded-lg bg-secondary p-1">
          {timeframes.map((tf) => (
            <button
              type="button"
              key={tf}
              onClick={() => setSelectedTimeframe(tf)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                selectedTimeframe === tf
                  ? "bg-ai-insight text-white"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>

        {/* Market status */}
        <div className="flex items-center gap-2 rounded-lg bg-secondary px-3 py-1.5">
          <Circle
            className={`h-2 w-2 ${marketOpen ? "fill-bullish text-bullish" : "fill-bearish text-bearish"}`}
          />
          <span className="text-xs font-medium text-foreground">
            Market {marketOpen ? "Open" : "Closed"}
          </span>
        </div>

        {/* Profile dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2 px-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                <User className="h-4 w-4 text-muted-foreground" />
              </div>
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onClick={loginWithUpstox} className="cursor-pointer">
              <Link2 className="mr-2 h-4 w-4" />
              Connect Upstox
            </DropdownMenuItem>
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Preferences</DropdownMenuItem>
            <DropdownMenuItem>Sign out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
