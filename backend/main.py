"""
Paper Trading Platform - Backend API
FastAPI server with authentication and trading
"""
from market_data import market_service
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List
from pydantic import BaseModel
import uvicorn

from database import engine, get_db, Base
from models import User, Portfolio, Order, Transaction, OrderType
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

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Paper Trading Platform API",
    description="Backend API with authentication and trading",
    version="0.3.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

# Run server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )