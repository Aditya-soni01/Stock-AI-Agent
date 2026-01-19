import { useEffect, useState } from "react";
import { analyzeStock } from "./api";
import PriceChart from "./components/PriceChart";
import Stats from "./components/Stats";

function App() {
  const [data, setData] = useState(null);
  const [symbol, setSymbol] = useState("AAPL");

  useEffect(() => {
    analyzeStock(symbol).then(setData);
  }, [symbol]);

  if (!data) return <p>Loading...</p>;

  const tradeMarkers = data.backtest.trades.map(t => ({
    date: t.exit_date,
    price: t.exit_price,
    pnl: t.pnl
  }));

  return (
    <div style={{ padding: 20 }}>
      <input
        value={symbol}
        onChange={e => setSymbol(e.target.value.toUpperCase())}
        placeholder="Enter stock symbol"
        style={{ padding: 8, fontSize: 16 }}
      />

      <h2>{data.symbol}</h2>
      <h3>Decision: {data.decision.action}</h3>

      <PriceChart
        prices={data.chart_data}
        trades={tradeMarkers}
      />

      <Stats stats={data.trade_statistics} />
    </div>
  );
}

export default App;
