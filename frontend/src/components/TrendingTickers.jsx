import { useState, useEffect } from 'react';
import { getTrending } from '../api';

const LABEL_COLORS = {
  bullish: '#16a34a',
  bearish: '#dc2626',
  neutral: '#6b7280',
};

export default function TrendingTickers({ onSelect, selected }) {
  const [tickers, setTickers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTrending()
      .then(setTickers)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="sidebar"><p className="muted">Loading...</p></div>;
  if (!tickers.length) return <div className="sidebar"><p className="muted">No trending tickers in last 24h.</p></div>;

  return (
    <div className="sidebar">
      <h3>Trending (24h)</h3>
      <ul className="ticker-list">
        {tickers.map((t, i) => (
          <li
            key={t.ticker}
            className={`ticker-item${selected === t.ticker ? ' active' : ''}`}
            onClick={() => onSelect(t.ticker)}
          >
            <span className="rank">{i + 1}</span>
            <span className="ticker-symbol">{t.ticker}</span>
            <span className="mentions">{t.mention_count}×</span>
            <span className="sentiment-dot" style={{ color: LABEL_COLORS[t.sentiment_label] }}>
              ● {t.sentiment_label}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
