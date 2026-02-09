"""
Paper Trading Platform - Backend API
FastAPI server with authentication and trading
"""
import os
from market_data import market_service
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List, Optional
from pydantic import BaseModel
import uvicorn
import json

from database import engine, get_db, Base
from models import User, Portfolio, Order, Transaction, OrderType, OrderStatus, Strategy, BacktestResult, StrategyType, StrategyStatus
from auth import (
    UserCreate, UserResponse, Token,
    create_user, authenticate_user, create_access_token,
    get_current_active_user, get_user_by_email, get_user_by_username,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from trading import (
    execute_buy_order, execute_sell_order,
    get_user_portfolio, get_user_orders, get_user_transactions
)
from strategy_engine import strategy_engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Paper Trading Platform API",
    description="Backend API with authentication and trading",
    version="0.3.0"
)

# Configure CORS
# Allow requests from frontend (update for production)
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative React port
    "http://127.0.0.1:5173",
    os.getenv("ALLOWED_ORIGINS", ""),  # Production frontend URL
]

# Remove empty strings
origins = [origin for origin in origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],  # Allow all if no origins specified
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Pydantic Schemas for Trading =====

class OrderCreate(BaseModel):
    """Schema for creating an order"""
    symbol: str
    order_type: str  # "BUY" or "SELL"
    quantity: float
    price: float


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: int
    symbol: str
    order_type: str
    quantity: float
    price: float
    total_amount: float
    status: str
    created_at: datetime
    executed_at: datetime = None

    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    """Schema for portfolio position"""
    id: int
    symbol: str
    quantity: float
    average_price: float
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Schema for transaction"""
    id: int
    symbol: str
    transaction_type: str
    quantity: float
    price: float
    total_amount: float
    balance_before: float
    balance_after: float
    created_at: datetime

    class Config:
        from_attributes = True

# ===== Public Endpoints =====

@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "Paper Trading Platform API is running!",
        "version": "0.3.0",
        "status": "healthy",
        "features": ["authentication", "trading", "portfolio", "orders"]
    }


@app.get("/api/hello")
async def hello():
    """Test endpoint"""
    return {
        "message": "Hello from the trading backend!",
        "checkpoint": "2 - Trading Engine"
    }


# ===== Authentication Endpoints =====

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if username already exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create user
    new_user = create_user(db=db, user=user)
    return new_user


@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get JWT token"""
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user


@app.get("/api/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """Get user profile with trading account info"""
    return current_user


# ===== Trading Endpoints =====

@app.post("/api/orders/create", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create and execute a new order (BUY or SELL)
    """
    # Validate order type
    if order_data.order_type.upper() not in ["BUY", "SELL"]:
        raise HTTPException(
            status_code=400,
            detail="Order type must be 'BUY' or 'SELL'"
        )
    
    # Validate quantity and price
    if order_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )
    
    if order_data.price <= 0:
        raise HTTPException(
            status_code=400,
            detail="Price must be greater than 0"
        )
    
    # Execute order based on type
    try:
        if order_data.order_type.upper() == "BUY":
            order = execute_buy_order(
                db=db,
                user=current_user,
                symbol=order_data.symbol,
                quantity=order_data.quantity,
                price=order_data.price
            )
        else:  # SELL
            order = execute_sell_order(
                db=db,
                user=current_user,
                symbol=order_data.symbol,
                quantity=order_data.quantity,
                price=order_data.price
            )
        
        return order
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute order: {str(e)}"
        )


