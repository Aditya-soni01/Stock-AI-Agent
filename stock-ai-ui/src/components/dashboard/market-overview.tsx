import { Card, CardContent } from "@/components/ui/card";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Brain,
  BarChart3,
} from "lucide-react";

const marketData = [
  {
    label: "NIFTY 50",
    value: "22,456.80",
    change: "+1.24%",
    trend: "up",
    icon: BarChart3,
  },
  {
    label: "SENSEX",
    value: "73,852.94",
    change: "+0.98%",
    trend: "up",
    icon: BarChart3,
  },
  {
    label: "Market Sentiment",
    value: "Bullish",
    change: "Strong momentum",
    trend: "up",
    icon: TrendingUp,
  },
  {
    label: "VIX",
    value: "14.28",
    change: "-5.2%",
    trend: "down",
    icon: Activity,
  },
  {
    label: "AI Confidence",
    value: "87",
    change: "High conviction",
    trend: "up",
    icon: Brain,
  },
];

export function MarketOverview() {
  return (
    <div className="grid grid-cols-5 gap-4">
      {marketData.map((item) => (
        <Card key={item.label} className="bg-card border-border">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary">
                <item.icon className="h-5 w-5 text-muted-foreground" />
              </div>
              {item.trend === "up" ? (
                <TrendingUp className="h-4 w-4 text-bullish" />
              ) : (
                <TrendingDown className="h-4 w-4 text-bearish" />
              )}
            </div>
            <div className="mt-3">
              <p className="text-xs text-muted-foreground">{item.label}</p>
              <p className="mt-1 text-xl font-semibold text-foreground">
                {item.value}
              </p>
              <p
                className={`mt-1 text-xs font-medium ${
                  item.trend === "up" ? "text-bullish" : "text-bearish"
                }`}
              >
                {item.change}
              </p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
