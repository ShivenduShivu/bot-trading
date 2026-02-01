"""
Market Data Service
Handles fetching real-time and historical stock data
Uses yfinance for data retrieval
"""

import yfinance as yf
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import pandas as pd
from fastapi import HTTPException


class MarketDataService:
    """
    Service to fetch stock market data
    """
    
    def __init__(self):
        # Cache for stock info (to avoid excessive API calls)
        self._cache = {}
        self._cache_duration = timedelta(minutes=5)
    
    def search_stock(self, query: str) -> List[Dict]:
        """
        Search for stocks by symbol or company name
        Returns list of matching stocks
        """
        try:
            # For now, we'll validate if symbol exists
            # In production, use a proper search API
            query = query.upper().strip()
            
            # Try to get stock info
            ticker = yf.Ticker(query)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return []
            
            return [{
                'symbol': info.get('symbol', query),
                'name': info.get('longName', info.get('shortName', 'N/A')),
                'exchange': info.get('exchange', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'type': info.get('quoteType', 'EQUITY')
            }]
        except Exception as e:
            print(f"Search error for {query}: {str(e)}")
            return []
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed information about a stock
        """
        try:
            symbol = symbol.upper().strip()
            
            # Check cache
            cache_key = f"info_{symbol}"
            if cache_key in self._cache:
                cached_data, cached_time = self._cache[cache_key]
                if datetime.now() - cached_time < self._cache_duration:
                    return cached_data
            
            # Fetch from API
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                return None
            
            # Extract relevant information
            stock_data = {
                'symbol': info.get('symbol', symbol),
                'name': info.get('longName', info.get('shortName', 'N/A')),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'previous_close': info.get('previousClose', 0),
                'open': info.get('open', info.get('regularMarketOpen', 0)),
                'day_high': info.get('dayHigh', info.get('regularMarketDayHigh', 0)),
                'day_low': info.get('dayLow', info.get('regularMarketDayLow', 0)),
                'volume': info.get('volume', info.get('regularMarketVolume', 0)),
                'market_cap': info.get('marketCap', 0),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'N/A'),
            }
            
            # Calculate price change
            if stock_data['current_price'] and stock_data['previous_close']:
                change = stock_data['current_price'] - stock_data['previous_close']
                change_percent = (change / stock_data['previous_close']) * 100
                stock_data['change'] = round(change, 2)
                stock_data['change_percent'] = round(change_percent, 2)
            else:
                stock_data['change'] = 0
                stock_data['change_percent'] = 0
            
            # Cache the data
            self._cache[cache_key] = (stock_data, datetime.now())
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a stock
        Quick method for price checks
        """
        try:
            symbol = symbol.upper().strip()
            ticker = yf.Ticker(symbol)
            
            # Try fast method first
            data = ticker.fast_info
            if hasattr(data, 'last_price'):
                return float(data.last_price)
            
            # Fallback to info
            info = ticker.info
            price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            return float(price) if price else None
            
        except Exception as e:
            print(f"Error fetching price for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[List[Dict]]:
        """
        Get historical price data for charts
        
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        try:
            symbol = symbol.upper().strip()
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return None
            
            # Convert to list of dicts
            data = []
            for index, row in hist.iterrows():
                data.append({
                    'date': index.isoformat(),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2),
                    'volume': int(row['Volume'])
                })
            
            return data
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a stock symbol is valid
        """
        try:
            symbol = symbol.upper().strip()
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info and info['symbol'] == symbol
        except:
            return False
    
    def get_market_status(self) -> Dict:
        """
        Get current market status
        """
        # This is simplified - in production, check actual exchange hours
        now = datetime.now()
        
        # US market hours (EST): 9:30 AM - 4:00 PM
        # This is a simplified check
        is_weekend = now.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        return {
            'is_open': not is_weekend,  # Simplified
            'message': 'Market is open' if not is_weekend else 'Market is closed',
            'timezone': 'EST'
        }


# Global instance
market_service = MarketDataService()