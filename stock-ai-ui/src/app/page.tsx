import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { MarketOverview } from "@/components/dashboard/market-overview"
import { StockChart } from "@/components/dashboard/stock-chart"
import { AIAnalysis } from "@/components/dashboard/ai-analysis"
import { TradeSetup } from "@/components/dashboard/trade-setup"
import { AIChat } from "@/components/dashboard/ai-chat"
import { WatchlistTable } from "@/components/dashboard/watchlist-table"

export default function Dashboard() {
    console.log("Dashboard rendered");
  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content area */}
      <div className="pl-56 transition-all duration-300">
        {/* Header */}
        <Header />

        {/* Dashboard content */}
        <main className="p-6 space-y-6">
          {/* Market Overview Cards */}
          <section>
            <MarketOverview />
          </section>

          {/* Main Analysis Section */}
          <section className="grid grid-cols-3 gap-6">
            {/* Stock Chart - Takes 2 columns */}
            <div className="col-span-2">
              <StockChart />
            </div>
            
            {/* AI Analysis Panel - Takes 1 column */}
            <div className="col-span-1">
              <AIAnalysis />
            </div>
          </section>

          {/* Trade Setup and AI Chat */}
          <section className="grid grid-cols-3 gap-6">
            {/* Trade Setup Card */}
            <div className="col-span-1">
              <TradeSetup />
            </div>
            
            {/* AI Chat Panel - Takes 2 columns */}
            <div className="col-span-2">
              <AIChat />
            </div>
          </section>

          {/* Watchlist & Signals Table */}
          <section>
            <WatchlistTable />
          </section>
        </main>
      </div>
    </div>
  )
}
