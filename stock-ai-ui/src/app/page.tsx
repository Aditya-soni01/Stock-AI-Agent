import { useCallback, useEffect, useMemo, useState } from "react";

import { Sidebar } from "@/components/dashboard/sidebar";
import { Header } from "@/components/dashboard/header";
import { MarketOverview } from "@/components/dashboard/market-overview";
import { StockChart } from "@/components/dashboard/stock-chart";
import { AIAnalysis } from "@/components/dashboard/ai-analysis";
import { TradeSetup } from "@/components/dashboard/trade-setup";
import { AIChat } from "@/components/dashboard/ai-chat";
import { WatchlistTable } from "@/components/dashboard/watchlist-table";
import {
  getDailyReport,
  getFeedStatus,
  getNiftyLivePrice,
  getPaperTrades,
  getRunnerStatus,
  getSessionReport,
  getErrorMessage,
  startPaperRunner,
  startUpstoxFeed,
  stopPaperRunner,
  type FeedStatusResponse,
  type LivePriceResponse,
  type PaperReportResponse,
  type PaperTradesResponse,
  type RunnerStatusResponse,
} from "@/lib/api";

const POLL_INTERVAL_MS = 5000;

interface DashboardData {
  livePrice: LivePriceResponse;
  feedStatus: FeedStatusResponse;
  runnerStatus: RunnerStatusResponse;
  dailyReport: PaperReportResponse;
  sessionReport: PaperReportResponse;
  trades: PaperTradesResponse;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isStartingBot, setIsStartingBot] = useState(false);
  const [isStoppingBot, setIsStoppingBot] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async (isInitial: boolean) => {
    if (isInitial) {
      setIsInitialLoading(true);
    } else {
      setIsRefreshing(true);
    }

    try {
      const [livePrice, feedStatus, runnerStatus, dailyReport, sessionReport, trades] =
        await Promise.all([
          getNiftyLivePrice(),
          getFeedStatus(),
          getRunnerStatus(),
          getDailyReport(),
          getSessionReport(),
          getPaperTrades(),
        ]);

      setData({
        livePrice,
        feedStatus,
        runnerStatus,
        dailyReport,
        sessionReport,
        trades,
      });
      setError(null);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsInitialLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    const refresh = async (isInitial: boolean) => {
      if (cancelled) return;
      await fetchDashboardData(isInitial);
    };

    void refresh(true);
    const interval = window.setInterval(() => {
      void refresh(false);
    }, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [fetchDashboardData]);

  const handleStartBot = useCallback(async () => {
    setIsStartingBot(true);
    setActionError(null);
    setActionMessage(null);

    try {
      try {
        await startUpstoxFeed();
      } catch (err) {
        throw new Error(`Feed failed to start: ${getErrorMessage(err)}`);
      }

      try {
        await startPaperRunner();
      } catch (err) {
        throw new Error(`Runner failed to start: ${getErrorMessage(err)}`);
      }

      setActionMessage("Bot start sequence completed.");
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setIsStartingBot(false);
      await fetchDashboardData(false);
    }
  }, [fetchDashboardData]);

  const handleStopBot = useCallback(async () => {
    setIsStoppingBot(true);
    setActionError(null);
    setActionMessage(null);

    try {
      await stopPaperRunner();
      setActionMessage("Bot stopped.");
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setIsStoppingBot(false);
      await fetchDashboardData(false);
    }
  }, [fetchDashboardData]);

  const isBusy = isInitialLoading || isRefreshing;

  const topBarData = useMemo(
    () => ({
      livePrice: data?.livePrice ?? null,
      feedStatus: data?.feedStatus ?? null,
      runnerStatus: data?.runnerStatus ?? null,
      isRefreshing,
    }),
    [data, isRefreshing],
  );

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />

      <div className="pl-0 md:pl-64 transition-all duration-300">
        <Header {...topBarData} />

        <main className="space-y-6 p-4 md:p-6">
          {error && (
            <section className="rounded-xl border border-[#ff5f5f]/40 bg-[#ff5f5f]/10 px-4 py-3 text-sm text-[#ff8e8e]">
              Dashboard refresh error: {error}
            </section>
          )}

          <section>
            <MarketOverview
              dailyReport={data?.dailyReport ?? null}
              sessionReport={data?.sessionReport ?? null}
              runnerStatus={data?.runnerStatus ?? null}
              trades={data?.trades ?? null}
              actionError={actionError}
              isLoading={isBusy}
            />
          </section>

          <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
            <div className="space-y-6 xl:col-span-8">
              <StockChart
                livePrice={data?.livePrice ?? null}
                feedStatus={data?.feedStatus ?? null}
                isLoading={isBusy}
              />
              <WatchlistTable trades={data?.trades ?? null} isLoading={isBusy} />
            </div>

            <div className="space-y-6 xl:col-span-4">
              <AIAnalysis
                runnerStatus={data?.runnerStatus ?? null}
                feedStatus={data?.feedStatus ?? null}
                sessionReport={data?.sessionReport ?? null}
                isLoading={isBusy}
              />
              <TradeSetup
                feedStatus={data?.feedStatus ?? null}
                runnerStatus={data?.runnerStatus ?? null}
                onStartBot={handleStartBot}
                onStopBot={handleStopBot}
                isStarting={isStartingBot}
                isStopping={isStoppingBot}
                actionError={actionError}
                actionMessage={actionMessage}
              />
              <AIChat />
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
