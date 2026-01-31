"""
Paper Trading Platform - Backend API
FastAPI server with authentication
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import uvicorn

from database import engine, get_db, Base
from models import User
from auth import (
    UserCreate, UserResponse, Token,
    create_user, authenticate_user, create_access_token,
    get_current_active_user, get_user_by_email, get_user_by_username,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Paper Trading Platform API",
    description="Backend API with authentication for paper trading",
    version="0.2.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Public Endpoints =====

@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "Paper Trading Platform API is running!",
        "version": "0.2.0",
        "status": "healthy",
        "features": ["authentication", "user_management"]
    }


@app.get("/api/hello")
async def hello():
    """Test endpoint"""
    return {
        "message": "Hello from the trading backend!",
        "checkpoint": "1 - Authentication System"
    }


# ===== Authentication Endpoints =====

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
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
    """
    Login and get JWT token
    """
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


# ===== Protected Endpoints (Require Authentication) =====

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile
    Requires valid JWT token
    """
    return current_user


@app.get("/api/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get user profile with trading account info
    """
    return current_user


# Run server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )