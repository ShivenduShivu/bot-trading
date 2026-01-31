import { useState, useEffect } from 'react';
import { getUserProfile, removeToken } from '../utils/api';
import './Dashboard.css';

function Dashboard({ onLogout }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
      // If token is invalid, logout
      handleLogout();
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    removeToken();
    onLogout();
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

      <div className="dashboard-content">
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

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h4>Market Data</h4>
            <p>Coming in Checkpoint 3</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💹</div>
            <h4>Place Trades</h4>
            <p>Coming in Checkpoint 2</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h4>Trading Bots</h4>
            <p>Coming in Checkpoint 4</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h4>Portfolio</h4>
            <p>Coming in Checkpoint 2</p>
          </div>
        </div>

        <div className="checkpoint-status">
          <h3>✅ Checkpoint 1 Complete!</h3>
          <ul>
            <li>✅ User authentication system</li>
            <li>✅ JWT token-based security</li>
            <li>✅ Protected dashboard</li>
            <li>✅ User profile management</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;