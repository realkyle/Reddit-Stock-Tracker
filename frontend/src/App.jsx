import { useState } from 'react';
import TrendingTickers from './components/TrendingTickers';
import TickerCard from './components/TickerCard';
import './App.css';

export default function App() {
  const [selectedTicker, setSelectedTicker] = useState(null);
  const [searchInput, setSearchInput] = useState('');

  function handleSearch(e) {
    e.preventDefault();
    const t = searchInput.trim().toUpperCase();
    if (t) {
      setSelectedTicker(t);
      setSearchInput('');
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Reddit Sentiment Tracker</h1>
        <form className="search-form" onSubmit={handleSearch}>
          <input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
            placeholder="Search ticker (e.g. NVDA)"
            maxLength={5}
          />
          <button type="submit">Go</button>
        </form>
      </header>

      <main className="main">
        <TrendingTickers onSelect={setSelectedTicker} selected={selectedTicker} />
        <div className="content">
          {selectedTicker
            ? <TickerCard ticker={selectedTicker} />
            : <p className="muted">Select a ticker from the list or search above.</p>
          }
        </div>
      </main>
    </div>
  );
}
