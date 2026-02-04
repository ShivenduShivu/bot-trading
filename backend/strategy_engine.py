"""
Strategy Engine
Implements trading strategies and backtesting logic
"""

import pandas as pd
import talib as ta
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

from market_data import market_service


class StrategyEngine:
    """
    Core engine for executing trading strategies
    """
    
    def __init__(self):
        self.market_service = market_service
    
    def calculate_sma(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data['close'].rolling(window=period).mean()
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        rsi_values = ta.RSI(data['close'].values, timeperiod=period)
        return pd.Series(rsi_values, index=data.index)
    
    def calculate_macd(self, data: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        macd, signal, hist = ta.MACD(
            data['close'].values,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )
        return (
            pd.Series(macd, index=data.index),
            pd.Series(signal, index=data.index),
            pd.Series(hist, index=data.index)
        )
    
    def sma_crossover_strategy(
        self,
        symbol: str,
        short_period: int,
        long_period: int,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000.0
    ) -> Dict:
        """
        SMA Crossover Strategy
        Buy when short SMA crosses above long SMA
        Sell when short SMA crosses below long SMA
        """
        # Get historical data
        days_diff = (datetime.strptime(end_date, '%Y-%m-%d') - 
                     datetime.strptime(start_date, '%Y-%m-%d')).days
        
        if days_diff <= 30:
            period = '1mo'
        elif days_diff <= 90:
            period = '3mo'
        elif days_diff <= 180:
            period = '6mo'
        else:
            period = '1y'
        
        historical_data = self.market_service.get_historical_data(symbol, period, '1d')
        
        if not historical_data:
            return {"error": "Failed to fetch historical data"}
        
        # Convert to DataFrame and strip timezone at parse time
        df = pd.DataFrame(historical_data)
        
        # Parse dates and immediately strip timezone
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
        df = df.set_index('date')
        
        # Convert string dates to datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Filter by date range
        df = df[(df.index >= start_dt) & (df.index <= end_dt)]
        
        if len(df) < long_period:
            return {"error": f"Insufficient data. Need at least {long_period} days, got {len(df)} days"}
        
        # Calculate SMAs
        df['sma_short'] = self.calculate_sma(df, short_period)
        df['sma_long'] = self.calculate_sma(df, long_period)
        
        # Drop NaN values
        df = df.dropna()
        
        if len(df) == 0:
            return {"error": "No valid data after calculating indicators"}
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['sma_short'] > df['sma_long'], 'signal'] = 1  # Buy signal
        df.loc[df['sma_short'] < df['sma_long'], 'signal'] = -1  # Sell signal
        
        # Detect crossovers
        df['position'] = df['signal'].diff()
        
        # Backtest
        return self._backtest_signals(df, initial_capital, symbol)
    
    def rsi_strategy(
        self,
        symbol: str,
        rsi_period: int,
        oversold_threshold: int,
        overbought_threshold: int,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000.0
    ) -> Dict:
        """
        RSI Strategy
        Buy when RSI < oversold_threshold (e.g., 30)
        Sell when RSI > overbought_threshold (e.g., 70)
        """
        # Get historical data
        days_diff = (datetime.strptime(end_date, '%Y-%m-%d') - 
                     datetime.strptime(start_date, '%Y-%m-%d')).days
        
        if days_diff <= 30:
            period = '1mo'
        elif days_diff <= 90:
            period = '3mo'
        elif days_diff <= 180:
            period = '6mo'
        else:
            period = '1y'
        
        historical_data = self.market_service.get_historical_data(symbol, period, '1d')
        
        if not historical_data:
            return {"error": "Failed to fetch historical data"}
        
        # Convert to DataFrame and strip timezone at parse time
        df = pd.DataFrame(historical_data)
        
        # Parse dates and immediately strip timezone
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
        df = df.set_index('date')
        
        # Convert string dates to datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Filter by date range
        df = df[(df.index >= start_dt) & (df.index <= end_dt)]
        
        # Calculate RSI
        df['rsi'] = self.calculate_rsi(df, rsi_period)
        
        # Drop NaN values
        df = df.dropna()
        
        if len(df) == 0:
            return {"error": "No valid data after calculating RSI"}
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['rsi'] < oversold_threshold, 'signal'] = 1  # Buy signal
        df.loc[df['rsi'] > overbought_threshold, 'signal'] = -1  # Sell signal
        
        # Backtest
        return self._backtest_signals(df, initial_capital, symbol)
    
    def macd_strategy(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000.0
    ) -> Dict:
        """
        MACD Strategy
        Buy when MACD crosses above signal line
        Sell when MACD crosses below signal line
        """
        # Get historical data
        days_diff = (datetime.strptime(end_date, '%Y-%m-%d') - 
                     datetime.strptime(start_date, '%Y-%m-%d')).days
        
        if days_diff <= 30:
            period = '1mo'
        elif days_diff <= 90:
            period = '3mo'
        elif days_diff <= 180:
            period = '6mo'
        else:
            period = '1y'
        
        historical_data = self.market_service.get_historical_data(symbol, period, '1d')
        
        if not historical_data:
            return {"error": "Failed to fetch historical data"}
        
        # Convert to DataFrame and strip timezone at parse time
        df = pd.DataFrame(historical_data)
        
        # Parse dates and immediately strip timezone
        df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
        df = df.set_index('date')
        
        # Convert string dates to datetime
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Filter by date range
        df = df[(df.index >= start_dt) & (df.index <= end_dt)]
        
        # Calculate MACD
        macd, signal, hist = self.calculate_macd(df)
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_hist'] = hist
        
        # Drop NaN values
        df = df.dropna()
        
        if len(df) == 0:
            return {"error": "No valid data after calculating MACD"}
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['macd'] > df['macd_signal'], 'signal'] = 1  # Buy signal
        df.loc[df['macd'] < df['macd_signal'], 'signal'] = -1  # Sell signal
        
        # Backtest
        return self._backtest_signals(df, initial_capital, symbol)
    
    def _backtest_signals(
        self,
        df: pd.DataFrame,
        initial_capital: float,
        symbol: str
    ) -> Dict:
        """
        Execute backtest based on generated signals
        """
        capital = initial_capital
        position = 0  # Number of shares held
        trades = []
        
        for index, row in df.iterrows():
            # Buy signal
            if row['signal'] == 1 and position == 0:
                shares_to_buy = capital // row['close']
                if shares_to_buy > 0:
                    cost = shares_to_buy * row['close']
                    capital -= cost
                    position = shares_to_buy
                    
                    trades.append({
                        'date': index.strftime('%Y-%m-%d'),
                        'type': 'BUY',
                        'price': round(row['close'], 2),
                        'shares': int(shares_to_buy),
                        'total': round(cost, 2)
                    })
            
            # Sell signal
            elif row['signal'] == -1 and position > 0:
                proceeds = position * row['close']
                capital += proceeds
                
                trades.append({
                    'date': index.strftime('%Y-%m-%d'),
                    'type': 'SELL',
                    'price': round(row['close'], 2),
                    'shares': int(position),
                    'total': round(proceeds, 2)
                })
                
                position = 0
        
        # Close any open position at the end
        if position > 0:
            final_value = position * df.iloc[-1]['close']
            capital += final_value
            trades.append({
                'date': df.index[-1].strftime('%Y-%m-%d'),
                'type': 'SELL',
                'price': round(df.iloc[-1]['close'], 2),
                'shares': int(position),
                'total': round(final_value, 2)
            })
        
        final_capital = capital
        total_return = ((final_capital - initial_capital) / initial_capital) * 100
        
        # Calculate metrics
        winning_trades = sum(1 for i in range(0, len(trades)-1, 2) 
                            if i+1 < len(trades) and trades[i+1]['total'] > trades[i]['total'])
        total_trades = len(trades) // 2
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'symbol': symbol,
            'initial_capital': initial_capital,
            'final_capital': round(final_capital, 2),
            'total_return': round(total_return, 2),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': round(win_rate, 2),
            'trades': trades[:50]  # Limit to first 50 trades for response size
        }


# Global instance
strategy_engine = StrategyEngine()