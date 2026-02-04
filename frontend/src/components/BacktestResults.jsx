import './BotBuilder.css';

function BacktestResults({ results }) {
  if (!results || !results.results) {
    return null;
  }

  const data = results.results;
  const isProfit = data.total_return >= 0;

  return (
    <div className="backtest-results">
      <h2>📊 Backtest Results</h2>

      {/* Performance Summary */}
      <div className="results-summary">
        <div className="summary-card highlight">
          <div className="summary-label">Total Return</div>
          <div className={`summary-value ${isProfit ? 'positive' : 'negative'}`}>
            {isProfit ? '+' : ''}{data.total_return.toFixed(2)}%
          </div>
          <div className="summary-sub">
            ${data.initial_capital.toLocaleString()} → ${data.final_capital.toLocaleString()}
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Profit/Loss</div>
          <div className={`summary-value ${isProfit ? 'positive' : 'negative'}`}>
            {isProfit ? '+' : ''}${(data.final_capital - data.initial_capital).toFixed(2)}
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Total Trades</div>
          <div className="summary-value">{data.total_trades}</div>
        </div>

        <div className="summary-card">
          <div className="summary-label">Win Rate</div>
          <div className={`summary-value ${data.win_rate >= 50 ? 'positive' : 'negative'}`}>
            {data.win_rate.toFixed(1)}%
          </div>
          <div className="summary-sub">
            {data.winning_trades}W / {data.losing_trades}L
          </div>
        </div>
      </div>

      {/* Trade History */}
      {data.trades && data.trades.length > 0 && (
        <div className="trades-section">
          <h3>📜 Trade History</h3>
          <div className="trades-table-container">
            <table className="trades-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Price</th>
                  <th>Shares</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {data.trades.map((trade, index) => (
                  <tr key={index} className={trade.type === 'BUY' ? 'buy-row' : 'sell-row'}>
                    <td>{trade.date}</td>
                    <td>
                      <span className={`trade-badge ${trade.type.toLowerCase()}`}>
                        {trade.type === 'BUY' ? '🟢 BUY' : '🔴 SELL'}
                      </span>
                    </td>
                    <td>${trade.price.toFixed(2)}</td>
                    <td>{trade.shares}</td>
                    <td>${trade.total.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {data.total_trades === 0 && (
        <div className="no-trades-message">
          <p>⚠️ No trades were executed during this period.</p>
          <p>Try:</p>
          <ul>
            <li>Adjusting strategy parameters</li>
            <li>Using a longer time period</li>
            <li>Selecting a different stock</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default BacktestResults;