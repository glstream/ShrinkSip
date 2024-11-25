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
        

class DrinkingWindowBase(BaseModel):
    start_time: time
    end_time: time
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
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
    repeat_pattern: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DrinkEntryBase(BaseModel):
    drink_type: str
    quantity: float
    timestamp: Optional[datetime] = datetime.utcnow()

class DrinkEntryCreate(DrinkEntryBase):
    pass

class DrinkEntryOut(DrinkEntryBase):
    id: int
    user_id: int
    is_within_drinking_window: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None