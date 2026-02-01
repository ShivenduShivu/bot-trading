"""
Database Models
Defines all database tables for the trading platform
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class User(Base):
    """
    User table - stores user account information
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User credentials
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # User profile
    full_name = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Virtual trading account
    virtual_balance = Column(Float, default=100000.0)  # Start with $100k
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class Portfolio(Base):
    """
    Portfolio table - stores user's current stock holdings
    Each row represents a position in a specific stock
    """
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stock information
    symbol = Column(String, nullable=False, index=True)  # e.g., "AAPL", "GOOGL"
    quantity = Column(Float, nullable=False, default=0.0)  # Number of shares
    average_price = Column(Float, nullable=False)  # Average buy price
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="portfolio")

    def __repr__(self):
        return f"<Portfolio {self.symbol}: {self.quantity} shares>"


class OrderType(str, enum.Enum):
    """Enum for order types"""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, enum.Enum):
    """Enum for order status"""
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class Order(Base):
    """
    Order table - stores all buy/sell orders
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order details
    symbol = Column(String, nullable=False, index=True)
    order_type = Column(Enum(OrderType), nullable=False)  # BUY or SELL
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)  # Price per share
    total_amount = Column(Float, nullable=False)  # quantity * price
    
    # Order status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)

    # Relationship
    user = relationship("User", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.order_type} {self.quantity} {self.symbol} @ ${self.price}>"


class Transaction(Base):
    """
    Transaction table - historical record of all executed trades
    This is the audit trail
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Transaction details (denormalized for historical record)
    symbol = Column(String, nullable=False, index=True)
    transaction_type = Column(Enum(OrderType), nullable=False)  # BUY or SELL
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Balance snapshot
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.transaction_type} {self.quantity} {self.symbol}>"