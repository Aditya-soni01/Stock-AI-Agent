export default function Stats({ stats }) {
  return (
    <div style={{ display: "flex", gap: 20 }}>
      <div>Win Rate: {stats.win_rate}%</div>
      <div>Profit Factor: {stats.profit_factor}</div>
      <div>Expectancy: {stats.expectancy}</div>
      <div>Max DD: {stats.max_drawdown}</div>
    </div>
  );
}
