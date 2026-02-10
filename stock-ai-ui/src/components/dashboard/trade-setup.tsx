import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Play, Star, Bell, Calculator } from "lucide-react"

export function TradeSetup() {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <Calculator className="h-5 w-5 text-ai-insight" />
          Trade Setup
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          {/* Entry Price */}
          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Entry Price</Label>
            <Input
              defaultValue="₹2,456.00"
              className="h-9 bg-input border-border text-foreground"
            />
          </div>
          
          {/* Stop Loss */}
          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Stop Loss</Label>
            <Input
              defaultValue="₹2,420.00"
              className="h-9 bg-input border-border text-bearish"
            />
          </div>
          
          {/* Target 1 */}
          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Target 1</Label>
            <Input
              defaultValue="₹2,490.00"
              className="h-9 bg-input border-border text-bullish"
            />
          </div>
          
          {/* Target 2 */}
          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Target 2</Label>
            <Input
              defaultValue="₹2,540.00"
              className="h-9 bg-input border-border text-bullish"
            />
          </div>
          
          {/* Risk % */}
          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Risk %</Label>
            <Input
              defaultValue="1.5%"
              className="h-9 bg-input border-border text-foreground"
            />
          </div>
          
          {/* Position Size */}
          <div className="space-y-1.5">
            <Label className="text-xs text-muted-foreground">Position Size</Label>
            <Input
              defaultValue="150 shares"
              className="h-9 bg-input border-border text-foreground"
              readOnly
            />
          </div>
        </div>

        {/* Calculated Risk-Reward Display */}
        <div className="flex items-center justify-between rounded-lg bg-secondary p-3">
          <span className="text-xs text-muted-foreground">Potential P/L</span>
          <div className="flex items-center gap-3">
            <span className="text-xs text-bearish">-₹5,400</span>
            <span className="text-muted-foreground">/</span>
            <span className="text-xs text-bullish">+₹12,600</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-3 gap-2">
          <Button className="h-9 bg-ai-insight text-white hover:bg-ai-insight/90">
            <Play className="mr-1.5 h-4 w-4" />
            Simulate
          </Button>
          <Button variant="outline" className="h-9 border-border text-foreground hover:bg-secondary bg-transparent">
            <Star className="mr-1.5 h-4 w-4" />
            Watchlist
          </Button>
          <Button variant="outline" className="h-9 border-border text-foreground hover:bg-secondary bg-transparent">
            <Bell className="mr-1.5 h-4 w-4" />
            Alert
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
