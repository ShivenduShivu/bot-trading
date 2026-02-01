/**
 * API Helper Functions
 * Centralized API calls to backend
 */

const API_BASE_URL = 'http://localhost:8000';

// ===== Authentication =====

export const registerUser = async (userData) => {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return await response.json();
};

export const loginUser = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return await response.json();
};

export const getUserProfile = async (token) => {
  const response = await fetch(`${API_BASE_URL}/api/profile`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch profile');
  }

  return await response.json();
};

// ===== Token Management =====

export const saveToken = (token) => {
  localStorage.setItem('access_token', token);
};

export const getToken = () => {
  return localStorage.getItem('access_token');
};

export const removeToken = () => {
  localStorage.removeItem('access_token');
};

export const isAuthenticated = () => {
  return !!getToken();
};

// ===== Trading API =====

/**
 * Create a new order (BUY or SELL)
 */
export const createOrder = async (orderData) => {
  const token = getToken();
  
  const response = await fetch(`${API_BASE_URL}/api/orders/create`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(orderData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create order');
  }

  return await response.json();
};

/**
 * Get user's portfolio
 */
export const getPortfolio = async () => {
  const token = getToken();
  
  const response = await fetch(`${API_BASE_URL}/api/portfolio`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch portfolio');
  }

  return await response.json();
};

/**
 * Get user's order history
 */
export const getOrders = async (limit = 50) => {
  const token = getToken();
  
  const response = await fetch(`${API_BASE_URL}/api/orders?limit=${limit}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch orders');
  }

  return await response.json();
};

/**
 * Get user's transaction history
 */
export const getTransactions = async (limit = 50) => {
  const token = getToken();
  
  const response = await fetch(`${API_BASE_URL}/api/transactions?limit=${limit}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch transactions');
  }

  return await response.json();
};

// ===== Market Data API =====

/**
 * Search for stocks
 */
export const searchStocks = async (query) => {
  const token = getToken();
  
  const response = await fetch(`${API_BASE_URL}/api/market/search?query=${encodeURIComponent(query)}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to search stocks');
  }

  return await response.json();
};

/**
 * Get detailed stock information
 */
export const getStockInfo = async (symbol) => {
  const token = getToken();
  
  const response = await fetch(`${API_BASE_URL}/api/market/stock/${symbol}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch stock info for ${symbol}`);
  }

  return await response.json();
};

/**
 * Get current stock price
 */
export const getStockPrice = async (symbol) => {
  const token = getToken();
  
  const response = await fetch(`${API_BASE_URL}/api/market/price/${symbol}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch price for ${symbol}`);
  }

  return await response.json();
};

/**
 * Get historical stock data for charts
 */
export const getStockHistory = async (symbol, period = '1mo', interval = '1d') => {
  const token = getToken();
  
  const response = await fetch(
    `${API_BASE_URL}/api/market/history/${symbol}?period=${period}&interval=${interval}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch historical data for ${symbol}`);
  }

  return await response.json();
};

/**
 * Get market status
 */
export const getMarketStatus = async () => {
  const token = getToken();
  
  const response = await fetch(`${API_BASE_URL}/api/market/status`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch market status');
  }

  return await response.json();
};