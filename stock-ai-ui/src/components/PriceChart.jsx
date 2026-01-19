import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot
} from "recharts";

export default function PriceChart({ prices, trades }) {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={prices}>
        <XAxis dataKey="date" hide />
        <YAxis />
        <Tooltip />

        <Line
          type="monotone"
          dataKey="price"
          stroke="#4f46e5"
          dot={false}
        />

        {trades.map((t, i) => (
          <ReferenceDot
            key={i}
            x={t.date}
            y={t.price}
            r={6}
            fill={t.pnl > 0 ? "green" : "red"}
            stroke="none"
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
