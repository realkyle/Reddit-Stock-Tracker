import {
  ComposedChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';

const formatTime = (iso) => {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:00`;
};

function mergeData(sentimentData, priceData) {
  const priceMap = {};
  for (const p of priceData) {
    const key = new Date(p.time).setMinutes(0, 0, 0);
    priceMap[key] = p.close;
  }
  return sentimentData.map((s) => ({
    time: s.time,
    sentiment: s.avg_sentiment,
    price: priceMap[new Date(s.time).setMinutes(0, 0, 0)] ?? null,
  }));
}

export default function PriceOverlay({ sentimentData, priceData }) {
  const data = mergeData(sentimentData, priceData);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={data} margin={{ top: 5, right: 40, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
        <XAxis
          dataKey="time"
          tickFormatter={formatTime}
          tick={{ fontSize: 11 }}
          interval="preserveStartEnd"
        />
        <YAxis
          yAxisId="sentiment"
          domain={[-1, 1]}
          tickFormatter={(v) => v.toFixed(1)}
          tick={{ fontSize: 11 }}
          label={{ value: 'Sentiment', angle: -90, position: 'insideLeft', offset: 12, fontSize: 11 }}
        />
        <YAxis
          yAxisId="price"
          orientation="right"
          tickFormatter={(v) => `$${v}`}
          tick={{ fontSize: 11 }}
          label={{ value: 'Price', angle: 90, position: 'insideRight', offset: 12, fontSize: 11 }}
        />
        <Tooltip
          labelFormatter={formatTime}
          formatter={(value, name) =>
            name === 'price'
              ? [`$${value?.toFixed(2)}`, 'Price']
              : [value?.toFixed(3), 'Sentiment']
          }
        />
        <Legend />
        <ReferenceLine yAxisId="sentiment" y={0} stroke="#999" strokeDasharray="4 4" />
        <Line
          yAxisId="sentiment"
          type="monotone"
          dataKey="sentiment"
          stroke="#6366f1"
          dot={false}
          strokeWidth={2}
          name="Sentiment"
        />
        <Line
          yAxisId="price"
          type="monotone"
          dataKey="price"
          stroke="#f59e0b"
          dot={false}
          strokeWidth={2}
          name="Price"
          connectNulls
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
