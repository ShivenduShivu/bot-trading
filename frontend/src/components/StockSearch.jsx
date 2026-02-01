import { useState } from 'react';
import { searchStocks, getStockInfo } from '../utils/api';
import './StockSearch.css';

function StockSearch({ onStockSelect }) {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');
  const [selectedStock, setSelectedStock] = useState(null);
  const [loadingInfo, setLoadingInfo] = useState(false);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery || searchQuery.length < 1) {
      setResults([]);
      return;
    }

    setSearching(true);
    setError('');

    try {
      const data = await searchStocks(searchQuery);
      setResults(data.results || []);
    } catch (err) {
      setError('Failed to search stocks');
      setResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value.toUpperCase();
    setQuery(value);
    
    // Debounce search
    if (value.length >= 1) {
      handleSearch(value);
    } else {
      setResults([]);
    }
  };

  const handleStockClick = async (stock) => {
    setLoadingInfo(true);
    setError('');

    try {
      const stockInfo = await getStockInfo(stock.symbol);
      setSelectedStock(stockInfo);
      setResults([]);
      setQuery(stock.symbol);
      
      if (onStockSelect) {
        onStockSelect(stockInfo);
      }
    } catch (err) {
      setError('Failed to load stock information');
    } finally {
      setLoadingInfo(false);
    }
  };

  const clearSelection = () => {
    setSelectedStock(null);
    setQuery('');
    setResults([]);
  };

  return (
    <div className="stock-search">
      <div className="search-input-container">
        <input
          type="text"
          className="search-input"
          placeholder="Search stocks (e.g., AAPL, TSLA, MSFT)..."
          value={query}
          onChange={handleInputChange}
          disabled={loadingInfo}
        />
        {query && (
          <button className="clear-button" onClick={clearSelection}>
            ✕
          </button>
        )}
      </div>

      {searching && (
        <div className="search-status">Searching...</div>
      )}

      {error && (
        <div className="search-error">{error}</div>
      )}

      {results.length > 0 && (
        <div className="search-results">
          {results.map((stock, index) => (
            <div
              key={index}
              className="search-result-item"
              onClick={() => handleStockClick(stock)}
            >
              <div className="result-symbol">{stock.symbol}</div>
              <div className="result-name">{stock.name}</div>
              <div className="result-exchange">{stock.exchange}</div>
            </div>
          ))}
        </div>
      )}

      {loadingInfo && (
        <div className="loading-info">Loading stock information...</div>
      )}

      {selectedStock && (
        <div className="selected-stock-info">
          <div className="stock-header">
            <div>
              <h3>{selectedStock.symbol}</h3>
              <p className="stock-name">{selectedStock.name}</p>
            </div>
            <div className="stock-price-main">
              <div className="current-price">
                ${selectedStock.current_price.toFixed(2)}
              </div>
              <div className={`price-change ${selectedStock.change >= 0 ? 'positive' : 'negative'}`}>
                {selectedStock.change >= 0 ? '+' : ''}
                ${selectedStock.change.toFixed(2)} ({selectedStock.change_percent.toFixed(2)}%)
              </div>
            </div>
          </div>

          <div className="stock-details-grid">
            <div className="detail-box">
              <span className="detail-label">Open</span>
              <span className="detail-value">${selectedStock.open.toFixed(2)}</span>
            </div>
            <div className="detail-box">
              <span className="detail-label">Previous Close</span>
              <span className="detail-value">${selectedStock.previous_close.toFixed(2)}</span>
            </div>
            <div className="detail-box">
              <span className="detail-label">Day High</span>
              <span className="detail-value">${selectedStock.day_high.toFixed(2)}</span>
            </div>
            <div className="detail-box">
              <span className="detail-label">Day Low</span>
              <span className="detail-value">${selectedStock.day_low.toFixed(2)}</span>
            </div>
            <div className="detail-box">
              <span className="detail-label">Volume</span>
              <span className="detail-value">{selectedStock.volume.toLocaleString()}</span>
            </div>
            <div className="detail-box">
              <span className="detail-label">Market Cap</span>
              <span className="detail-value">
                ${(selectedStock.market_cap / 1000000000).toFixed(2)}B
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default StockSearch;