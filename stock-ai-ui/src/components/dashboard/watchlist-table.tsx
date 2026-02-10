import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Eye, TrendingUp, TrendingDown, Minus } from "lucide-react";

const watchlistData = [
  {
    symbol: "RELIANCE",
    trend: "Bullish",
    signal: "BUY",
    confidence: 87,
    timeframe: "15m",
    lastUpdated: "2 min ago",
  },
  {
    symbol: "TCS",
    trend: "Bearish",
    signal: "SELL",
    confidence: 72,
    timeframe: "1h",
    lastUpdated: "5 min ago",
  },
  {
    symbol: "HDFC BANK",
    trend: "Range",
    signal: "WAIT",
    confidence: 65,
    timeframe: "15m",
    lastUpdated: "1 min ago",
  },
  {
    symbol: "INFY",
    trend: "Bullish",
    signal: "BUY",
    confidence: 81,
    timeframe: "Daily",
    lastUpdated: "10 min ago",
  },
  {
    symbol: "ICICI BANK",
    trend: "Bullish",
    signal: "BUY",
    confidence: 79,
    timeframe: "15m",
    lastUpdated: "3 min ago",
  },
  {
    symbol: "BHARTI AIRTEL",
    trend: "Bearish",
    signal: "SELL",
    confidence: 68,
    timeframe: "1h",
    lastUpdated: "7 min ago",
  },
];

const getTrendIcon = (trend: string) => {
  switch (trend) {
    case "Bullish":
      return <TrendingUp className="h-4 w-4 text-bullish" />;
    case "Bearish":
      return <TrendingDown className="h-4 w-4 text-bearish" />;
    default:
      return <Minus className="h-4 w-4 text-caution" />;
  }
};

const getSignalBadge = (signal: string) => {
  switch (signal) {
    case "BUY":
      return (
        <Badge className="bg-bullish/20 text-bullish hover:bg-bullish/30 font-semibold">
          BUY
        </Badge>
      );
    case "SELL":
      return (
        <Badge className="bg-bearish/20 text-bearish hover:bg-bearish/30 font-semibold">
          SELL
        </Badge>
      );
    default:
      return (
        <Badge className="bg-caution/20 text-caution hover:bg-caution/30 font-semibold">
          WAIT
        </Badge>
      );
  }
};

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 80) return "text-bullish";
  if (confidence >= 70) return "text-caution";
  return "text-muted-foreground";
};

export function WatchlistTable() {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <Eye className="h-5 w-5 text-ai-insight" />
          Watchlist & Signals
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-lg border border-border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="text-muted-foreground text-xs font-medium">
                  Symbol
                </TableHead>
                <TableHead className="text-muted-foreground text-xs font-medium">
                  Trend
                </TableHead>
                <TableHead className="text-muted-foreground text-xs font-medium">
                  Signal
                </TableHead>
                <TableHead className="text-muted-foreground text-xs font-medium">
                  Confidence
                </TableHead>
                <TableHead className="text-muted-foreground text-xs font-medium">
                  Timeframe
                </TableHead>
                <TableHead className="text-muted-foreground text-xs font-medium text-right">
                  Updated
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {watchlistData.map((item) => (
                <TableRow
                  key={item.symbol}
                  className="border-border cursor-pointer transition-colors hover:bg-secondary/50"
                >
                  <TableCell className="font-medium text-foreground">
                    {item.symbol}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1.5">
                      {getTrendIcon(item.trend)}
                      <span className="text-sm text-muted-foreground">
                        {item.trend}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>{getSignalBadge(item.signal)}</TableCell>
                  <TableCell>
                    <span
                      className={`font-medium ${getConfidenceColor(item.confidence)}`}
                    >
                      {item.confidence}%
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className="border-border text-muted-foreground font-normal"
                    >
                      {item.timeframe}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-right text-sm">
                    {item.lastUpdated}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
