from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.Database.Database import Base


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True)
    is_active = Column(Boolean, default=True)
    queries = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey must refer to 'users.id'
    user = relationship("User", back_populates="auth_tokens")
    
