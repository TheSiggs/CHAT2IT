from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.Database.Database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(length=255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now, index=True)
    last_queried = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True)
    is_active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'))  # ForeignKey must refer to 'users.id'
    user = relationship("User", back_populates="sessions")
