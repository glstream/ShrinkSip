# models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Time, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, time

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    timezone = Column(String(50), default='UTC')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    drinking_windows = relationship("DrinkingWindow", back_populates="user")
    drink_logs = relationship("DrinkLog", back_populates="user")


class DrinkingWindow(Base):
    __tablename__ = 'drinking_windows'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)  # Pre-calculated
    duration_hours = Column(Integer, nullable=False)  # Store duration as well
    repeat_pattern = Column(String(50), default='daily')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    # Relationships
    user = relationship("User", back_populates="drinking_windows")

class DrinkLog(Base):
    __tablename__ = "drink_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    drink_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)  # E.g., 1 beer, 0.5 wine glass
    timestamp = Column(DateTime, default=datetime.utcnow)
    logged_in_window = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="drink_logs")