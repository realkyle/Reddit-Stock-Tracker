import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';

const formatTime = (iso) => {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:00`;
};

export default function SentimentChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
        <XAxis
          dataKey="time"
          tickFormatter={formatTime}
          tick={{ fontSize: 11 }}
          interval="preserveStartEnd"
        />
        <YAxis
          domain={[-1, 1]}
          tickFormatter={(v) => v.toFixed(1)}
          tick={{ fontSize: 11 }}
        />
        <Tooltip
          labelFormatter={formatTime}
          formatter={(v) => [v.toFixed(3), 'Sentiment']}
        />
        <ReferenceLine y={0} stroke="#999" strokeDasharray="4 4" />
        <Line
          type="monotone"
          dataKey="avg_sentiment"
          stroke="#6366f1"
          dot={false}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
