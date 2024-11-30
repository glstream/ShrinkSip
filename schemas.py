# schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, time

class UserBase(BaseModel):
    email: EmailStr

class User(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    timezone: str
    created_at: datetime

    class Config:
        orm_mode = True
        



class DrinkLogBase(BaseModel):
    drink_type: str
    quantity: float
    timestamp: Optional[datetime] = None  # Defaults to now if not provided

# DrinkLog Create Schema
class DrinkLogCreate(DrinkLogBase):
    pass

# DrinkLog Output Schema
class DrinkLogOut(BaseModel):
    id: int
    user_id: int
    drink_type: str
    quantity: float
    timestamp: datetime
    logged_in_window: bool  

    class Config:
        orm_mode = True

class DrinkingWindowBase(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_hours: Optional[int] = None
    repeat_pattern: Optional[str] = 'daily'
    is_active: Optional[bool] = True

class DrinkingWindowCreate(DrinkingWindowBase):
    pass

class DrinkingWindowUpdate(DrinkingWindowBase):
    pass

class DrinkingWindowOut(BaseModel):
    id: int
    user_id: int
    start_time: time
    end_time: time
    duration_hours: int  # Include in the output schema
    repeat_pattern: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None