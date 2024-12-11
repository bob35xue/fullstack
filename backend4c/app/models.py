import uuid
import sqlalchemy as sa
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .database import Base
from passlib.context import CryptContext
import pytz
from zoneinfo import ZoneInfo
import time

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get local timezone
local_tz = datetime.now().astimezone().tzinfo

# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    issues = relationship("Issue", back_populates="user")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_code = Column(Integer)
    product_name = Column(String)
    response = Column(String)
    created_at = Column(DateTime(timezone=True))
    user = relationship("User", back_populates="issues")

    @staticmethod
    def get_current_time():
        """Get current time in local timezone"""
        return datetime.now(local_tz)

# Pydantic Models for API
class UserBase(BaseModel):
    email: str
    full_name: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True

class IssueBase(BaseModel):
    query: str

class IssueCreate(IssueBase):
    pass

class IssueInDB(IssueBase):
    id: int
    response: str
    product_code: int
    product_name: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True