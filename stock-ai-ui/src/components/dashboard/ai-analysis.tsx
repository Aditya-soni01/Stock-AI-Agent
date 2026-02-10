import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  ChevronDown,
  ChevronUp,
  Brain,
  TrendingUp,
  Gauge,
  Target,
  AlertTriangle,
} from "lucide-react";
import { useState } from "react";

export function AIAnalysis() {
  const [reasoningExpanded, setReasoningExpanded] = useState(false);

  return (
    <Card className="bg-card border-border h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-ai-insight/20">
            <Brain className="h-5 w-5 text-ai-insight" />
          </div>
          <CardTitle className="text-lg font-semibold text-foreground">
            AI Analysis
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Trend */}
        <div className="flex items-center justify-between rounded-lg bg-secondary p-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Trend</span>
          </div>
          <Badge className="bg-bullish/20 text-bullish hover:bg-bullish/30">
            Bullish
          </Badge>
        </div>

        {/* Momentum */}
        <div className="rounded-lg bg-secondary p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gauge className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Momentum</span>
            </div>
            <span className="text-sm font-medium text-foreground">Strong</span>
          </div>
          <Progress
            value={78}
            className="mt-2 h-1.5 bg-muted [&>[data-slot=progress-indicator]]:bg-bullish"
          />
        </div>

        {/* AI Verdict */}
        <div className="rounded-lg border border-bullish/30 bg-bullish/10 p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-muted-foreground">
              AI Verdict
            </span>
            <Badge className="bg-bullish text-primary-foreground text-base font-bold px-4 py-1">
              BUY
            </Badge>
          </div>
        </div>

        {/* Confidence Level */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              Confidence Level
            </span>
            <span className="text-sm font-bold text-ai-insight">87%</span>
          </div>
          <Progress
            value={87}
            className="h-2 bg-muted [&>[data-slot=progress-indicator]]:bg-ai-insight"
          />
        </div>

        {/* Risk-Reward Ratio */}
        <div className="flex items-center justify-between rounded-lg bg-secondary p-3">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Risk-Reward</span>
          </div>
          <span className="text-sm font-medium text-bullish">1 : 2.5</span>
        </div>

        {/* Key Reasoning */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-caution" />
            <span className="text-sm font-medium text-foreground">
              Key Reasoning
            </span>
          </div>
          <ul className="space-y-1.5 text-xs text-muted-foreground">
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-bullish" />
              Price above 20 & 50 EMA with bullish crossover
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-bullish" />
              RSI at 58, room for upward movement
            </li>
            <li className="flex items-start gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-bullish" />
              Strong volume confirming breakout
            </li>
          </ul>
        </div>

        {/* Why this signal? */}
        <button
          type="button"
          onClick={() => setReasoningExpanded(!reasoningExpanded)}
          className="flex w-full items-center justify-between rounded-lg border border-border p-3 text-left transition-colors hover:bg-secondary"
        >
          <span className="text-sm font-medium text-ai-insight">
            Why this signal?
          </span>
          {reasoningExpanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </button>

        {reasoningExpanded && (
          <div className="rounded-lg bg-secondary p-3 text-xs text-muted-foreground leading-relaxed">
            The AI detected a bullish flag pattern forming after a strong
            uptrend. The consolidation is healthy with decreasing volume, and
            the recent breakout attempt shows increasing buying pressure. MACD
            histogram is turning positive, and the stock is holding above key
            moving averages. Institutional delivery data also shows
            accumulation.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