@app.get("/api/portfolio", response_model=List[PortfolioResponse])
async def get_portfolio(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's current portfolio (all positions)
    """
    portfolio = get_user_portfolio(db, current_user.id)
    return portfolio


@app.get("/api/orders", response_model=List[OrderResponse])
async def get_orders(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's order history
    """
    orders = get_user_orders(db, current_user.id, limit)
    return orders


@app.get("/api/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's transaction history
    """
    transactions = get_user_transactions(db, current_user.id, limit)
    return transactions

# ===== Market Data Endpoints =====

@app.get("/api/market/search")
async def search_stocks(
    query: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for stocks by symbol
    """
    if not query or len(query) < 1:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 1 character"
        )
    
    results = market_service.search_stock(query)
    return {"results": results}


@app.get("/api/market/stock/{symbol}")
async def get_stock_info(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a stock
    """
    stock_data = market_service.get_stock_info(symbol)
    
    if not stock_data:
        raise HTTPException(
            status_code=404,
            detail=f"Stock symbol '{symbol}' not found"
        )
    
    return stock_data


@app.get("/api/market/price/{symbol}")
async def get_stock_price(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current price for a stock
    """
    price = market_service.get_current_price(symbol)
    
    if price is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch price for '{symbol}'"
        )
    
    return {
        "symbol": symbol.upper(),
        "price": price,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/market/history/{symbol}")
async def get_stock_history(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d",
    current_user: User = Depends(get_current_active_user)
):
    """
    Get historical price data for charts
    
    Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    historical_data = market_service.get_historical_data(symbol, period, interval)
    
    if not historical_data:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch historical data for '{symbol}'"
        )
    
    return {
        "symbol": symbol.upper(),
        "period": period,
        "interval": interval,
        "data": historical_data
    }


@app.get("/api/market/status")
async def get_market_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current market status
    """
    return market_service.get_market_status()

# ===== Strategy/Bot Endpoints =====

class StrategyCreate(BaseModel):
    """Schema for creating a strategy"""
    name: str
    description: Optional[str] = None
    strategy_type: str  # "SMA_CROSSOVER", "RSI", "MACD"
    parameters: dict  # Strategy-specific parameters


class StrategyResponse(BaseModel):
    """Schema for strategy response"""
    id: int
    name: str
    description: Optional[str]
    strategy_type: str
    parameters: str
    status: str
    total_trades: int
    winning_trades: int
    total_profit_loss: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class BacktestRequest(BaseModel):
    """Schema for backtest request"""
    strategy_type: str
    symbol: str
    parameters: dict
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    initial_capital: float = 10000.0


class BacktestResponse(BaseModel):
    """Schema for backtest results"""
    id: int
    strategy_id: Optional[int]
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    trades: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@app.post("/api/strategies/create", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new trading strategy/bot
    """
    # Validate strategy type
    valid_types = ["SMA_CROSSOVER", "RSI", "MACD"]
    if strategy.strategy_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Create strategy
    new_strategy = Strategy(
        user_id=current_user.id,
        name=strategy.name,
        description=strategy.description,
        strategy_type=StrategyType[strategy.strategy_type],
        parameters=json.dumps(strategy.parameters),
        status=StrategyStatus.INACTIVE
    )
    
    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)
    
    return new_strategy


@app.get("/api/strategies", response_model=List[StrategyResponse])
async def get_user_strategies(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all strategies for current user
    """
    strategies = db.query(Strategy).filter(
        Strategy.user_id == current_user.id
    ).order_by(Strategy.created_at.desc()).all()
    
    return strategies


@app.get("/api/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific strategy
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return strategy


@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a strategy
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete(strategy)
    db.commit()
    
    return {"message": "Strategy deleted successfully"}


@app.post("/api/strategies/backtest")
async def backtest_strategy(
    backtest: BacktestRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Run a backtest for a strategy
    Returns performance metrics and trade history
    """
    try:
        # Validate and parse dates (ensure timezone-naive for database)
        try:
            start_date = datetime.strptime(backtest.start_date, '%Y-%m-%d').replace(tzinfo=None)
            end_date = datetime.strptime(backtest.end_date, '%Y-%m-%d').replace(tzinfo=None)
        except ValueError as ve:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format. Use YYYY-MM-DD: {str(ve)}"
            )
        
        if start_date >= end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )
        
        # Run backtest based on strategy type
        result = None
        
        if backtest.strategy_type == "SMA_CROSSOVER":
            params = backtest.parameters
            if 'short_period' not in params or 'long_period' not in params:
                raise HTTPException(
                    status_code=400,
                    detail="SMA_CROSSOVER requires 'short_period' and 'long_period' parameters"
                )
            
            result = strategy_engine.sma_crossover_strategy(
                symbol=backtest.symbol,
                short_period=int(params['short_period']),
                long_period=int(params['long_period']),
                start_date=backtest.start_date,
                end_date=backtest.end_date,
                initial_capital=backtest.initial_capital
            )
        
        elif backtest.strategy_type == "RSI":
            params = backtest.parameters
            if 'rsi_period' not in params or 'oversold' not in params or 'overbought' not in params:
                raise HTTPException(
                    status_code=400,
                    detail="RSI requires 'rsi_period', 'oversold', and 'overbought' parameters"
                )
            
            result = strategy_engine.rsi_strategy(
                symbol=backtest.symbol,
                rsi_period=int(params['rsi_period']),
                oversold_threshold=int(params['oversold']),
                overbought_threshold=int(params['overbought']),
                start_date=backtest.start_date,
                end_date=backtest.end_date,
                initial_capital=backtest.initial_capital
            )
        
        elif backtest.strategy_type == "MACD":
            result = strategy_engine.macd_strategy(
                symbol=backtest.symbol,
                start_date=backtest.start_date,
                end_date=backtest.end_date,
                initial_capital=backtest.initial_capital
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid strategy type"
            )
        
        # Check for errors
        if 'error' in result:
            raise HTTPException(
                status_code=400,
                detail=result['error']
            )
        
        # Save backtest result
        backtest_result = BacktestResult(
            strategy_id=None,  # Not linked to a strategy yet
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            initial_capital=backtest.initial_capital,
            final_capital=result['final_capital'],
            total_return=result['total_return'],
            total_trades=result['total_trades'],
            winning_trades=result['winning_trades'],
            losing_trades=result['losing_trades'],
            win_rate=result['win_rate'],
            trades=json.dumps(result['trades'])
        )
        
        db.add(backtest_result)
        db.commit()
        db.refresh(backtest_result)
        
        return {
            "backtest_id": backtest_result.id,
            "results": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@app.get("/api/backtests", response_model=List[BacktestResponse])
async def get_backtests(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get backtest history for current user
    """
    backtests = db.query(BacktestResult).filter(
        BacktestResult.user_id == current_user.id
    ).order_by(BacktestResult.created_at.desc()).limit(limit).all()
    
    return backtests


@app.get("/api/backtests/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific backtest result
    """
    backtest = db.query(BacktestResult).filter(
        BacktestResult.id == backtest_id,
        BacktestResult.user_id == current_user.id
    ).first()
    
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    return backtest

# ===== Analytics Endpoints =====

@app.get("/api/analytics/portfolio-performance")
async def get_portfolio_performance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio performance over time (equity curve)
    """
    # Get all transactions ordered by date
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.asc()).all()
    
    if not transactions:
        return {
            "equity_curve": [],
            "total_profit_loss": 0,
            "total_return_percent": 0
        }
    
    # Build equity curve
    equity_curve = []
    initial_balance = 100000.0  # Starting balance
    
    for txn in transactions:
        equity_curve.append({
            "date": txn.created_at.strftime('%Y-%m-%d'),
            "balance": round(txn.balance_after, 2),
            "profit_loss": round(txn.balance_after - initial_balance, 2)
        })
    
    # Calculate metrics
    current_balance = transactions[-1].balance_after if transactions else initial_balance
    total_profit_loss = current_balance - initial_balance
    total_return_percent = (total_profit_loss / initial_balance) * 100
    
    return {
        "equity_curve": equity_curve,
        "total_profit_loss": round(total_profit_loss, 2),
        "total_return_percent": round(total_return_percent, 2),
        "initial_balance": initial_balance,
        "current_balance": round(current_balance, 2)
    }


@app.get("/api/analytics/trade-statistics")
async def get_trade_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed trading statistics
    """
    # Get all executed orders
    orders = db.query(Order).filter(
        Order.user_id == current_user.id,
        Order.status == OrderStatus.EXECUTED
    ).all()
    
    if not orders:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0,
            "average_win": 0,
            "average_loss": 0,
            "largest_win": 0,
            "largest_loss": 0,
            "profit_factor": 0
        }
    
    # Pair buy and sell orders
    buy_orders = [o for o in orders if o.order_type == OrderType.BUY]
    sell_orders = [o for o in orders if o.order_type == OrderType.SELL]
    
    wins = []
    losses = []
    
    # Simple P&L calculation (match orders by symbol)
    for sell in sell_orders:
        # Find corresponding buy
        buys = [b for b in buy_orders if b.symbol == sell.symbol and b.created_at < sell.created_at]
        if buys:
            buy = buys[-1]  # Most recent buy before this sell
            profit = (sell.price - buy.price) * min(buy.quantity, sell.quantity)
            if profit > 0:
                wins.append(profit)
            else:
                losses.append(abs(profit))
    
    total_trades = len(wins) + len(losses)
    winning_trades = len(wins)
    losing_trades = len(losses)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    average_win = sum(wins) / len(wins) if wins else 0
    average_loss = sum(losses) / len(losses) if losses else 0
    largest_win = max(wins) if wins else 0
    largest_loss = max(losses) if losses else 0
    
    total_wins = sum(wins)
    total_losses = sum(losses)
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": round(win_rate, 2),
        "average_win": round(average_win, 2),
        "average_loss": round(average_loss, 2),
        "largest_win": round(largest_win, 2),
        "largest_loss": round(largest_loss, 2),
        "profit_factor": round(profit_factor, 2)
    }


@app.get("/api/analytics/backtest-comparison")
async def compare_backtests(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compare all backtest results
    """
    backtests = db.query(BacktestResult).filter(
        BacktestResult.user_id == current_user.id
    ).order_by(BacktestResult.created_at.desc()).limit(10).all()
    
    if not backtests:
        return {"backtests": []}
    
    comparison = []
    for bt in backtests:
        comparison.append({
            "id": bt.id,
            "date": bt.created_at.strftime('%Y-%m-%d'),
            "total_return": round(bt.total_return, 2),
            "total_trades": bt.total_trades,
            "win_rate": round(bt.win_rate, 2),
            "initial_capital": bt.initial_capital,
            "final_capital": bt.final_capital
        })
    
    return {"backtests": comparison}


@app.get("/api/analytics/risk-metrics")
async def get_risk_metrics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Calculate risk-adjusted performance metrics
    """
    # Get all transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.asc()).all()
    
    if len(transactions) < 2:
        return {
            "sharpe_ratio": 0,
            "max_drawdown": 0,
            "max_drawdown_percent": 0,
            "volatility": 0
        }
    
    # Calculate daily returns
    returns = []
    for i in range(1, len(transactions)):
        prev_balance = transactions[i-1].balance_after
        curr_balance = transactions[i].balance_after
        daily_return = (curr_balance - prev_balance) / prev_balance
        returns.append(daily_return)
    
    if not returns:
        return {
            "sharpe_ratio": 0,
            "max_drawdown": 0,
            "max_drawdown_percent": 0,
            "volatility": 0
        }
    
    # Calculate metrics
    import numpy as np
    
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    
    # Sharpe Ratio (assuming risk-free rate of 0 for simplicity)
    sharpe_ratio = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0
    
    # Max Drawdown
    balances = [t.balance_after for t in transactions]
    peak = balances[0]
    max_drawdown = 0
    max_drawdown_percent = 0
    
    for balance in balances:
        if balance > peak:
            peak = balance
        drawdown = peak - balance
        drawdown_percent = (drawdown / peak * 100) if peak > 0 else 0
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            max_drawdown_percent = drawdown_percent
    
    # Volatility (annualized)
    volatility = std_return * np.sqrt(252) * 100
    
    return {
        "sharpe_ratio": round(float(sharpe_ratio), 2),
        "max_drawdown": round(float(max_drawdown), 2),
        "max_drawdown_percent": round(float(max_drawdown_percent), 2),
        "volatility": round(float(volatility), 2)
    }

# ===== AI Strategy Builder Endpoints =====

class AIStrategyRequest(BaseModel):
    """Schema for AI strategy generation request"""
    prompt: str
    

class AIStrategyOptimizeRequest(BaseModel):
    """Schema for strategy optimization request"""
    strategy_type: str
    symbol: str
    parameters: dict


@app.post("/api/ai/generate-strategy")
async def generate_strategy_from_prompt(
    request: AIStrategyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate strategy parameters from natural language
    """
    try:
        # Import here to avoid issues
        from ai_strategy_service import ai_strategy_service
        
        result = ai_strategy_service.parse_strategy_request(request.prompt)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate strategy: {str(e)}"
        )


@app.post("/api/ai/optimize-strategy")
async def optimize_strategy_parameters(
    request: AIStrategyOptimizeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered parameter optimization suggestions
    """
    try:
        from ai_strategy_service import ai_strategy_service
        
        result = ai_strategy_service.optimize_strategy(
            request.strategy_type,
            request.symbol,
            request.parameters
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize strategy: {str(e)}"
        )


@app.post("/api/ai/explain-results")
async def explain_backtest_results(
    results: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get plain English explanation of backtest results
    """
    try:
        from ai_strategy_service import ai_strategy_service
        
        explanation = ai_strategy_service.explain_backtest_results(results)
        return {"explanation": explanation}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to explain results: {str(e)}"
        )

# Run server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )