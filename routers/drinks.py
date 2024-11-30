from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models import DrinkLog, DrinkingWindow
from schemas import DrinkLogCreate, DrinkLogOut
from dependencies import get_current_user
from typing import List

router = APIRouter(
    prefix="/drinks",
    tags=["Drink Logs"]
)

@router.post("/", response_model=DrinkLogOut)
def log_drink(
    drink_log: DrinkLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check if there is an active drinking window
    active_window = db.query(DrinkingWindow).filter(
        DrinkingWindow.user_id == current_user.id,
        DrinkingWindow.is_active == True
    ).first()

    logged_in_window = False  # Default to outside the window

    if active_window:
        # Determine if the drink is within the active window
        if drink_log.timestamp is None:
            drink_log.timestamp = datetime.utcnow()

        drink_time = drink_log.timestamp.time()
        if active_window.start_time <= drink_time <= active_window.end_time:
            logged_in_window = True

    # Log the drink with the calculated status
    new_drink = DrinkLog(
        drink_type=drink_log.drink_type,
        quantity=drink_log.quantity,
        timestamp=drink_log.timestamp,
        logged_in_window=logged_in_window,
        user_id=current_user.id
    )
    db.add(new_drink)
    db.commit()
    db.refresh(new_drink)
    return new_drink

@router.get("/", response_model=List[DrinkLogOut])
def get_drink_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Fetch all drink logs for the current user
    logs = db.query(DrinkLog).filter(DrinkLog.user_id == current_user.id).all()
    
    return logs

@router.get("/weekly-usage", response_model=List[DrinkLogOut])
def get_weekly_logged_drinks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=7)
    drinks = db.query(DrinkLog).filter(
        DrinkLog.user_id == current_user.id,
        DrinkLog.timestamp >= seven_days_ago
    ).all()
    return drinks

@router.get("/summary")
def get_drink_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    logs = db.query(DrinkLog).filter(DrinkLog.user_id == current_user.id).all()
    total_drinks = len(logs)
    in_window = sum(1 for log in logs if log.logged_in_window)
    out_window = total_drinks - in_window

    return {
        "total_drinks": total_drinks,
        "in_window": in_window,
        "out_window": out_window
    }

@router.delete("/{drink_id}", status_code=204)
def delete_drink(
    drink_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Fetch the drink log
    drink = db.query(DrinkLog).filter(
        DrinkLog.id == drink_id,
        DrinkLog.user_id == current_user.id
    ).first()

    if not drink:
        raise HTTPException(status_code=404, detail="Drink log not found")

    # Delete the drink log
    db.delete(drink)
    db.commit()
    return