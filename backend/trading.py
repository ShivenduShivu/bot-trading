"""
Trading Logic
Handles order execution, portfolio management, and transactions
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models import User, Portfolio, Order, Transaction, OrderType, OrderStatus
from datetime import datetime
from typing import Optional


def get_portfolio_position(db: Session, user_id: int, symbol: str) -> Optional[Portfolio]:
    """
    Get user's position for a specific symbol
    """
    return db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.symbol == symbol
    ).first()


def update_or_create_portfolio(
    db: Session,
    user_id: int,
    symbol: str,
    quantity: float,
    price: float,
    is_buy: bool
):
    """
    Update portfolio after trade execution
    
    For BUY: Add to position, update average price
    For SELL: Remove from position
    """
    position = get_portfolio_position(db, user_id, symbol)
    
    if is_buy:
        if position:
            # Update existing position
            # Calculate new average price: weighted average
            total_cost = (position.quantity * position.average_price) + (quantity * price)
            new_quantity = position.quantity + quantity
            position.average_price = total_cost / new_quantity
            position.quantity = new_quantity
            position.updated_at = datetime.utcnow()
        else:
            # Create new position
            position = Portfolio(
                user_id=user_id,
                symbol=symbol,
                quantity=quantity,
                average_price=price
            )
            db.add(position)
    else:  # SELL
        if position:
            position.quantity -= quantity
            position.updated_at = datetime.utcnow()
            
            # If position is now 0 or negative, remove it
            if position.quantity <= 0:
                db.delete(position)
    
    db.commit()


def execute_buy_order(
    db: Session,
    user: User,
    symbol: str,
    quantity: float,
    price: float
) -> Order:
    """
    Execute a BUY order
    
    Steps:
    1. Validate user has enough balance
    2. Create order record
    3. Deduct balance
    4. Update portfolio
    5. Create transaction record
    """
    total_cost = quantity * price
    
    # Validation
    if user.virtual_balance < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Required: ${total_cost:.2f}, Available: ${user.virtual_balance:.2f}"
        )
    
    # Create order
    order = Order(
        user_id=user.id,
        symbol=symbol.upper(),
        order_type=OrderType.BUY,
        quantity=quantity,
        price=price,
        total_amount=total_cost,
        status=OrderStatus.EXECUTED,
        executed_at=datetime.utcnow()
    )
    db.add(order)
    db.flush()  # Get order.id without committing
    
    # Update user balance
    balance_before = user.virtual_balance
    user.virtual_balance -= total_cost
    balance_after = user.virtual_balance
    
    # Update portfolio
    update_or_create_portfolio(db, user.id, symbol.upper(), quantity, price, is_buy=True)
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        order_id=order.id,
        symbol=symbol.upper(),
        transaction_type=OrderType.BUY,
        quantity=quantity,
        price=price,
        total_amount=total_cost,
        balance_before=balance_before,
        balance_after=balance_after
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(order)
    
    return order


def execute_sell_order(
    db: Session,
    user: User,
    symbol: str,
    quantity: float,
    price: float
) -> Order:
    """
    Execute a SELL order
    
    Steps:
    1. Validate user has enough shares
    2. Create order record
    3. Add balance
    4. Update portfolio
    5. Create transaction record
    """
    # Check if user has this position
    position = get_portfolio_position(db, user.id, symbol.upper())
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You don't own any shares of {symbol}"
        )
    
    if position.quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient shares. You own {position.quantity}, trying to sell {quantity}"
        )
    
    total_proceeds = quantity * price
    
    # Create order
    order = Order(
        user_id=user.id,
        symbol=symbol.upper(),
        order_type=OrderType.SELL,
        quantity=quantity,
        price=price,
        total_amount=total_proceeds,
        status=OrderStatus.EXECUTED,
        executed_at=datetime.utcnow()
    )
    db.add(order)
    db.flush()
    
    # Update user balance
    balance_before = user.virtual_balance
    user.virtual_balance += total_proceeds
    balance_after = user.virtual_balance
    
    # Update portfolio
    update_or_create_portfolio(db, user.id, symbol.upper(), quantity, price, is_buy=False)
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        order_id=order.id,
        symbol=symbol.upper(),
        transaction_type=OrderType.SELL,
        quantity=quantity,
        price=price,
        total_amount=total_proceeds,
        balance_before=balance_before,
        balance_after=balance_after
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(order)
    
    return order


def get_user_portfolio(db: Session, user_id: int):
    """
    Get all portfolio positions for a user
    """
    return db.query(Portfolio).filter(Portfolio.user_id == user_id).all()


def get_user_orders(db: Session, user_id: int, limit: int = 50):
    """
    Get user's order history
    """
    return db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.created_at.desc()).limit(limit).all()


def get_user_transactions(db: Session, user_id: int, limit: int = 50):
    """
    Get user's transaction history
    """
    return db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.created_at.desc()).limit(limit).all()