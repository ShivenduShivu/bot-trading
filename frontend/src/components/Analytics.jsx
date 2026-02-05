import { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  getPortfolioPerformance,
  getTradeStatistics,
  getBacktestComparison,
  getRiskMetrics
} from '../utils/api';
import './Analytics.css';

function Analytics() {
  const [portfolioData, setPortfolioData] = useState(null);
  const [tradeStats, setTradeStats] = useState(null);
  const [backtestData, setBacktestData] = useState(null);
  const [riskMetrics, setRiskMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    setError('');

    try {
      const [portfolio, trades, backtests, risk] = await Promise.all([
        getPortfolioPerformance(),
        getTradeStatistics(),
        getBacktestComparison(),
        getRiskMetrics()
      ]);

      setPortfolioData(portfolio);
      setTradeStats(trades);
      setBacktestData(backtests);
      setRiskMetrics(risk);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="loading-spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-error">
        <p>❌ {error}</p>
        <button onClick={loadAnalytics}>Retry</button>
      </div>
    );
  }

  const isProfit = portfolioData?.total_profit_loss >= 0;

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h1>📊 Performance Analytics</h1>
        <p>Track your trading performance and optimize your strategies</p>
      </div>

      {/* Portfolio Performance Summary */}
      <div className="analytics-section">
        <h2>💰 Portfolio Performance</h2>
        <div className="performance-cards">
          <div className={`perf-card highlight ${isProfit ? 'positive' : 'negative'}`}>
            <div className="perf-label">Total Profit/Loss</div>
            <div className="perf-value">
              {isProfit ? '+' : ''}${portfolioData?.total_profit_loss?.toLocaleString()}
            </div>
            <div className="perf-sub">
              {isProfit ? '+' : ''}{portfolioData?.total_return_percent?.toFixed(2)}% Return
            </div>
          </div>

          <div className="perf-card">
            <div className="perf-label">Initial Balance</div>
            <div className="perf-value">
              ${portfolioData?.initial_balance?.toLocaleString()}
            </div>
          </div>

          <div className="perf-card">
            <div className="perf-label">Current Balance</div>
            <div className="perf-value">
              ${portfolioData?.current_balance?.toLocaleString()}
            </div>
          </div>

          <div className="perf-card">
            <div className="perf-label">Total Trades</div>
            <div className="perf-value">{tradeStats?.total_trades || 0}</div>
            <div className="perf-sub">
              {tradeStats?.winning_trades || 0}W / {tradeStats?.losing_trades || 0}L
            </div>
          </div>
        </div>
      </div>

      {/* Equity Curve */}
      {portfolioData?.equity_curve && portfolioData.equity_curve.length > 0 && (
        <div className="analytics-section">
          <h2>📈 Equity Curve</h2>
          <div className="chart-card">
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={portfolioData.equity_curve}>
                <defs>
                  <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#667eea" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="date" 
                  stroke="#718096"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="#718096"
                  style={{ fontSize: '12px' }}
                  tickFormatter={(value) => `$${value.toLocaleString()}`}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px'
                  }}
                  formatter={(value) => `$${value.toLocaleString()}`}
                />
                <Area 
                  type="monotone" 
                  dataKey="balance" 
                  stroke="#667eea" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorBalance)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Risk Metrics */}
      {riskMetrics && (
        <div className="analytics-section">
          <h2>⚠️ Risk Metrics</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">📊</div>
              <div className="metric-content">
                <div className="metric-label">Sharpe Ratio</div>
                <div className="metric-value">{riskMetrics.sharpe_ratio}</div>
                <div className="metric-desc">Risk-adjusted return</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">📉</div>
              <div className="metric-content">
                <div className="metric-label">Max Drawdown</div>
                <div className="metric-value negative">
                  -{riskMetrics.max_drawdown_percent?.toFixed(2)}%
                </div>
                <div className="metric-desc">
                  ${riskMetrics.max_drawdown?.toLocaleString()}
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">📈</div>
              <div className="metric-content">
                <div className="metric-label">Volatility</div>
                <div className="metric-value">{riskMetrics.volatility?.toFixed(2)}%</div>
                <div className="metric-desc">Annualized</div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🎯</div>
              <div className="metric-content">
                <div className="metric-label">Win Rate</div>
                <div className={`metric-value ${tradeStats?.win_rate >= 50 ? 'positive' : 'negative'}`}>
                  {tradeStats?.win_rate?.toFixed(1)}%
                </div>
                <div className="metric-desc">
                  {tradeStats?.winning_trades}W / {tradeStats?.losing_trades}L
                </div>
              </div>
            </div>
          </div>

          <div className="metrics-explanation">
            <h3>📖 Understanding Risk Metrics</h3>
            <div className="explanation-grid">
              <div className="explanation-item">
                <strong>Sharpe Ratio:</strong> Higher is better. Above 1 is good, above 2 is excellent.
                Measures return per unit of risk.
              </div>
              <div className="explanation-item">
                <strong>Max Drawdown:</strong> Largest peak-to-trough decline. Lower is better.
                Shows worst-case loss scenario.
              </div>
              <div className="explanation-item">
                <strong>Volatility:</strong> Measure of price fluctuation. Lower means more stable returns.
              </div>
              <div className="explanation-item">
                <strong>Win Rate:</strong> Percentage of profitable trades. 50%+ is generally good,
                but should be combined with profit factor.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Trade Statistics */}
      {tradeStats && tradeStats.total_trades > 0 && (
        <div className="analytics-section">
          <h2>💹 Trade Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Average Win</div>
              <div className="stat-value positive">
                +${tradeStats.average_win?.toFixed(2)}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Average Loss</div>
              <div className="stat-value negative">
                -${tradeStats.average_loss?.toFixed(2)}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Largest Win</div>
              <div className="stat-value positive">
                +${tradeStats.largest_win?.toFixed(2)}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Largest Loss</div>
              <div className="stat-value negative">
                -${tradeStats.largest_loss?.toFixed(2)}
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Profit Factor</div>
              <div className={`stat-value ${tradeStats.profit_factor >= 1 ? 'positive' : 'negative'}`}>
                {tradeStats.profit_factor?.toFixed(2)}
              </div>
              <div className="stat-hint">
                {tradeStats.profit_factor >= 1.5 ? 'Excellent' :
                 tradeStats.profit_factor >= 1 ? 'Good' : 'Needs Improvement'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Backtest Comparison */}
      {backtestData?.backtests && backtestData.backtests.length > 0 && (
        <div className="analytics-section">
          <h2>🤖 Backtest Performance Comparison</h2>
          <div className="chart-card">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={backtestData.backtests}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="date" 
                  stroke="#718096"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="#718096"
                  style={{ fontSize: '12px' }}
                  label={{ value: 'Return (%)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px'
                  }}
                  formatter={(value) => `${value}%`}
                />
                <Legend />
                <Bar 
                  dataKey="total_return" 
                  fill="#667eea"
                  name="Return (%)"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="backtest-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Return</th>
                  <th>Trades</th>
                  <th>Win Rate</th>
                  <th>Final Capital</th>
                </tr>
              </thead>
              <tbody>
                {backtestData.backtests.map((bt) => (
                  <tr key={bt.id}>
                    <td>{bt.date}</td>
                    <td className={bt.total_return >= 0 ? 'positive' : 'negative'}>
                      {bt.total_return >= 0 ? '+' : ''}{bt.total_return}%
                    </td>
                    <td>{bt.total_trades}</td>
                    <td>{bt.win_rate}%</td>
                    <td>${bt.final_capital.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* No Data Message */}
      {(!portfolioData?.equity_curve || portfolioData.equity_curve.length === 0) && (
        <div className="no-data-message">
          <div className="no-data-icon">📊</div>
          <h3>No Trading Data Yet</h3>
          <p>Start trading or run backtests to see your analytics here!</p>
          <div className="no-data-actions">
            <a href="#trade" className="action-link">Start Trading</a>
            <a href="#bots" className="action-link">Run Backtest</a>
          </div>
        </div>
      )}
    </div>
  );
}

export default Analytics;