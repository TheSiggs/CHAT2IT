from sqlalchemy.orm import Session
from src.Entity.User import User
from src.Repository.AuthTokenRepository import get_auth_token


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_auth_token(db: Session, auth_token: str):
    user = get_auth_token(db=db, auth_token=auth_token)
    if user:
        user_id = user.user_id
        return db.query(User).filter(User.id == user_id).first()
    else:
        return None

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session):
    db_user = User()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
