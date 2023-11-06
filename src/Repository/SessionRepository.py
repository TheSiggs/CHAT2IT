import uuid

from sqlalchemy.orm import Session
from src.Entity.Session import Session as SessionEmbedding
from src.Schema.Session.SessionCreate import SessionCreate

def get_session(db: Session, session_id: int):
    return db.query(SessionEmbedding).filter(SessionEmbedding.id == session_id).first()


def get_session_by_session_id(db: Session, session_id: str):
    return db.query(SessionEmbedding).filter(SessionEmbedding.session_id == session_id).first()

def get_sessions_by_user(db: Session, user_id: int):
    return db.query(SessionEmbedding).filter(SessionEmbedding.user_id == user_id).all()


def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SessionEmbedding).offset(skip).limit(limit).all()


def create_session(db: Session, user_id: str, session_id: uuid):
    db_item = SessionEmbedding(user_id=int(user_id), session_id=str(session_id))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
