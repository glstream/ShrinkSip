from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import timedelta, datetime
from typing import Optional
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


from database import get_db
from schemas import UserCreate, UserOut, Token
from models import User
from dependencies import get_password_hash, verify_password, authenticate_user, create_access_token

# Initialize the router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=hashed_password,
        timezone='UTC'  # Or get from user input
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

