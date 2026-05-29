const BASE = 'http://localhost:8000';

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return res.json();
}

export const getTrending = () => get('/tickers/trending');
export const getSentiment = (symbol) => get(`/tickers/${symbol}/sentiment`);
export const getPrice = (symbol) => get(`/tickers/${symbol}/price`);
export const getCombined = (symbol) => get(`/tickers/${symbol}/combined`);
export const getFeed = () => get('/feed');
