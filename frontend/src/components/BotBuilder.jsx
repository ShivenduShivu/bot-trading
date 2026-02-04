import { useState } from 'react';
import { runBacktest } from '../utils/api';
import BacktestResults from './BacktestResults';
import './BotBuilder.css';

function BotBuilder() {
  const [formData, setFormData] = useState({
    strategy_type: 'SMA_CROSSOVER',
    symbol: '',
    start_date: '2025-09-01',
    end_date: '2026-01-31',
    initial_capital: 10000,
    // SMA parameters
    short_period: 10,
    long_period: 30,
    // RSI parameters
    rsi_period: 14,
    oversold: 30,
    overbought: 70,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResults(null);
    setLoading(true);

    try {
      // Build parameters based on strategy type
      let parameters = {};

      if (formData.strategy_type === 'SMA_CROSSOVER') {
        parameters = {
          short_period: parseInt(formData.short_period),
          long_period: parseInt(formData.long_period),
        };
      } else if (formData.strategy_type === 'RSI') {
        parameters = {
          rsi_period: parseInt(formData.rsi_period),
          oversold: parseInt(formData.oversold),
          overbought: parseInt(formData.overbought),
        };
      } else if (formData.strategy_type === 'MACD') {
        parameters = {};
      }

      const backtestData = {
        strategy_type: formData.strategy_type,
        symbol: formData.symbol.toUpperCase(),
        parameters: parameters,
        start_date: formData.start_date,
        end_date: formData.end_date,
        initial_capital: parseFloat(formData.initial_capital),
      };

      const response = await runBacktest(backtestData);
      setResults(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderParameterInputs = () => {
    switch (formData.strategy_type) {
      case 'SMA_CROSSOVER':
        return (
          <>
            <div className="param-group">
              <label htmlFor="short_period">Short Period (days)</label>
              <input
                type="number"
                id="short_period"
                name="short_period"
                value={formData.short_period}
                onChange={handleChange}
                min="5"
                max="50"
              />
              <span className="param-hint">Faster moving average (e.g., 10, 20)</span>
            </div>
            <div className="param-group">
              <label htmlFor="long_period">Long Period (days)</label>
              <input
                type="number"
                id="long_period"
                name="long_period"
                value={formData.long_period}
                onChange={handleChange}
                min="20"
                max="200"
              />
              <span className="param-hint">Slower moving average (e.g., 30, 50, 200)</span>
            </div>
          </>
        );

      case 'RSI':
        return (
          <>
            <div className="param-group">
              <label htmlFor="rsi_period">RSI Period</label>
              <input
                type="number"
                id="rsi_period"
                name="rsi_period"
                value={formData.rsi_period}
                onChange={handleChange}
                min="5"
                max="30"
              />
              <span className="param-hint">Standard is 14 days</span>
            </div>
            <div className="param-group">
              <label htmlFor="oversold">Oversold Threshold</label>
              <input
                type="number"
                id="oversold"
                name="oversold"
                value={formData.oversold}
                onChange={handleChange}
                min="20"
                max="40"
              />
              <span className="param-hint">Buy signal (standard: 30)</span>
            </div>
            <div className="param-group">
              <label htmlFor="overbought">Overbought Threshold</label>
              <input
                type="number"
                id="overbought"
                name="overbought"
                value={formData.overbought}
                onChange={handleChange}
                min="60"
                max="80"
              />
              <span className="param-hint">Sell signal (standard: 70)</span>
            </div>
          </>
        );

      case 'MACD':
        return (
          <div className="param-info">
            <p>📊 MACD uses standard parameters (12, 26, 9)</p>
            <p>No configuration needed!</p>
          </div>
        );

      default:
        return null;
    }
  };

  const getStrategyDescription = () => {
    switch (formData.strategy_type) {
      case 'SMA_CROSSOVER':
        return '📈 Buy when short SMA crosses above long SMA. Sell when it crosses below. Great for trending markets.';
      case 'RSI':
        return '📊 Buy when RSI drops below oversold level. Sell when it rises above overbought level. Best for range-bound markets.';
      case 'MACD':
        return '📉 Buy when MACD line crosses above signal line. Sell when it crosses below. Combines trend and momentum.';
      default:
        return '';
    }
  };

  return (
    <div className="bot-builder-container">
      <div className="bot-builder-header">
        <h2>🤖 Backtest Trading Strategies</h2>
        <p>Test your trading ideas on historical data before risking real money!</p>
      </div>

      <div className="bot-builder-content">
        <div className="backtest-form-card">
          <form onSubmit={handleSubmit}>
            {/* Strategy Selection */}
            <div className="form-section">
              <h3>1️⃣ Choose Strategy</h3>
              <div className="strategy-selector">
                <label className={`strategy-option ${formData.strategy_type === 'SMA_CROSSOVER' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="strategy_type"
                    value="SMA_CROSSOVER"
                    checked={formData.strategy_type === 'SMA_CROSSOVER'}
                    onChange={handleChange}
                  />
                  <div className="strategy-card">
                    <div className="strategy-icon">📈</div>
                    <div className="strategy-name">SMA Crossover</div>
                    <div className="strategy-desc">Moving Average Strategy</div>
                  </div>
                </label>

                <label className={`strategy-option ${formData.strategy_type === 'RSI' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="strategy_type"
                    value="RSI"
                    checked={formData.strategy_type === 'RSI'}
                    onChange={handleChange}
                  />
                  <div className="strategy-card">
                    <div className="strategy-icon">📊</div>
                    <div className="strategy-name">RSI</div>
                    <div className="strategy-desc">Overbought/Oversold</div>
                  </div>
                </label>

                <label className={`strategy-option ${formData.strategy_type === 'MACD' ? 'active' : ''}`}>
                  <input
                    type="radio"
                    name="strategy_type"
                    value="MACD"
                    checked={formData.strategy_type === 'MACD'}
                    onChange={handleChange}
                  />
                  <div className="strategy-card">
                    <div className="strategy-icon">📉</div>
                    <div className="strategy-name">MACD</div>
                    <div className="strategy-desc">Trend & Momentum</div>
                  </div>
                </label>
              </div>

              <div className="strategy-description">
                {getStrategyDescription()}
              </div>
            </div>

            {/* Stock & Dates */}
            <div className="form-section">
              <h3>2️⃣ Select Stock & Period</h3>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="symbol">Stock Symbol</label>
                  <input
                    type="text"
                    id="symbol"
                    name="symbol"
                    value={formData.symbol}
                    onChange={handleChange}
                    placeholder="e.g., AAPL, TSLA, MSFT"
                    required
                    style={{ textTransform: 'uppercase' }}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="initial_capital">Initial Capital ($)</label>
                  <input
                    type="number"
                    id="initial_capital"
                    name="initial_capital"
                    value={formData.initial_capital}
                    onChange={handleChange}
                    min="1000"
                    step="1000"
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="start_date">Start Date</label>
                  <input
                    type="date"
                    id="start_date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="end_date">End Date</label>
                  <input
                    type="date"
                    id="end_date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Strategy Parameters */}
            <div className="form-section">
              <h3>3️⃣ Configure Parameters</h3>
              <div className="parameters-container">
                {renderParameterInputs()}
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="error-message">
                ❌ {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              className="run-backtest-button"
              disabled={loading || !formData.symbol}
            >
              {loading ? '⏳ Running Backtest...' : '🚀 Run Backtest'}
            </button>
          </form>
        </div>

        {/* Results Section */}
        {results && (
          <BacktestResults results={results} />
        )}
      </div>
    </div>
  );
}

export default BotBuilder;