from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

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
    
@router.get("/weekly-usage")
def get_weekly_drinking_windows(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Get the past 7 days
    today = datetime.now().date()
    past_week = [today - timedelta(days=i) for i in range(7)]
    user_id = current_user.id

    # Query to fetch applicable windows for the past week
    query = f"""
        WITH date_series AS (
            SELECT generate_series(
                NOW()::date - interval '6 days',
                NOW()::date,
                interval '1 day'
            )::date AS active_date
        ),
        active_windows AS (
            SELECT
                ds.active_date,
                dw.id AS window_id,
                dw.start_time,
                dw.end_time,
                dw.duration_hours,
                dw.repeat_pattern,
                dw.is_active,
                dw.created_at,
                dw.updated_at
            FROM date_series ds
            LEFT JOIN drinking_windows dw
                ON dw.user_id = :user_id
                AND dw.created_at::date <= ds.active_date
                AND (dw.is_active OR dw.updated_at::date >= ds.active_date)
        )
        SELECT DISTINCT ON (active_date)
            active_date,
            window_id,
            start_time,
            end_time,
            duration_hours,
            repeat_pattern,
            is_active,
            created_at,
            updated_at
        FROM active_windows
        ORDER BY active_date ASC, created_at DESC;
    """
    result = db.execute(query, {"user_id": user_id}).fetchall()

    # Format the results
    return [
        {
            "active_date": row["active_date"],
            "window_id": row["window_id"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "duration_hours": row["duration_hours"],
            "repeat_pattern": row["repeat_pattern"],
            "is_active": row["is_active"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        for row in result
    ]

@router.post("/", response_model=DrinkingWindowOut)
def create_drinking_window(
    drinking_window: DrinkingWindowCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check if user already has an active drinking window
    existing_active_window = db.query(DrinkingWindow).filter(
        DrinkingWindow.user_id == current_user.id,
        DrinkingWindow.is_active == True
    ).first()

    if existing_active_window:
        raise HTTPException(
            status_code=400,
            detail="You already have an active drinking window. Please deactivate it before creating a new one."
        )

    # Calculate end_time based on start_time and duration_hours
    start_time = drinking_window.start_time
    duration_hours = drinking_window.duration_hours
    end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=duration_hours)).time()

    # Create the new drinking window
    new_window = DrinkingWindow(
        start_time=start_time,
        end_time=end_time,
        duration_hours=duration_hours,
        repeat_pattern=drinking_window.repeat_pattern,
        is_active=drinking_window.is_active,
        user_id=current_user.id,
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
    # Fetch the drinking window belonging to the current user
    window = db.query(DrinkingWindow).filter(
        DrinkingWindow.id == window_id,
        DrinkingWindow.user_id == current_user.id
    ).first()

    if not window:
        raise HTTPException(status_code=404, detail="Drinking window not found")

    # If activating a window, deactivate all other windows
    if window_update.is_active and not window.is_active:
        # Deactivate all other active windows
        db.query(DrinkingWindow).filter(
            DrinkingWindow.user_id == current_user.id,
            DrinkingWindow.is_active == True,
            DrinkingWindow.id != window_id
        ).update({"is_active": False}, synchronize_session=False)

    # Update fields dynamically based on the provided values
    update_data = window_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(window, key, value)

    # Recalculate the end_time if the start_time or duration_hours are updated
    if "start_time" in update_data or "duration_hours" in update_data:
        window.end_time = (
            datetime.combine(datetime.today(), window.start_time) +
            timedelta(hours=window.duration_hours)
        ).time()

    # Commit the changes to the database and refresh the window instance
    db.commit()
    db.refresh(window)

    # Return the updated window, FastAPI will automatically use DrinkingWindowOut to serialize it
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


