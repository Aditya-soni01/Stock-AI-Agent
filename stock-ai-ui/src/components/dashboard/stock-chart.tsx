import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";

const indicators = ["EMA", "SMA", "RSI", "MACD", "VWAP"];

// Generate realistic candlestick data
const generateChartData = () => {
  const data = [];
  let basePrice = 2450;
  const times = [
    "9:15",
    "9:30",
    "9:45",
    "10:00",
    "10:15",
    "10:30",
    "10:45",
    "11:00",
    "11:15",
    "11:30",
    "11:45",
    "12:00",
    "12:15",
    "12:30",
    "12:45",
    "13:00",
    "13:15",
    "13:30",
    "13:45",
    "14:00",
    "14:15",
    "14:30",
    "14:45",
    "15:00",
    "15:15",
    "15:30",
  ];

  for (let i = 0; i < times.length; i++) {
    const volatility = Math.random() * 30 - 15;
    const open = basePrice;
    const close = basePrice + volatility + (Math.random() > 0.4 ? 5 : -3);
    const high = Math.max(open, close) + Math.random() * 10;
    const low = Math.min(open, close) - Math.random() * 10;
    const volume = Math.floor(Math.random() * 500000 + 100000);
    const ema = basePrice + Math.sin(i / 3) * 15;

    data.push({
      time: times[i],
      open,
      close,
      high,
      low,
      volume,
      ema,
      candleColor: close > open ? "bullish" : "bearish",
    });

    basePrice = close;
  }
  return data;
};

const chartData = generateChartData();

export function StockChart() {
  const [activeIndicators, setActiveIndicators] = useState<string[]>(["EMA"]);

  const toggleIndicator = (indicator: string) => {
    setActiveIndicators((prev) =>
      prev.includes(indicator)
        ? prev.filter((i) => i !== indicator)
        : [...prev, indicator],
    );
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-lg font-semibold text-foreground">
            RELIANCE
          </CardTitle>
          <div className="mt-1 flex items-center gap-3">
            <span className="text-2xl font-bold text-foreground">
              ₹2,456.80
            </span>
            <span className="rounded bg-bullish/20 px-2 py-0.5 text-sm font-medium text-bullish">
              +2.34%
            </span>
          </div>
        </div>
        <div className="flex gap-1">
          {indicators.map((indicator) => (
            <Button
              key={indicator}
              variant={
                activeIndicators.includes(indicator) ? "default" : "outline"
              }
              size="sm"
              onClick={() => toggleIndicator(indicator)}
              className={
                activeIndicators.includes(indicator)
                  ? "h-7 bg-ai-insight text-white hover:bg-ai-insight/90"
                  : "h-7 border-border text-muted-foreground hover:bg-secondary"
              }
            >
              {indicator}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={chartData}
              margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="hsl(var(--border))"
                opacity={0.5}
              />
              <XAxis
                dataKey="time"
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={{ stroke: "hsl(var(--border))" }}
                tickLine={{ stroke: "hsl(var(--border))" }}
              />
              <YAxis
                yAxisId="price"
                domain={["dataMin - 20", "dataMax + 20"]}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                axisLine={{ stroke: "hsl(var(--border))" }}
                tickLine={{ stroke: "hsl(var(--border))" }}
              />
              <YAxis
                yAxisId="volume"
                orientation="right"
                domain={[0, "dataMax"]}
                tick={false}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                  color: "hsl(var(--foreground))",
                }}
                labelStyle={{ color: "hsl(var(--muted-foreground))" }}
              />

              {/* Support and Resistance lines */}
              <ReferenceLine
                y={2480}
                stroke="hsl(var(--bearish))"
                strokeDasharray="5 5"
                label={{
                  value: "Resistance",
                  fill: "hsl(var(--bearish))",
                  fontSize: 10,
                }}
              />
              <ReferenceLine
                y={2420}
                stroke="hsl(var(--bullish))"
                strokeDasharray="5 5"
                label={{
                  value: "Support",
                  fill: "hsl(var(--bullish))",
                  fontSize: 10,
                }}
              />

              {/* Volume bars at bottom */}
              <Bar
                dataKey="volume"
                fill="hsl(var(--muted))"
                opacity={0.3}
                yAxisId="volume"
              />

              {/* Price line */}
              <Line
                type="monotone"
                dataKey="close"
                stroke="hsl(var(--ai-insight))"
                strokeWidth={2}
                dot={false}
                yAxisId="price"
              />

              {/* EMA line if active */}
              {activeIndicators.includes("EMA") && (
                <Line
                  type="monotone"
                  dataKey="ema"
                  stroke="hsl(var(--caution))"
                  strokeWidth={1.5}
                  strokeDasharray="5 5"
                  dot={false}
                  yAxisId="price"
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
