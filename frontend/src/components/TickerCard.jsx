import { useState, useEffect } from 'react';
import { getCombined } from '../api';
import PriceOverlay from './PriceOverlay';

const LABEL_COLORS = {
  bullish: '#16a34a',
  bearish: '#dc2626',
  neutral: '#6b7280',
};

export default function TickerCard({ ticker }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);
    setError(null);
    setData(null);
    getCombined(ticker)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [ticker]);

  if (loading) return <div className="card"><p className="muted">Loading {ticker}…</p></div>;
  if (error) return <div className="card error"><p>No data found for <strong>{ticker}</strong>. Try a ticker the scraper has seen recently.</p></div>;

  const latest = data.sentiment.at(-1);
  const sentimentLabel = latest?.sentiment_label ?? 'neutral';
  const sentimentScore = latest?.avg_sentiment ?? 0;
  const hasChart = data.sentiment.length > 0 && data.price.length > 0;

  return (
    <div className="card">
      <div className="card-header">
        <h2>{ticker}</h2>
        <span className="badge" style={{ background: LABEL_COLORS[sentimentLabel] }}>
          {sentimentLabel} ({sentimentScore > 0 ? '+' : ''}{sentimentScore.toFixed(3)})
        </span>
      </div>
      {hasChart
        ? <PriceOverlay sentimentData={data.sentiment} priceData={data.price} />
        : <p className="muted">Not enough data to render chart yet — wait for the next pipeline run.</p>
      }
    </div>
  );
}
