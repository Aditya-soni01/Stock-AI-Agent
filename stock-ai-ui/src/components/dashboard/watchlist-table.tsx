import { Eye } from "lucide-react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { PaperTrade, PaperTradesResponse } from "@/lib/api";

interface WatchlistTableProps {
  trades: PaperTradesResponse | null;
  isLoading: boolean;
}

function formatInr(value: number | null | undefined): string {
  if (typeof value !== "number") return "--";
  return `INR ${value.toFixed(2)}`;
}

function formatWhen(value: string | null | undefined): string {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function sortTrades(trades: PaperTrade[]): PaperTrade[] {
  return [...trades].sort((a, b) => {
    const ta = new Date(a.entry_time ?? 0).getTime();
    const tb = new Date(b.entry_time ?? 0).getTime();
    return tb - ta;
  });
}

export function WatchlistTable({ trades, isLoading }: WatchlistTableProps) {
  const rows = sortTrades(trades?.trades ?? []);

  return (
    <section className="glass-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-[#1a2e1a] px-5 py-4">
        <h3 className="flex items-center gap-2 text-2xl font-medium text-white">
          <Eye className="h-4 w-4 text-[#00ff88]" />
          Live Trade Log
        </h3>
        <span className="text-xs text-[#8fa98f]">Updated from API polling</span>
      </div>

      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-[#1a2e1a] bg-[#050a05] hover:bg-[#050a05]">
              <TableHead className="text-xs font-semibold uppercase tracking-[0.1em] text-[#8fa98f]">Instrument</TableHead>
              <TableHead className="text-xs font-semibold uppercase tracking-[0.1em] text-[#8fa98f]">Type</TableHead>
              <TableHead className="text-right text-xs font-semibold uppercase tracking-[0.1em] text-[#8fa98f]">Entry</TableHead>
              <TableHead className="text-right text-xs font-semibold uppercase tracking-[0.1em] text-[#8fa98f]">Current/Exit</TableHead>
              <TableHead className="text-right text-xs font-semibold uppercase tracking-[0.1em] text-[#8fa98f]">PnL</TableHead>
              <TableHead className="text-right text-xs font-semibold uppercase tracking-[0.1em] text-[#8fa98f]">Updated</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              <TableRow className="border-[#1a2e1a]">
                <TableCell colSpan={6} className="text-[#8fa98f]">
                  Loading trade log...
                </TableCell>
              </TableRow>
            )}

            {!isLoading && rows.length === 0 && (
              <TableRow className="border-[#1a2e1a]">
                <TableCell colSpan={6} className="text-[#8fa98f]">
                  No paper trades yet.
                </TableCell>
              </TableRow>
            )}

            {!isLoading &&
              rows.map((trade) => {
                const pnl = trade.pnl ?? 0;
                const directionHint = `${trade.reason ?? ""} ${trade.strategy_name ?? ""}`.toLowerCase();
                const type = directionHint.includes("short") || directionHint.includes("sell")
                  ? "SHORT"
                  : directionHint.includes("long") || directionHint.includes("buy")
                    ? "LONG"
                    : "--";
                return (
                  <TableRow key={trade.trade_id ?? `${trade.symbol}-${trade.entry_time}`} className="border-[#1a2e1a] hover:bg-[#0b150b]">
                    <TableCell className="font-medium text-white">{trade.symbol ?? "--"}</TableCell>
                    <TableCell>
                      <span
                        className={`rounded-md border px-2 py-1 text-[10px] font-semibold ${
                          type === "SHORT"
                            ? "border-[#ff5f5f] bg-[#ff5f5f]/10 text-[#ff9f9f]"
                            : type === "LONG"
                              ? "border-[#00ff88] bg-[#00ff88]/10 text-[#8dffbf]"
                              : "border-[#1a2e1a] bg-[#0b120b] text-[#8fa98f]"
                        }`}
                      >
                        {type}
                      </span>
                    </TableCell>
                    <TableCell className="text-right text-white">{formatInr(trade.entry_price)}</TableCell>
                    <TableCell className="text-right text-white">{formatInr(trade.exit_price ?? trade.entry_price)}</TableCell>
                    <TableCell className={`text-right font-semibold ${pnl >= 0 ? "text-[#00ff88]" : "text-[#ff6f6f]"}`}>
                      {formatInr(trade.pnl)}
                    </TableCell>
                    <TableCell className="text-right text-[#8fa98f]">{formatWhen(trade.exit_time ?? trade.entry_time)}</TableCell>
                  </TableRow>
                );
              })}
          </TableBody>
        </Table>
      </div>
    </section>
  );
}
