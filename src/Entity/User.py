from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from src.Database.Database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True)
    is_active = Column(Boolean, default=True)

    sessions = relationship('Session', back_populates="user")
    auth_tokens = relationship('AuthToken', back_populates="user")

