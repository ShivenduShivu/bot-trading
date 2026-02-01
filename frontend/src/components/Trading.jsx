import { useState, useEffect } from 'react';
import { createOrder, getPortfolio, getUserProfile } from '../utils/api';
import './Trading.css';
import StockSearch from './StockSearch';
import PriceChart from './PriceChart';

function Trading({ onBalanceUpdate }) {
    const [formData, setFormData] = useState({
        symbol: '',
        orderType: 'BUY',
        quantity: '',
        price: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [portfolio, setPortfolio] = useState([]);
    const [balance, setBalance] = useState(0);
    const [selectedSymbol, setSelectedSymbol] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [portfolioData, profileData] = await Promise.all([
                getPortfolio(),
                getUserProfile(localStorage.getItem('access_token'))
            ]);
            setPortfolio(portfolioData);
            setBalance(profileData.virtual_balance);
        } catch (err) {
            console.error('Failed to load data:', err);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
        setSuccess('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        // Validation
        if (!formData.symbol || !formData.quantity || !formData.price) {
            setError('All fields are required');
            return;
        }

        if (parseFloat(formData.quantity) <= 0) {
            setError('Quantity must be greater than 0');
            return;
        }

        if (parseFloat(formData.price) <= 0) {
            setError('Price must be greater than 0');
            return;
        }

        setLoading(true);

        try {
            const orderData = {
                symbol: formData.symbol.toUpperCase(),
                order_type: formData.orderType,
                quantity: parseFloat(formData.quantity),
                price: parseFloat(formData.price)
            };

            const order = await createOrder(orderData);

            const total = order.total_amount;
            const action = order.order_type === 'BUY' ? 'Bought' : 'Sold';

            setSuccess(
                `✅ ${action} ${order.quantity} shares of ${order.symbol} @ $${order.price} (Total: $${total.toFixed(2)})`
            );

            // Reset form
            setFormData({
                symbol: '',
                orderType: 'BUY',
                quantity: '',
                price: ''
            });

            // Reload portfolio and balance
            await loadData();

            // Notify parent component
            if (onBalanceUpdate) {
                onBalanceUpdate();
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const calculatePositionValue = (position) => {
        return position.quantity * position.average_price;
    };

    const getTotalPortfolioValue = () => {
        return portfolio.reduce((sum, pos) => sum + calculatePositionValue(pos), 0);
    };

    return (
        <div className="trading-container">
            <div className="trading-header">
                <h2>📊 Trading Dashboard</h2>
                <div className="balance-indicator">
                    <span className="balance-label">Available Balance:</span>
                    <span className="balance-value">
                        ${balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                </div>
            </div>

            <div className="trading-content">
                {/* Order Form */}
                <div className="order-form-card">
                    <h3>Place Order</h3>

                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <div className="form-group full-width">
                                <label>Search & Select Stock</label>
                                <StockSearch
                                    onStockSelect={(stock) => {
                                        setFormData({
                                            ...formData,
                                            symbol: stock.symbol,
                                            price: stock.current_price.toString()
                                        });
                                        setSelectedSymbol(stock.symbol);
                                    }}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="orderType">Order Type</label>
                                <select
                                    id="orderType"
                                    name="orderType"
                                    value={formData.orderType}
                                    onChange={handleChange}
                                >
                                    <option value="BUY">Buy</option>
                                    <option value="SELL">Sell</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="quantity">Quantity</label>
                                <input
                                    type="number"
                                    id="quantity"
                                    name="quantity"
                                    value={formData.quantity}
                                    onChange={handleChange}
                                    placeholder="Number of shares"
                                    step="0.01"
                                    min="0"
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="price">Price per Share</label>
                                <input
                                    type="number"
                                    id="price"
                                    name="price"
                                    value={formData.price}
                                    onChange={handleChange}
                                    placeholder="Price in USD"
                                    step="0.01"
                                    min="0"
                                />
                            </div>
                        </div>

                        {formData.quantity && formData.price && (
                            <div className="order-summary">
                                <span>Total:</span>
                                <span className="total-amount">
                                    ${(parseFloat(formData.quantity || 0) * parseFloat(formData.price || 0)).toFixed(2)}
                                </span>
                            </div>
                        )}

                        {error && (
                            <div className="error-message">
                                ❌ {error}
                            </div>
                        )}

                        {success && (
                            <div className="success-message">
                                {success}
                            </div>
                        )}

                        <button
                            type="submit"
                            className={`order-button ${formData.orderType.toLowerCase()}`}
                            disabled={loading}
                        >
                            {loading ? '⏳ Processing...' : `${formData.orderType === 'BUY' ? '💰 Buy' : '💸 Sell'} Shares`}
                        </button>
                    </form>
                </div>

                {/* Portfolio */}
                <div className="portfolio-card">
                    <h3>📈 Your Portfolio</h3>

                    {portfolio.length === 0 ? (
                        <div className="empty-state">
                            <p>No positions yet. Start trading to build your portfolio!</p>
                        </div>
                    ) : (
                        <>
                            <div className="portfolio-summary">
                                <div className="summary-item">
                                    <span className="summary-label">Total Positions:</span>
                                    <span className="summary-value">{portfolio.length}</span>
                                </div>
                                <div className="summary-item">
                                    <span className="summary-label">Portfolio Value:</span>
                                    <span className="summary-value">
                                        ${getTotalPortfolioValue().toLocaleString('en-US', { minimumFractionDigits: 2 })}
                                    </span>
                                </div>
                            </div>

                            <div className="portfolio-list">
                                {portfolio.map((position) => (
                                    <div key={position.id} className="portfolio-item">
                                        <div className="position-header">
                                            <span className="position-symbol">{position.symbol}</span>
                                            <span className="position-quantity">
                                                {position.quantity} shares
                                            </span>
                                        </div>
                                        <div className="position-details">
                                            <div className="detail-item">
                                                <span className="detail-label">Avg Price:</span>
                                                <span className="detail-value">
                                                    ${position.average_price.toFixed(2)}
                                                </span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">Total Value:</span>
                                                <span className="detail-value">
                                                    ${calculatePositionValue(position).toFixed(2)}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                </div>
            </div>
            {/* Price Chart */}
            {selectedSymbol && (
                <div className="chart-section">
                    <PriceChart symbol={selectedSymbol} />
                </div>
            )}
        </div>
    );
}

export default Trading;