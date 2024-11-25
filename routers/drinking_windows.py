from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import DrinkingWindow
from schemas import DrinkingWindowCreate, DrinkingWindowOut, DrinkingWindowUpdate
from dependencies import get_current_user


# Initialize the router
router = APIRouter(
    prefix="/drinking-windows",
    tags=["Drinking Windows"]
)

@router.get("/", response_model=List[DrinkingWindowOut])
def get_drinking_windows(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    windows = db.query(DrinkingWindow).filter(DrinkingWindow.user_id == current_user.id).all()
    return windows

@router.post("/", response_model=DrinkingWindowOut)
def create_drinking_window(
    drinking_window: DrinkingWindowCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_window = DrinkingWindow(
        **drinking_window.dict(),
        user_id=current_user.id
    )
    db.add(new_window)
    db.commit()
    db.refresh(new_window)
    return new_window

@router.put("/{window_id}", response_model=DrinkingWindowOut)
def update_drinking_window(
    window_id: int,
    window_update: DrinkingWindowUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    window = db.query(DrinkingWindow).filter(
        DrinkingWindow.id == window_id,
        DrinkingWindow.user_id == current_user.id
    ).first()

    if not window:
        raise HTTPException(status_code=404, detail="Drinking window not found")

    for key, value in window_update.dict(exclude_unset=True).items():
        setattr(window, key, value)

    db.commit()
    db.refresh(window)
    return window

@router.delete("/{window_id}", status_code=204)
def delete_drinking_window(
    window_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    window = db.query(DrinkingWindow).filter(
        DrinkingWindow.id == window_id,
        DrinkingWindow.user_id == current_user.id
    ).first()

    if not window:
        raise HTTPException(status_code=404, detail="Drinking window not found")

    db.delete(window)
    db.commit()
    return
