"""
AI Strategy Service - Using Google Gemini (Fallback-First Approach)
Since Gemini API is having issues, we use keyword fallback as primary
"""

import os
import json
from typing import Dict


class AIStrategyService:
    """
    Service for strategy generation
    Uses keyword-based parsing (reliable, free, instant)
    """
    
    def __init__(self):
        pass
    
    def parse_strategy_request(self, user_prompt: str) -> Dict:
        """
        Convert natural language to strategy parameters
        
        Args:
            user_prompt: User's description of desired strategy
            
        Returns:
            Dictionary with strategy type and parameters
        """
        return self._parse_with_keywords(user_prompt)
    
    def optimize_strategy(self, strategy_type: str, symbol: str, base_params: Dict) -> Dict:
        """
        Suggest parameter optimizations
        
        Args:
            strategy_type: Type of strategy
            symbol: Stock symbol
            base_params: Current parameters
            
        Returns:
            Suggested optimizations
        """
        return self._create_optimizations(base_params)
    
    def explain_backtest_results(self, results: Dict) -> str:
        """
        Explain backtest results
        
        Args:
            results: Backtest results dictionary
            
        Returns:
            Plain English explanation
        """
        total_return = results.get('total_return', 0)
        total_trades = results.get('total_trades', 0)
        win_rate = results.get('win_rate', 0)
        
        if total_return > 10:
            performance = "excellent"
        elif total_return > 5:
            performance = "good"
        elif total_return > 0:
            performance = "modest"
        elif total_return > -5:
            performance = "slightly negative"
        else:
            performance = "poor"
        
        return f"This strategy showed {performance} performance with a {total_return:.2f}% return over the test period. It executed {total_trades} trades with a {win_rate:.1f}% win rate. {'This suggests the strategy has potential and could be refined further.' if total_return > 0 else 'Consider adjusting parameters or trying a different strategy for this stock.'}"
    
    def _parse_with_keywords(self, user_prompt: str) -> Dict:
        """
        Keyword-based strategy parsing
        Fast, reliable, and free!
        """
        prompt_lower = user_prompt.lower()
        
        # Detect strategy type
        if any(word in prompt_lower for word in ['rsi', 'oversold', 'overbought', 'relative strength']):
            strategy_type = "RSI"
            parameters = {"rsi_period": 14, "oversold": 30, "overbought": 70}
            explanation = "RSI strategy: Buys when RSI drops below 30 (oversold), sells when it rises above 70 (overbought). Works best in range-bound markets where prices oscillate."
            
        elif any(word in prompt_lower for word in ['macd', 'convergence', 'divergence']):
            strategy_type = "MACD"
            parameters = {}
            explanation = "MACD strategy: Buys when MACD line crosses above signal line (bullish crossover), sells when it crosses below (bearish crossover). Effective in trending markets."
            
        else:
            # Default to SMA Crossover
            strategy_type = "SMA_CROSSOVER"
            
            # Try to detect period numbers
            import re
            numbers = re.findall(r'\b(\d+)[-\s]?(?:day|period|ma|sma)\b', prompt_lower)
            if len(numbers) >= 2:
                short_period = min(int(numbers[0]), int(numbers[1]))
                long_period = max(int(numbers[0]), int(numbers[1]))
            else:
                short_period = 10
                long_period = 30
            
            parameters = {"short_period": short_period, "long_period": long_period}
            explanation = f"Moving average crossover: Buys when {short_period}-period MA crosses above {long_period}-period MA (golden cross), sells on death cross. Classic trend-following strategy."
        
        # Detect symbol
        symbol_map = {
            'aapl': 'AAPL', 'apple': 'AAPL',
            'tsla': 'TSLA', 'tesla': 'TSLA',
            'msft': 'MSFT', 'microsoft': 'MSFT',
            'googl': 'GOOGL', 'goog': 'GOOGL', 'google': 'GOOGL',
            'amzn': 'AMZN', 'amazon': 'AMZN',
            'nvda': 'NVDA', 'nvidia': 'NVDA',
            'meta': 'META', 'facebook': 'META',
            'spy': 'SPY', 's&p': 'SPY',
            'qqq': 'QQQ', 'nasdaq': 'QQQ'
        }
        
        symbol = 'SPY'  # Default
        for key, val in symbol_map.items():
            if key in prompt_lower:
                symbol = val
                break
        
        # Detect timeframe
        if '1 month' in prompt_lower or '1mo' in prompt_lower:
            backtest_period = '1mo'
        elif '3 month' in prompt_lower or '3mo' in prompt_lower:
            backtest_period = '3mo'
        elif '1 year' in prompt_lower or '1y' in prompt_lower or '12 month' in prompt_lower:
            backtest_period = '1y'
        else:
            backtest_period = '6mo'
        
        # Determine confidence
        if any(x in prompt_lower for x in ['rsi', 'macd', 'moving average', 'crossover']):
            confidence = 'high'
        elif len(prompt_lower.split()) > 10:
            confidence = 'medium'
        else:
            confidence = 'medium'
        
        print(f"✅ Parsed strategy: {strategy_type} for {symbol} (keyword-based)")
        
        return {
            "strategy_type": strategy_type,
            "parameters": parameters,
            "symbol": symbol,
            "backtest_period": backtest_period,
            "explanation": explanation,
            "confidence": confidence
        }
    
    def _create_optimizations(self, base_params: Dict) -> Dict:
        """
        Generate parameter optimizations
        """
        if 'short_period' in base_params:
            # SMA optimization
            short = base_params['short_period']
            long = base_params['long_period']
            
            return {
                "conservative": {
                    "short_period": int(short * 1.5),
                    "long_period": int(long * 1.3),
                    "explanation": "Longer periods reduce noise and false signals, but may lag true trend changes"
                },
                "balanced": {
                    "short_period": short,
                    "long_period": long,
                    "explanation": "Standard parameters balance signal frequency with reliability"
                },
                "aggressive": {
                    "short_period": max(5, int(short * 0.7)),
                    "long_period": int(long * 0.8),
                    "explanation": "Shorter periods catch trends earlier but generate more false signals"
                },
                "recommendation": "Start with balanced parameters, then try conservative if you get too many false signals, or aggressive if you're missing trends"
            }
        else:
            # RSI optimization  
            return {
                "conservative": {
                    "rsi_period": base_params.get('rsi_period', 14),
                    "oversold": 20,
                    "overbought": 80,
                    "explanation": "Extreme thresholds mean fewer but stronger signals"
                },
                "balanced": {
                    "rsi_period": base_params.get('rsi_period', 14),
                    "oversold": 30,
                    "overbought": 70,
                    "explanation": "Standard RSI thresholds used by most traders"
                },
                "aggressive": {
                    "rsi_period": base_params.get('rsi_period', 14),
                    "oversold": 40,
                    "overbought": 60,
                    "explanation": "Moderate thresholds generate more frequent trading opportunities"
                },
                "recommendation": "Balanced parameters work well for most stocks. Adjust based on the stock's typical volatility."
            }


# Global instance
ai_strategy_service = AIStrategyService()