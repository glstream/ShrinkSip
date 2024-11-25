from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserOut
from models import User
from dependencies import get_current_user, get_password_hash

# Initialize the router
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=UserOut)
def read_users_me(
    current_user: User = Depends(get_current_user),
):
    """Retrieve the currently logged-in user's profile."""
    return current_user


@router.get("/protected-endpoint")
def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.email}!"}

