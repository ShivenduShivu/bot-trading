import { useState, useEffect } from 'react';
import { getUserProfile, removeToken, getOrders, getTransactions } from '../utils/api';
import Trading from './Trading';
import './Dashboard.css';
import BotBuilder from './BotBuilder';
import Analytics from './Analytics';
import AIStrategyBuilder from './AIStrategyBuilder';

function Dashboard({ onLogout }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('overview'); // 'overview', 'trading', 'history'
  const [orders, setOrders] = useState([]);
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const userData = await getUserProfile(token);
      setUser(userData);
    } catch (err) {
      setError('Failed to load profile');
      handleLogout();
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const [ordersData, transactionsData] = await Promise.all([
        getOrders(50),
        getTransactions(50)
      ]);
      setOrders(ordersData);
      setTransactions(transactionsData);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleLogout = () => {
    removeToken();
    onLogout();
  };

  const handleViewChange = async (view) => {
    setCurrentView(view);
    if (view === 'history') {
      await loadHistory();
    }
  };

  const handleBalanceUpdate = () => {
    loadUserProfile();
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">⏳ Loading your account...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>📈 Paper Trading Platform</h1>
        <button onClick={handleLogout} className="logout-button">
          🚪 Logout
        </button>
      </header>

      {/* Navigation Tabs */}
      <div className="dashboard-nav">
        <button
          className={`nav-tab ${currentView === 'overview' ? 'active' : ''}`}
          onClick={() => handleViewChange('overview')}
        >
          🏠 Overview
        </button>
        <button
          className={`nav-tab ${currentView === 'trading' ? 'active' : ''}`}
          onClick={() => handleViewChange('trading')}
        >
          💹 Trade
        </button>
        <button
          className={`nav-tab ${currentView === 'bots' ? 'active' : ''}`}
          onClick={() => handleViewChange('bots')}
        >
          🤖 Bots
        </button>
        <button
          className={`nav-tab ${currentView === 'analytics' ? 'active' : ''}`}
          onClick={() => handleViewChange('analytics')}
        >
          📊 Analytics
        </button>
        <button
          className={`nav-tab ${currentView === 'ai-builder' ? 'active' : ''}`}
          onClick={() => handleViewChange('ai-builder')}
        >
          🤖 AI Builder
        </button>
        <button
          className={`nav-tab ${currentView === 'history' ? 'active' : ''}`}
          onClick={() => handleViewChange('history')}
        >
          📜 History
        </button>
      </div>

      {/* Content Area */}
      <div className="dashboard-content">
        {currentView === 'overview' && (
          <>
            <div className="welcome-section">
              <h2>Welcome back, {user.username}! 👋</h2>
              <p className="user-email">{user.email}</p>
            </div>

            <div className="account-card">
              <h3>💰 Your Trading Account</h3>
              <div className="balance-display">
                <span className="balance-label">Virtual Balance</span>
                <span className="balance-amount">
                  ${user.virtual_balance.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </span>
              </div>
              <div className="account-info">
                <div className="info-item">
                  <span className="info-label">Account Status:</span>
                  <span className="info-value status-active">
                    {user.is_active ? '✅ Active' : '❌ Inactive'}
                  </span>
                </div>
                <div className="info-item">
                  <span className="info-label">Member Since:</span>
                  <span className="info-value">
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </span>
                </div>
              </div>
            </div>

            <div className="quick-actions">
              <button
                className="action-button primary"
                onClick={() => handleViewChange('trading')}
              >
                💹 Start Trading
              </button>
              <button
                className="action-button secondary"
                onClick={() => handleViewChange('history')}
              >
                📜 View History
              </button>
            </div>

            <div className="checkpoint-status">
              <h3>✅ Checkpoint 2 Progress</h3>
              <ul>
                <li>✅ User authentication system</li>
                <li>✅ JWT token-based security</li>
                <li>✅ Order placement (BUY/SELL)</li>
                <li>✅ Portfolio management</li>
                <li>✅ Transaction tracking</li>
                <li>⏳ Coming Next: Real market data</li>
              </ul>
            </div>
          </>
        )}

        {currentView === 'trading' && (
          <Trading onBalanceUpdate={handleBalanceUpdate} />
        )}

        {currentView === 'bots' && (
          <BotBuilder />
        )}

        {currentView === 'analytics' && (
          <Analytics />
        )}
        
        {currentView === 'ai-builder' && (
          <AIStrategyBuilder />
        )}

        {currentView === 'history' && (
          <div className="history-container">
            {/* Orders History */}
            <div className="history-section">
              <h3>📋 Order History</h3>
              {orders.length === 0 ? (
                <div className="empty-state">
                  <p>No orders yet. Place your first trade!</p>
                </div>
              ) : (
                <div className="history-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Symbol</th>
                        <th>Type</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Total</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.map((order) => (
                        <tr key={order.id}>
                          <td>
                            {new Date(order.created_at).toLocaleString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </td>
                          <td className="symbol-cell">{order.symbol}</td>
                          <td>
                            <span className={`type-badge ${order.order_type.toLowerCase()}`}>
                              {order.order_type}
                            </span>
                          </td>
                          <td>{order.quantity}</td>
                          <td>${order.price.toFixed(2)}</td>
                          <td>${order.total_amount.toFixed(2)}</td>
                          <td>
                            <span className={`status-badge ${order.status.toLowerCase()}`}>
                              {order.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Transactions History */}
            <div className="history-section">
              <h3>💳 Transaction History</h3>
              {transactions.length === 0 ? (
                <div className="empty-state">
                  <p>No transactions yet.</p>
                </div>
              ) : (
                <div className="history-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Symbol</th>
                        <th>Type</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Amount</th>
                        <th>Balance After</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transactions.map((txn) => (
                        <tr key={txn.id}>
                          <td>
                            {new Date(txn.created_at).toLocaleString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </td>
                          <td className="symbol-cell">{txn.symbol}</td>
                          <td>
                            <span className={`type-badge ${txn.transaction_type.toLowerCase()}`}>
                              {txn.transaction_type}
                            </span>
                          </td>
                          <td>{txn.quantity}</td>
                          <td>${txn.price.toFixed(2)}</td>
                          <td
                            className={txn.transaction_type === 'BUY' ? 'negative' : 'positive'}
                          >
                            {txn.transaction_type === 'BUY' ? '-' : '+'}
                            ${txn.total_amount.toFixed(2)}
                          </td>
                          <td>${txn.balance_after.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;